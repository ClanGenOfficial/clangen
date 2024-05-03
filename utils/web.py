from http.server import SimpleHTTPRequestHandler
import os
import zipfile
import sys
from shutil import copytree, rmtree

build_path = "build"
static_path = "static"
zip_name = "clangen.apk"
zip_path = os.path.join(build_path, zip_name)
version_path = "version.ini"

pack_paths = [
    "languages",
    "resources",
    "scripts",
    "sprites",
    version_path,
    "changelog.txt",
    "main.py",
    "webMain.py",
]

pack_ignore = [
    "__pycache__",
]


def pack():
    """
    Packs all of pack_paths into a zip file with a parent folder of "assets"
    """

    if os.path.exists(build_path):
        rmtree(build_path)
    
    copytree(static_path, build_path)
    
    with zipfile.ZipFile(zip_path, "w") as zf:
        for path in pack_paths:
            if os.path.isdir(path):
                if path in pack_ignore:
                    continue
                for dirname, subdirs, files in os.walk(path):
                    if dirname in pack_ignore:
                        continue
                    zf.write(dirname, os.path.join("assets", dirname))
                    for filename in files:
                        zf.write(os.path.join(dirname, filename), os.path.join("assets", dirname, filename))
            else:
                zf.write(path, os.path.join("assets", path))

    print(f"Packaged to {zip_path}")

def serve():
    port = 8000

    if sys.argv.__contains__("--port"):
        port = int(sys.argv[sys.argv.index("--port") + 1])

    import http.server

    os.chdir(build_path)

    class CORSRequestHandler (SimpleHTTPRequestHandler):
        def end_headers (self):
            self.send_header('Access-Control-Allow-Origin', '*')
            SimpleHTTPRequestHandler.end_headers(self)

    
    handler = http.server.SimpleHTTPRequestHandler

    with http.server.HTTPServer(("", port), CORSRequestHandler) as httpd:
        print(f"Serving at http://localhost:{port}")
        httpd.serve_forever()

    

if __name__ == "__main__":
    if "-h" in sys.argv or "--help" in sys.argv:
        print("Usage: python utils/web.py [--no-pack] [serve] [--port <port>]")
        sys.exit(0)

    if "--no-pack" not in sys.argv:
        if os.path.exists(version_path):
            print("Regenerating version.ini")
            os.remove(version_path)
        else:
            print("Generating version.ini")
        from version import main as make_version_ini
        make_version_ini(silent = True)
        pack()

    if "serve" in sys.argv:
        serve()