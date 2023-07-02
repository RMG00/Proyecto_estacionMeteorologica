import psycopg2
import smbus2
import bme280
import time
class sensor_db():
    def __init__(self, host, port, database, user, password):
        self.estacion_id = 1
        ##------------------DB------------------##        
        self.conn = psycopg2.connect(
            host = host,
            port = port,
            database = database,
            user = user,
            password = password)
        self.cursor = self.conn.cursor()
        print("Conectado ...")
	
        ##----------------------------------------------##
        ##------Sensor Temp, presion y Humedad:---------##
        print("parametros de calibracion")
        self.port_sensor = 1
        self.address = 0x76
        self.bus = smbus2.SMBus(self.port_sensor)
        self.calibration_params = bme280.load_calibration_params(self.bus, self.address)
        ##-------------------------------------##
    ##----------------------Configuracion DB, Postgres-----------------------------------##
    ##----------------------------------Lectura de Humedad, Temperatura y Presion--------##
    def get_data(self):
        status = False
        while status == False:
            data = bme280.sample(self.bus, self.address, self.calibration_params)
            if data != None:
                status = True
        return data.temperature, data.humidity, data.pressure 
    ## -------------------------------------------------------------------------##
    ##------------------------------Commit de datos guardados-------------------##
    def insertar_y_guardar(self,
                           temperatura, 
                           humedad, 
                           presion):


        self.cursor.execute(f"""
            INSERT INTO data_node (estacion_id, timestamp)
            VALUES ('{self.estacion_id}', NOW())
        """)
        time.sleep(1)

        insert_query = f"""
            INSERT INTO temperatura (valor_temp, tiempo_id)
            SELECT {temperatura:.3f}, id
            FROM data_node
            ORDER BY id DESC
            LIMIT 1
        """
        self.cursor.execute(insert_query)

        insert_query = f"""
            INSERT INTO humedad (valor_hum, tiempo_id)
            SELECT {humedad:.3f}, id
            FROM data_node
            ORDER BY id DESC
            LIMIT 1
        """
        self.cursor.execute(insert_query)

        insert_query = f"""
            INSERT INTO presion (valor_pres, tiempo_id)
            SELECT {presion:.3f}, id
            FROM data_node
            ORDER BY id DESC
            LIMIT 1
        """
        self.cursor.execute(insert_query)

        self.conn.commit()

	
    ##-------------------------------------------------------------------------##
def avg(lista):
    return sum(lista)/len(lista)
