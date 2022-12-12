from flask import Flask, render_template, request, jsonify
from flask_mqtt import Mqtt
app = Flask(__name__, template_folder='templates', static_folder='static')

@app.route("/")
def home():
    return render_template('login.html')

@app.route("/dati")
def salvador():
    return render_template('test.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
