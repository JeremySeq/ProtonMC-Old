
function sendDownloadRequest() {

    loading = document.getElementById("loading");
    loading_complete = document.getElementById("loading-complete");

    loading.style.visibility = "visible";

    fetch("request_download_mods", {
        method: "POST"
    })
    .then((response) => {
        if (response.status == 200) {
            console.log("200")

            loading.style.visibility = "hidden";

            window.location.href = "download_zip";
        }
    });
}