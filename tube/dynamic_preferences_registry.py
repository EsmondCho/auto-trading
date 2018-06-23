from dynamic_preferences.preferences import Section
from dynamic_preferences.registries import global_preferences_registry
from dynamic_preferences.types import FloatPreference

tube = Section('tube')

@global_preferences_registry.register
class BithumbTransactionFee(FloatPreference):
    section = tube
    name = 'bithumbTransactionFee'
    default = 0.15

@global_preferences_registry.register
class BittrexTransactionFee(FloatPreference):
    section = tube
    name = 'bittrexTransactionFee'
    default = 0.25
