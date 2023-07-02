from flask import Flask, render_template, jsonify
import psycopg2

app = Flask(__name__)

@app.route('/')
def mostrar_datos():
    return render_template('graficas.html')

@app.route('/datos')
def obtener_datos():
    conn = psycopg2.connect(database="meteorologic_db", user="web", password="1431", host="localhost", port="5432")
    cursor = conn.cursor()
    
    query = "SELECT temperatura.valor_temp, humedad.valor_hum, presion.valor_pres, data_node.timestamp " \
            "FROM data_node " \
            "JOIN temperatura ON data_node.id = temperatura.tiempo_id " \
            "JOIN humedad ON data_node.id = humedad.tiempo_id " \
            "JOIN presion ON data_node.id = presion.tiempo_id " \
            "ORDER BY timestamp  LIMIT 100" \
            

    cursor.execute(query)
    datos = cursor.fetchall()

    cursor.close()
    conn.close()

    temperatura = [dato[0] for dato in datos]
    humedad = [dato[1] for dato in datos]
    presion = [dato[2] for dato in datos]
    timestamp = [dato[3] for dato in datos]

    data = {
        'temperatura': temperatura,
        'humedad': humedad,
        'presion': presion,
        'timestamp': timestamp
    }

    return jsonify(data)

if __name__ == '__main__':
    app.run(port=8080)
