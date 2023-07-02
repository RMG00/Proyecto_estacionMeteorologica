from object import *


inicio = 0
step = 30 # paso en segundos
fin = 300 # fin del loop en segundos


time.sleep(120)

sensorDB = sensor_db("meteorologic_db", "5432","meteorologic_db" ,"admin", "1431")
print("todo bien ....")

while True:
    lista_temperatura = []
    lista_presion = []
    lista_humedad = []

    while inicio != fin:
        temperatura, humedad, presion = sensorDB.get_data()
        lista_temperatura.append(temperatura)
        lista_humedad.append(humedad)
        lista_presion.append(presion)
        inicio = inicio + step
        time.sleep(step)

    inicio = 0
    temp_out = avg(lista_temperatura)
    hum_out = avg(lista_humedad)/100
    pres_out = avg(lista_presion)
    sensorDB.insertar_y_guardar(temperatura=temp_out, humedad=hum_out, presion= pres_out)
    print(f"temp = {temp_out:.5} [C]; hum = {hum_out:.3} % ; pres = {pres_out:.6g} [hPa]")
