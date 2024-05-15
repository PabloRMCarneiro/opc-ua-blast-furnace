from asyncua.common.subscription import DataChangeNotif, SubHandler
from asyncua import Client, Node
import numpy as np
import threading
import asyncio
import time
import os
import platform
from dotenv import load_dotenv
from typing import List

load_dotenv()


SERVER_ENDPOINT_OPC  = os.getenv('SERVER_ENDPOINT_OPC')
NODE_TEMPERATURE     = os.getenv('NODE_TEMPERATURE')
NODE_REF_TEMPERATURE = os.getenv('NODE_REF_TEMPERATURE')
NODE_HEAT_FLOW       = os.getenv('NODE_HEAT_FLOW')
NODE_KP              = os.getenv('NODE_KP')
NODE_KI              = os.getenv('NODE_KI')
NODE_KD              = os.getenv('NODE_KD')

# Parâmetros do forno 
C_m = 1000  # Capacidade térmica do material (J/K)
T_amb = 300  # Temperatura ambiente (K)
R = 10  # Resistência térmica (K/W)
dt = 1

# Parâmetros do controlador
KP = 5
KI = 2
KD = 1
temperature = [T_amb]
ref_temperature = T_amb
erro = [0, ref_temperature - temperature[0]]
heat_flow = [28]



def temperature_derivate(T, Q):
    dTdt = (Q / C_m) - ((T - T_amb) / R)
    return dTdt

def simulation_blast_furnace(last_temperature, last_heat_flow, dt):
    k1 = temperature_derivate(last_temperature, last_heat_flow)
    k2 = temperature_derivate(last_temperature + 0.5 * dt * k1, last_heat_flow)
    k3 = temperature_derivate(last_temperature + 0.5 * dt * k2, last_heat_flow)
    k4 = temperature_derivate(last_temperature + dt * k3, last_heat_flow)
    
    dTdt = (k1 + 2 * k2 + 2 * k3 + k4) / 6.0
    
    current_temperature = last_temperature + dTdt * dt
    
    return current_temperature

def PID_controller(erro):
    erro = np.array(erro)
    erro_anterior = erro[-2]
    erro_atual = erro[-1]

    curent_heat_flow = KP * erro_atual + KI * np.sum(erro) + KD * (erro_atual - erro_anterior)

    return curent_heat_flow

def run_simulation():

    asyncio.run(write_values_opc([NODE_KP, NODE_KI, NODE_KD, NODE_REF_TEMPERATURE], [KP, KI, KD, ref_temperature]))

    i = 1
    while True:
        os.system('clear' if platform.system() == 'Linux' else 'cls')
        print('\033[96mSIMULATION\033[0m\n'.center(45))
        print('-'*45)

        start = time.time()

        heat_flow.append(PID_controller(erro))
        temperature.append(simulation_blast_furnace(temperature[i-1], heat_flow[i-1], dt))
        erro.append(ref_temperature - temperature[i])
        
        asyncio.run(write_values_opc([NODE_TEMPERATURE, NODE_HEAT_FLOW], [temperature[i], heat_flow[i]]))

        print(f'\033[31m{"TEMPERATURE".ljust(15)}: {str(temperature[-1]).ljust(20)} K\033[0m')
        print(f'\033[91m{"HEAT_FLOW".ljust(15)}: {str(heat_flow[-1]).ljust(20)} W\033[0m')
        print(f'\033[32m{"REF_TEMPERATURE".ljust(15)}: {str(ref_temperature).ljust(20)} K\033[0m\n')

        print(f'\033[92m{"KP".ljust(15)}: {str(KP).ljust(20)}\033[0m')
        print(f'\033[93m{"KI".ljust(15)}: {str(KI).ljust(20)}\033[0m')
        print(f'\033[94m{"KD".ljust(15)}: {str(KD).ljust(20)}\033[0m')

        print('-'*45)
        print(f'Timestamp: {time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())}')

        end = time.time()

        if end - start < 1:
            time.sleep((1 - (end - start)))
        else:
            time.sleep(1)

        i += 1

async def write_values_opc(node_names: List, values: List):
    async with Client(url=SERVER_ENDPOINT_OPC) as client:
        for node_name, value in zip(node_names, values):
            node = client.get_node(node_name)
            await node.write_value(float(value))

class HandlerOPCNodes(SubHandler):
    def __init__(self):
        self._queue = asyncio.Queue()

    async def get_node_name(self, node: Node):
        display_name = await node.read_attribute(4)
        return display_name.Value.Value.Text
    
    async def datachange_notification(self, node: Node, value, data: DataChangeNotif) -> None:
        global ref_temperature, KP, KI, KD

        node_name = await self.get_node_name(node)
        if node_name.upper() == 'REF_TEMPERATURE':
            if value != None:
                ref_temperature = value
        elif node_name.upper() == 'KP':
            if value != None:
                KP = value
        elif node_name.upper() == 'KI':
            if value != None:
                KI = value
        elif node_name.upper() == 'KD':
            if value != None:
                KD = value

async def sub_nodes_opc() -> None:
    async with Client(url=SERVER_ENDPOINT_OPC) as client:
        node_ref_temperature = client.get_node(NODE_REF_TEMPERATURE)
        node_kp = client.get_node(NODE_KP)
        node_ki = client.get_node(NODE_KI)
        node_kd = client.get_node(NODE_KD)

        handler = HandlerOPCNodes()

        subscription_ref_temperature = await client.create_subscription(period=0, handler=handler)
        await subscription_ref_temperature.subscribe_data_change(node_ref_temperature)

        subscription_kp = await client.create_subscription(period=0, handler=handler)
        await subscription_kp.subscribe_data_change(node_kp)

        subscription_ki = await client.create_subscription(period=0, handler=handler)


        await subscription_ki.subscribe_data_change(node_ki)

        subscription_kd = await client.create_subscription(period=0, handler=handler)
        await subscription_kd.subscribe_data_change(node_kd)


        while True:
            await asyncio.sleep(0.01)

if __name__ == '__main__':

    threading.Thread(target=run_simulation).start()
    asyncio.run(sub_nodes_opc())