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
TITLE = "#+title"
DATE = "#+date"
TAGS = "#+tags"
ORG_COMMENT = "#"
ORG_LIST = "+"
ORG_FILE_EXTENSION = ".org"
HTML_FILE_EXTENSION = ".html"
HTML_HEADER = """<!doctype html>
<html lang="en">
  <head>
    <title>TITLE</title>
      <link rel="stylesheet" href="style.css">
      <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
      <meta charset="UTF-8">
  </head>
  <body>
"""
HTML_FOOTER = """
  </body>
</html>
"""

inside_code_block = False
inside_list = False


def translate_org_file(org_file):
    if not org_file.endswith(ORG_FILE_EXTENSION):
        raise Exception("Must provide an org-mode file.")

    output_lines = [HTML_HEADER.replace("TITLE",
                                        org_file.replace(ORG_FILE_EXTENSION, ""))]
    with open(org_file, 'r') as input:
        for line in input:
            if line.startswith("\n"):
                continue
            output_lines.append(translate_line(line))
    output_lines.append(HTML_FOOTER)

    html_file = org_file.replace(ORG_FILE_EXTENSION, HTML_FILE_EXTENSION)
    with open(html_file, 'w') as output:
        output.write(bs("".join(output_lines), "html.parser").prettify())


def translate_headings(line):
    # Translate headings
    # NOTE: these are order-dependent
    if line.startswith(H6):
        return "<h6>" + line.replace(H6, "") + "</h6>"
    if line.startswith(H5):
        return "<h5>" + line.replace(H5, "") + "</h5>"
    if line.startswith(H4):
        return "<h4>" + line.replace(H4, "") + "</h4>"
    if line.startswith(H3):
        return "<h3>" + line.replace(H3, "") + "</h3>"
    if line.startswith(H2):
        return "<h2>" + line.replace(H2, "") + "</h2>"
    if line.startswith(H1):
        return "<h1>" + line.replace(H1, "") + "</h1>"

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

    line = re.sub("(?<!<)/(.*?)/", "<em>\\1</em>", line)  # Use negative lookbehind to avoid matching closing HTML tags
    line = re.sub("\\*(.*?)\\*", "<strong>\\1</strong>", line)
    line = re.sub("_(.*?)_", "<u>\\1</u>", line)
    line = re.sub("~(.*?)~", "<code>\\1</code>", line)
    line = re.sub("=(.*?)=", "<samp>\\1</samp>", line)
    line = re.sub("\\+(.*?)\\+", "<del>\\1</del>", line)

    return line


translate_org_file("../orgmode-website/sample-post.org")
translate_org_file("../org-mode/resources/source-based/the_science_of_selling.org")

