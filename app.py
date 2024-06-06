import datetime
import json
import os
from threading import Thread

from dotenv import load_dotenv
from flask import Flask, render_template, redirect, request, url_for, send_file
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)

import db
import setup
from login import *

load_dotenv()

app = Flask(__name__)

secret_key = os.getenv('SECRET_KEY')
if secret_key is None:
    print("Create the .env file with the SECRET_KEY variable")
    exit()
app.config["SECRET_KEY"] = os.getenv('SECRET_KEY')

login_manager = LoginManager(app)
login_manager.login_view = 'loginPage'  # loginPage is the function name to redirect to if user is trying to access unauthorized pages


@login_manager.user_loader
def load_user(user_id: str) -> Optional[User]:
    return User.get(user_id)


setup.setup()

with open("users.json") as file:
    data = json.load(file)
    for key in data:
        users[key] = User(
            id=key,
            username=data[key]["username"],
            password=data[key]["password"],
            permissions=data[key]["permissions"]
        )

serverList = db.getServerInfo()


def getServer(name):
    for server in serverList:
        if server.name == name:
            return server
    return None


@app.route("/")
def index():
    return redirect('/servers/')


# login page
@app.route("/login/")
def loginPage():
    logout_user()
    return render_template('login.html')


# login redirect method
@app.get("/users/<id>/<password>")
def login(id, password):
    user = User.get(id)
    print(user)
    if user and user.password == password:
        login_user(user)
        return redirect(url_for("index"))
    return redirect("/login", code=302)


@app.get("/validate/<id>/<password>")
def validateLogin(id, password):
    user = User.get(id)
    print(user)
    if user and user.password == password:
        login_user(user)
        return 'Valid'
    return 'Invalid'


@app.route("/servers/")
@login_required
def serversPage():
    return render_template('servers.html', servers=serverList)


@app.route('/<server>/dashboard/')
@login_required
def dashboard(server):
    return render_template('dashboard.html', server=server)


@app.route('/<server>/overview/')
@login_required
def overview(server):
    # this renders the overview.html file as if serverstatus is off no matter what it actually is because 
    # checking if it is off will take too long and the javascript will asynchronously request it anyway

    # serverStatus = "ON" if getServer(server).isOn() else "OFF"
    return render_template('overview.html', serverstatus="OFF")


@app.route('/<server>/backups/')
@login_required
def backups(server):
    backups = db.readInfo(server).backuplist()

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

    if len(backups) == 0:
        dayDiffReturn = 'Never'
    else:
        latestBackupTime = get_datetime(backups[0])
        today = datetime.datetime.now()
        dayDiff = (today - latestBackupTime)
        dayDiffReturn = str(dayDiff.days) + ' days ago'

    return render_template('backups.html', backups=backups, latest_backup=dayDiffReturn)


@app.route('/<server>/options/')
@login_required
def server_options(server):
    if current_user.permissions <= 2:
        print("Unauthorized")
        return "Unauthorized", 403
    return render_template('options.html', properties=getServer(server).getServerProperties())


@app.route('/<server>/files/')
@login_required
def filesPage(server):
    return render_template('files.html')


@app.route('/<server>/getFiles', methods=['POST'])
@login_required
def getFilesAt(server):
    mcserver = getServer(server)
    files = mcserver.getFilesInFolder(request.form.get('path'))

    return files


@app.route('/<server>/start/', methods=["POST"])
@login_required
def startServer(server):
    mcserver = getServer(server)

    if not mcserver.isOn():
        mcserver.startServer()

    return "Success", 200


@app.route("/<server>/stop/", methods=["POST"])
@login_required
def stopServer(server):
    mcserver = getServer(server)
    if mcserver.isOn:
        mcserver.stop()

    return "Success", 200


@app.route("/<server>/isOn/", methods=["GET"])
@login_required
def isServerOn(server):
    mcserver = getServer(server)
    if mcserver != None:
        serverstatus = "ON" if mcserver.isOn() else "OFF"
        return serverstatus, 200
    else:
        return "Invalid Server Name", 400


@app.route("/<server>/console/", methods=["GET"])
@login_required
def getConsole(server):
    mcserver = getServer(server)
    return "<br>".join(mcserver.console)


@app.route("/<server>/sendCommand/", methods=["POST"])
@login_required
def sendCommand(server):
    if current_user.permissions <= 3:
        print("Unauthorized")
        return "Unauthorized", 403
    mcserver = getServer(server)

    command = request.form.get("command")
    print("/" + command)

    if command == 'stop':
        stopServer(server)
    else:
        mcserver.runCommand(command)

    return '', 200


@app.route("/<server>/createBackup/", methods=["POST"])
@login_required
def createBackup(server):
    mcserver = getServer(server)

    backupThread = Thread(target=mcserver.backup)
    backupThread.daemon = True
    backupThread.start()

    return '', 200


@app.route("/<server>/restoreBackup/", methods=["POST"])
@login_required
def restoreBackup(server):
    if current_user.permissions <= 4:
        print("Unauthorized")
        return "Unauthorized", 403

    mcserver = getServer(server)

    print(request.form.get("backupName"))

    mcserver.restore(request.form.get("backupName"))

    return '', 200


@app.route("/<server>/saveProperties/", methods=["POST"])
@login_required
def saveProperties(server):
    if current_user.permissions <= 3:
        print("Unauthorized")
        return "Unauthorized", 403

    mcserver = getServer(server)

    dict = {}
    for i, x in enumerate(request.form.keys()):
        dict[x] = request.form.get(x)

    mcserver.changeServerProperties(dict)

    return '', 200


@app.route("/<server>/players/", methods=["GET"])
@login_required
def getPlayers(server):
    mcserver = getServer(server)
    return mcserver.getPlayers()


@app.route("/unauthorized_page", methods=["GET"])
def getUnauthorizedPage():
    return render_template("unauthorized_page.html")


@app.route("/<server>/mods/", methods=["GET"])
@login_required
def downloadMods(server):
    mcserver = getServer(server)
    if mcserver.hasModsFolder():
        return render_template("download_mods.html")
    else:
        return "No mods folder found"


@app.route("/<server>/dashboard/request_download_mods/", methods=["POST"])
@login_required
def createZipOfMods(server):
    mcserver = getServer(server)
    mcserver.createModsZip()
    return '', 200


@app.route('/<server>/dashboard/download_zip/')
@login_required
def download(server):
    mcserver = getServer(server)
    path = f'mod_zips/{mcserver.name}.zip'
    return send_file(path, as_attachment=True)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80, debug=False)
