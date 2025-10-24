const path = window.location.pathname;
const parts = path.split('/').filter(part => part !== '');
const question_id = parts[parts.length - 1];

fetch('/api/centrifugo/token/')
    .then(response => response.json())
    .then(data => {
        const centrifuge = new Centrifuge('ws://localhost/connection/websocket', {
            token: data.token
        });
        const subscription = centrifuge.newSubscription(question_id);

        subscription.on('publication', function (message) {
            console.log(message)
            let card = message.data.html
            answers_div.innerHTML = card + answers_div.innerHTML
        });

        subscription.subscribe();
        centrifuge.connect();
    });
