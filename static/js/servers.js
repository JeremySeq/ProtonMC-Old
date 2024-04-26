
var rows = document.querySelectorAll("tr");
var server_rows = [];
for (var i = 1; i < rows.length; i++) {
    server_rows.push(rows[i]);
}
console.log(server_rows);

for (var i = 0; i < server_rows.length; i++) {
    server_rows[i].addEventListener("click", function() {
        console.log(this.firstElementChild.textContent);
        window.location = "/" + this.firstElementChild.textContent + "/dashboard";
    });
}