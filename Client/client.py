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
        pass

    def request_nodes(self, name: str, file_path: str, action: str, folder_name):
        namendode_response = requests.get(f'{self.namenode_url}/request_nodes',
                                          params={'name': name, 'size': os.path.getsize(file_path), 'action': action, 'folder_name': folder_name})
        return namendode_response.json()

    def write(self, metadata: dict, file_str: str):
        blocks = metadata.get('blocks')
        with open(file_str, mode='rb') as f:
            part = 0
            for block in blocks:
                print(int(block.get('block_size')))
                subfile = f.read(block.get('block_size'))
                print("subfile_part:", part, subfile)
                response = requests.post(
                    f'{block.get('ip')}/write', json={'name': f'{metadata.get('name')}_part{part}', 'data': subfile.decode('utf-8'), 'path': metadata.get('path')})
                part += 1
                if subfile == None:
                    break

    def read(self,):
        pass


if __name__ == '__main__':
    namenode_url = os.environ.get('NAMENODE_URL')
    client = Client(1, '2', namenode_url,)
    metadata: dict = client.request_nodes(
        'egxampli.txt', 'cosa.txt', 'write', 'documents')
    client.write(metadata, "cosa.txt")
