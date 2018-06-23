from django.contrib import admin
from .models import *


class EventLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'tube_id', 'stage', 'event', 'price', 'time_stamp')


class TransferInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'coin_amt', 'src', 'dest', 'currency', 'transfer_type')


class OrderInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_id', 'order_type', 'market_counter', 'market_base', 'coin_amt', 'value', 'exchange')


class ErrorInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'desc')


admin.site.register(EventLog, EventLogAdmin)
admin.site.register(TransferInfo, TransferInfoAdmin)
admin.site.register(OrderInfo, OrderInfoAdmin)
admin.site.register(ErrorInfo, ErrorInfoAdmin)
