import os
import zmq
import hashlib
import json
import uuid

context = zmq.Context()

socket_proxy = context.socket(zmq.REP)
socket_proxy.bind('tcp://*:7777')

servers = []

def hashData(data):
    sha1Hash = hashlib.sha1(data)
    sha1Hashed = sha1Hash.hexdigest()
    return sha1Hashed

def readFile(dir):
    with open(dir, 'rb') as f:
        data = f.read()
        return data

def writeFile(filename, data):
    with open(filename, 'wb') as f:
        f.write(data)

def readJson(filename):
    with open(filename) as json_file:
        try:
            dict_global = json.load(json_file)
        except:
            dict_global = {}
    return dict_global

def writeJson(filename, dict_global):
    data_json = json.dumps(dict_global)
    archivo_json = open(filename,"w")
    archivo_json.write(data_json)
    archivo_json.close()

def updateDataJson(user, filename, hash, server_ip):
    dict_global = readJson('data.json')

    if dict_global:
        users = dict_global.keys()
        if user in users:
            files = dict_global[user]
            if filename in files:
                file_link = files[filename]
                exist_hash = False
                for part in file_link["parts"]:
                    if part[0] == hash:
                        exist_hash = True
                if exist_hash:
                    pass # print("este hash ya existe")
                else:
                    hash_server = [hash, server_ip]
                    file_link["parts"].append(hash_server) # print("se agrego un hash")
            else:
                file_link = {'parts': [[hash, server_ip]], 'link': str(uuid.uuid1())}
                files[filename] = file_link # print("se agrego un archivo")
        else:
            file_link = {'parts': [[hash, server_ip]], 'link': str(uuid.uuid1())}
            file = {filename: file_link}
            dict_global[user] = file # print("se creo un nuevo usuario")
    else:
        file_link = {'parts': [[hash, server_ip]], 'link': str(uuid.uuid1())}
        file = {filename: file_link}
        dict_global[user] = file # print("se creo un nuevo usuario")
    writeJson('data.json', dict_global)

def upload(parts):
    parts = int(parts)
    parts_servers = ""
    number_servers = len(servers)
    server = 0
    part = 0
    print(servers)
    if servers:
        while part != parts:
            if servers[server][1] == 0:
                pass # no hago nada y dejo que cambie de servidor
            else:
                parts_servers += str(part+1)
                parts_servers += "->"
                parts_servers += servers[server][0]
                servers[server][1] -= 1
                parts_servers += ","
                part += 1
            if server == number_servers - 1:
                server = 0
            else:
                server += 1
        parts_servers = parts_servers[:len(parts_servers) - 1]
        print(servers)
    return parts_servers

def getFileParts(user, filename):
    dict_global = readJson('data.json')
    parts = []

    if dict_global:
        users = dict_global.keys()
        if user in users:
            files = dict_global[user]
            if filename in files:
                file_link = files[filename]
                parts = file_link["parts"]
    
    return parts


def downloadPart(part):
    listdir = os.listdir("./files/")
    data = None

    if part in listdir:
        filename = "./files/" + part
        data = readFile(filename)

    return data

def shareLink(user, filename):
    dict_global = readJson('data.json')
    link = ""

    if dict_global:
        users = dict_global.keys()
        if user in users:
            files = dict_global[user]
            if filename in files:
                file_link = files[filename]
                link = file_link["link"]
    
    return link

def downloadLink(link):
    dict_global = readJson('data.json')
    parts = []
    filename = ""

    if dict_global:
        users = dict_global.keys()
        for user in users:
            files = dict_global[user]
            for file in files:
                file_link = files[file]
                # link = file_link["link"]
                if link == file_link["link"]:
                    filename = file
                    parts = file_link["parts"]
                    break
    return filename, parts


def list_files(user):
    dict_global = readJson('data.json')
    files = []

    if dict_global:
        users = dict_global.keys()
        if user in users:
            files = dict_global[user].keys()
    
    return files
    
####################################################################################################
while True:
    multipart = socket_proxy.recv_multipart()
    action = multipart[0].decode('utf-8')

    if action == "upload":
        parts = multipart[1].decode('utf-8')
        parts_servers = upload(parts)
        socket_proxy.send_string(parts_servers)

    if action == "update_json":
        user = multipart[1].decode('utf-8')
        filename = multipart[2].decode('utf-8')
        hash = multipart[3].decode('utf-8')
        server_ip = multipart[4].decode('utf-8')
        updateDataJson(user, filename, hash, server_ip)
        socket_proxy.send_string("Se actualizo el Json")

    elif action == "download":
        user = multipart[1].decode('utf-8')
        filename = multipart[2].decode('utf-8')
        parts = getFileParts(user, filename)
        str_parts = ""
        for part in parts:
            hash = str(part[0])
            server = str(part[1])
            str_parts += f"{hash},{server};"
        str_parts = str_parts[:len(str_parts) - 1]
        socket_proxy.send_string(str_parts)

    elif action == "list":
        user = multipart[1].decode('utf-8')
        files = list_files(user)
        listToStr = ' '.join([str(elem) for elem in files])
        socket_proxy.send_string(listToStr)

    elif action == "sharelink":
        user = multipart[1].decode('utf-8')
        filename = multipart[2].decode('utf-8')
        link = shareLink(user, filename)
        socket_proxy.send_string(link)

    elif action == "downloadlink":
        user = multipart[1].decode('utf-8')
        link = multipart[2].decode('utf-8')
        filename, parts = downloadLink(link)
        str_parts = ""
        for part in parts:
            hash = str(part[0])
            server = str(part[1])
            str_parts += f"{hash},{server};"
        str_parts = str_parts[:len(str_parts) - 1]
        socket_proxy.send_multipart([filename.encode('utf-8'), str_parts.encode('utf-8')])

    elif action == "new_server":
        server_ip = multipart[1].decode('utf-8')
        server_space = int(multipart[2].decode('utf-8'))
        servers.append([server_ip, server_space])
        socket_proxy.send_string("ok")
