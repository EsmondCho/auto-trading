from django.db import models
from exchange.models import Exchange, Currency


EVENT = (
    (0, "INIT"),
    (1, "CLOSE"),
    (2, "BID"),
    (3, "ASK"),
    (4, "WITHDRAWAL"),
    (5, "DEPOSIT"),
    (6, "ERROR"),
    (7, "CANCEL")
)

ORDER_TYPE = (
    (0, "BID"),
    (1, "ASK")
)

TRANSFER_TYPE = (
    (0, "DEPOSIT"),
    (1, "WITHDRAWAL")
)


class EventLog(models.Model):
    id = models.AutoField(primary_key=True)
    tube_id = models.BigIntegerField()
    stage = models.IntegerField()
    event = models.IntegerField(choices=EVENT)
    price = models.BigIntegerField()
    time_stamp = models.DateTimeField(blank=True, null=True)
    eventinfo_id = models.IntegerField(null=True)


class TransferInfo(models.Model):
    id = models.AutoField(primary_key=True)
    coin_amt = models.DecimalField(max_digits=32, decimal_places=8)
    src = models.ForeignKey(Exchange, related_name="source_exchange")
    dest = models.ForeignKey(Exchange, related_name="destination_exchange")
    currency = models.ForeignKey(Currency)
    transfer_type = models.IntegerField(choices=TRANSFER_TYPE)


class OrderInfo(models.Model):
    id = models.AutoField(primary_key=True)
    order_id = models.CharField(max_length=255)
    order_type = models.IntegerField(choices=ORDER_TYPE)
    market_counter = models.ForeignKey(Currency, related_name="market_counter_currency")
    market_base = models.ForeignKey(Currency, related_name="market_base_currency")
    coin_amt = models.DecimalField(max_digits=32, decimal_places=8)
    value = models.DecimalField(max_digits=32, decimal_places=8)
    exchange = models.ForeignKey(Exchange)


class ErrorInfo(models.Model):
    id = models.AutoField(primary_key=True)
    desc = models.TextField()
