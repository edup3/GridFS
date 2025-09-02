import requests
from flask import Flask, request, Response
import os
app = Flask(__name__)
DATANODE_URL = 'http://127.0.0.1:12345'
NAMENODE_URL = 'http://127.0.0.1:5000'
STORAGE_DIR = os.path.join(os.getcwd(), "storage")


def register_to_cluster():
    try:
        resp = requests.post(f"{NAMENODE_URL}/register_datanode", json={
            "ip": DATANODE_URL,
        })
        print("Registro con NameNode:", resp.json())
    except Exception as e:
        print("Error registrando con NameNode:", e)


@app.route("/write", methods=["POST"])
def write():
    if request.method == "POST":
        data: dict = request.get_json()
        print(data)
        path = data["path"]
        content = data["data"]
        block_path = os.path.join(STORAGE_DIR, path)
        print(STORAGE_DIR)
        print(block_path)
        os.makedirs(block_path, exist_ok=True)
        with open(f"{block_path}/{data.get('name')}.dat", mode="a") as file:
            file.write(data.get('data'))
    return Response(status=200)


if __name__ == "__main__":
    register_to_cluster()
    app.run(debug=True, port=12345)
