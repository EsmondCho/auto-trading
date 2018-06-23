from django.db import models


# 주문정보
class Order(models.Model):
    id = models.AutoField(primary_key=True)
    exchange = models.ForeignKey('Exchange') # 거래소
    counter = models.IntegerField(verbose_name="counter_currency_id") # 교환통화
    base = models.IntegerField(verbose_name="base_currency_id") # 기축통화
    euid = models.CharField(max_length=255) # exchange unique id
    type = models.ForeignKey('Type') # bid, ask, buy, sell
    amount = models.DecimalField(max_digits=32, decimal_places=8)
    price = models.DecimalField(max_digits=32, decimal_places=8)
    total = models.DecimalField(max_digits=32, decimal_places=8)
    src_btc_price = models.DecimalField(max_digits=32, decimal_places=8)
    src2btc = models.DecimalField(max_digits=32, decimal_places=8)
    dest_price = models.DecimalField(max_digits=32, decimal_places=8)
    registered_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True, blank=True, null=True)

    @property
    def market(self):
        counter = Currency.objects.get(id=self.counter).symbol
        base = Currency.objects.get(id=self.base).symbol
        return counter + "/" + base


# 화폐
class Currency(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=40)
    symbol = models.CharField(max_length=10)

    def __str__(self):
        return '{}'.format(self.name)


# 거래소
class Exchange(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30, null=False, blank=False)

    def __str__(self):
        return '{}'.format(self.name)


# bid, ask, buy, sell
class Type(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30, null=False, blank=False)


#지갑 맵핑
class WalletAddress(models.Model):
    id = models.AutoField(primary_key=True)
    exchange = models.ForeignKey('Exchange') # 거래소
    currency = models.ForeignKey('Currency') # 화폐
    address = models.CharField(max_length=200, null=False, blank=False)
    tag = models.CharField(max_length=100, null=True, blank=True)


#출금 수수료 맵핑
class WithdrawalFee(models.Model):
    id = models.AutoField(primary_key=True)
    exchange = models.ForeignKey('Exchange') # 거래소
    currency = models.ForeignKey('Currency') # 화폐
    fee = models.DecimalField(max_digits=32, decimal_places=8)
