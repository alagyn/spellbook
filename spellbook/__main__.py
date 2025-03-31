import http.server
from argparse import ArgumentParser
import shutil
import mimetypes

from spellbook.generator import Spellbook

spellbook = None


class Handler(http.server.BaseHTTPRequestHandler):

    def __init__(self, request, client_address, server):
        super().__init__(request, client_address, server)

    def do_GET(self):
        with spellbook:
            spellbook.regen()
            if self.path == "/":
                data = spellbook.getText()
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.send_header("Content-Length", f"{len(data)}")
                self.end_headers()
                self.wfile.write(data)
            elif self.path.startswith("/icon-"):
                idx = int(self.path[len("/icon-"):])
                if 0 <= idx < len(spellbook.links):
                    self.send_response(200)
                    iconPath = spellbook.links[idx].icon
                    self.send_header("Content-Type",
                                     mimetypes.guess_type(iconPath))
                    with open(iconPath, mode='rb') as f:
                        data = f.read()
                    self.send_header("Content-Length", f'{len(data)}')
                    self.end_headers()
                    self.wfile.write(data)
                else:
                    self.send_error(http.HTTPStatus.NOT_FOUND)
            elif self.path.startswith("/favicon"):
                self.send_response(200)
                iconPath = spellbook.favicon
                self.send_header("Content-Type",
                                 mimetypes.guess_type(iconPath))
                with open(iconPath, mode='rb') as f:
                    data = f.read()
                self.send_header("Content-Length", f'{len(data)}')
                self.end_headers()
                self.wfile.write(data)
            else:
                self.send_error(http.HTTPStatus.NOT_FOUND)


def main():
    parser = ArgumentParser()

    parser.add_argument("--port", default=8000)
    parser.add_argument("--config", default="spellbook.yaml")

    args = parser.parse_args()

    port = int(args.port)
    config = str(args.config)

    global spellbook
    spellbook = Spellbook(config)

    httpd = http.server.ThreadingHTTPServer(("", port), Handler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
