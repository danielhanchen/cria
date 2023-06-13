"""
    Copyright Daniel Han-Chen
    Inspired from https://github.com/matthewwithanm/python-markdownify
    and https://github.com/lm-sys/FastChat.

    Cleaning code sections.
"""
__all__ = [
    "markdownify",
    "markdownify_fast",
]

from re import compile as RE_COMPILE, IGNORECASE as RE_IGNORECASE
REMOVE_HTML_TAGS = RE_COMPILE("</?[a-z]{3,}[^>]{0,}>")
CHECK_CODY_CODE  = RE_COMPILE(r'^[\s]{0,}(?:class="([^\s]{0,10})")?'\
                              r'>?([^\s]{0,10})(?:copy[\s]{0,}code)+', flags = RE_IGNORECASE)
PRE_TAG     = "<pre"
PRE_END_TAG = "</pre>"

def cleanup_code(text : str) -> str:
    """ First cleanup code sections by deleting <span> <div> etc """
    i = 0
    while (code_start := text.find(PRE_TAG, i)) != -1:

        start = code_start + len(PRE_TAG)
        if (code_end := text.find(PRE_END_TAG, start)) == -1: break
        code = REMOVE_HTML_TAGS.sub("", text[start : code_end])

        """ Check if Copy Code exists """
        if (attrs := CHECK_CODY_CODE.match(code)):
            # pythonCopy Code takes priority over class="python"
            language = attrs.group(2) or attrs.group(1) or ""
            pre = f'<pre class="{language}">'
            code = code[attrs.span(0)[1]:]
        else:
            pre = PRE_TAG
        pass
        
        text = f"{text[:code_start]}{pre}{code}{text[code_end:]}"
        i = code_start + len(pre) + len(code) + len(PRE_END_TAG)
    pass
    return text
pass
