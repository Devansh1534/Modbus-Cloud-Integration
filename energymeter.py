from pymodbus.client.serial import ModbusSerialClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
import mysql.connector
from datetime import datetime

#MySQL connection
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="root",
  database="mydb"
)
# Modbus client
client = ModbusSerialClient(method='rtu', port='COM6', baudrate=9600, stopbits=1, bytesize=8, parity='E')
client.connect()

def hex_to_binary(hex_str):
    binary_str = bin(int(hex_str, 16))[2:].zfill(16)
    return binary_str

def main(result_registers):
    hex_value_0 = format(result_registers[0], 'X').zfill(4) 
    hex_value_1 = format(result_registers[1], 'X').zfill(4) 
    binary_0 = hex_to_binary(hex_value_0)
    binary_1 = hex_to_binary(hex_value_1)
    concatenated_binary = binary_1 + binary_0
    return concatenated_binary

result = client.read_holding_registers(address=142, count=2, slave=1)
result_registers = result.registers

concatenated_binary = main(result_registers)

def binary_to_float(binary_str):
    sign_bit = int(binary_str[0])
    exponent_bits = binary_str[1:9]
    fraction_bits = binary_str[9:]
    exponent = int(exponent_bits, 2) - 127
    fraction = 1
    for i in range(len(fraction_bits)):
        fraction += int(fraction_bits[i]) * 2**(-1 - i)
    value = (-1) ** sign_bit * fraction * 2 ** exponent
    return value

result = binary_to_float(concatenated_binary)
voltage = result


mycursor = mydb.cursor()
sql = "INSERT INTO energydata (voltage, event_timestamp) VALUES (%s, %s)"
current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
voltage_val = voltage
mycursor.execute(sql, (voltage_val, current_timestamp))
mydb.commit()
mycursor.close()
mydb.close()

print(result)