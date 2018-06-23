from dynamic_preferences.preferences import Section
from dynamic_preferences.registries import global_preferences_registry
from dynamic_preferences.types import StringPreference

dashboard = Section('dashboard')


@global_preferences_registry.register
class CoinBlackList(StringPreference):
    section = dashboard
    name = 'coinBlackList'
    default = ''
