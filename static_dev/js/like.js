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
        let count_likes = Number(like_btn.innerText)
        count_likes -= 1
        like_btn.innerText = String(count_likes)
    }
    else {
        like_btn.classList.add('btn-success')
        like_btn.classList.remove('btn-outline-secondary')
        is_question_liked = true
        let count_likes = Number(like_btn.innerText)
        count_likes += 1
        like_btn.innerText = String(count_likes)
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
        let count_likes = Number(btn.innerText)
        count_likes -= 1
        btn.innerText = String(count_likes)
    }
    else {
        btn.classList.add('btn-success')
        btn.classList.remove('btn-outline-secondary')
        let count_likes = Number(btn.innerText)
        count_likes += 1
        btn.innerText = String(count_likes)
    }
}