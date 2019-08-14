import re

from django import template
from django.utils.html import format_html
register = template.Library()

@register.simple_tag
def guess_page(url):

    # if "hostname" in url:

    patter = re.compile(r'hostname=([^&]*)')
    searchObj  = patter.search(url)
    if searchObj:
        kv = searchObj.group()
        kv = kv.split("=")
        keys = kv[0]
        vales = kv[1]
        page_ele = '''?%s=%s&page='''%(keys,vales)
    else:
    # elif "server_info" in url:
    #     page_ele = '''?page='''
    # else:
        page_ele = '''?page='''
    return format_html(page_ele)