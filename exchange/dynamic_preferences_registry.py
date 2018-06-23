from dynamic_preferences.preferences import Section
from dynamic_preferences.registries import global_preferences_registry
from dynamic_preferences.types import StringPreference

exchange = Section('exchange')

@global_preferences_registry.register
class BithumbApiKey(StringPreference):
    section = exchange
    name = 'bithumbApiKey'
    default = ''

@global_preferences_registry.register
class BithumbApiSecret(StringPreference):
    section = exchange
    name = 'bithumbApiSecret'
    default = ''

@global_preferences_registry.register
class BittrexApiKey(StringPreference):
    section = exchange
    name = 'bittrexApiKey'
    default = ''

@global_preferences_registry.register
class BittrexApiSecret(StringPreference):
    section = exchange
    name = 'bittrexApiSecret'
    default = ''
