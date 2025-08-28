from flask import Flask
from database.db import db, Node
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
db.init_app(app)
with app.app_context():
    db.create_all()


@app.route("/")
def home():
    metadata = {
        "usuario": "Eduardo",
        "file": "example.txt",
        "ips": ['http://127.0.0.1:12345/write', 'http://127.0.0.1:12345/write', 'http://127.0.0.1:12345/write']
    }
    return metadata


if __name__ == "__main__":
    app.run(debug=True)
