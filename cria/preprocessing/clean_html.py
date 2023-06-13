"""
    Copyright Daniel Han-Chen
    Inspired from https://github.com/matthewwithanm/python-markdownify
    and https://github.com/lm-sys/FastChat.

    Slimmed down and performant version of the original Markdownify module.
    Ported to work with ShareGPT outputs.

    Super fast parser uses LXML and cchardet.
    See https://thehftguy.com/2020/07/28/making-beautifulsoup-parsing-10-times-faster.
"""
__all__ = [
    "markdownify",
    "markdownify_sharegpt",
]

from ._builder import HTMLParserTreeBuilder_Fast, LXMLTreeBuilder_Fast
from bs4 import BeautifulSoup, NavigableString
from re import compile as RE_COMPILE
WHITESPACE_RE = RE_COMPILE(r"[\t ]+")
NEWLINE     = "\n"
TAB         = "\t"
SPEECH      = '"'
SPEECH_RE   = r'\"'
IS_NESTED_NODE_SET  = frozenset(('ol', 'ul', 'li', 'table', 'thead', 'tbody', 'tfoot', 'tr', 'td', 'th',))

def convert_pre(el, text, as_inline):
    if not text: return ""
    code_language = el.attrs.get("class")
    code_language = "" if not code_language else code_language[0]
    return f"\n```{code_language}\n{text}\n```\n"
pass

def convert_h1(el, text, as_inline):
    text = text.strip() # [Fix newline start in header tags] (https://github.com/matthewwithanm/python-markdownify/pull/89)
    return f'{text}\n{"=" * len(text)}\n' if text else ""
pass

def convert_h2(el, text, as_inline):
    text = text.strip() # [Fix newline start in header tags] (https://github.com/matthewwithanm/python-markdownify/pull/89)
    return f'{text}\n{"-" * len(text)}\n' if text else ""
pass

def convert_a(el, text, as_inline):
    if not text: return ""
    prefix = " " if text[0]  == " " else ""
    suffix = " " if text[-1] == " " else ""
    if not (text := text.strip()): return ""

    el_get_attrs = el.attrs.get
    href  = el_get_attrs("href",  "")
    title = el_get_attrs("title", "")
    if (text.replace(r'\_', '_') == href and not title):
        return f"<{href}>"

    title_part = f' "{title.replace(SPEECH, SPEECH_RE)}"' if title else ""
    return f"{prefix}[{text}]({href}{title_part}){suffix}" if href else text
pass

def convert_b(el, text, as_inline):
    if not text: return ""
    prefix = " " if text[0]  == " " else ""
    suffix = " " if text[-1] == " " else ""
    if not (text := text.strip()): return ""
    return f"{prefix}**{text}**{suffix}"
pass

def convert_code(el, text, as_inline):
    if not text: return ""
    if el.parent.name == "pre": return text
    prefix = " " if text[0]  == " " else ""
    suffix = " " if text[-1] == " " else ""
    if not (text := text.strip()): return ""
    return f"{prefix}`{text}`{suffix}"
pass

def convert_del(el, text, as_inline):
    if not text: return ""
    prefix = " " if text[0]  == " " else ""
    suffix = " " if text[-1] == " " else ""
    if not (text := text.strip()): return ""
    return f"{prefix}~~{text}~~{suffix}"
pass

def convert_em(el, text, as_inline):
    if not text: return ""
    prefix = " " if text[0]  == " " else ""
    suffix = " " if text[-1] == " " else ""
    if not (text := text.strip()): return ""
    return f"{prefix}*{text}*{suffix}"
pass

def convert_img(el, text, as_inline):
    el_attrs_get = el.attrs.get
    alt   = el_attrs_get("alt",   "")
    src   = el_attrs_get("src",   "")
    title = el_attrs_get("title", "")
    if as_inline: return alt
    title_part = f' "{title.replace(SPEECH, SPEECH_RE)}"' if title else ""
    return f"![{alt}]({src}{title_part})"
pass

def convert_list(el, text, as_inline):
    # Converting a list to inline is undefined.
    # Ignoring convert_to_inline for list.
    _next = el.next_sibling
    while el:
        if el.name == "li":
            # remove trailing newline since nested
            return f"\n{NEWLINE.join(f'{TAB}{x}' for x in text.split(NEWLINE)).rstrip() if text else ''}"
        pass
        el = el.parent
    pass

    before_paragraph = (_next and _next.name != "ul" and _next.name != "ol")
    return f"{text}{NEWLINE if before_paragraph else ''}"
pass

def convert_li(el, text, as_inline):
    parent = el.parent
    if parent and parent.name == "ol":
        start  = int(parent.attrs.get("start", 1))
        bullet = f"{(start + parent.index(el))}."
    else:
        depth = -1
        while el:
            if el.name == "ul": depth += 1
            el = el.parent
        pass

        i = depth % 3
        if   i == 0: bullet = "*"
        elif i == 1: bullet = "+"
        else:        bullet = "-"
    pass
    return f"{bullet} {text.strip()}\n"
pass

def convert_sub(el, text, as_inline):
    if not text: return ""
    prefix = " " if text[0]  == " " else ""
    suffix = " " if text[-1] == " " else ""
    if not (text := text.strip()): return ""
    return f"{prefix}{text}{suffix}"
pass

