import requests
from dataclasses import dataclass
import os
from dotenv import load_dotenv
import cmd

load_dotenv()


@dataclass
class Client(cmd.Cmd):
    intro = "Bienvenido a MiniHDFS CLI. Escribe 'help' o '?' para ver comandos.\n"
    prompt = "hdfs> "
    current_dir = "/root"
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

    def read_block(self, datanode_ip, block_path, block_name, part) -> str:
        block_content = requests.get(
            f'{datanode_ip}/read', params={'block_path': block_path, 'block_name': block_name, 'part': part})
        return block_content.json()['data']

    def read_file(self, metadata):
        file_name: str = metadata['name']
        block_list: list = metadata['blocks']
        path: str = metadata['path']
        with open(file_name, mode='w') as f:
            for block_metadata in block_list:
                ip = block_metadata['ip']
                block_content = self.read_block(
                    ip, path, file_name, block_metadata['part'])
                print(block_content)
                f.write(block_content)


if __name__ == '__main__':
    namenode_url = os.environ.get('NAMENODE_URL')
    client = Client(1, '2', namenode_url,)
    metadata: dict = client.request_nodes(
        'egxampli.txt', 'cosa.txt', 'read', 'documents')
    # client.write(metadata, "cosa.txt")
    client.read_file(metadata)
