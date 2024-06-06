import json
import mc

serversJson = "servers.json"


def writeInfo(name: str, ip: str, query_port: int, rcon_port: int, password: str, server_location: str,
              backup_location: str):
    infoList = [name, ip, query_port, rcon_port, password, server_location, backup_location]
    file = open(serversJson, 'r')
    data = json.load(file)
    file.close()
    data[name] = infoList

    # with open(serversJson) as file:
    #     data = json.load(file)
    #     data[name] = infoList

    file = open(serversJson, 'w')
    json.dump(data, file, indent=4)
    file.close()


def readInfo(name):
    file = open(serversJson, 'r')
    data = json.load(file)
    try:
        return mc.MCserver(*data[name])
    except KeyError:
        pass


def getServerInfo() -> list[mc.MCserver]:
    file = open(serversJson, 'r')
    data = json.load(file)
    servers = []
    for server_name in data:
        servers.append(mc.MCserver(*data[server_name]))

    return servers
