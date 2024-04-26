var menu_button = document.getElementById("menu-button");

var sidebar_links = document.querySelectorAll(".sidebar-link");

var sidebar = document.querySelector(".sidebar");

var page = 0;


menu_button.addEventListener("click", openMenu);


// checks the url and loads the appropriate page so that reloading the page loads the same content
if (window.location.href.endsWith("#backups")) {
    openPage(1);
}
else if (window.location.href.endsWith("#options")) {
    openPage(2);
}
else if (window.location.href.endsWith("#files")) {
    openPage(3);
}
else if (window.location.href.endsWith("#mods")) {
    openPage(4);
}
else {
    openPage(0);
}


function isSidebarOpen() {
    if (sidebar.style.left != "0%") {
        return false;
    } else {
        return true;
    }
}

// document.body.addEventListener('click', closeMenu, true);

document.addEventListener("click", function(event) {
    // If user clicks inside the element, do nothing
    if (event.target.closest("#menu-button")) return
    if (event.target.closest(".sidebar")) return

    if (!isSidebarOpen()) return
    // If user clicks outside the element, hide it!
    closeMenu();
})

function openMenu() {
    sidebar.style.left = "0%";
}

function closeMenu() {
    sidebar.style.left = "-100%";
}


sidebar_links[0].addEventListener("click", function() {
    openPage(0);
});

sidebar_links[1].addEventListener("click", function() {
    openPage(1);
});

sidebar_links[2].addEventListener("click", function() {
    openPage(2);
});
sidebar_links[3].addEventListener("click", function() {
    openPage(3);
});
sidebar_links[4].addEventListener("click", function() {
    openPage(4);
});

function openPage(pageToOpen) {
    if (isSidebarOpen()) {
        closeMenu();
    }
    sidebar_links[page].style.borderLeft = "none";
    sidebar_links[page].style.backgroundImage = "none";

    page = pageToOpen;

    if (page == 0) {
        loadDoc("/" + server + "/overview");
    }
    else if (page == 1) {
        loadDoc("/" + server + "/backups");
    } else if (page == 2) {
        loadDoc("/" + server + "/options");
    } else if (page == 3) {
        loadDoc("/" + server + "/files");
    } else if (page == 4) {
        loadDoc("/" + server + "/mods");
    }


    sidebar_links[page].style.borderLeft = "solid 3px var(--accent)";
    sidebar_links[page].style.backgroundImage = "linear-gradient(to right, var(--lighter-background), var(--background))";
}


function loadDoc(url) {

    loadingSign();
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
        document.getElementById("content").innerHTML = this.responseText;

        // start backup javascript
        if (page == 1) {
            beginBackupJS();
        }
        else if (page == 2) {
            beginOptionsJS();
        }
        else if (page == 3) {
            beginFilesJS();
        }
    } else if (this.status == 403) {
        var xhttp2 = new XMLHttpRequest();
        xhttp2.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                document.getElementById("content").innerHTML = this.responseText;
            }
        };
        xhttp2.open("GET", "/unauthorized_page", true);
        xhttp2.send();
    }
    };
    xhttp.open("GET", url, true);
    xhttp.send();
}

function getUnauthorizedPage() {
    
}

function loadingSign() {
    document.getElementById("content").innerHTML = "<div class=\"loading-spinner\"></div>";
}




// only for backup page
function beginBackupJS() {
    var selectedBackup;
    var backups = document.querySelectorAll(".backup-list-item");

    for (var i = 0; i < backups.length; i++) {
        backups[i].addEventListener("click", function() {
            var restoreButton = document.querySelector(".restore");

            if (selectedBackup != null) {
                selectedBackup.style.backgroundColor = "";
                selectedBackup.style.color = "var(--darker-text)";
            }

            if (this == selectedBackup) {
                selectedBackup = null;
                
                restoreButton.classList.remove('active-restore');
                // restoreButton.style.backgroundColor = "var(--secondary-button)";
            } else {
                selectedBackup = this;
                this.style.backgroundColor = "var(--primary-button)";
                this.style.color = "var(--text)";

                restoreButton.classList.add('active-restore');
                // restoreButton.style.backgroundColor = "var(--primary-button)";
            }
        });
    }

    var backupButton = document.querySelector(".backup");

    backupButton.addEventListener("click", function() {
        
        $.post("/" + server + "/createBackup", {},
        function(data, status) {
        alert("Backup request sent.")
        });

    });

    var restoreButton = document.querySelector(".restore");
    restoreButton.addEventListener("click", function() {
        if (selectedBackup != null) {
            alert("Restore request sent.")
            $.post("/" + server + "/restoreBackup", {
                backupName: selectedBackup.innerHTML
            },
            function(data, status) {
                alert("Restore Complete.")
            }).fail(function(response) {
                if (response.status == 403) {
                    alert("Unauthorized")
                }
            });
        }
    });
}


