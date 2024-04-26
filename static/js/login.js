function validateForm() {
    var username = document.forms["form"]["username"].value;
    var password = document.forms["form"]["password"].value;
    if (username == "" || password == "") {
        return false;
    }

    const request = new XMLHttpRequest();
    request.open('GET', '/validate/' + username + '/' + password, false);  // `false` makes the request synchronous
    request.send();

    if (request.status === 200) {
        if (request.response == 'Valid') {
            window.location = "/users/" + username + "/" + password;
            return false;
        } else {
            alert('No account found with this username and password', 'danger')
            return false;
        }
    }

    return false;
}