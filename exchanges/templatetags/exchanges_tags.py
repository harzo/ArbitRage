from exchanges.models import Currency
from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def code_to_name(code):
    currency = Currency.objects.filter(code=code).first()

    return currency.name if currency else "N/A"


@register.filter
@stringfilter
def currency_sign(value, arg):
    if type(arg) != Currency:
        return value

    return value+" "+arg.sign if arg.sign_after else arg.sign+value


@register.filter
@stringfilter
def currency_format(value, arg):
    if type(arg) != Currency:
        return value

    return "{0:.8f}".format(float(value)) if arg.crypto else "{0:.2f}".format(float(value))


@register.filter
def divide(value, arg):
    try:
        return value / arg
    except:
        return None


@register.filter
def multiply(value, arg):
    try:
        return value * arg
    except:
        return None