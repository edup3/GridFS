from flask import Flask, request, jsonify
from database.db import db, User, Folder
from utils import NameNode
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
app.config["JWT_SECRET_KEY"] = "super-clave-ultra-secreta"
jwt = JWTManager(app)
db.init_app(app)
with app.app_context():
    db.create_all()


@app.route("/login", methods=["POST"])
def login():
    data = request.json
    user: User = User.query.filter_by(username=data["username"]).first()
    if not user or not user.check_password(data["password"]):
        return jsonify({"error": "Credenciales inválidas"}), 401

    token = create_access_token(identity=str(user.id))
    return jsonify(access_token=token)


@app.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return {"error": "Faltan campos"}, 400

    # Verificar si ya existe
    if User.query.filter_by(username=username).first():
        return {"error": "Usuario ya existe"}, 400

    # Crear usuario
    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    root_folder = Folder('root', None, user.id)
    # crear root folder del usuario
    db.session.add(root_folder)
    db.session.commit()

    return {"message": "Usuario creado con éxito"}, 201


@app.route("/register_datanode", methods=["POST"])
def register_datanode():
    data: dict = request.json
    host = data.get("ip")
    port = data.get("port")
    response = NameNode.register_datanode(host, port)
    return response


@app.route("/request_nodes")
@jwt_required()
def home():
    user_id = get_jwt_identity()
    request_args: dict = request.args
    file_size: int = request_args.get('size')  # bytes
    file_name: str = request_args.get('name')
    action: str = request_args.get('action')
    folder_path: str = request_args.get('path')
    if action == 'write':
        metadata = NameNode.write(file_name, file_size, folder_path, user_id)
    elif action == 'read':
        metadata = NameNode.read(f'{folder_path}/{file_name}', user_id)
    elif action == 'delete':
        metadata = NameNode.delete_file(f'{folder_path}/{file_name}', user_id)
    return metadata


@app.route("/list", methods=["GET"])
@jwt_required()
def get_folder_contents():
    user_id = get_jwt_identity()
    path = request.args.get('path')
    folder = NameNode.resolve_path(path, 'Folder', user_id)
    content = folder.files + folder.children
    content = [str(item) for item in content]
    return {'items': content}, 200


@app.route("/mkdir", methods=["POST"])
@jwt_required()
def make_directory():
    user_id = get_jwt_identity()
    path = request.json.get('wd')
    directory_name = request.json.get('directory_name')
    folder = NameNode.create_folder(path, directory_name, user_id)
    return {'status': 'folder created succesfully'}, 200

@app.route("/cd", methods=["GET"])
@jwt_required()
def change_directory():
    user_id = get_jwt_identity()
    path = request.args.get('path')
    folder_path = NameNode.change_directory(path,user_id)
    if not folder_path:
        return {'folder no existe'},500
    return {'new_path': folder_path}, 200
@app.route("/delete_folder", methods=["DELETE"])
@jwt_required()
def delete_directory():
    user_id = get_jwt_identity()
    path = request.args.get('directory_path')
    print(path)
    folder_path = NameNode.delete_folder(path,user_id)
    if not folder_path:
        return {'folder no existe'},500
    return {'new_path': folder_path}, 200