import json
import uuid


def dataJson(user, filename, hash):
    with open('data.json') as json_file:
        try:
            dict_global = json.load(json_file)
        except:
            dict_global = {}

    if dict_global:
        users = dict_global.keys()
        print(users)
        if user in users:
            print(user)
            files = dict_global[user]
            print(files)
            if filename in files:
                print(filename)
                file_link = files[filename]
                print(file_link)
                if hash in file_link["parts"]:
                    pass # print("este hash ya existe")
                else:
                    file_link["parts"].append(hash) # print("se agrego un hash")
            else:
                file_link = {'parts': [hash], 'link': str(uuid.uuid1())}
                files[filename] = file_link # print("se agrego un archivo")
        else:
            file_link = {'parts': [hash], 'link': str(uuid.uuid1())}
            file = {filename: file_link}
            dict_global[user] = file # print("se creo un nuevo usuario")
    else:
        file_link = {'parts': [hash], 'link': str(uuid.uuid1())}
        file = {filename: file_link}
        dict_global[user] = file # print("se creo un nuevo usuario")

    data_json = json.dumps(dict_global)
    archivo_json = open("data.json","w")
    archivo_json.write(data_json)
    archivo_json.close()



dataJson('josue', 'startwars.mkv', 'eeeeee')

# {
#     "josue": {
#         "movie.mkv": {
#             "parts": [
#                 "ttttt"
#             ],
#             "link": "094f2b17-2231-11ec-b548-00f48dc23d1e"
#         }
#     }
# }