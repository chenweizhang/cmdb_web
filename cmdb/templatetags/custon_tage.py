from django import template
from django.utils.html import format_html
register = template.Library()

@register.simple_tag
def guess_page(url):

    if "query_server_info" in url:
        kv = url.split("?")[-1].split("=")
        keys = kv[0]
        vales = kv[1]
        page_ele = '''?%s=%s&page='''%(keys,vales)

    elif "server_info" in url:
        page_ele = '''?page='''
    else:
        page_ele = ''
    return format_html(page_ele)