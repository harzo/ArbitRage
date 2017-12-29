from exchanges.models import Currency
from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def code_to_name(code):
    currency = Currency.objects.filter(code=code).first()

    return currency.name if currency else "N/A"