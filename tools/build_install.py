"""Make install.html a single file that works on its own.

1. Embeds scene/scene.svg in the <script type="text/plain" id="scene"> block at the end of the page,
   so every picture shows offline. One tag per line, so a text reader never meets one 100 KB line.
2. Copies the page's "For Claude Code" steps (div.claude) as plain text into the comment at the top,
   between CLAUDE-STEPS:BEGIN and :END. A Claude Code that is handed the file reads it in pages;
   this way the steps are on the first page. Edit the steps on the page, then run this.

tools/gen_scene.py runs this after it writes the scene; you can also run it on its own:

    python3 tools/build_install.py
"""
import html as entities
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCENE = re.compile(r'(<script type="text/plain" id="scene">).*?(</script>)', re.S)
STEPS = re.compile(r"(CLAUDE-STEPS:BEGIN\n).*?(CLAUDE-STEPS:END)", re.S)
CLAUDE_DIV = re.compile(r'<div class="claude">(.*?)</div>', re.S)


def one(pattern, repl, text, what):
    new, count = pattern.subn(repl, text, count=0)
    if count != 1:
        raise SystemExit(f"install.html needs exactly one {what} (found {count})")
    return new


def steps_as_text(page):
    found = CLAUDE_DIV.findall(page)
    if len(found) != 1:
        raise SystemExit(f'install.html needs exactly one <div class="claude"> (found {len(found)})')
    body = found[0]
    number = 0

    def item(_):
        nonlocal number
        number += 1
        return f"\n{number}. "

    body = re.sub(r"<li>", item, body)
    body = re.sub(r"<pre>(.*?)</pre>", lambda m: "\n" + "\n".join("\x00" + l for l in m.group(1).splitlines()) + "\n", body, flags=re.S)
    text = entities.unescape(re.sub(r"<[^>]+>", "", body))
    lines = []
    for line in text.splitlines():
        line = line.rstrip()
        if line.startswith("\x00"):  # a <pre> line: keep it as is, indented
            line = "     " + line[1:]
        else:
            line = re.sub(r"\s+", " ", line).strip()
        if line or (lines and lines[-1]):
            lines.append(line)
    text = "\n".join(lines).strip() + "\n"
    if "--" in text:
        raise SystemExit("the Claude steps contain '--', which can't go inside an HTML comment")
    return text


def build():
    svg = (ROOT / "scene" / "scene.svg").read_text()
    if "</script" in svg.lower():
        raise SystemExit("scene.svg contains '</script' and can't be embedded in install.html")
    svg = svg.replace("><", ">\n<")  # whitespace between SVG tags draws nothing
    page = ROOT / "install.html"
    text = page.read_text()
    text = one(SCENE, lambda m: m.group(1) + "\n" + svg + "\n" + m.group(2), text, '<script type="text/plain" id="scene"> block')
    steps = steps_as_text(text)
    text = one(STEPS, lambda m: m.group(1) + steps + m.group(2), text, "CLAUDE-STEPS:BEGIN/END pair")
    page.write_text(text)
    print("install.html: scene embedded, Claude steps copied to the top,", len(text), "chars")


if __name__ == "__main__":
    build()
