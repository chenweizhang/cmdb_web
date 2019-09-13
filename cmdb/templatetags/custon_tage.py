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

@register.simple_tag
def approval_page(current_page,loop_num):
    offset =abs(current_page-loop_num)

    if offset < 4:
        if current_page == loop_num:
            page_ele = '''<li class="active"><a href="?page=%s">%s</a></li>''' % (loop_num,loop_num)

        else:
            page_ele = '''<li class=""><a href="?page=%s">%s</a></li>'''%(loop_num,loop_num)

        return format_html(page_ele)

    else:
        return ''