import io
import logging
import psycopg2
from decimal import Decimal
from flask import Flask, Response, render_template
from threading import Condition
from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput
from flask_socketio import SocketIO
import time
from datetime import datetime

app = Flask(__name__)
socketio = SocketIO(app)

class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stream.mjpg')
def stream():
    def generate():
        try:
            while True:
                with output.condition:
                    output.condition.wait()
                    frame = output.frame
                yield b'--FRAME\r\n'
                yield b'Content-Type: image/jpeg\r\n\r\n'
                yield frame
                yield b'\r\n'

        except Exception as e:
            logging.warning('Removed streaming client: %s', str(e))

    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=FRAME')

@socketio.on('request_data')
def handle_request_data():
    conn = psycopg2.connect(host='localhost', database='meteorologic_db', user='web', password='1431')
    cursor = conn.cursor()

    try:
        while True:
            cursor.execute('''
                SELECT data_node.timestamp, humedad.valor_hum, presion.valor_pres, temperatura.valor_temp
                FROM data_node
                JOIN humedad ON data_node.id = humedad.id
                JOIN presion ON data_node.id = presion.id
                JOIN temperatura ON data_node.id = temperatura.id
                ORDER BY data_node.id DESC LIMIT 1
            ''')
            data = cursor.fetchall()
            if data:
                serialized_data = [list(map(convert_decimal, row)) for row in data]
                socketio.emit('data_response', serialized_data)
            time.sleep(5)  # Espera 5 segundos antes de realizar la siguiente consulta
    finally:
        cursor.close()
        conn.close()

def convert_decimal(value):
    if isinstance(value, Decimal):
        return float(value)
    elif isinstance(value, datetime):
        return value.strftime('%Y-%m-%d %H:%M:%S')
    return value

if __name__ == '__main__':
    picam2 = Picamera2()
    picam2.create_video_configuration(main={"size": (1280, 720)})

    # Iniciar vista previa de la cámara para permitir el enfoque automático
    picam2.start_preview()
    time.sleep(2)  # Esperar 2 segundos para que el enfoque se ajuste adecuadamente

    output = StreamingOutput()
    picam2.start_recording(JpegEncoder(), FileOutput(output))

    try:
        socketio.run(app, host='0.0.0.0', port=8000)
    finally:
        picam2.stop_recording()
