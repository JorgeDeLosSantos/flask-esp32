from flask import Flask, render_template, request, jsonify, redirect, url_for, json
from flask_socketio import SocketIO, emit
import pandas as pd
# import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

sensors_ids = ["01", "02", "03", "04", "05"]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    sensors_values = [get_last_read(sensor_id) for sensor_id in sensors_ids]
    return render_template("dashboard.html", sensors_info=zip(sensors_ids, sensors_values))

def get_last_read(sensor_id):
    df = pd.read_csv(f"data/{sensor_id}.csv")
    return df.iloc[-1,0]

def get_last_nreads(sensor_id, n):
    df = pd.read_csv(f"data/{sensor_id}.csv")
    return list(df.iloc[-1:-n:-1,0])

@app.route("/sensor/<sensor_id>")
def sensor(sensor_id):
    sensor_value = get_last_read(sensor_id)
    last_reads = get_last_nreads(sensor_id, 10)
    return render_template("sensor.html", sensor_id=sensor_id, sensor_value=sensor_value, last_reads=last_reads)

@app.route('/sensor-data', methods=['POST'])
def sensor_data():
    if request.content_type != 'application/json':
        data = request.form.to_dict()
    else:
        data = request.get_json() # obtener los datos enviados por el ESP32 en formato JSON
        data = json.loads(data)
    sensor_id = data["sensor_id"] # obtener los datos enviados por el ESP32 en formato JSON
    sensor_value = data["sensor_value"]
    # procesar los datos y almacenarlos en una base de datos o en una variable global
    with open(f"data/{sensor_id}.csv", 'a') as f:
        f.write(str(sensor_value)+"\n")
    last_reads = get_last_nreads(sensor_id, 10)
    to_send = {"sensor_id":sensor_id,"sensor_value": sensor_value, "last_reads": last_reads}
    socketio.emit("update", to_send)
    socketio.emit("updateChart", to_send)
    return 'OK' # enviar una respuesta al ESP32 indicando que los datos se recibieron correctamente

@app.route('/send-fake-data')
def send_fake_data():
    return render_template("send-fake-data.html")