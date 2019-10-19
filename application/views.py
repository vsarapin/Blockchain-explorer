from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.template.context_processors import csrf
from django.http import HttpResponse
from .generate import Generate
from .import_interpreter import Import
from .validator import Validator
from .genesis_creator import GenesisCreator
from .balance import Balance
from .send import Send
from .pending_pool import PendingPool
from .mine import Mine
from .index import IndexBlocks
from .models import Generated, Miner, Outputs
from django.db import IntegrityError
from ecdsa import SigningKey, VerifyingKey, SECP256k1, util
from binascii import hexlify, unhexlify
from base58 import b58encode, b58decode, b58decode_check
from django.db import connection
from django.contrib.auth import logout as auth_logout, login as auth_login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
import itertools
import json
import hashlib
import codecs
import os

from .form import Search

def index(request):
    return render(request, "index.html")

def login(request):
    return render(request, "registration/login.html")

def logout(request):
    auth_logout(request)
    return redirect('/')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            auth_login(request, user)
            return redirect('/')
    else:
        form = UserCreationForm()
    return render(request, "registration/register.html", {'form': form})

def return_blocks(request):
    block_info = IndexBlocks()
    return HttpResponse(block_info.return_all_blocks())


def block_info(request, height):
    block = IndexBlocks()
    block_info, max_len =  block.return_block_info(height)
    return render(request, "block.html", {'info': block_info, 'max': max_len})

def tx_info(request, tx_hash):
    if not request.user.is_authenticated:
            return redirect('/')
    block = IndexBlocks()
    tx = block.tx_info(tx_hash)
    return render(request, "tx.html", {'tx': tx, 'hash': tx_hash})

@csrf_exempt
def search(request):
    if request.method == 'POST':
        form = Search(request.POST)
        if form.is_valid():
            search = form.cleaned_data.get("q")
            try:
                search = int(search)
                block = IndexBlocks()
                block_info, max_len = block.return_block_info(search)
                return render(request, "block.html", {'info': block_info, 'max': max_len})
            except ValueError:
                block = IndexBlocks()
                tx = block.tx_info(search)
                return render(request, "tx.html", {'tx': tx, 'hash': search})
        else:
            raise Http404()
    return HttpResponse(0)





def check_genesis_block(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM application_blocks")
        row = cursor.fetchone()
        if row[0] == 0:
            return HttpResponse(0)
    return HttpResponse(1)


def send(request):
    send_from = request.GET.get('from')
    send_to = request.GET.get('to')
    send_amount = request.GET.get('amount')
    send_fee = request.GET.get('fee')
    user_id = request.user.id
    send = Send(send_from, send_to, send_amount, send_fee, user_id)
    income_data_validation = send.check_income_data()
    return HttpResponse(income_data_validation)


def delete(request):
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM application_generated")
    return HttpResponse(False)


def get_user_addresses(request):
    addresses = Generated.objects.filter(user_id=request.user.id).values_list('address', flat=True)
    string = ''
    for address in addresses:
        string += address + ','
    if len(string):
        return HttpResponse(string)
    return HttpResponse(0)


def check_miners_key_exists(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM application_miner")
        row = cursor.fetchone()
        if row[0] == 1:
            return HttpResponse(1)
    return HttpResponse(0)


def get_miner_addresses(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT address FROM application_miner")
        row = cursor.fetchone()
        if row:
            return HttpResponse(row)
    return HttpResponse('')


def generate_keys(request):
    generate = Generate()
    content = generate.generate_keys()
    splited = content.split(',')
    if len(splited) == 4:
        keys = Generated(private_key=splited[0], wif=splited[1], public_key=splited[2], address=splited[3], user_id=request.user.id)
        keys.save()
    return HttpResponse(content)


def create_and_mine_genesis_block(request):
    genesis = GenesisCreator()
    return HttpResponse(genesis.create_genesis())


def miner_generate(request):
    generate = Generate()
    content = generate.generate_keys()
    splited = content.split(',')
    if len(splited) == 4:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM application_miner")
            keys = Miner(private_key=splited[0], wif=splited[1], public_key=splited[2], address=splited[3])
            keys.save()
    return HttpResponse(content)


def import_key(request):
    import_key = Import()
    content = import_key.import_key(request.GET.get('key'))
    splited = content.split(',')
    if len(splited) == 4:
        try:
            keys = Generated(private_key=splited[0], wif=splited[1], public_key=splited[2], address=splited[3], user_id=request.user.id)
            keys.save()
        except IntegrityError:
            return HttpResponse('WIF already exists!')
    return HttpResponse(content)


def miner_import(request):
    import_key = Import()
    content = import_key.import_key(request.GET.get('key'))
    splited = content.split(',')
    if len(splited) == 4:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM application_miner")
            keys = Miner(private_key=splited[0], wif=splited[1], public_key=splited[2], address=splited[3])
            keys.save()
    return HttpResponse(content)


def return_block_count(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM application_blocks")
        row = cursor.fetchall()
    return HttpResponse(row[0])

@csrf_exempt
def broadcast(request):
    if request.method == "POST":
        pending = PendingPool(json.loads(request.body)['raw_tx'])
        return HttpResponse(pending.submit_tx())

def count_balance(request):
    address = request.GET.get('address')
    balance = Balance()
    res = balance.calculate_balance(address)
    return HttpResponse(res)

def mine_pendings(request):
    mine = Mine()
    return HttpResponse(mine.mine())


def mine(request):
    if not request.user.is_authenticated:
            return redirect('/')
    return render(request, "mine.html")

def address_info(request, wallet_address):
    if not request.user.is_authenticated:
            return redirect('/')
    tmp_input = []
    outputs = Outputs.objects.filter(address_to=wallet_address)
    for input in outputs:
        tmp_input.append([
            {'tx_hash': input.tx_hash},
        ])
    return render(request, "wallet_address.html", { 'wallet_address': wallet_address, 'inputs': tmp_input })

def wallet(request):
    if not request.user.is_authenticated:
            return redirect('/')
    return render(request, "wallet.html")