def convert_tr(el, text, as_inline):
    th = 0
    td = 0
    descendants = el.descendants
    for children in descendants:
        th += (children.name == "th")
        td += (children.name == "td")
    pass
    n = th + td
    m = n-1 if n != 0 else 0
    parent      = el.parent
    name        = parent.name
    no_previous = not el.previous_sibling
    is_tbody    = name == "tbody"

    # [Support conversion of header rows in tables without th tag] (https://github.com/matthewwithanm/python-markdownify/pull/83)
    is_headrow = (td == 0) \
                 or (no_previous and not is_tbody) \
                 or (no_previous and     is_tbody and parent.parent.find("thead") is None)

    if is_headrow and no_previous:
        # first row and is headline: print headline underline
        return f"|{text}\n| {'--- | '*m}{'---' if n != 0 else ''} |\n"

    elif (no_previous and ((name == "table") or (is_tbody and not parent.previous_sibling))):
        # first row, not headline, and:
        # - the parent is table or
        # - the parent is tbody at the beginning of a table.
        # print empty headline above this row
        return f"| {' | '*m} |\n| {'--- | '*m}{'---' if n != 0 else ''} |\n|{text}\n"
    else:
        return f"|{text}\n"
pass

def convert_blockquote(el, text, as_inline):
    if as_inline or not text: return text
    text = text.strip() # [Strip text before adding blockquote markers] (https://github.com/matthewwithanm/python-markdownify/pull/76)
    return f"\n{NEWLINE.join(f'> {x}' for x in text.split(NEWLINE))}\n"
pass

FUNCTIONS = {
    "a"          : convert_a,
    "b"          : convert_b,
    "strong"     : convert_b,
    "code"       : convert_code,
    "kbd"        : convert_code,
    "samp"       : convert_code,
    "pre"        : convert_pre,
    "del"        : convert_del,
    "s"          : convert_del,
    "em"         : convert_em,
    "i"          : convert_em,
    "img"        : convert_img,
    "list"       : convert_list,
    "ul"         : convert_list,
    "ol"         : convert_list,
    "li"         : convert_li,
    "sub"        : convert_sub,
    "sup"        : convert_sub,
    "tr"         : convert_tr,
    "blockquote" : convert_blockquote,

    # [Fix newline start in header tags] (https://github.com/matthewwithanm/python-markdownify/pull/89)
    "h1"         : convert_h1,
    "h2"         : convert_h2,
    "h3"         : lambda el, text, c: text if c else    f"### {text.strip()}\n",
    "h4"         : lambda el, text, c: text if c else   f"#### {text.strip()}\n",
    "h5"         : lambda el, text, c: text if c else  f"##### {text.strip()}\n",
    "h6"         : lambda el, text, c: text if c else f"###### {text.strip()}\n",

    "hr"         : lambda el, text, c: "\n\n---\n\n",
    "table"      : lambda el, text, c: f"\n\n{text}\n",
    "td"         : lambda el, text, c: f" {text.strip()} |", # [Tables not converted well - paragraphs] (https://github.com/matthewwithanm/python-markdownify/issues/90)
    "th"         : lambda el, text, c: f" {text} |",
    "br"         : lambda el, text, c: ""   if c else "  \n",
    "p"          : lambda el, text, c: text if c else f"{text}\n",
}

def process_tag(node, as_inline, children_only = False, clean_whitespaces = True):
    text = ""
    # markdown headings or cells can't include
    # block elements (elements w/newlines)
    name = node.name
    isHeading = ("h1" <= name <= "h6")
    isCell = (name == "td" or name == "th")
    convert_children_as_inline = as_inline or (not children_only and (isHeading or isCell))

    # Remove whitespace-only textnodes in purely nested nodes
    if name in IS_NESTED_NODE_SET:
        children = node.children
        for el in children:
            # Only extract (remove) whitespace-only text node if any of the conditions is true:
            # - el is the first element in its parent
            # - el is the last  element in its parent
            # - el is adjacent to an nested node
            if isinstance(el, NavigableString) and el.isspace() and ( \
                (not (_prev := el.previous_sibling) or _prev.name in IS_NESTED_NODE_SET) or \
                (not (_next := el.next_sibling)     or _next.name in IS_NESTED_NODE_SET)
            ):
                el.extract()

    # Convert the children first
    children = node.children
    for el in children:
        if isinstance(el, NavigableString):
            text += process_text(el)
        else:
            text += process_tag (el, convert_children_as_inline, False, clean_whitespaces)

    if not children_only and name in FUNCTIONS:
        text = FUNCTIONS[name](node, text, as_inline)

    return text
pass

def process_text(el, clean_whitespaces = True):
    text = str(el)
    if not (parent := el.parent): return text
    name    = parent.name
    _next   = el.next_sibling
    is_pre  = name == "pre"
    is_code = name == "code"

    # Dont remove any whitespace when handling pre or code in pre
    if clean_whitespaces and not (is_pre or (is_code and parent.parent.name == "pre")):
        text = WHITESPACE_RE.sub(" ", text)

    if not is_pre and not is_code:
        if "_" in text or "*" in text:
            text = text.replace("_", r"\_").replace("*", r"\*")

    # remove trailing whitespaces if any of the following condition is true:
    # - current text node is the last node in li
    # - current text node is followed by an embedded list
    if ((name == "li") and (not _next or _next.name == "ul" or _next.name == "ol")):
        text = text.rstrip()

    return text
pass

def markdownify(text              : str,
                fast              : bool = False,
                clean_whitespaces : bool = True) -> str:
    if fast:
        soup = BeautifulSoup(text, "lxml",        )
    else:
        soup = BeautifulSoup(text, "html.parser", )
    return process_tag(soup, as_inline = False, children_only = True, clean_whitespaces = clean_whitespaces)
pass

def markdownify_sharegpt(text : str) -> str:
    """
        We must not remove multiple whitespaces due to code sections!
    """
    soup = BeautifulSoup(text, "lxml", builder = LXMLTreeBuilder_Fast)
    return process_tag(soup, as_inline = False, children_only = True, clean_whitespaces = False)
pass
