function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        let cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            let cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

let csrftoken = getCookie('csrftoken');
let raw_tx = '';

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

function displayGenesisButtonOrNot(bool) {
    if (bool) {
        document.getElementById('generate_genesis').style.display = 'none';
        document.getElementById('send_from_div').style.display = 'block';
        document.getElementById('send_to_div').style.display = 'block';
        document.getElementById('send_amount_div').style.display = 'block';
        document.getElementById('send_fee_div').style.display = 'block';
        document.getElementById('send_button').style.display = 'block';
    } else {
        document.getElementById('send_from_div').style.display = 'none';
        document.getElementById('send_to_div').style.display = 'none';
        document.getElementById('send_amount_div').style.display = 'none';
        document.getElementById('send_fee_div').style.display = 'none';
        document.getElementById('send_button').style.display = 'none';
        document.getElementById('generate_genesis').style.display = 'block';
    }
}

let check_balance = document.getElementById('balance_button');
check_balance.addEventListener('click', function () {
    let addressForBalance = document.getElementById('balance').value;
    let xhr = new XMLHttpRequest();
    xhr.open('GET', '/wallet/balance/?address=' + addressForBalance, false);
    xhr.send();
    if (xhr.status !== 200) {
        console.log(xhr.status + ': ' + xhr.statusText)
    } else {
        M.AutoInit();
        M.toast({html: 'This address has ' + xhr.responseText + ' coins!', displayLength: 5000});
        console.log()
    }
});

let xhr = new XMLHttpRequest();
xhr.open('GET', '/wallet/check_genesis_block', false);
xhr.send();
if (xhr.status !== 200) {
    console.log(xhr.status + ': ' + xhr.statusText)
} else {
    if (xhr.responseText == 1) {
        displayGenesisButtonOrNot(true);
    } else {
        displayGenesisButtonOrNot(false);
        let generate_genesis = document.getElementById('generate_genesis');
        generate_genesis.addEventListener('click', function () {
                let xhr = new XMLHttpRequest();
                xhr.open('GET', '/wallet/check_miners_key_exists', false);
                xhr.send();
                if (xhr.status !== 200) {
                    console.log(xhr.status + ': ' + xhr.statusText)
                } else {
                    if (xhr.responseText == 1) {
                        displayGenesisButtonOrNot(true);
                        let xhr = new XMLHttpRequest();
                        xhr.open('GET', '/wallet/generate_genesis_block', false);
                        xhr.send();
                        if (xhr.status !== 200) {

                        } else {
                            M.AutoInit();
                            M.toast({html: 'Genesis block created'})
                        }
                    } else {
                        M.AutoInit();
                        M.toast({html: 'Generate miner`s key first!'})
                    }
                }
            }
        )
    }
}

let broadcast = document.getElementById('broadcast');

let send_button = document.getElementById('send_button');
send_button.addEventListener('click', function () {
    let send_from = document.getElementById('send_from').value;
    let send_to = document.getElementById('send_to').value;
    let send_amount = document.getElementById('send_amount').value;
    let send_fee = document.getElementById('send_fee').value;

    let xhr = new XMLHttpRequest();
    xhr.open('GET', '/wallet/send/?from=' + send_from + "&to=" + send_to + "&amount=" + Number(send_amount) + "&fee=" + Number(send_fee), false);
    xhr.send();
    if (xhr.status !== 200) {
        console.log(xhr.status + ': ' + xhr.statusText)
    } else {
        if (xhr.responseText === "Not enough coins on __from__ balance!") {
            M.AutoInit();
            M.toast({html: 'Not enough coins on balance!'});
            let audio = new Audio("/static/sounds/minerals.mp3");
            audio.volume = 1;
            audio.play();
        } else if (xhr.responseText.substr(0, 9) != "010000000") {
            M.AutoInit();
            M.toast({html: xhr.responseText})
        } else {
            document.getElementById('send_from').value = '';
            document.getElementById('send_to').value = '';
            document.getElementById('send_amount').value = '';
            document.getElementById('send_fee').value = '';

            document.getElementById('send_button').style.display = "none";
            document.getElementById('from').style.display = "none";
            document.getElementById('to').style.display = "none";
            document.getElementById('amount').style.display = "none";
            document.getElementById('fee').style.display = "none";
            broadcast.style.display = "block";
            raw_tx = xhr.responseText;
            console.log(raw_tx);
            M.AutoInit();
            M.toast({html: 'Raw transaction created, you may see it in console!'});
        }
    }
});

let broadcast_button = document.getElementById('broadcast_button');
broadcast_button.addEventListener('click', function () {
    let xhr_1 = new XMLHttpRequest();
    let body = JSON.stringify({'raw_tx': raw_tx});
    xhr_1.open('POST', '/wallet/broadcast/', false);
    xhr_1.setRequestHeader('Content-type', 'application/json; charset=utf-8');
    xhr_1.setRequestHeader('X-CSRFToken', csrftoken);
    xhr_1.send(body);
    if (xhr_1.status !== 200) {
        console.log(xhr.status + ': ' + xhr.statusText)
    } else {
        if (xhr_1.responseText === "True") {
            document.getElementById('send_button').style.display = "block";
            document.getElementById('from').style.display = "block";
            document.getElementById('to').style.display = "block";
            document.getElementById('amount').style.display = "block";
            document.getElementById('fee').style.display = "block";
            broadcast.style.display = "none";
            M.AutoInit();
            M.toast({html: 'Broadcasted successfully!'});
        }
    }
});

let delete_button = document.getElementById('delete');
delete_button.addEventListener('click', function () {
    let xhr = new XMLHttpRequest();
    xhr.open('GET', '/wallet/delete', false);
    xhr.send();
    if (xhr.status !== 200) {
        console.log(xhr.status + ': ' + xhr.statusText)
    } else {
        let collection = document.getElementById('collection');
        while (collection.firstChild) {
            collection.removeChild(collection.firstChild);
        }
        let input = createAddressInput();
        collection.appendChild(input)
    }
});


let addresses = document.getElementById('tab5');
addresses.addEventListener('click', function () {
    let xhr = new XMLHttpRequest();
    xhr.open('GET', '/wallet/get_addresses', false);
    xhr.send();
    if (xhr.status !== 200) {
        console.log(xhr.status + ': ' + xhr.statusText)
    } else {
        let collection = document.getElementById('collection');
        while (collection.firstChild) {
            collection.removeChild(collection.firstChild);
        }
        let len = xhr.responseText.split(',').length;
        if (len === 1) {
            let input = createAddressInput();
            collection.appendChild(input)
        } else {
            let splited = xhr.responseText.split(',');
            for (let i = 0; i < len - 1; i++) {
                let input = createAddressInput(splited[i])
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

let generate = document.getElementById('new_key');
generate.addEventListener('click', function () {
    let xhr = new XMLHttpRequest();
    xhr.open('GET', '/wallet/new', false);
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

import_key = document.getElementById('import');
import_key.addEventListener('click', function () {
    let key = document.getElementById('imported_key').value
    let params = '?key=' + key;
    let xhr = new XMLHttpRequest();
    xhr.open('GET', '/wallet/import/' + params, false);
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
            document.getElementById('imported_' + index).value = xhr.responseText.split(',')[index - 1];
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
})