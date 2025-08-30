from flask import Flask, request
from database.db import db, Folder, File
from sqlalchemy import select
import math


class NameNode:
    def read():
        pass

    def get():
        pass

    def pwd():
        pass

    def open():
        pass

    def close():
        pass

    def write(file_name: str, file_size: int):
        print(f'escribiendo {file_name} de tamaño {file_size}')
        print("Escrita la metadata")
        return math.ceil(file_size/64)


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
db.init_app(app)
with app.app_context():
    db.create_all()
    print(db.session.get(Folder, 2).parent)


@app.route("/request_nodes")
def home():
    request_args: dict = request.args
    file_size: int = int(request_args.get('size'))  # bytes
    file_name: str = request_args.get('name')
    action: str = request_args.get('action')
    if action == 'write':
        NameNode.write(file_name, file_size)
    elif action == 'read':
        NameNode.read(file_name)
    block_size = 64
    blocks = math.ceil(file_size/block_size)
    print(blocks)

    metadata = {
        "usuario": "Eduardo",
        "file": file_name,
        "ips": ['http://127.0.0.1:12345/write' for i in range(blocks)],
        'block_size': block_size
    }
    return metadata


if __name__ == "__main__":
    pass
    # app.run(debug=True)
