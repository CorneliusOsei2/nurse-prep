import markdown
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name='md')
def render_markdown(value):
    html = markdown.markdown(value, extensions=['extra', 'nl2br'])
    return mark_safe(html)
