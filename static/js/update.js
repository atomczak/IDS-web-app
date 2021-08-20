var URL = "http://127.0.0.1:5000/api/"
var alertMessage = null;

function updateField(fieldName) {
    var fieldValue = document.getElementById(fieldName).value;
    fetch(URL + fieldName + "&" + fieldValue)
    // .then(function (response) {
    //     debugger;
    //     return response.body;
    // })
    // .then(function (data) {
    //     // document.getElementById(fieldName).value = "NOWY TEKST";
    //     // document.getElementById("demo2").innerHTML = JSON.stringify(data.number);
    //     console.log(data);
    // }).catch(function () {
    //     console.log("Error");
    // });
}

function updateSpecificationName(specId) {
    var fieldValue = document.getElementById('spec_' + specId).value;
    fetch(URL + "specificationName&" + specId + "&" + fieldValue)
}

function updateSpecification(e) {
    var data = { id: e.target.id, value: e.target.value }
    fetch(URL + 'specification', {
        method: 'POST', // *GET, POST, PUT, DELETE, etc.
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data) // body data type must match "Content-Type" header
    }).then((result) => console.log(result)).catch((error) => console.log(error))
}

function updateEntity(e) {
    var data = { id: e.target.id, value: e.target.value }
    fetch(URL + 'entity', {
        method: 'POST', // *GET, POST, PUT, DELETE, etc.
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data) // body data type must match "Content-Type" header
    }).then((result) => console.log(result)).catch((error) => console.log(error))
}

function downalodIds() {
    fetch(URL + 'download-ids')
        // .then(console.log('success'))
        // .catch((error) => console.log(error))
}