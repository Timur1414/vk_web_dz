async function correct(answer_id) {
    let input = document.getElementById(`answer_input_${answer_id}`)
    let response = await fetch(`/api/mark_answer/?answer_id=${answer_id}`)
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