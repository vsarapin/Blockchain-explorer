from django.db import models


class Generated(models.Model):
    private_key = models.CharField(max_length=255)
    wif = models.CharField(max_length=255)
    public_key = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    user_id = models.IntegerField()

class Miner(models.Model):
    private_key = models.CharField(max_length=255)
    wif = models.CharField(max_length=255)
    public_key = models.CharField(max_length=255)
    address = models.CharField(max_length=255)

class Pendings(models.Model):
    id = models.AutoField(primary_key=True)
    raw_tx = models.CharField(max_length=1000)

class Utxo(models.Model):
    id = models.AutoField(primary_key=True)
    tx_hash = models.CharField(max_length=1000)
    tx_raw =  models.CharField(max_length=1000)
    output_number = models.CharField(max_length=1000)
    amount = models.CharField(max_length=1000)
    address = models.CharField(max_length=1000)

class Inputs(models.Model):
    address_from = models.CharField(max_length=1000)
    block_hash = models.CharField(max_length=1000)
    prev_output = models.CharField(max_length=1000)
    outpoint = models.CharField(max_length=1000)
    sequence = models.CharField(max_length=1000)
    tx_hash = models.CharField(max_length=1000)
    value = models.CharField(max_length=1000)
    sigscript = models.CharField(max_length=1000)

class Outputs(models.Model):
    address_to = models.CharField(max_length=1000)
    type = models.CharField(max_length=1000)
    scriptpubkey_hex = models.CharField(max_length=1000)
    spending_tx = models.CharField(max_length=1000)
    tx_hash = models.CharField(max_length=1000)
    value = models.CharField(max_length=1000)

class Blocks(models.Model):
    id = models.AutoField(primary_key=True)
    version = models.CharField(max_length=1000)
    height = models.CharField(max_length=1000)
    nonce = models.CharField(max_length=1000)
    block_hash = models.CharField(max_length=1000)
    previous_block_hash = models.CharField(max_length=1000)
    merkle_root = models.CharField(max_length=1000)
    timestamp = models.CharField(max_length=1000)
    number_of_transactions = models.CharField(max_length=1000)