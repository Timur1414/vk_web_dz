let timer = setTimeout(1000)


async function find() {
    let input = search_input.value
    if (input === "") {
        search_datalist.innerHTML = ""
        search_datalist.classList.remove('show')
        return
    }
    let response = await fetch(`/api/search_questions/?text=${input}`)
    let data = await response.json()
    search_datalist.innerHTML = data.html
    search_datalist.classList.add('show')
}

function search() {
    clearTimeout(timer)
    timer = setTimeout(find, 1000)
}