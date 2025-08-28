import requests
from flask import Flask, request, Response
app = Flask(__name__)


@app.route("/write", methods=["POST"])
def write():
    if request.method == "POST":
        dic: dict = request.get_json()
        print(f"escribiendo {dic.get("file")}")
    return Response(status=200)


if __name__ == "__main__":
    app.run(debug=True, port=12345)
