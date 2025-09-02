from flask import Flask, request
from database.db import db, Folder, File, Block, Datanode
from sqlalchemy import select
import math
import random as rd


class NameNode:
    def read(file_name: str):
        file = db.session.execute(
            select(File).filter_by(name=file_name)).scalar_one()
        blocks: list[Block] = file.blocks
        blocks_meta = []
        for block in blocks:
            blocks_meta.append({
                'ip': block.datanode.ip,
                'part': block.part,
            })

        file_meta = {
            'name': file.name,
            'path': file.get_path(),
            'blocks': blocks_meta
        }
        return file_meta

    def get():
        pass

    def pwd():
        pass

    def open():
        pass

    def close():
        pass

    def create_dir():
        pass

    def write(file_name: str, file_size: int, folder_name: str):
        # block_size ajustable
        block_size = 64
        # busqueda deberia ser por path
        folder = Folder.query.filter_by(name=folder_name).first()
        # busqueda deberia ser por path
        if File.query.filter_by(name=file_name).all():
            return {'message': 'file already exists'}, 500
        file = File(file_name, file_size, folder.id)
        db.session.add(file)
        db.session.commit()
        blocks = math.ceil(file_size/block_size)
        datanodes = Datanode.query.all()
        if not datanodes:
            return {"error": "No hay datanodes registrados"}, 500
        blocks_meta = []
        for part in range(blocks):
            random_datanode = rd.choice(datanodes)
            block = Block(file.id, random_datanode.id, part)
            db.session.add(block)
            db.session.commit()
            blocks_meta.append({
                'ip': block.datanode.ip,
                'part': block.part,
                'block_size': block_size
            })

        file_meta = {
            'name': file.name,
            'path': file.get_path(),
            'blocks': blocks_meta
        }
        print(file_meta)
        return file_meta


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
db.init_app(app)
with app.app_context():
    db.create_all()


@app.route("/register_datanode", methods=["POST"])
def register_datanode():
    data = request.json
    host = data.get("ip")

    dn = Datanode.query.filter_by(ip=host).first()
    if not dn:
        dn = Datanode(ip=host, port=12345, capacity=1000)
        db.session.add(dn)
        db.session.commit()
    else:
        return {"status": "already registered"}

    return {"status": "registered"}


@app.route("/request_nodes")
def home():
    request_args: dict = request.args
    file_size: int = int(request_args.get('size'))  # bytes
    file_name: str = request_args.get('name')
    action: str = request_args.get('action')
    folder_name: str = request_args.get('folder_name')
    if action == 'write':
        metadata = NameNode.write(file_name, file_size, folder_name)
    elif action == 'read':
        metadata = NameNode.read(file_name)
    return metadata


if __name__ == "__main__":
    pass
    # app.run(debug=True)
