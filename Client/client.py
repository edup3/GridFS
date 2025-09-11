import requests
from dataclasses import dataclass
import os
from dotenv import load_dotenv
import cmd
import shlex
from requests import Response

load_dotenv()


class Client(cmd.Cmd):
    intro = "Bienvenido a GridHDFS CLI. Escribe 'help' o '?' para ver comandos.\n"
    token = None
    wd: str = ''
    user: str
    prompt = f"GridHDFS: {wd}> "
    namenode_url: str = os.environ.get('NAMENODE_URL')

    def _auth_headers(self):
        return {"Authorization": f"Bearer {self.token}"} if self.token else {}

    def request_nodes(self, name: str, local_file_path: str, action: str, path: str):
        if action == 'read':
            namendode_response = requests.get(f'{self.namenode_url}/request_nodes',
                                              params={'name': name, 'action': action, 'path': path}, headers=self._auth_headers())
        elif action == 'write':
            namendode_response = requests.get(f'{self.namenode_url}/request_nodes',
                                              params={'name': name, 'size': os.path.getsize(local_file_path), 'action': action, 'path': path}, headers=self._auth_headers())
        elif action == 'delete':
            namendode_response = requests.get(f'{self.namenode_url}/request_nodes',
                                              params={'name': name, 'action': action, 'path': path}, headers=self._auth_headers())
        return namendode_response.json()

    def write(self, metadata: dict, file_str: str):

        blocks = metadata.get('blocks')
        with open(file_str, mode='rb') as f:
            part = 0
            for block in blocks:
                print(int(block.get('block_size')))
                subfile = f.read(block.get('block_size'))
                print(metadata)
                print("subfile_part:", part, subfile)
                response = requests.post(
                    f'{block.get('ip')}:{block.get('port')}/write', json={'name': f'{metadata.get('name')}_part{part}', 'data': subfile.decode('utf-8'), 'path': metadata.get('path')}, headers=self._auth_headers())
                part += 1
                if subfile == None:
                    break

    def read_block(self, datanode_ip, datanode_port, block_path, block_name, part) -> str:
        block_content = requests.get(
            f'{datanode_ip}:{datanode_port}/read', params={'block_path': block_path, 'block_name': block_name, 'part': part}, headers=self._auth_headers())
        return block_content.json()['data']

    def read_file(self, metadata, local_file_name):
        file_name: str = metadata['name']
        if not local_file_name:
            local_file_name = file_name
        block_list: list = metadata['blocks']
        path: str = metadata['path']
        with open(local_file_name, mode='w') as f:
            for block_metadata in block_list:
                ip = block_metadata['ip']
                port = block_metadata['port']
                block_content = self.read_block(
                    ip, port, path, file_name, block_metadata['part'])
                f.write(block_content)

    def print_file(self, metadata):
        file_name: str = metadata['name']
        block_list: list = metadata['blocks']
        path: str = metadata['path']
        for block_metadata in block_list:
            ip = block_metadata['ip']
            port = block_metadata['port']
            block_content = self.read_block(
                ip, port, path, file_name, block_metadata['part'])
            print(block_content)

    def create_directory(self, directory_name):
        response = requests.post(
            f'{namenode_url}/mkdir', json={'wd': self.wd, 'directory_name': directory_name}, headers=self._auth_headers())
        if response.ok:
            print('directorio creado correctamente')
            return

    def delete_files(self, metadata: dict):
        blocks = metadata.get('blocks')
        for block in blocks:
            response = requests.delete(
                f'{block.get('ip')}:{block.get('port')}/delete_file', params={'block_name': f'{metadata.get('name')}_part{block.get('part')}', 'block_path': metadata.get('path')}, headers=self._auth_headers())

    def remove_file(self, file_name):
        metadata: Response = self.request_nodes(
            file_name, '', 'delete', self.wd)
        self.delete_files(metadata)
        print('Archivo borrado correctamente')

    def remove_directory(self, folder_path):
        metadata: Response = requests.delete(f'{namenode_url}/delete_folder',params={'directory_path':f'{self.wd}/{folder_path}'},headers=self._auth_headers())
        if metadata.ok:
            print('Directorio borrado correctamente')
        else:
            print('El directorio tiene que estar vacio')

    
        # Commands

    def do_register(self, arg):
        """
        Registrar un usuario y crea su carpeta root en el namenode
        uso: register <nombre_de_usuario> <contraseña>
        """
        args = shlex.split(arg)
        name, password = args
        response = requests.post(
            f'{namenode_url}/register', json={'username': name, 'password': password})
        print(response.json().get('message'))

    def do_login(self, arg):
        """Login: login <usuario> <contraseña>"""
        args = shlex.split(arg)
        user, password = args
        resp = requests.post(f"{namenode_url}/login",
                             json={"username": user, "password": password})
        if resp.status_code == 200:
            self.token = resp.json()["access_token"]
            self.wd = 'root/'
            self.prompt = f"GridHDFS: {self.wd}> "
            print("Login exitoso")
        else:
            print("Error:", resp.json())

    def do_put(self, arg):
        """
        Escribir un archivo del sistema local a HDFS
        uso: put <archivo_local> <nombre_remoto>
        """
        args = shlex.split(arg)
        if not self.token:
            print('No estas logeado, intenta hacer login primero')
            return
        if len(args) != 2:
            print("Uso: put <archivo_local> <nombre_remoto>")
            return
        local_file, remote_file = args
        metadata: Response = self.request_nodes(
            remote_file, local_file, 'write', self.wd)
        if metadata.status_code == 500:
            print(metadata.json().get('error'))
            return
        self.write(metadata, local_file)

    def do_get(self, arg):
        """
        Copiar un archivo del sistema HDFS a local
        uso: get <nombre_remoto> [archivo_local]
        """
        if not self.token:
            print('No estas logeado, intenta hacer login primero')
            return
        args = shlex.split(arg)
        if len(args) == 1:
            remote_file = args[0]
            metadata = self.request_nodes(
                remote_file, remote_file, 'read', self.wd)
            self.read_file(metadata, remote_file)
            return

        elif len(args) != 2:
            print("Uso: get <nombre_remoto> [archivo_local]")
            return

        local_file, remote_file = args
        metadata = self.request_nodes(remote_file, local_file, 'read', self.wd)
        self.read_file(metadata, local_file)

    def do_cd(self, arg):
        """
        Cambiar directorio de trabajo
        uso: cd <ruta_directorio>
        """
        if not self.token:
            print('No estas logeado, intenta hacer login primero')
            return
        if not arg:
            return
        if self.wd == 'root/' and arg == '..':
            return
        if arg == '..':
            path = self.wd.split("/")[:-1]
            self.wd = "/".join(path) if len(path)>1 else f'{path[0]}/'
            self.prompt = f"GridHDFS: {self.wd}> "
            return
        new_path = requests.get(f'{namenode_url}/cd',params={'path':f'{self.wd}/{arg}'},headers=self._auth_headers())
        self.wd = new_path.json().get('new_path')
        self.prompt = f"GridHDFS: {self.wd}> "
        print(new_path)

    def do_ls(self, arg):
        """
        Lista archivos y carpetas en el directorio actual o en una ruta
        uso: ls [ruta]
        """
        if not self.token:
            print('No estas logeado, intenta hacer login primero')
            return
        path = arg.strip() if arg else self.wd
        resp = requests.get(f"{self.namenode_url}/list",
                            params={"path": path}, headers=self._auth_headers())
        items = resp.json().get('items')
        if not items:
            print('Directorio Vacio')
        for item in items:
            print(item)

    def do_pwd(self, arg):
        """
        Muestra el directorio actual
        uso: pwd
        """
        if not self.token:
            print('No estas logeado, intenta hacer login primero')
            return
        print(self.wd)

    def do_mkdir(self, arg):
        """
        Crea un directorio en el directorio actual
        uso: mkdir <nombre_directorio>
        """
        if not self.token:
            print('No estas logeado, intenta hacer login primero')
            return
        if not arg:
            print('uso: mkdir <nombre_directorio>')
            return
        self.create_directory(arg)

    def do_cat(self, arg):
        """
        Imprime los contenidos de un archivo
        uso: cat <nombre archivo>
        """
        if not self.token:
            print('No estas logeado, intenta hacer login primero')
            return
        if not arg:
            print("Uso: cat <nombre_archivo_remoto>")
            return

        remote_file = arg
        metadata = self.request_nodes(
            remote_file, remote_file, 'read', self.wd)
        self.print_file(metadata)

    def do_rm(self, arg):
        """
        Muestra el directorio actual
        uso: rm <nombre archivo>
        """
        if not self.token:
            print('No estas logeado, intenta hacer login primero')
            return
        if not arg:
            print('uso: rm <nombre archivo>')
            return
        self.remove_file(arg)

    def do_rmdir(self, arg):
        if not self.token:
            print('No estas logeado, intenta hacer login primero')
        self.remove_directory(arg)
        pass

    def do_exit(self, arg):
        """
        Salir del programa
        uso: exit
        """
        return True


if __name__ == '__main__':
    namenode_url = os.environ.get('NAMENODE_URL')
    Client().cmdloop()