// only for options page
function beginOptionsJS() {
    var saveButton = document.querySelector(".save-properties");

    saveButton.addEventListener("click", function() {


        var propertiesList = document.querySelectorAll(".property");
        var valueList = document.querySelectorAll(".value");

        var dictionary = {};

        for (var i = 0; i < propertiesList.length; i++) {
            dictionary[propertiesList[i].innerHTML] = valueList[i].value;
        }


        $.post("/" + server + "/saveProperties", dictionary, function(data, status) {

            alert(status);

        });
    });
}



currentPath = "\\";
// only for files page
function beginFilesJS() {
    
    var explorerList = document.querySelector(".explorer-list");

    var pathElement = document.querySelector(".explorer-path");

    var folderIcon = "<i class=\"fa-solid fa-folder\"></i>";

    var filesIcon = "<i class=\"fa-solid fa-file-lines\"></i>";

    files = {};


    function requestFiles() {
        $.post("/" + server + "/getFiles", {
            path: currentPath
        }, function(data, status) {
            loadFilesIntoExplorer(data);
            pathElement.innerHTML = currentPath;
        });
    
    }
    requestFiles();
    
    function loadFilesIntoExplorer(files) {
        var adding = ""

        for (let key in files) {
            var value = files[key];
        
            if (value == "folder") {
                var toAdd = "<li class=\"folder\">" +folderIcon + key + "</li>" + "\n"
            } else {
                var toAdd = "<li class=\"file\">" + filesIcon + key + "</li>" + "\n"
            }

            adding += toAdd;
        }

        explorerList.innerHTML = adding;


        var folders = document.querySelectorAll(".folder");
        for (var i = 0; i < folders.length; i++) {
            folders[i].addEventListener("click", function() {
                currentPath = currentPath + this.textContent + "\\";
                
                requestFiles();
            });
        }
    }

    var back_button = document.querySelector(".back-button");
    back_button.addEventListener("click", function() {
        folders = currentPath.split("\\");
        folders.pop();
        folders.pop();
        newPath = folders.join("\\") + "\\";

        currentPath = newPath;
        requestFiles();
    });


    // submit files - CHUNKED FILE UPLOADING - DOES NOT FULLY WORK
    function initSubmitFiles() {
        var submit_files_button = document.querySelector(".submit-files-button");
        submit_files_button.addEventListener("click", function() {
            var files = document.querySelector(".upload-files")
            for (file of files.files) {
                const chunkSize = 200*1024; // 200 kb
                let offset = 0;

                filename = file.name;
                console.log(filename);
                console.log(file.size);
                while (offset < file.size) {
                    const chunk = file.slice(offset, offset + chunkSize);
                    const formData = new FormData();


                    formData.append('file', chunk);
                    formData.append('path', currentPath);
                    formData.append('name', filename);
                
                    try {
                        fetch("/" + server + "/sendFiles/", {
                            method: 'POST',
                            body: formData,
                        })
                        .then(data => {
                            console.log('Response:', data);
                            // Handle server response
                            
                        })
                        .catch(error => {
                            console.error('Error:', error);
                            
                        });
                        
                        offset += chunkSize;
                    } catch (error) {
                        console.error('Error uploading chunk:', error);
                        break;
                    }
                }


                // tell server the file is complete
                finalFormData = new FormData();
                finalFormData.append('complete', "true");
                fetch("/" + server + "/sendFiles", {
                    method: 'POST',
                    body: finalFormData,
                })
                .then(data => {
                    console.log('Response:', data);
                    // Handle server response
                    requestFiles();
                })
                .catch(error => {
                    console.error('Error:', error);
                });
                
            }
        });
    }
}