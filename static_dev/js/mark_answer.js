function get_cookie(name) {
    let cookie_value = null
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';')
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim()
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookie_value = decodeURIComponent(cookie.substring(name.length + 1))
                break
            }
        }
    }
    return cookie_value;
}


async function correct(answer_id) {
    let input = document.getElementById(`answer_input_${answer_id}`)
    let response = await fetch(`/api/mark_answer/?answer_id=${answer_id}`, {
        method: 'POST',
        headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': get_cookie('csrftoken'),
        },
    })
    if (response.status !== 200) {
        let data = await response.json()
        alert(data.message)
        return
    }
    let correct = input.classList.contains('checked')
    if (correct)
        input.classList.remove('checked')
    else
        input.classList.add('checked')
}

function disable_btn() {
    let answer_btn = document.getElementById('answer_btn')
    answer_btn.disabled = true
}