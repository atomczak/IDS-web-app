function addSpecification(event) {
    event.preventDefault();
    fetch("/add_specification")
        .then(results => { console.log(results) })
        .catch(error => { console.log(error) })
}

document.getElementById("add-specification").addEventListener("click", addSpecification)
