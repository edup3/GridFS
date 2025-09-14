import requests
from flask import Flask, request, Response
import os
from dotenv import load_dotenv
load_dotenv()
app = Flask(__name__)
DATANODE_URL = os.environ.get('DATANODE_URL')
NAMENODE_URL = os.environ.get('NAMENODE_URL')
PORT = os.environ.get('FLASK_RUN_PORT')
STORAGE_DIR = os.path.join(os.getcwd(), "storage")


def register_to_cluster():
    try:
        resp = requests.post(f"{NAMENODE_URL}/register_datanode", json={
            "ip": DATANODE_URL, 'port': PORT
        })
        print("Registro con NameNode:", resp.json())
    except Exception as e:
        print("Error registrando con NameNode:", e)


register_to_cluster()


@app.route("/write", methods=["POST"])
def write():
    if request.method == "POST":
        data: dict = request.get_json()
        path = data["path"]
        content = data["data"]
        block_path = os.path.join(STORAGE_DIR, path)
        os.makedirs(block_path, exist_ok=True)
        with open(f"{block_path}/{data.get('name')}.dat", mode="w") as file:
            file.write(data.get('data'))
    return Response(status=200)


@app.route("/read", methods=["GET"])
def read():
    if request.method == "GET":
        data: dict = request.args
        print(data)
        path = data["block_path"]
        name = data["block_name"]
        part = data["part"]
        block_path = os.path.join(STORAGE_DIR, path)
        with open(f"{block_path}/{name}_part{part}.dat", mode="r") as file:
            content = file.read()
    return {'data': content}, 200


@app.route("/delete_file", methods=["DELETE"])
def delete_file():
    if request.method == "DELETE":
        data: dict = request.args
        path = data["block_path"]
        name = data["block_name"]
        block_path = os.path.join(STORAGE_DIR, path)
        file_path = os.path.join(block_path, name)
        try:
            os.remove(f'{file_path}.dat')
        except Exception as e:
            print(f"An error occurred: {e}")
        try:
            os.rmdir(block_path)
        except:
            pass
        return {'status': 'borrado correctamente'}, 200

