function createAddressInput(text) {
    let input = document.createElement('input');
    input.classList.add('collection-item');
    if (text === undefined) {
        input.value = "No addresses yet."
    } else {
        input.value = text
    }
    input.style.color = "red";
    input.style.fontSize = "12px";
    input.style.textAlign = "center";
    input.style.height = "25px";
    input.style.cursor = "pointer";
    input.readOnly = true;
    input.style.marginTop = "1px";
    return input
}

let mine = document.getElementById('mine');
mine.addEventListener('click', function () {
    let xhr = new XMLHttpRequest();
    xhr.open('GET', '/miner/mine_pendings', false);
    xhr.send();
    if (xhr.status !== 200) {
        console.log(xhr.status + ': ' + xhr.statusText)
    } else {
        if (xhr.responseText == "Need more transactions!") {
            M.AutoInit();
            M.toast({html: 'Need more transactions!'});
        }
        if (xhr.responseText == "True") {
            M.AutoInit();
            M.toast({html: 'Mined!'});
        }
        console.log(xhr.responseText)
    }
});

let generate = document.getElementById('new_key');
generate.addEventListener('click', function () {
    let xhr = new XMLHttpRequest();
    xhr.open('GET', '/miner/new', false);
    xhr.send();
    if (xhr.status !== 200) {
        console.log(xhr.status + ': ' + xhr.statusText)
    } else {
        let index = 1;
        while (index <= 4) {
            let generated = document.getElementById('disabled_' + index);
            generated.style.font = "italic bold 10px arial,serif";
            generated.style.color = "red";
            generated.style.marginTop = "-10px";
            generated.style.cursor = "pointer";
            generated.readOnly = true;
            generated.addEventListener('click', function () {
                generated.select();
                document.execCommand("copy");
                M.AutoInit();
                M.toast({html: 'Copied to clipboard!'})
            });
            index++
        }
        index = 1;
        while (index <= 4) {
            document.getElementById('disabled_' + index).value = xhr.responseText.split(',')[index - 1];
            index++
        }
    }
});

let import_key = document.getElementById('import');
import_key.addEventListener('click', function () {
    let key = document.getElementById('imported_key').value;
    let params = '?key=' + key;
    let xhr = new XMLHttpRequest();
    xhr.open('GET', '/miner/import' + params, false);
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.send();
    if (xhr.status !== 200) {
        console.log(xhr.status + ': ' + xhr.statusText)
    } else {
        let index = 1;
        while (index <= 4) {
            document.getElementById('import_' + index).style.display = "block"
            index++
        }
        index = 1;
        while (index <= 4) {
            document.getElementById('imported_' + index).value = xhr.responseText.split(',')[index - 1]
            index++
        }
        index = 1;
        while (index <= 4) {
            let generated_import = document.getElementById('imported_' + index);
            generated_import.style.font = "italic bold 10px arial,serif";
            generated_import.style.color = "red";
            generated_import.style.marginTop = "-10px";
            generated_import.style.cursor = "pointer";
            generated_import.readOnly = true;
            generated_import.addEventListener('click', function () {
                generated_import.select();
                document.execCommand("copy");
                M.AutoInit();
                M.toast({html: 'Copied to clipboard!'})
            });
            index++
        }
        document.getElementById('imported_key').style.font = "italic bold 10px arial,serif";
        document.getElementById('imported_key').style.color = "red"
    }
});

let addresses = document.getElementById('tab4');
addresses.addEventListener('click', function () {
    let xhr = new XMLHttpRequest();
    xhr.open('GET', '/miner/get_addresses', false);
    xhr.send();
    if (xhr.status !== 200) {
        console.log(xhr.status + ': ' + xhr.statusText)
    } else {
        let collection = document.getElementById('collection');
        while (collection.firstChild) {
            collection.removeChild(collection.firstChild);
        }
        let len = xhr.responseText.length;
        if (len <= 1) {
            let input = createAddressInput();
            collection.appendChild(input)
        } else {
            let input = createAddressInput(xhr.responseText);
            collection.appendChild(input);
            let child = collection.firstChild;
            child.addEventListener('click', function () {
                child.select();
                document.execCommand("copy");
                M.AutoInit();
                M.toast({html: 'Copied to clipboard!'})
            })
        }
    }
});