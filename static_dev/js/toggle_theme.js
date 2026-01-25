const theme_btn = document.getElementById('theme_btn')
let current_theme = localStorage.getItem('theme') || 'light'
save_theme_on_server(current_theme)

theme_btn.addEventListener('click', async function () {
    current_theme = current_theme === 'light' ? 'dark' : 'light'
    await apply_theme(current_theme)
    localStorage.setItem('theme', current_theme)
});

async function save_theme_on_server(theme) {
    try {
        await fetch('/api/toggle_theme/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': api_app.get_cookie('csrftoken'),
            },
            body: JSON.stringify({theme: theme})
        });
    } catch (err) {
        console.log('Theme not saved on server:', err)
    }
}

async function apply_theme(theme) {
    document.documentElement.setAttribute('data-bs-theme', theme);
    await save_theme_on_server(theme)
    if (theme === 'dark') {
        theme_btn.classList.add('btn-light')
        theme_btn.classList.remove('btn-dark')
        theme_btn.innerText = 'Светлая тема'
    } else {
        theme_btn.classList.add('btn-dark')
        theme_btn.classList.remove('btn-light')
        theme_btn.innerText = 'Тёмная тема'
    }
}