from django import template

register = template.Library()


@register.filter
def get_item(value, key):
    """
    Access dictionary value by key inside templates.

    Usage:
        {{ my_dict|get_item:"some_key" }}
    """
    if isinstance(value, dict):
        return value.get(key)
    return None