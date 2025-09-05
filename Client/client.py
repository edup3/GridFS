import requests
from dataclasses import dataclass
import os
from dotenv import load_dotenv
import cmd
import shlex

load_dotenv()


class Client(cmd.Cmd):
    intro = "Bienvenido a MiniHDFS CLI. Escribe 'help' o '?' para ver comandos.\n"
    prompt = "hdfs> "
    id: int = 1
    wd: str = "root/"
    namenode_url: str = os.environ.get('NAMENODE_URL')
    def menu(self):
        pass

    def request_nodes(self, name: str, file_path: str, action: str, path: str):
        namendode_response = requests.get(f'{self.namenode_url}/request_nodes',
                                          params={'name': name, 'size': os.path.getsize(file_path), 'action': action, 'path': path})
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
                f.write(block_content)

    def do_put(self, arg):
        args = shlex.split(arg)
        if len(args) != 2:
            print("Uso: put <archivo_local> <nombre_remoto>")
            return
        local_file, remote_file = args
        metadata = self.request_nodes(remote_file,local_file,'write',self.wd)
        self.write(metadata,local_file)

    def do_get(self, arg):
        args = shlex.split(arg)
        if len(args) != 2:
            print("Uso: put <archivo_local> <nombre_remoto>")
            return
        local_file, remote_file = args
        metadata = self.request_nodes(remote_file,local_file,'read',self.wd)
        self.read_file(metadata)



    def do_cd(self, arg):
        new_path = os.path.normpath(os.path.join(self.current_dir, arg))


    def do_ls(self, arg):
        path = arg.strip() if arg else self.wd
        resp = requests.get(f"{self.namenode_url}/list", params={"path": path})
        print(resp)

    def do_pwd(self,arg):
        print(self.wd)


if __name__ == '__main__':
    namenode_url = os.environ.get('NAMENODE_URL')
    Client().cmdloop()
    # client = Client(namenode_url,1)
    # metadata: dict = client.request_nodes(
    #     'egxampli.txt', 'cosa.txt', 'read', 'root/documents')
    # # client.write(metadata, "cosa.txt")
    # client.read_file(metadata)
