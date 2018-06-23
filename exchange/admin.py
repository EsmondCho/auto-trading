from django.contrib import admin
from .models import *


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'exchange', 'counter', 'base', 'market', 'euid', 'type',
                    'amount', 'price', 'total', 'registered_time', 'modified_time')


class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'symbol')


class ExchangeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


class TypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


class WalletAddressAdmin(admin.ModelAdmin):
    list_display = ('id', 'exchange', 'currency', 'address', 'tag')


class WithdrawalFeeAdmin(admin.ModelAdmin):
    list_display = ('id', 'exchange', 'currency', 'fee')


admin.site.register(Order, OrderAdmin)
admin.site.register(Currency, CurrencyAdmin)
admin.site.register(Exchange, ExchangeAdmin)
admin.site.register(Type, TypeAdmin)
admin.site.register(WalletAddress, WalletAddressAdmin)
admin.site.register(WithdrawalFee, WithdrawalFeeAdmin)
