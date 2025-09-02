from flask import Flask, request
from database.db import db
from utils import NameNode


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
db.init_app(app)
with app.app_context():
    db.create_all()


@app.route("/register_datanode", methods=["POST"])
def register_datanode():
    data: dict = request.json
    host = data.get("ip")
    port = data.get("port")
    response = NameNode.register_datanode(host, port)
    return response


@app.route("/request_nodes")
def home():
    request_args: dict = request.args
    file_size: int = int(request_args.get('size'))  # bytes
    file_name: str = request_args.get('name')
    action: str = request_args.get('action')
    folder_path: str = request_args.get('path')
    if action == 'write':
        metadata = NameNode.write(file_name, file_size, folder_path)
    elif action == 'read':
        metadata = NameNode.read(f'{folder_path}/{file_name}')
    return metadata


if __name__ == "__main__":
    pass
    # app.run(debug=True)
