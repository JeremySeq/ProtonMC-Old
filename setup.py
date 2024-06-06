import os
import json


def setup():
    willExit = False
    if os.path.isfile('users.json'):
        pass
    else:
        willExit = True
        print("users.json does not exist")
        print('Creating users.json...')

        dictionary = {
            "admin": {
                "username": "admin",
                "password": "123",
                "permissions": 5
            }
        }

        # Serializing json
        json_object = json.dumps(dictionary, indent=4)
        with open("users.json", "w") as outfile:
            outfile.write(json_object)
        print('DONE\nYou may want to add/change users in users.json before starting.')

    if os.path.isfile('servers.json'):
        pass
    else:
        willExit = True
        print("servers.json does not exist")
        print('Creating servers.json...')

        dictionary = {
            "A Server": [
                "A Server",
                "192.168.0.50",
                25565,
                25575,
                "rconPassword",
                "C:\\Users\\user\\Documents\\MinecraftServers\\AServer\\",
                "C:\\Users\\user\\Documents\\MinecraftServers\\Backups\\AServer\\"
            ]
        }

        # Serializing json
        json_object = json.dumps(dictionary, indent=4)
        with open("servers.json", "w") as outfile:
            outfile.write(json_object)
        print('DONE\nFill out servers.json before starting.')

    if willExit:
        exit()


if __name__ == '__main__':
    setup()
