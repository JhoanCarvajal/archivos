import os
import zmq
import sys

context = zmq.Context()

socket_proxy = context.socket(zmq.REQ)
socket_proxy.connect('tcp://localhost:7777')

action = "new_server"
server_ip = sys.argv[1]
server_space = sys.argv[2]


socket_proxy.send_multipart([action.encode('utf-8'), server_ip.encode('utf-8'), server_space.encode('utf-8')])
m = socket_proxy.recv_string()
print(m)
    
####################################################################################################

socket_client = context.socket(zmq.REP)
socket_client.bind('tcp://'+server_ip)
CHUNK_SIZE = 250 * 1024

def readFile(dir):
    with open(dir, 'rb') as f:
        data = f.read()
        return data

def writeFile(filename, data):
    with open(filename, 'wb') as f:
        f.write(data)

def upload(sha1_hashed, data):
    filename = f"files/{sha1_hashed}"
    writeFile(filename, data)
    message = "Se cargo el archivo"
    return message

def downloadPart(hash):
    listdir = os.listdir("./files/")
    data = None

    if hash in listdir:
        filename = "./files/" + hash
        data = readFile(filename)

    return data

###################################################################################################
while True:
    multipart = socket_client.recv_multipart()
    action = multipart[0].decode('utf-8')

    if action == "upload":
        sha1_hashed = multipart[1].decode('utf-8')
        data = multipart[2]
        message = upload(sha1_hashed, data)
        socket_client.send_string(message)
    elif action == "download_parts":
        hash = multipart[1].decode('utf-8')
        data = downloadPart(hash)
        socket_client.send_multipart([data])