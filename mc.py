import socket
from mcipc.query import Client as Query
from mcipc.rcon.je import Client
import os
import shutil
import datetime
from queue import Queue, Empty
import subprocess
from threading import Thread
import zipfile

MAX_CONSOLE_LINES = 64


class MCserver:
    def __init__(self, name, ip, query_port, rcon_port, password, server_location, backup_location):
        self.ip = ip
        self.query_port = query_port
        self.rcon_port = rcon_port
        self.password = password
        self.server_location = server_location
        self.backup_location = backup_location
        self.name = name
        self.console = []

    def __str__(self):
        return self.name

    def isOn(self):
        try:
            with Client(self.ip, self.query_port, timeout=1.5) as client:
                return True
        except socket.timeout as timeout:
            return False
        except ConnectionRefusedError as e:
            return False

    def connectRCON(self) -> bool:
        if self.client_connected:
            return True
        try:
            # self.client = Client(self.ip, self.rcon_port, timeout=1.5)
            self.client.connect()
            return True
        except ConnectionRefusedError as error:
            return False

    def getSeed(self):
        with Client(self.ip, self.rcon_port, passwd=self.password) as client:
            seed = client.seed
            return seed

    def getPlayers(self) -> list[str]:
        try:
            with Query(self.ip, self.query_port) as client:
                return client.stats(full=True)["players"]
        except socket.timeout as timeout:
            return []
        except ConnectionRefusedError as e:
            return []
        except ConnectionResetError as e:
            return []

    def stop(self):
        self.runCommand("stop")

    def runCommand(self, command):
        with Client(self.ip, self.rcon_port, passwd=self.password) as client:
            response = client.run(command)
            self.console.append(response)

    def backup(self):
        month = datetime.datetime.now().month
        day = datetime.datetime.now().day
        year = datetime.datetime.now().year
        hour = datetime.datetime.now().hour
        minute = datetime.datetime.now().minute

        a = self.server_location
        b = f'{self.backup_location}\\{month}-{day}-{year}_{hour}-{minute}'
        os.mkdir(b)

        self.copy(a, b)
        print("Done backup.")

    def restore(self, backup_name):
        self.delete(self.server_location)
        path = f"{self.backup_location}\\{backup_name}"
        self.copy(path, self.server_location)

        print("Restored backup.")

    def copy(self, origin, target):
        print("Copying {} to {}".format(origin, target))
        files = os.listdir(origin)
        for file_name in files:
            src = f"{origin}\\{file_name}"
            dst = f"{target}\\{file_name}"
            if os.path.isfile(src):
                shutil.copy2(src, dst)
            elif os.path.isdir(src):
                os.mkdir(dst)
                self.copy(src, dst)

    def delete(self, target):
        files = os.listdir(target)
        for file_name in files:
            file = f"{target}\\{file_name}"
            if os.path.isfile(file):
                os.remove(file)
            elif os.path.isdir(file):
                self.delete(file)
                os.rmdir(file)

    def createFile(self, dir, name, content):
        path = f"{self.server_location}{dir}\\{name}"
        file = open(path, 'wb')
        file.write(content)
        file.close()

    def appendFile(self, dir, name, content):
        path = f"{self.server_location}{dir}\\{name}"
        try:
            file = open(path, 'ab')
            file.write(content)
        except FileNotFoundError:
            file = open(path, 'wb')
            file.write(content)
        file.close()

    def backuplist(self):

        files = os.listdir(self.backup_location)

        def get_datetime(entry):
            templist = entry.split("_")
            date = templist[0].split('-')
            time = templist[1].split('-')

            month = int(date[0])
            day = int(date[1])
            year = int(date[2])
            hour = int(time[0])
            minute = int(time[1])
            return datetime.datetime(year, month, day, hour, minute)

        sorted_backups = sorted(files, key=get_datetime, reverse=True)

        return sorted_backups

    def getServerProperties(self):
        path = f"{self.server_location}\\server.properties"
        file = open(path, 'r')
        propertiesDict = {}
        for x in file.readlines():
            # ignore comments at beginning of server.properties file
            if x.startswith("#"):
                continue

            if (x.startswith("rcon.password") or x.startswith("rcon.port") or x.startswith(
                    "query.port") or x.startswith("server-ip")):
                continue

            templist = x.strip().split('=')
            propertiesDict[templist[0]] = templist[1]
        return propertiesDict

    def changeServerProperties(self, newProperties: dict):
        # path = f"{self.server_location}\\server.properties"
        # file = open(path, 'r')
        # newList = file.readlines()
        # for i, x in enumerate(newList):
        #     templist = x.strip().split('=')

        #     # find correct property
        #     if (templist[0].strip() == property.strip()):
        #         # replace value with new value
        #         newList[i] = f"{property.strip()}={newValue.strip()}"

        # # write
        # writeFile = open(path, 'w')
        # writeFile.write('\n'.join(newList))

        path = f"{self.server_location}\\server.properties"
        file = open(path, 'r')
        newList = file.readlines()

        # Set newList with newProperties
        for key in newProperties:
            value = newProperties[key]

            for x in newList:
                if x.startswith("#"):
                    continue
                if x.strip().split("=")[0] == key:
                    newList[newList.index(x)] = f"{key}={value}\n"

        # Write entire list to file
        file.close()
        file = open(path, 'w')
        file.write("".join(newList))
        file.close()

    def getFilesInFolder(self, folder):
        dir = f"{self.server_location}\\{folder}"
        files = os.listdir(dir)
        filesDict = {}
        for file_name in files:
            file_loc = f"{dir}\\{file_name}"
            if os.path.isfile(file_loc):
                filesDict[file_name] = "file"
            elif os.path.isdir(file_loc):
                filesDict[file_name] = "folder"

        return filesDict

    def createModsZip(self):
        zf = zipfile.ZipFile(f"mod_zips/{self.name}.zip", "w")
        for dirname, subdirs, files in os.walk(os.path.join(self.server_location, "mods")):
            for filename in files:
                zf.write(os.path.join(dirname, filename), arcname=filename)
        zf.close()

    def hasModsFolder(self):
        if os.path.exists(os.path.join(self.server_location, "mods")):
            return True
        else:
            return False

    def startServer(self):
        serverRunPath = self.server_location + "run.bat"

        global s
        s = subprocess.Popen("\"" + serverRunPath + "\"", stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)

        def server_read_lines(process, queue):
            while True:
                if process.poll() is not None:
                    return
                queue.put((process.stdout.readline()).decode())

        # server reading thread
        qs = Queue()
        ts = Thread(target=server_read_lines, args=(s, qs))
        ts.daemon = True
        ts.start()

        while s.poll() is None:  # loop while the server process is running

            # just pass-through data from the server to the terminal output
            try:
                line = qs.get_nowait()
            except Empty:
                pass
            else:
                if line != "":
                    print(line)
                    self.console.append(line)

                    if len(self.console) > MAX_CONSOLE_LINES:
                        for x in range(len(self.console) - MAX_CONSOLE_LINES):
                            self.console.remove(self.console[0])
