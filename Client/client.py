import requests


def write():
    r = requests.get("http://127.0.0.1:5000")
    for ip in r.json()['ips']:
        print(f"escribiendo en {ip}")
        response = requests.post(ip, json=r.json())
        if response.ok:
            print("escrito correctamente")
        else:
            print('algo paso')


if __name__ == '__main__':
    write()
