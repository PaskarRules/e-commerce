var modal = document.getElementById("myModal");

var btns = document.getElementsByClassName("myBtn");

var span = document.getElementsByClassName("close")[0];

var modal_content = document.getElementById("modal-content");

for (let i = 0; i < btns.length; i++) {
    btns[i].onclick = function () {
        $.ajax({
            type: 'GET',
            async: true,
            url: '/ajax/order-' + btns[i].textContent,
            data: "",
            success: function (data) {
                data = JSON.parse(data)
                modal_content.innerText = ''
                modal_content.innerHTML +=
                    '<div class="cart-row">\n' +
                    '<div style="flex:2"><strong></strong></div>\n' +
                    '<div style="flex:2"><p align="left"><strong>Продукт</strong></p></div>\n' +
                    '<div style="flex:1"><p align="left"><strong>Ціна</strong></p></div>\n' +
                    '<div style="flex:1"><p align="left"><strong>Кількість</strong></p></div>\n' +
                    '<div style="flex:1"><p align="left"><strong>Загальна вартість</strong></p></div>\n' +
                    '</div>'
                for (var j = 0; j < data.length; j++) {
                    modal_content.innerHTML +=

                        '<div class="cart-row">\n' +
                        '<div style="flex:2"><img class="row-image" src="' + data[j].image + '"></div>\n' +
                        '<div style="flex:2"><a href="../' + data[j].url + '">' + data[j].name + '</a></div>\n' +
                        '<div style="flex:1"><p>' + data[j].price + ' UAH' + '</p></div>\n' +
                        '<div style="flex:1">\n' +
                        '<p class="quantity">' + data[j].qty + '</p>\n' +
                        '</div>\n' +
                        '<div style="flex:1"><p>' + Number(data[j].total.toFixed(2)) + ' UAH' + '</p></div>\n' +
                        '</div>'
                }
            },
            dataType: 'json',
        });

        modal.style.display = "block";
    }
}

span.onclick = function () {
    modal.style.display = "none";
}


window.onclick = function (event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}
