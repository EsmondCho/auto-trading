class Currency:

    def __init__(self, currency):
        self.currency = currency

    def __repr__(self):
        return 'Currency(%s)' % self.currency

    def __str__(self):
        return '%s' % self.currency

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)


class CurrencyPair:

    def __init__(self, counter, base):
        self.counter = counter
        self.base = base

    def getcounter(self):
        return self.counter

    def getbase(self):
        return self.base

    def __repr__(self):
        return 'CurrencyPair(%s, %s)' % (self.counter, self.base)

    def __str__(self):
        return '%s/%s' % (self.counter, self.base)
