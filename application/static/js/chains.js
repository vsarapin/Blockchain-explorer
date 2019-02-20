$('.dropdown-trigger').dropdown();
$(document).ready(function () {
    $('.modal').modal();
});

function createAddressInput(text) {
    let input = document.createElement('input');
    input.classList.add('collection-item');
    if (text === undefined) {
        input.value = "Pending pool is empty."
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

let node = document.getElementById('add_node');
let block_height = 0;
node.addEventListener('click', function () {
    let value = document.getElementById('node_value').value;
    let xhr = new XMLHttpRequest();
    xhr.open('GET', '/chains/add_node/?node=' + value, false);
    xhr.send();
    if (xhr.status !== 200) {
        console.log(xhr.status + ': ' + xhr.statusText)
    } else {
        block_height = xhr.responseText;
        console.log(xhr.responseText);
    }
});

let consensus = document.getElementById('consensus');
consensus.addEventListener('click', function () {
        let xhr = new XMLHttpRequest();
        xhr.open('GET', '/chains/block_counter', false);
        xhr.send();
        if (xhr.status !== 200) {
            console.log(xhr.status + ': ' + xhr.statusText)
        } else {
            let value = document.getElementById('node_value').value;
            let xhr = new XMLHttpRequest();
            xhr.open('GET', value + '/chains/waiting_for_request/?count=' + block_height, false);
            xhr.send();
            if (xhr.status !== 200) {
                console.log(xhr.status + ': ' + xhr.statusText)
            } else {
                if (xhr.responseText == "give_me") {
                    let xhr = new XMLHttpRequest();
                    xhr.open('GET', '/chains/give_blocks' + xhr.responseText, false);
                    xhr.send();
                    if (xhr.status !== 200) {
                        console.log(xhr.status + ': ' + xhr.statusText)
                    } else {
                        let xhr = new XMLHttpRequest();
                        xhr.open('GET', value + '/chains/consensus/?blocks=' + xhr.responseText, false);
                        xhr.send();
                    }
                } else {
                    let xhr = new XMLHttpRequest();
                    console.log(xhr.responseText)
                    xhr.open('GET', '/chains/consensus/?blocks=' + xhr.responseText, false);
                    xhr.send();
                    if (xhr.status !== 200) {
                        console.log(xhr.status + ': ' + xhr.statusText)
                    } else {
                        M.AutoInit();
                        M.toast({html: 'Copied to clipboard!'})
                    }
                }
            }
        }
    }
);

let utxo = document.getElementById('tab4');
utxo.addEventListener('click', function () {
    let xhr = new XMLHttpRequest();
    xhr.open('GET', '/chains/utxo', false);
    xhr.send();
    if (xhr.status !== 200) {
        console.log(xhr.status + ': ' + xhr.statusText)
    } else {
        let collection = document.getElementById('collection');
        if (xhr.responseText == false) {
            let input = utxoNotExists();
            collection.appendChild(input);
        } else {
            while (collection.firstChild) {
                collection.removeChild(collection.firstChild);
            }
            let delTxRaw = JSON.parse(xhr.responseText)

            Object.keys(delTxRaw).map(function (key) {
                for (let index = 0; index < delTxRaw[key].length; index++) {
                    delete delTxRaw[key][index].tx_raw
                }
            });
            let pre = document.createElement('pre');
            pre.innerHTML = syntaxHighlight(JSON.stringify(delTxRaw, undefined, 2));
            collection.appendChild(pre);
        }
    }
});

function syntaxHighlight(json) {
    json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function (match) {
        let cls = 'number';
        if (/^"/.test(match)) {
            if (/:$/.test(match)) {
                cls = 'key';
            } else {
                cls = 'string';
            }
        } else if (/true|false/.test(match)) {
            cls = 'boolean';
        } else if (/null/.test(match)) {
            cls = 'null';
        }
        return '<span style="word-break: break-word" class="' + cls + '">' + match + '</span>';
    });
}

function utxoNotExists() {
    let input = document.createElement('input');
    input.classList.add('collection-item');
    input.value = "No utxo set yet.";
    input.style.color = "red";
    input.style.fontSize = "12px";
    input.style.textAlign = "center";
    input.style.height = "25px";
    input.style.cursor = "pointer";
    input.readOnly = true;
    return input
}

function form_modal_dialogs(event) {
    let block_number = event.path[0].id;
    let xhr = new XMLHttpRequest();
    xhr.open('GET', '/chains/show_block/?height=' + parseInt(block_number), false);
    xhr.send();
    if (xhr.status !== 200) {
        console.log(xhr.status + ': ' + xhr.statusText)
    } else {
        let block_info = document.getElementById('block_info');
        while (block_info.firstChild) {
            block_info.removeChild(block_info.firstChild);
        }
        let block_json = JSON.parse(xhr.responseText);
        let pre = document.createElement('pre');
        pre.innerHTML = syntaxHighlight(JSON.stringify(block_json, undefined, 2));
        block_info.appendChild(pre);
    }
}

function get_blocks_count() {
    let xhr = new XMLHttpRequest();
    xhr.open('GET', '/chains/block_counter', false);
    xhr.send();
    if (xhr.status !== 200) {
        console.log(xhr.status + ': ' + xhr.statusText)
    } else {
        let ul = document.getElementById('dropdown1');
        if (parseInt(xhr.responseText) != 0) {
            for (let index = 1; index <= parseInt(xhr.responseText); index++) {
                let li = document.createElement('li');
                let a = document.createElement('a');
                a.textAlign = "center";
                a.innerText = index;
                a.id = index;
                a.setAttribute("data-target", "modal1");
                a.addEventListener('click', form_modal_dialogs);
                a.classList.add('modal-trigger');
                li.appendChild(a);
                ul.appendChild(li)
            }
        } else {
            let li = document.createElement('li');
            let a = document.createElement('a');
            a.innerText = 'No blocks yet!';
            li.appendChild(a);
            ul.appendChild(li);
        }
    }
}

let addresses = document.getElementById('tab3');
addresses.addEventListener('click', function () {
    let xhr = new XMLHttpRequest();
    xhr.open('GET', '/chains/pendings', false);
    xhr.send();
    if (xhr.status !== 200) {
        console.log(xhr.status + ': ' + xhr.statusText)
    } else {
        let collection = document.getElementById('collection_pendings');
        while (collection.firstChild) {
            collection.removeChild(collection.firstChild);
        }
        let array = xhr.responseText.split(',');
        let array2 = array.filter(element => element !== "");
        let len = array2.length;
        if (len === 0) {
            let input = createAddressInput();
            collection.appendChild(input)
        } else {
            let collection = document.getElementById('collection_pendings');
            let array = xhr.responseText.split(',');
            let array2 = array.filter(element => element !== "");
            while (collection.firstChild) {
                collection.removeChild(collection.firstChild);
            }
            for (let i = 0; i < len; i++) {
                let input = createAddressInput(array2[i]);
                collection.appendChild(input)
            }
            let children = collection.children;
            Object.keys(children).map(function (item) {
                children[item].addEventListener('click', function () {
                    children[item].select();
                    document.execCommand("copy");
                    M.AutoInit();
                    M.toast({html: 'Copied to clipboard!'})
                })
            })
        }
    }
});

get_blocks_count()
