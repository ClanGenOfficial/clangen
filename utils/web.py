import os
import zipfile
import sys

pack_paths = [
    "languages",
    "resources",
    "scripts",
    "sprites",
    "version.ini",
    "changelog.txt",
    "main.py",
    "webMain.py",
]

pack_ignore = [
    "__pycache__",
]

build_path = "build"
zip_name = "clangen.apk"
zip_path = os.path.join(build_path, zip_name)


def pack():
    """
    Packs all of pack_paths into a zip file with a parent folder of "assets"
    """

    if not os.path.exists(build_path):
        os.mkdir(build_path)
    
    if os.path.exists(zip_path):
        os.remove(zip_path)
    
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
    
    handler = http.server.SimpleHTTPRequestHandler

    with http.server.HTTPServer(("", port), handler) as server:
        # Serve files
        print("Serving on port", port)
        server.serve_forever()

    

if __name__ == "__main__":
    if "-h" in sys.argv or "--help" in sys.argv or len(sys.argv) == 1:
        print("Usage: python utils/web.py [--no-pack] [serve] [--port <port>]")
        sys.exit(0)

    if "--no-pack" not in sys.argv:
        pack()

    if "serve" in sys.argv:
        serve()