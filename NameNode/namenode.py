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
    file_size: int = request_args.get('size')  # bytes
    file_name: str = request_args.get('name')
    action: str = request_args.get('action')
    folder_path: str = request_args.get('path')
    if action == 'write':
        metadata = NameNode.write(file_name, file_size, folder_path)
    elif action == 'read':
        metadata = NameNode.read(f'{folder_path}/{file_name}')
    elif action == 'delete':
        metadata = NameNode.delete_file(f'{folder_path}/{file_name}')
    return metadata


@app.route("/list", methods=["GET"])
def get_folder_contents():
    path = request.args.get('path')
    folder = NameNode.resolve_path(path, 'Folder')
    content = folder.files + folder.children
    content = [str(item) for item in content]
    return {'items': content}, 200


@app.route("/mkdir", methods=["POST"])
def make_directory():
    path = request.json.get('wd')
    directory_name = request.json.get('directory_name')
    folder = NameNode.create_folder(path, directory_name)
    return {'status': 'folder created succesfully'}, 200


if __name__ == "__main__":
    pass
    # app.run(debug=True)
