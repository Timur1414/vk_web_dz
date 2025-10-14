let is_question_liked = false
if (is_liked.innerText === 'True')
    is_question_liked = true


async function question_like(question_id) {
    let response = await fetch(`/api/question_like/?question_id=${question_id}`)
    if (response.status !== 200)
        return
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
}

async function answer_like(answer_id) {
    let btn = document.getElementById(`answer_like_btn_${answer_id}`)
    let response = await fetch(`/api/answer_like/?answer_id=${answer_id}`)
    if (response.status !== 200)
        return
    let liked = btn.classList.contains('btn-success')
    if (liked) {
        btn.classList.remove('btn-success')
        btn.classList.add('btn-outline-secondary')
    }
    else {
        btn.classList.add('btn-success')
        btn.classList.remove('btn-outline-secondary')
    }
}