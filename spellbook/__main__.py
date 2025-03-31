import http.server
from argparse import ArgumentParser
import shutil
import mimetypes

from spellbook.generator import Spellbook, FAVICON

spellbook = None


class Handler(http.server.BaseHTTPRequestHandler):

    def __init__(self, request, client_address, server):
        super().__init__(request, client_address, server)

    def sendImage(self, path: str):
        self.send_response(200)
        self.send_header("Content-Type", mimetypes.guess_type(path))
        with open(path, mode='rb') as f:
            data = f.read()
        self.send_header("Content-Length", f'{len(data)}')
        self.end_headers()
        self.wfile.write(data)

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
                    iconPath = spellbook.links[idx].icon
                    self.sendImage(iconPath)
                else:
                    self.send_error(http.HTTPStatus.NOT_FOUND)
            elif self.path.startswith("/favicon"):
                self.sendImage(FAVICON)
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

    print(f"View at http://localhost:{port}")

    httpd = http.server.ThreadingHTTPServer(("", port), Handler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Shutting down")


if __name__ == '__main__':
    main()
