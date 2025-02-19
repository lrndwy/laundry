from django import template

register = template.Library()

@register.filter
def startswith(value, arg):
    """
    Filter untuk mengecek apakah string dimulai dengan arg tertentu
    """
    return str(value).startswith(str(arg))