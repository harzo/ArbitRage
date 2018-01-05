from django.contrib import admin

from .models import ExchangePairSettings


class ExchangePairSettingsAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'update_frequency')
    list_editable = ('update_frequency',)

    fields = ['left', 'right', 'update_frequency']


admin.site.register(ExchangePairSettings, ExchangePairSettingsAdmin)
