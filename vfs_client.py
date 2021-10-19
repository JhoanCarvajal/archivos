import os
import zmq
import sys
import hashlib

context = zmq.Context()

socket_client_proxy = context.socket(zmq.REQ)
socket_client_proxy.connect('tcp://localhost:7777')

socket_client_server = context.socket(zmq.REQ) #socket para conectarme a los servidores

CHUNK_SIZE = 250 * 1024

user = sys.argv[1]
action = sys.argv[2]

def socketClientServer(ip_server):
    socket_client_server.connect('tcp://'+ip_server)
    return socket_client_server

def numberFileParts(filename):
    size = os.path.getsize(filename)
    if (size%CHUNK_SIZE)==0:
        parts = size / CHUNK_SIZE
    else:
        parts = int(size / CHUNK_SIZE + 1)

    return parts

def hashData(data):
    sha1_hash = hashlib.sha1(data)
    sha1_hashed = sha1_hash.hexdigest()
    return sha1_hashed

def writeFile(filename, data):
    with open(filename, 'ab') as f:
        f.write(data)

def upload(filename):
    parts = str(numberFileParts(filename))
    print(parts)
    socket_client_proxy.send_multipart([action.encode('utf-8'), parts.encode('utf-8')])
    parts_servers = socket_client_proxy.recv_string()
    print(parts_servers)
    parts_servers = parts_servers.split(",")
    for i in range(len(parts_servers)):
        parts_servers[i] = parts_servers[i].split("->")
    print(parts_servers)
    
    with open(filename, 'rb') as f:
        read_bytes = f.read(CHUNK_SIZE)
        part = 0
        while read_bytes:
            server_ip = parts_servers[part][1]
            socket_client_server = socketClientServer(server_ip)
            sha1_hashed = hashData(read_bytes)
            socket_client_server.send_multipart([action.encode('utf-8'), sha1_hashed.encode('utf-8'), read_bytes])
            read_bytes = f.read(CHUNK_SIZE)
            part += 1
            m = socket_client_server.recv_string()
            print(m)
            socket_client_proxy.send_multipart([b"update_json", user.encode('utf-8'), filename.encode('utf-8'), sha1_hashed.encode('utf-8'), server_ip.encode('utf-8')])
            recv_proxy = socket_client_proxy.recv_string()
            print(recv_proxy)

def getFileParts(filename):
    socket_client_proxy.send_multipart([action.encode('utf-8'), user.encode('utf-8'), filename.encode('utf-8')])
    str_parts = socket_client_proxy.recv_string()
    parts = str_parts.split(";")
    for i in range(len(parts)):
        parts[i] = parts[i].split(",")
    return parts

def downloadParts(filename, parts):
    action = "download_parts"
    for part in parts:
        hash = part[0]
        server_ip = part[1]
        socket_client_server = socketClientServer(server_ip)
        socket_client_server.send_multipart([action.encode('utf-8'), hash.encode('utf-8')])
        m = socket_client_server.recv_multipart()
        writeFile(filename, m[0])
    print("Se dercargo el archivo")

def userFilesList():
    socket_client_proxy.send_multipart([action.encode('utf-8'), user.encode('utf-8')])
    files = socket_client_proxy.recv_string()
    files = files.split(" ")
    print("###################")
    for file in files:
        print(file)
    print("###################")

def shareLink(filename):
    socket_client_proxy.send_multipart([action.encode('utf-8'), user.encode('utf-8'), filename.encode('utf-8')])
    link = socket_client_proxy.recv_string()
    print("Link para compartir: ")
    print(link)

def downloadLink(link):
    socket_client_proxy.send_multipart([action.encode('utf-8'), user.encode('utf-8'), link.encode('utf-8')])
    m = socket_client_proxy.recv_multipart()
    filename = m[0].decode('utf-8')
    str_parts = m[1].decode('utf-8')
    parts = str_parts.split(";")
    for i in range(len(parts)):
        parts[i] = parts[i].split(",")
    return filename, parts


###############################################################################################
if action == "upload":
    filename = sys.argv[3]
    upload(filename)
elif action == "download":
    filename = sys.argv[3]
    parts = getFileParts(filename)
    downloadParts(filename, parts)
elif action == "sharelink":
    filename = sys.argv[3]
    shareLink(filename)
elif action == "downloadlink":
    link =  sys.argv[3]
    filename, parts = downloadLink(link)
    downloadParts(filename, parts)
elif action == "list":
    userFilesList()