# ST0263 Tópicos Especiales en Telemática

## Estudiantes:

- Eduardo Piñeros Manjarres, eapinerosm@eafit.edu.co
- Natalia Ceballos Posada, nceballosp@eafit.edu.co

## Profesor:

- Edwin Montoya Munera, emontoya@eafit.edu.co

# GRIDFS - Proyecto 1

## 1. Descripción de la actividad

### 1.1. Que aspectos cumplió o desarrolló de la actividad propuesta por el profesor (requerimientos funcionales y no funcionales)

- Sistema básico DFS conexiones entre NameNode, DataNode y Client para el manejo de bloques de archivos y sus metadatos
- Autenticación básica para separación de archivos entre usuarios.
- Encriptación de los bloques.

### 1.2. Que aspectos NO cumplió o desarrolló de la actividad propuesta por el profesor (requerimientos funcionales y no funcionales)

- No hay implementación de heartbeats de parte de los DataNode para asegurar su funcionamiento
- Manejo de fallas y logs correctamente documentados sin tumbar el sistema
- Tamaño de bloques no ajustable, 64mb.

## 2. Información general de diseño de alto nivel, arquitectura, patrones, mejores prácticas utilizadas.

- Separación de la lógica de negocio en el archivo utils, y configuracion de la base de datos y ORM en el archivo db para el namenode
- Separación  del código y las funciones basadas en clases

## 3. Descripción del ambiente de desarrollo y técnico.

- **Lenguaje de Programación:**
    - Python
    
- **Librerías/Paquetes:**
    - blinker v.1.9.0
    - cached-property v.2.0.1
    - certifi v.2025.8.3
    - cffi v.2.0.0
    - charset-normalizer v.3.4.3
    - click v.8.2.1
    - colorama v.0.4.6
    - cryptography v.45.0.7
    - cryptography-fernet v.0.1.0
    - dotenv v.0.9.9
    - fernet v.1.0.1
    - Flask v.3.1.2
    - Flask-JWT-Extended v.4.7.1
    - Flask-SQLAlchemy v.3.1.1
    - greenlet v3.2.4
    - idna v.3.10
    - inflection v.0.5.1
    - itsdangerous v.2.2.0
    - Jinja2 v.3.1.6
    - MarkupSafe v.3.0.2
    - mypy_extensions v.1.1.0
    - pyaes v.1.6.1
    - pycparser v.2.23
    - PyJWT v.2.10.1
    - python-dotenv v.1.1.1
    - requests v.2.32.5
    - SQLAlchemy v.2.0.43
    - sqlalchemy-orm v.1.2.10
    - typing-inspect v.0.9.0
    - typing_extensions v.4.15.0
    - urllib3 v.2.5.0
    - Werkzeug v.3.1.3
    
- **Como se compila y ejecuta.**

En el NameNode:

`Flask --app namenode run --debug`

En el DataNode:

`Flask —app datanode run —p 12345 —debug`

En el Cliente:

