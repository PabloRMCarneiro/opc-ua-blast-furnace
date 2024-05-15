from asyncua.common.subscription import DataChangeNotif, SubHandler
from asyncua import Client, Node
import asyncio
import sys
import os
from dotenv import load_dotenv

load_dotenv()

HOST                 = os.getenv('HOST')
PORT                 = int(os.getenv('PORT'))

SERVER_ENDPOINT_OPC  = str(os.getenv('SERVER_ENDPOINT_OPC'))
NODE_TEMPERATURE     = str(os.getenv('NODE_TEMPERATURE'))
NODE_REF_TEMPERATURE = str(os.getenv('NODE_REF_TEMPERATURE'))
NODE_HEAT_FLOW       = str(os.getenv('NODE_HEAT_FLOW'))
NODE_KP              = str(os.getenv('NODE_KP'))
NODE_KI              = str(os.getenv('NODE_KI'))
NODE_KD              = str(os.getenv('NODE_KD'))


def create_log_error(message):
    with open('./files/log_error.txt', 'a') as file:
        file.write(message + '\n')

class HandlerOPCNodes(SubHandler):
    def __init__(self):
        self._queue = asyncio.Queue()
        self.client_writer = None 

    async def get_node_name(self, node: Node):
        display_name = await node.read_attribute(4)
        return display_name.Value.Value.Text
    
    async def datachange_notification(self, node: Node, value, data: DataChangeNotif) -> None:
        timestamp = data.monitored_item.Value.SourceTimestamp.strftime('%Y-%m-%d %H:%M:%S')
        node_name = await self.get_node_name(node)
        if (value and timestamp) != None:
            message = f'{node_name},{value},{timestamp}'
            print(f'\033[92m{str(node_name).ljust(25)} : {str(value).ljust(20)} | Timestamp: {timestamp}\033[0m')
            if self.client_writer:
                await send_to_client(self.client_writer, message)

handler = HandlerOPCNodes()

async def send_to_client(writer, message):
    try:
        writer.write(message.encode())
        await writer.drain()
        print('\n' + f"\033[95m{'SEND TO CLIENT'.ljust(25)} : {message.ljust(20)}\033[0m" + '\n')
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        create_log_error(f'{__file__} - {exc_tb.tb_lineno} - {str(e)}')

async def write_values_opc(node_name, value):
    async with Client(url=SERVER_ENDPOINT_OPC) as client:

        if node_name.upper() == 'REF_TEMPERATURE':
            node = client.get_node(NODE_REF_TEMPERATURE)
            await node.write_value(value)
        elif node_name.upper() == 'KP':
            node = client.get_node(NODE_KP)
            await node.write_value(value)
        elif node_name.upper() == 'KI':
            node = client.get_node(NODE_KI)
            await node.write_value(value)
        elif node_name.upper() == 'KD':
            node = client.get_node(NODE_KD)
            await node.write_value(value)

async def handle_client(reader, writer):
    addr = writer.get_extra_info('peername')
    connetion_message = f"\033[93mCONNECTION OF {addr} ACCEPTED\033[0m"
    print('\n' + '-'*90)
    print(connetion_message.center(90))
    print('-'*90 + '\n')

    try:
        while True:

            global handler
            handler.client_writer = writer

            request = await reader.read(1024)
            if not request:
                return 
            
            received_message = request.decode('utf-8').split(',')
            if len(received_message) == 2:
                print('\n' + '-'*90)
                print(f"\033[94m{'RECEIVED FROM CLIENT'.ljust(25)} : {received_message[0].ljust(20)} | Value: {received_message[1]}\033[0m")
                print('-'*90 + '\n')

                node_name, value = received_message
                await write_values_opc(node_name, float(value))

    except Exception as e:
        create_log_error(f'{__file__} - {sys.exc_info()[2].tb_lineno} - {str(e)}')

async def start_server():
    server = await asyncio.start_server(handle_client, HOST, PORT)
    async with server:
        header_message = f"\033[96mSERVER STARTED AT {HOST}:{PORT}\033[0m"
        print('-'*90)
        print(header_message.center(90))
        print('-'*90+'\n')
        await server.serve_forever()

async def sub_nodes_opc():
    async with Client(url=SERVER_ENDPOINT_OPC) as client:
        node_temperature = client.get_node(NODE_TEMPERATURE)
        node_ref_temperature = client.get_node(NODE_REF_TEMPERATURE)
        node_heat_flow = client.get_node(NODE_HEAT_FLOW)
        node_kp = client.get_node(NODE_KP)
        node_ki = client.get_node(NODE_KI)
        node_kd = client.get_node(NODE_KD)

        global handler
        subscription_temperature = await client.create_subscription(period=0, handler=handler)
        await subscription_temperature.subscribe_data_change(node_temperature)

        subscription_desired_temperature = await client.create_subscription(period=0, handler=handler)
        await subscription_desired_temperature.subscribe_data_change(node_ref_temperature)

        subscription_heat_flow = await client.create_subscription(period=0, handler=handler)
        await subscription_heat_flow.subscribe_data_change(node_heat_flow)

        subscription_kp = await client.create_subscription(period=0, handler=handler)
        await subscription_kp.subscribe_data_change(node_kp)

        subscription_ki = await client.create_subscription(period=0, handler=handler)
        await subscription_ki.subscribe_data_change(node_ki)

        subscription_kd = await client.create_subscription(period=0, handler=handler)
        await subscription_kd.subscribe_data_change(node_kd)

        while True:
            await asyncio.sleep(0.1)

async def main():
    server_task = asyncio.create_task(start_server())  
    opc_task = asyncio.create_task(sub_nodes_opc())
    await asyncio.gather(server_task, opc_task)

if __name__ == "__main__":
    asyncio.run(main())
