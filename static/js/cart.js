var updateBtns = document.getElementsByClassName('update-cart')

for (i = 0; i < updateBtns.length; i++) {
    updateBtns[i].addEventListener('click', function () {
        var productId = this.dataset.product
        var action = this.dataset.action
        // console.log('productId:', productId, 'Action:', action)
        // console.log('USER:', user)

        if (user == 'AnonymousUser') {
            addCookieItem(productId, action)
        } else {
            updateUserOrder(productId, action)
        }
    })
}

function updateUserOrder(productId, action) {
    var url = '/update_item/'

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({'productId': productId, 'action': action})
    })
        .then((response) => {
            return response.json();
        })
        .then((data) => {
            location.reload()
        });
}

function addCookieItem(productId, action) {
    if (action == 'add') {
        if (cart[productId] == undefined) {
            cart[productId] = {'quantity': 1}

        } else {
            cart[productId]['quantity'] += 1
        }
    }

    if (action == 'remove') {
        cart[productId]['quantity'] -= 1

        if (cart[productId]['quantity'] <= 0) {
            delete cart[productId];
        }
    }

    if (action == 'cancel') {
        delete cart[productId];
    }
    console.log('CART:', cart)
    document.cookie = 'cart=' + JSON.stringify(cart) + ";domain=;path=/"

    location.reload()
}

var updateInput = document.getElementsByClassName('update-cart-input')

for (i = 0; i < updateInput.length; i++) {
    updateInput[i].addEventListener('input', function (evt) {
        var productId = this.dataset.product
        var action = this.dataset.action
        var values = this.value
        console.log('productId:', productId, 'Action:', action)

        if (user == 'AnonymousUser') {
            addCookieItemInput(productId, action, values)
        } else {
            updateUserOrderInput(productId, action, values)
        }
    })
}


function updateUserOrderInput(productId, action, value) {
    console.log('User is authenticated, sending data...')

    var url = '/update_item/'

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({'productId': productId, 'action': action, 'value': value})
    })
        .then((response) => {
            return response.json();
        })
        .then((data) => {
            location.reload()
        });
}

function addCookieItemInput(productId, action, value) {
    console.log('User is not authenticated')
    console.log(value)
    if (action == 'set' && value) {
        value = parseInt(value)
        if (cart[productId] == undefined) {
            cart[productId] = {'quantity': value}
        } else {
            cart[productId]['quantity'] = value
        }
    }

    if (cart[productId]['quantity'] <= 0) {
        console.log('Item should be deleted')
        delete cart[productId];
    }
    console.log('CART:', cart)
    document.cookie = 'cart=' + JSON.stringify(cart) + ";domain=;path=/"

    location.reload()
}

var cancelBtns = document.getElementsByClassName('cncl-order')

for (i = 0; i < cancelBtns.length; i++) {
    cancelBtns[i].addEventListener('click', function () {
        var orderId = this.dataset.order
        var action = this.dataset.action
        console.log('order:', orderId, 'Action:', action)

        cancelOrder(orderId, action)
    })
}

function cancelOrder(orderId, action) {
    var url = '/cancel_order/'

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({'orderId': orderId, 'action': action})
    })
        .then((response) => {
            return response.json();
        })
        .then((data) => {
            location.reload()
        });
}