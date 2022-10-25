from distutils import text_file
import sys
import cgi
import time
import mimetypes
import posixpath
from docxtpl import DocxTemplate
from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
from io import StringIO
import urllib
import html

HOST_NAME = "0.0.0.0"
PORT = 8080


def read_html_template(path):
    """function to read HTML file"""
    try:
        with open(path) as f:
            file = f.read()
    except Exception as e:
        file = e
    return file


class PythonServer(SimpleHTTPRequestHandler):
    """Python HTTP Server that handles GET and POST requests"""
    paths = ["documente_create"]
    flag = 0
    def do_GET(self):
        path = self.translate_path(self.path)
        if self.path == '/':
            self.path = './templates/index.html'
            file = read_html_template(self.path)
            self.send_response(200, "OK")
            self.end_headers()
            self.wfile.write(bytes(file, "utf-8"))
        #asta e pentru cazul cand URL-ul e catre un fisier si nu folder
        elif not os.path.isdir(path):
            ctype = self.guess_type(path)
            try:
                # Always read in binary mode. Opening files in text mode may cause
                # newline translations, making the actual size of the content
                # transmitted *less* than the content-length!
                f = open(path, 'rb')
                f.seek(0, os.SEEK_END)
                filesize = f.tell()
                f.seek(0, os.SEEK_SET)
            except IOError:
                self.send_error(404, "File not found")
                return None
            self.send_response(200)
            self.send_header("Content-type", ctype)
            fs = os.fstat(f.fileno())
            self.send_header("Content-Length", str(fs[6]))
            self.send_header("Last-Modified", self.date_time_string(time.time()))
            self.send_header("Cache-control", "no-cache, no-store, must-revalidate, max-age=0, proxy-revalidate, no-transform")
            self.send_header("Pragma", "no-cache")
            self.end_headers()
        else:
            path = './documente_create'
            self.path = './templates/folder.html'
            file = read_html_template(self.path)
            table_row = ""
            if self.flag == 0:
                try:
                    list = os.listdir(path)
                except os.error:
                    self.send_error(404, "No permission to list directory")
                    return None
            else:
                try:
                    list = self.paths
                except os.error:
                    self.send_error(404, "No permission to list directory")
                    return None
            list.sort(key=lambda a: a.lower())

            for dirname in list:
                table_row += "<tr>"
                name = os.path.basename(dirname)
                name = name.encode("utf8")
                fullname = dirname.encode('utf8')
                displayname = linkname = name
                # Append / for directories or @ for symbolic links
                if os.path.isdir(fullname):
                    displayname = name + "/"
                    linkname = name + "/"
                if os.path.islink(fullname):
                    displayname = name + "@"
                    # Note: a link to a directory displays with @ and links with /
                table_row += "<td>"
                table_row += '<a href="%s">%s</a>' % (urllib.parse.quote(fullname), urllib.parse.quote(fullname))
                table_row += "</td>"
                table_row += "</tr>"

            file = file.replace("{{user_records}}", table_row)
            self.send_response(200, "OK")
            self.end_headers()
            self.wfile.write(bytes(file, "utf-8"))

    def translate_path(self, path):
        """Translate a /-separated PATH to the local filename syntax.
        Components that mean special things to the local file system
        (e.g. drive or directory names) are ignored.  (XXX They should
        probably be diagnosed.)
        """
        # abandon query parameters
        path = path.split('?',1)[0]
        path = path.split('#',1)[0]
        path = posixpath.normpath(urllib.parse.unquote(path))
        words = path.split('/')
        words = filter(None, words)
        path = os.getcwd()
        for word in words:
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            if word in (os.curdir, os.pardir): continue
            path = os.path.join(path, word)
        return path

    def guess_type(self, path):
        """Guess the type of a file.
        Argument is a PATH (a filename).
        Return value is a string of the form type/subtype,
        usable for a MIME Content-type header.
        The default implementation looks the file's extension
        up in the table self.extensions_map, using application/octet-stream
        as a default; however it would be permissible (if
        slow) to look inside the data to make a better guess.
        """

        base, ext = posixpath.splitext(path)
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        ext = ext.lower()
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        else:
            return self.extensions_map['']

    if not mimetypes.inited:
        mimetypes.init() # try to read system mime.types
    extensions_map = mimetypes.types_map.copy()
    extensions_map.update({
        '': 'application/octet-stream', # Default
        '.docx': 'application/msword',
        })

    def do_POST(self):
        if self.path == '/success':

            ctype, pdict = cgi.parse_header(self.headers.get('content-type'))
            pdict['boundary'] = bytes(pdict['boundary'], 'utf-8')

            if ctype == 'multipart/form-data':
                fields = cgi.parse_multipart(self.rfile, pdict)

                doc = DocxTemplate("./templates/template.docx")

                context = {
                "numar_iesire":fields.get("numar_iesire")[0],
                "data":fields.get("data")[0],
                "nume_societate":fields.get("nume_societate")[0],
                "nume_administrator":fields.get("nume_administrator")[0],
                "valoare_contract":fields.get("valoare_contract")[0],
                "pretul_include":fields.get("pretul_include")[0],
                "durata_executie":fields.get("durata_executie")[0],
                "plata_procent_avans":fields.get("plata_procent_avans")[0],
                "plata_procent_ramas":fields.get("plata_procent_ramas")[0],
                }

                doc.render(context)
                timestr = time.strftime("%d%m%Y-%H%M%S")
                nume_fisier = "./documente_create/contract-" + timestr + ".docx"
                doc.save(nume_fisier)

                self.send_response(200)
                self.send_header('Content-type', 'application/docx')
                self.send_header('Content-Disposition', 'attachment; filename="contract_servicii_' + fields.get("nume_societate")[0] + '.docx"')
                self.end_headers()
                with open(nume_fisier, 'rb') as file: 
                    self.wfile.write(file.read()) # Read the file and send the contents 

if __name__ == "__main__":
    server = HTTPServer((HOST_NAME, PORT), PythonServer)
    print(f"Server started http://{HOST_NAME}:{PORT}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
        print("Server stopped successfully")
        sys.exit(0)
