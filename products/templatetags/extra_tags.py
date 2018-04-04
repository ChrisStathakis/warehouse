

from django import template
register = template.Library()

@register.simple_tag
def multiply(qty, price_buy, *args, **kwargs):
    # you would need to do any localization of the result here
    return float(qty * price_buy)

def total_value_item_cart(qty,price,*args, **kwargs):
    return qty*price