const SERVER = "http://127.0.0.1:8000";

async function fetchRecommendations(uid) {
    try {
        let res = await fetch(SERVER + "/recommend?user_id=" + uid);
        let data = await res.json();

        showCards(data);
    } catch (e) {
        console.log(e);
    }
}