from django.urls import path, include

from django.contrib import admin

admin.autodiscover()

import application.views

from django.conf.urls.static import static

# To add a new path, first import the app:
# import blog
#
# Then add the new path:
# path('blog/', blog.urls, name="blog")
#
# Learn more here: https://docs.djangoproject.com/en/2.1/topics/http/urls/

urlpatterns = [
    path("", application.views.index, name="index"),
    path("show_blocks/", application.views.return_blocks, name="return_blocks"),
    path("block/<int:height>", application.views.block_info, name="block_info"),
    path("tx/<tx_hash>", application.views.tx_info, name="tx_info"),
    path("search/", application.views.search, name="search"),

    path("wallet/", application.views.wallet, name="wallet"),
    path("wallet/new", application.views.generate_keys, name="generate_keys"),
    path("wallet/import/", application.views.import_key, name="import_key"),
    path("wallet/get_addresses/", application.views.get_user_addresses, name="get_user_addresses"),
    path("wallet/delete/", application.views.delete, name="delete"),
    path("wallet/send/", application.views.send, name="send"),
    path("wallet/check_genesis_block/", application.views.check_genesis_block, name="check_genesis_block"),
    path("wallet/check_miners_key_exists/", application.views.check_miners_key_exists, name="check_miners_key_exists"),
    path("wallet/generate_genesis_block/", application.views.create_and_mine_genesis_block,
         name="create_and_mine_genesis_block"),
    path("wallet/balance/", application.views.count_balance, name="count_balance"),
    path("wallet/send/", application.views.send, name="send"),
    path("wallet/broadcast/", application.views.broadcast, name="broadcast"),

    path("mine/", application.views.mine, name="mine"),
    path("miner/new", application.views.miner_generate, name="miner_generate"),
    path("miner/import", application.views.miner_import, name="miner_import"),
    path("miner/get_addresses/", application.views.get_miner_addresses, name="get_miner_addresses"),
    path("miner/mine_pendings/", application.views.mine_pendings, name="mine_pendings"),

    path("chains/block_counter/", application.views.return_block_count, name="return_block_count"),
]
