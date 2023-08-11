from flask import Flask, make_response, jsonify
from positions import data


app = Flask(__name__)

@app.rout('/positions', methods = ['GET'])
def get_positions():
    return make_response(
        jsonify(data)
    )

app.run()