from opcua import Server, Subscription
import time
import os
import platform
from dotenv import load_dotenv

load_dotenv()


SERVER_ENDPOINT_OPC  = os.getenv('SERVER_ENDPOINT_OPC')

server = Server()

server.set_endpoint(SERVER_ENDPOINT_OPC)
server.set_server_name('FreeOpcUa Server')

uri = 'http://example.org'
idx = server.register_namespace(uri)

objects = server.nodes.objects
variable_obj = objects.add_object(idx, 'TP_SDA')

temperature = variable_obj.add_variable(idx, 'TEMPERATURE', 0)
temperature.set_writable()

ref_temperature = variable_obj.add_variable(idx, 'REF_TEMPERATURE', 0)
ref_temperature.set_writable()

heat_flow = variable_obj.add_variable(idx, 'HEAT_FLOW', 0)
heat_flow.set_writable()

kp = variable_obj.add_variable(idx, 'KP', 0)
kp.set_writable()

ki = variable_obj.add_variable(idx, 'KI', 0)
ki.set_writable()

kd = variable_obj.add_variable(idx, 'KD', 0)
kd.set_writable()

server.start()

try:
    while True:
      os.system('clear' if platform.system() == 'Linux' else 'cls')
      print(f'\033[96m{"OPC UA server is up and running!".upper().center(50)}\033[0m')
      print('-'*50)
      print('Temperature Control System OPC UA Server'.upper().center(50))
      print('-'*50)
      print(f'\033[31m{temperature.get_display_name().Text.ljust(25)}: {str(temperature.get_value()).ljust(25)}\033[0m')
      print(f'\033[91m{heat_flow.get_display_name().Text.ljust(25)}: {str(heat_flow.get_value()).ljust(25)}\033[0m')
      print(f'\033[32m{ref_temperature.get_display_name().Text.ljust(25)}: {str(ref_temperature.get_value()).ljust(25)}\033[0m')
      print(f'\033[92m{kp.get_display_name().Text.ljust(25)}: {str(kp.get_value()).ljust(25)}\033[0m')
      print(f'\033[93m{ki.get_display_name().Text.ljust(25)}: {str(ki.get_value()).ljust(25)}\033[0m')
      print(f'\033[94m{kd.get_display_name().Text.ljust(25)}: {str(kd.get_value()).ljust(25)}\033[0m')
      print('-'*50)

      time.sleep(1/30)
except KeyboardInterrupt:
    print('OPC UA server is shutting down')
    server.stop()