Ir a la carpeta donde esta el archivo [`client.py`](http://client.py) y ejecutar

`python [client.py](http://client.py/)`
Variables de entorno configuradas en `.env`

- **Descripción y como se configura los parámetros del proyecto**
    
    Los parámetros se configuran en variables .env para las ips o urls del NameNode y los DataNode
    
    Los puertos pueden ser configurados en los Dockerfile en el caso de despliegue o ajustados usando la variable FLASK_RUN_PORT en el .env 
    

- **Estructura del proyecto:**

```
GridFS/
|-- Client/
|   |-- .env
|   |-- client.py
|-- DataNode/
|   |-- datanode.py
|   |-- Dockerfile
|   |-- requirements.txt
|-- NameNode/
|   |-- database/
|       |-- __init__.py
|       |-- db.py 
|   |-- instance/
|       |-- project.db
|   |-- namenode.py
|   |-- Dockerfile
|   |-- requirements.txt
|   |-- utils.py
```

## 4. Descripción del ambiente de EJECUCIÓN (en producción)

- **Lenguaje de Programación:**
    - Python
    
- **Librerías/Paquetes:**
    - blinker v.1.9.0
    - cached-property v.2.0.1
    - certifi v.2025.8.3
    - cffi v.2.0.0
    - charset-normalizer v.3.4.3
    - click v.8.2.1
    - colorama v.0.4.6
    - cryptography v.45.0.7
    - cryptography-fernet v.0.1.0
    - dotenv v.0.9.9
    - fernet v.1.0.1
    - Flask v.3.1.2
    - Flask-JWT-Extended v.4.7.1
    - Flask-SQLAlchemy v.3.1.1
    - greenlet v3.2.4
    - idna v.3.10
    - inflection v.0.5.1
    - itsdangerous v.2.2.0
    - Jinja2 v.3.1.6
    - MarkupSafe v.3.0.2
    - mypy_extensions v.1.1.0
    - pyaes v.1.6.1
    - pycparser v.2.23
    - PyJWT v.2.10.1
    - python-dotenv v.1.1.1
    - requests v.2.32.5
    - SQLAlchemy v.2.0.43
    - sqlalchemy-orm v.1.2.10
    - typing-inspect v.0.9.0
    - typing_extensions v.4.15.0
    - urllib3 v.2.5.0
    - Werkzeug v.3.1.3
    
- **Como se compila y ejecuta.**

`sudo docker build . -t namenode`

`sudo docker run -p 5000:5000 --name namenode_1 namenode`

`sudo docker build . -t datanode`

`sudo docker run -p 5000:5000 --name datanode_1 datanode`
Variables de entorno configuradas en `.env`

- **IP o nombres de dominio en nube o en la máquina servidor.**

IP NameNode Elastica desplegada: http://34.205.202.49:5000

- **Descripción y como se configura los parámetros del proyecto**

Los parámetros se configuran en variables .env para las ips o urls del NameNode y los DataNode

Los puertos pueden ser configurados en los Dockerfile en el caso de despliegue o ajustados usando la variable FLASK_RUN_PORT en el `.env` 

### 5. Como se lanza el servidor?.

Para lanzar los servidores se debe tener una maquina aws con docker y git instalados para cada nodo

### Guía NameNode

1. Dentro de una instancia EC2 en AWS clonar el repositorio usando `git clone https://github.com/edup3/GridFS`
2. Cambiar el directorio de trabajo a la carpeta NameNode del proyecto `cd GridFS/NameNode/`
3. Crear la imagen docker para el proyecto `sudo docker build . -t namenode`
4. Instanciar un contenedor de la imagen previamente creada asegurándonos de mapear los puertos correctamente `sudo docker run -p 5000:5000 --name namenode_1 namenode`

### Guía DataNode

1. Dentro de una instancia EC2 en AWS clonar el repositorio usando `git clone https://github.com/edup3/GridFS`
2. Cambiar el directorio de trabajo a la carpeta DataNode del proyecto `cd GridFS/DataNode/`
3. Crear y configurar un archivo .env para declarar la url del namenode al que se va a registrar y la url del datanode(sin incluir el puerto) `nano .env`
    
    Ejemplo:
    
    ![Screenshot 2025-09-14 142448.png](attachment:24e8ae65-aa8d-48fd-822e-45934a094a17:Screenshot_2025-09-14_142448.png)
    
4. Crear la imagen docker para el proyecto `sudo docker build . -t datanode`
5. Instanciar un contenedor de la imagen previamente creada `sudo docker run -p 5000:5000 --name datanode_1 datanode`
6. Repetir el proceso en diferentes maquinas para contar con varios datanodes (opcional)

- **Mini guía de como un usuario utilizaría el software o la aplicación**

Para ejecutar la CLI el cliente debe configurar en un archivo .env la url del namenode de la siguiente manera en el folder GridFS/Client:

![image.png](attachment:8c169aa3-4151-4dcc-85ae-8887a2996ce0:image.png)

Luego debe ejecutar el script de python  `py ./client.py`

para mas ayuda con los comandos puede utilizar el comando `help [nombre del comando]`

## 5. Otra información que considere relevante para esta actividad.

Para el despliegue con AWS las maquinas deben tener instalado git y docker
