import os
from io import StringIO
import yaml
import tempest
from threading import Semaphore


class Link:

    def __init__(self, title: str, icon: str, href: str, desc: str):
        self.title = title
        self.icon = icon
        self.href = href
        self.desc = desc


APP_DIR = os.path.dirname(__file__)
TEMPLATE_DIR = os.path.join(APP_DIR, "template")

TEMPLATE = os.path.join(TEMPLATE_DIR, "spellbook-template.html")
FAVICON = os.path.join(TEMPLATE_DIR, "favicon.ico")


class Spellbook:

    def __init__(self, configFile: str):
        self.lock = Semaphore()
        self.links: list[Link] = []
        self.title = ""
        self.page_bg = ""
        self.tile_bg = ""
        self.tile_fg = ""
        self.tile_title_bg = ""
        self.tile_title_fg = ""

        self.template = tempest.parse_template_file(TEMPLATE, "[[", "]]")
        self.config_file = configFile
        self.configModTime = os.path.getmtime(self.config_file)

        self.text: bytes = b''

        self._parse_config()
        self._generate()

    def __enter__(self):
        self.lock.acquire()

    def __exit__(self, type, value, traceback):
        self.lock.release()

    def regen(self):
        modTime = os.path.getmtime(self.config_file)
        if modTime != self.configModTime:
            self._parse_config()
            self._generate()

    def _parse_config(self) -> None:
        with open(self.config_file, mode='rb') as f:
            config = yaml.load(f, yaml.Loader)

        meta = config["meta"]

        self.title = meta['title']
        colors = config["colors"]

        self.page_bg = colors["bg"]
        self.tile_bg = colors["tileBg"]
        self.tile_fg = colors["tileFg"]
        self.tile_title_bg = colors["tileTitleBg"]
        self.tile_title_fg = colors["tileTitleFg"]

        links = config["links"]
        self.links.clear()
        for l in links:
            self.links.append(Link(l["title"], l["icon"], l['url'], l['desc']))

    def _generate(self):
        out = StringIO()
        values = {"book": self}
        self.template.generate(out, values)
        self.text = out.getvalue().encode()

    def getText(self) -> bytes:
        return self.text
