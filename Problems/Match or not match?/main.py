import re


def matched(template, string):
    return bool(re.match(template, string))
