window.addEventListener("load", (event) => {
    updateServerStatus();
    updateConsole();
    updatePlayers();
});

startTimer = 0;


function startServer() {
    if (Date.now() - startTimer < 1000*10) {
        alert("Stop spamming!");
    } else {
        $.post("/" + server + "/start/", {}, function(data, status) {

        });
    }
    startTimer = Date.now();
}


function stopServer() {
    $.post("/" + server + "/stop/", {}, function(data, status) {

    });
}


function updateServerStatus() {
    var serverStatus = document.querySelector(".serverstatus");
    if (page == 0 && serverStatus != null) {
        $.get("/" + server + "/isOn/", {}, function(data, status) {
            
            if (data == "ON") {
                serverStatus.innerHTML = data;
                serverStatus.style.color = "rgb(14, 182, 14)";

            } else {
                serverStatus.innerHTML = "OFF";
                serverStatus.style.color = "rgb(231, 21, 21)";
            }
        })
    }
}



setInterval(updateServerStatus, 5000);

function updateConsole() {
    var commandConsole = document.querySelector(".console");
    if (page == 0 && commandConsole != null) {
        $.get("/" + server + "/console/", {}, function(data, status) {
            commandConsole.innerHTML = data;
            var objDiv = document.getElementById("console");
            objDiv.scrollTop = objDiv.scrollHeight;
        });
    }
}

setInterval(updateConsole, 2000);

function sendCommand() {
    var request = new XMLHttpRequest();
    var command = document.forms["commandForm"]["command"].value;
    request.open('POST', '/' + server + '/sendCommand/');
    // send command in form data
    var formData = new FormData();
    formData.append('command', command);
    
    request.send(formData);
    document.forms["commandForm"].reset();

    request.onload = function() {
        if (request.status === 200) {
            updateConsole();
        } else if (request.status == 403) {
            alert(request.responseText);
        }
    }    

    return false;
}

function updatePlayers() {
    var player_list = document.querySelector(".player-list");
    if (page == 0 && console != null) {
        $.get("/" + server + "/players/", {}, function(data, status) {
            if (data.length == 0) {
                var no_players_text = "<h3 class=\"no-players\">No Players Online</h3>";
                player_list.innerHTML = no_players_text;
            } else {
                var player_list_text = "";
                for (var i = 0; i < data.length; i++) {
                    // using minotar api
                    var player_head_image = "https://minotar.net/helm/" + data[i] + "/100.png"

                    var player_element = "<div class=\"player-element\"><img class=\"player-img\" src=\""
                    + player_head_image + "\" alt=\"\"><p>" + data[i] + "</p></div>"
                    player_list_text += player_element
                }
                player_list.innerHTML = player_list_text;
            }
            
        });
    }
}

setInterval(updatePlayers, 5000);