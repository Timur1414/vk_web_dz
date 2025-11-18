document.addEventListener('DOMContentLoaded', function () {
    const messages = document.querySelectorAll('.alert');

    messages.forEach(function (message) {
        setTimeout(function () {
            message.style.opacity = '0';
            setTimeout(function () {
                message.remove();
            }, 300);
        }, 5000);
    });
});