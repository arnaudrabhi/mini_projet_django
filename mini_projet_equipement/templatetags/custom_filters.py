from django import template

register = template.Library()


@register.filter
def replace_underscores(value):
    return value.replace('_', ' ')


@register.filter(name='get_enum_value')
def get_enum_value(value, enum_name):
    try:
        enum_class = globals()[enum_name]
        enum_value = getattr(enum_class, value)
        return enum_value.value
    except (AttributeError, KeyError):
        return value
