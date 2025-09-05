from database.db import db, Folder, File, Block, Datanode
from sqlalchemy import select
import math
import random as rd


class NameNode:

    def register_datanode(host, port):
        dn = Datanode.query.filter_by(ip=host).first()
        if not dn:
            dn = Datanode(ip=host, port=port, capacity=1000)
            db.session.add(dn)
            db.session.commit()
        else:
            return {"status": "already registered"}

        return {"status": "registered"}

    def resolve_path(path: str, classtype: str):
        parts = [p for p in path.strip("/").split("/") if p]
        if not parts:
            return None

        # Buscar la raíz
        current_folder = db.session.query(Folder).filter_by(
            name=parts[0], parent_folder=None).first()
        if not current_folder:
            return None
        elif len(parts) == 1:
            return current_folder

        for part in parts[1:-1]:  # todos menos el último
            current_folder = db.session.query(Folder).filter_by(
                name=part,
                parent_folder=current_folder.id
            ).first()
            if not current_folder:
                return None

        # # Última parte → puede ser carpeta o archivo
        last = parts[-1]
        if classtype == 'Folder':
            # Buscar folder
            folder = db.session.query(Folder).filter_by(
                name=last,
                parent_folder=current_folder.id
            ).first()
            if folder:
                return folder
        elif classtype == 'File':
            # Buscar archivo
            file = db.session.query(File).filter_by(
                name=last,
                parent_folder=current_folder.id
            ).first()
            if file:
                return file
        return None

    def read(file_path: str):
        file: File = NameNode.resolve_path(file_path, 'File')
        blocks: list[Block] = file.blocks
        blocks_meta = []
        for block in blocks:
            blocks_meta.append({
                'ip': block.datanode.ip,
                'part': block.part,
            })

        file_meta = {
            'name': file.name,
            'path': file.get_path(),
            'blocks': blocks_meta
        }
        print(file_meta)
        return file_meta

    def write(file_name: str, file_size: int, folder_path: str):
        # block_size ajustable
        block_size = 64
        # busqueda deberia ser por path
        folder: Folder = NameNode.resolve_path(folder_path, 'Folder')
        # busqueda deberia ser por path
        if folder.query.filter_by(name=file_name).first():
            return {'message': 'file already exists'}, 500
        file = File(file_name, file_size, folder.id)
        db.session.add(file)
        db.session.commit()
        blocks = math.ceil(file_size/block_size)
        datanodes = Datanode.query.all()
        if not datanodes:
            return {"error": "No hay datanodes registrados"}, 500
        blocks_meta = []
        for part in range(blocks):
            random_datanode = rd.choice(datanodes)
            block = Block(file.id, random_datanode.id, part)
            db.session.add(block)
            db.session.commit()
            blocks_meta.append({
                'ip': block.datanode.ip,
                'part': block.part,
                'block_size': block_size
            })

        file_meta = {
            'name': file.name,
            'path': file.get_path(),
            'blocks': blocks_meta
        }
        return file_meta
