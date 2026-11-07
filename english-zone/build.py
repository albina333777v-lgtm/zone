# Собирает проект «English Zone». Запускать после любой правки:  python build.py
#  1) вставляет общую часть parts/core.html (значки, перевод RU/KG, WhatsApp/2ГИС, нижняя панель на телефоне)
#     в каждый вариант между метками CORE:START и CORE:END;
#  2) вставляет в каждый вариант тёмную полосу-переключатель сверху (блок SWITCH): сайты 1/2/3 и ПК/Телефон;
#     внутри index.html полоса скрыта — там свой переключатель;
#  3) встраивает три варианта внутрь index.html, чтобы он работал одним файлом.
import json, re, pathlib

here = pathlib.Path(__file__).parent
files = ["v1-zona.html", "v2-shagi.html", "v3-sezon.html"]
names = ["Зона", "Шаги", "Сезон"]
core = (here / "parts" / "core.html").read_text(encoding="utf-8")

SWITCH_CSS = """<style>
  .sw-bar{position:sticky;top:0;z-index:100;display:none;align-items:center;gap:12px;flex-wrap:wrap;
    background:#141414;color:#fff;font:500 13px/1.2 system-ui,"Segoe UI",sans-serif;
    padding:7px max(12px,env(safe-area-inset-right)) 7px max(12px,env(safe-area-inset-left))}
  body.has-sw .sw-bar{display:flex}
  body.has-sw header{top:var(--swh,44px)}
  .sw-bar .sw-t{font-weight:700;letter-spacing:.08em;white-space:nowrap}
  .sw-bar .sw-t span{font-weight:400;letter-spacing:0;color:#9a9a9a;margin-left:6px}
  .sw-bar .sw-g{display:flex;background:#2a2a2a;border-radius:9px;padding:3px}
  .sw-bar .sw-g:first-of-type{margin-left:auto}
  .sw-bar a{color:#cfcfcf;text-decoration:none;padding:6px 11px;border-radius:7px;white-space:nowrap}
  .sw-bar a:hover{color:#fff}
  .sw-bar a[aria-current="true"]{background:#fff;color:#141414;font-weight:600}
  .sw-bar a:focus-visible{outline:2px solid #FFAE2B;outline-offset:2px}
  @media (max-width:700px){.sw-bar .sw-t{display:none}.sw-bar .sw-g:first-of-type{margin-left:0}.sw-bar .sw-g{flex:1}.sw-bar a{flex:1;text-align:center;padding:6px 4px}}
</style>"""

def switch_block(i):
    sites = "".join(
        f'<a href="{f}" aria-current="{"true" if j == i else "false"}">{j+1} · {n}</a>'
        for j, (f, n) in enumerate(zip(files, names)))
    dev = (f'<a href="{files[i]}" aria-current="true">ПК</a>'
           f'<a href="index.html#v{i+1}-mob" aria-current="false">Телефон</a>')
    return ("<!--SWITCH:START-->\n" + SWITCH_CSS +
            '\n<nav class="sw-bar" aria-label="Переключатель макетов"><div class="sw-t">ENGLISH ZONE<span>макеты сайта</span></div>'
            f'<div class="sw-g" role="group" aria-label="Сайт">{sites}</div>'
            f'<div class="sw-g" role="group" aria-label="Устройство">{dev}</div></nav>'
            '\n<script>if(window.top===window.self){document.body.classList.add("has-sw");const swh=()=>{const h=document.querySelector(".sw-bar").offsetHeight;document.body.style.setProperty("--swh",h+"px");document.documentElement.style.scrollPaddingTop=(h+90)+"px";};swh();addEventListener("resize",swh);}</script>\n'
            "<!--SWITCH:END-->")

designs = {}
for i, f in enumerate(files):
    p = here / f
    html = p.read_text(encoding="utf-8")
    html = re.sub(r"<!--CORE:START-->.*?<!--CORE:END-->",
                  lambda m: "<!--CORE:START-->\n" + core + "\n<!--CORE:END-->", html, flags=re.S)
    if "<!--SWITCH:START-->" in html:
        html = re.sub(r"<!--SWITCH:START-->.*?<!--SWITCH:END-->", lambda m: switch_block(i), html, flags=re.S)
    else:
        html = html.replace("<body>", "<body>\n" + switch_block(i), 1)
    p.write_text(html, encoding="utf-8")
    designs[f] = html

data = json.dumps(designs, ensure_ascii=False).replace("</", "<\\/")  # "</" ломает тег <script>
index = here / "index.html"
html = re.sub(r"<!--DESIGNS:START-->.*?<!--DESIGNS:END-->",
              lambda m: "<!--DESIGNS:START--><script>const DESIGNS=" + data + ";</script><!--DESIGNS:END-->",
              index.read_text(encoding="utf-8"), flags=re.S)
index.write_text(html, encoding="utf-8")
print("index.html обновлён:", ", ".join(files))
