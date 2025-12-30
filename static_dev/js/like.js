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


let is_question_liked = false
if (is_liked.innerText === 'True')
    is_question_liked = true


async function question_like(question_id) {
    let response = await fetch(`/api/question_like/?question_id=${question_id}`, {
        method: 'POST',
        headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': get_cookie('csrftoken'),
        },
    })
    let data = await response.json()
    if (response.status !== 200) {
        alert(data.message)
        return
    }
    let count_likes = data.count
    if (is_question_liked) {
        like_btn.classList.remove('btn-success')
        like_btn.classList.add('btn-outline-secondary')
        is_question_liked = false
    }
    else {
        like_btn.classList.add('btn-success')
        like_btn.classList.remove('btn-outline-secondary')
        is_question_liked = true
    }
    like_btn.innerText = '👍: ' + String(count_likes)
}

async function answer_like(answer_id) {
    let btn = document.getElementById(`answer_like_btn_${answer_id}`)
    let response = await fetch(`/api/answer_like/?answer_id=${answer_id}`, {
        method: 'POST',
        headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': get_cookie('csrftoken'),
        },
    })
    let data = await response.json()
    if (response.status !== 200) {
        alert(data.message)
        return
    }
    let liked = btn.classList.contains('btn-success')
    let count_likes = data.count
    if (liked) {
        btn.classList.remove('btn-success')
        btn.classList.add('btn-outline-secondary')
    }
    else {
        btn.classList.add('btn-success')
        btn.classList.remove('btn-outline-secondary')
    }
    btn.innerText = '👍: ' + String(count_likes)
}