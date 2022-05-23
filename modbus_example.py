import random
import time

from pymodbus.client.sync import ModbusSerialClient

client = ModbusSerialClient(method="rtu", port="COM4", stopbits=1, bytesize=8, parity='N', baudrate=19200)
print(client.connect())
try:
    result = client.read_holding_registers(address=0, count=1, unit=1)
    print(result.registers)  # Returns attribute error if result don't have recv registers
except AttributeError:
    print("No connection")
while True:
    result = client.read_holding_registers(0, 1, unit=1)
    print(result.registers)
    time.sleep(.1)


# # Запись регистра на позицию 40001 со значением 15
# write_result = client.write_register(1, 118, unit=1)
# print(write_result)
# write_result = client.write_registers(0, [1, 2, 3, 4, 0, 0, 1], unit=1)
# print(write_result)
#
# try:
#     result = client.read_holding_registers(address=0, count=30, unit=1)
#     print(result.registers)  # Returns attribute error if result don't have recv registers
# except AttributeError:
#     print("No connection")

# result = client.write_coil(0, 0)
# result = client.write_coil(1, 0)


# result = client.read_coils(address=0, count=10, unit=1)
# print(result.bits)

# # Чтение 10 регистров начиная с 40001 адреса
# try:
#     result = client.read_holding_registers(address=40001, count=10, unit=1)
#     print(result.registers)  # Returns attribute error if result don't have recv registers
# except AttributeError:
#     print("No connection")
#
#
# # Запись регистра на позицию 40001 со значением 15
# write_result = client.write_register(40001, 15, unit=1)
# print(write_result)
#
# # Чтение 10 регистров начиная с 40001 адреса
# result = client.read_holding_registers(address=40001, count=10, unit=1)
# print(result.registers)
#
#
# result = client.readwrite_registers(readaddress=40001, read_count=10, write_address=40001,
#                                     write_registers=(22, 33, 44, 55), unit=1)
# print(result.registers)
#
# while True:
#     time.sleep(0.5)
#     write_result = client.write_register(40001, random.randint(0, 20), unit=1)
#     print(write_result)
