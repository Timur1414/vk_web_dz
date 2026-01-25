from django import template

register = template.Library()


@register.filter
def add_class(field, css_class):
    """
    Adds the given css class to the given field.
    """
    return field.as_widget(attrs={"class": css_class})


@register.filter
def get_item(dictionary, key):
    """
    Returns value from dictionary by key.
    """
    return dictionary.get(key)
