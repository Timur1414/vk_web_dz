async function correct(answer_id) {
    let input = document.getElementById(`answer_input_${answer_id}`)
    let response = await fetch(`/api/answer_check/?answer_id=${answer_id}`)
    if (response.status !== 200)
        return
    let correct = input.classList.contains('checked')
    if (correct)
        input.classList.remove('checked')
    else
        input.classList.add('checked')
}