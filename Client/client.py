import requests
from dataclasses import dataclass
import os
from dotenv import load_dotenv
import argparse

load_dotenv()


@dataclass
class Client:
    id: int
    wd: str
    namenode_url: str

    def menu(self):
        opcion = input("comandos put,get,pwd")
        if opcion == 1:
            pass

    def request_nodes(self, name: str, file_path: str, action: str):
        namendode_response = requests.get(f'{self.namenode_url}/request_nodes',
                                          params={'name': name, 'size': os.path.getsize(file_path), 'action': action})
        return namendode_response.json()

    def write(self, metadata: dict, file_str: str):
        ips = metadata.get('ips')
        with open(file_str, mode='rb') as f:
            part = 0
            for ip in ips:
                subfile = f.read(metadata.get('block_size'))
                print(subfile.decode())
                response = requests.post(
                    ip, json={'name': f'{metadata.get('file')}_part{part}', 'data': subfile.decode('utf-8')})
                part += 1
                if subfile == None:
                    break

    def read(self,):
        pass


if __name__ == '__main__':
    namenode_url = os.environ.get('NAMENODE_URL')
    client = Client(1, '2', namenode_url,)
    metadata: dict = client.request_nodes('egxampli.txt', 'cosa.txt', "write")
    print(metadata)
    client.write(metadata, "cosa.txt")
    pass
