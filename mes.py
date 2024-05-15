from asyncua.common.subscription import DataChangeNotif, SubHandler
from asyncua import Client, Node
from dotenv import load_dotenv
import asyncio
import os

load_dotenv()

SERVER_ENDPOINT_OPC = os.getenv('SERVER_ENDPOINT_OPC')
NODE_TEMPERATURE    = os.getenv('NODE_TEMPERATURE')


class HandlerTemperatureOPCNode(SubHandler):
    def __init__(self):
        self._queue = asyncio.Queue()

    async def get_node_name(self, node: Node):
        display_name = await node.read_attribute(4)
        return display_name.Value.Value.Text
    
    async def datachange_notification(self, node: Node, value, data: DataChangeNotif) -> None:
        timestamp = data.monitored_item.Value.SourceTimestamp.strftime('%Y-%m-%d %H:%M:%S')
        node_name = await self.get_node_name(node)
        
        if (value and timestamp) != None:
            print(f'\033[92m{str(node_name)} : {str(value).ljust(20)} | Timestamp: {timestamp}\033[0m')

            with open('./files/mes.txt', 'a') as file:
                file.write(f'{node_name},{value},{timestamp}\n')

async def sub_node_temperature_opc() -> None:
    async with Client(url=SERVER_ENDPOINT_OPC) as client:
        node_temperature = client.get_node(NODE_TEMPERATURE)

        handler = HandlerTemperatureOPCNode()
        subscription = await client.create_subscription(period=0, handler=handler)
        await subscription.subscribe_data_change(node_temperature)

        while True:
            await asyncio.sleep(0.1)

if __name__ == '__main__':
    asyncio.run(sub_node_temperature_opc())
