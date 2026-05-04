function doSearch() {
    var uid = document.getElementById("uid-input").value;
    var err = document.getElementById("err-box");

    if (!uid || uid < 1) {
        err.innerText = "Invalid ID";
        return;
    }

    fetchRecommendations(uid);
}