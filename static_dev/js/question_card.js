function open_card(id) {
    window.location = `/question/${id}`
}

function open_tag(event, tag) {
    event.stopPropagation()
    window.location = `/tag/${tag}/`
}
