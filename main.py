from bs4 import BeautifulSoup as bs
import re

H6 = "****** "
H5 = "***** "
H4 = "**** "
H3 = "*** "
H2 = "** "
H1 = "* "
BEGIN_CODE_BLOCK = "#+begin_src"
END_CODE_BLOCK = "#+end_src"
TITLE = "#+TITLE:"
DATE = "#+DATE:"
TAGS = "#+TAGS:"
LANGUAGE = "#+LANGUAGE:"
AUTHOR = "#+AUTHOR:"
DESCRIPTION = "#+DESCRIPTION:"
ORG_COMMENT = "#"
ORG_LIST = "+"
ORG_FILE_EXTENSION = ".org"
HTML_FILE_EXTENSION = ".html"
HTML_HEADER = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="LANGUAGE" lang="LANGUAGE">
  <head>
    <title>TITLE</title>
    <link rel="stylesheet" href="style.css">
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <meta charset="UTF-8">
    <meta name="author" content="AUTHOR">
    <meta name="keywords" content="TAGS">
    <meta name="description" content="DESCRIPTION">
  </head>
  <body>
"""
HTML_FOOTER = """
  </body>
</html>
"""

inside_code_block = False
inside_list = False


def export_to_html(org_file):
    if not org_file.endswith(ORG_FILE_EXTENSION):
        raise Exception("Must provide an org-mode file.")

    output_lines = []
    title, language, date, tags, author, description = "", "", "", "", "", ""
    with open(org_file, 'r') as input:
        for line in input:
            if line.startswith("\n"):
                continue
            if line.startswith(TITLE):
                title = line.replace(TITLE, "").strip()
                continue
            if line.startswith(LANGUAGE):
                language = line.replace(LANGUAGE, "").strip()
                continue
            if line.startswith(DATE):
                date = line.replace(DATE, "").strip()
                continue
            if line.startswith(TAGS):
                tags = line.replace(TAGS, "").strip()
                continue
            if line.startswith(AUTHOR):
                author = line.replace(AUTHOR, "").strip()
                continue
            if line.startswith(DESCRIPTION):
                description = line.replace(DESCRIPTION, "").strip()
                continue
            output_lines.append(translate_line(line))

    output_lines = [HTML_HEADER.replace("TITLE", title)
                               .replace("LANGUAGE", language)
                               .replace("TAGS", tags)
                               .replace("DESCRIPTION", description)
                               .replace("AUTHOR", author)] + output_lines
    output_lines.append(HTML_FOOTER)

    html_file = org_file.replace(ORG_FILE_EXTENSION, HTML_FILE_EXTENSION)
    with open(html_file, 'w') as output:
        output.write(bs("".join(output_lines), "html.parser").prettify())


def translate_headings(line):
    # Translate headings
    # NOTE: these are order-dependent
    if line.startswith(H6):
        return f'<h6>{line[7:]}</h6>'
    if line.startswith(H5):
        return f'<h5>{line[6:]}</h5>'
    if line.startswith(H4):
        return f'<h4>{line[5:]}</h4>'
    if line.startswith(H3):
        return f'<h3>{line[4:]}</h3>'
    if line.startswith(H2):
        return f'<h2>{line[3:]}</h2>'
    if line.startswith(H1):
        return f'<h1>{line[2:]}</h1>'

    # Rudimentary parsing of code blocks
    # Handle proper syntax highlighting later
    global inside_code_block
    if line.startswith(BEGIN_CODE_BLOCK):
        inside_code_block = True
        return "<pre><code>"
    if line.startswith(END_CODE_BLOCK):
        inside_code_block = False
        return "</code></pre>"

    global inside_list
    if line.startswith(ORG_LIST):
        inside_list = True
        return f'<li>{line[2:]}</li>'  # Remove the initial "+ "
    else:
        inside_list = False

    # Handle comments
    if line.startswith(ORG_COMMENT):
        return ""

    # Default to <p>
    return f'{line}\n' if inside_code_block else "<p>" + line + "</p>"


def translate_line(line):
    line = line.replace("\n", "").strip()
    line = translate_headings(line)  # must come _before_ following code

    # Don't want to apply formatting to code
    if inside_code_block:
        return line

    # Only slashes preceded by a space should be italicized. Use positive lookbehind for space
    line = re.sub("(?<= )/(.*?)/", "<em>\\1</em>", line)
    line = re.sub("\\*(.*?)\\*", "<strong>\\1</strong>", line)
    line = re.sub("_(.*?)_", "<u>\\1</u>", line)
    line = re.sub("~(.*?)~", "<code>\\1</code>", line)
    line = re.sub("=(.*?)=", "<samp>\\1</samp>", line)
    line = re.sub("\\+(.*?)\\+", "<del>\\1</del>", line)
    line = re.sub(r"\[\[(.*?)]\[(.*?)]]", r"<a href=\1>\2</a>", line)

    return line


export_to_html("../orgmode-website/sample-post.org")
export_to_html("../org-mode/resources/source-based/the_science_of_selling.org")
