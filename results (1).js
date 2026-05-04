function showCards(data) {
    var area = document.getElementById("cards-area");
    area.innerHTML = "";

    data.recommendations.forEach(item => {
        let div = document.createElement("div");

        div.innerHTML = `
            <p>Product: ${item.product_id}</p>
            <p>Category: ${item.category}</p>
            <p>Price: ${item.price}</p>
        `;

        area.appendChild(div);
    });
}