from pymodbus.client.sync import ModbusSerialClient


client = ModbusSerialClient(method="rtu", port="COM2", stopbits=1, bytesize=8, parity='N', baudrate=9600)
client.connect()

# Чтение 10 регистров начиная с 40001 адреса
result = client.read_holding_registers(address=40001, count=10, unit=1)
print(result.registers)

# Запись регистра на позицию 40001 со значением 15
write_result = client.write_register(40001, 15, unit=1)
print(write_result)

# Чтение 10 регистров начиная с 40001 адреса
result = client.read_holding_registers(address=40001, count=10, unit=1)
print(result.registers)


result = client.readwrite_registers(readaddress=40001, read_count=10, write_address=40001,
                                    write_registers=(22, 33, 44, 55), unit=1)
print(result.registers)

# Чтение 10 регистров начиная с 40000 адреса
result = client.read_holding_registers(address=40000, count=10, unit=1)
print(result.registers)

# Чтение 10 регистров начиная с 40000 адреса
result = client.read_holding_registers(address=40000, count=10, unit=1)
print(result.registers)
