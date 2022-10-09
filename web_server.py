import sys
import cgi
import time
from docxtpl import DocxTemplate
from http.server import HTTPServer, SimpleHTTPRequestHandler
import os

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

    def do_GET(self):
        path = 'documente_create'
        if self.path == '/':
            self.path = './templates/form.html'
            file = read_html_template(self.path)
            self.send_response(200, "OK")
            self.end_headers()
            self.wfile.write(bytes(file, "utf-8"))
        elif os.path.isdir(path):
            try:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(str(os.listdir(path)).encode())
            except Exception:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(b'error')
        else:
            try:
                with open(path, 'rb') as f:
                    data = f.read()
                self.send_response(200)
                self.end_headers()
                self.wfile.write(data)
            # error handling skipped
            except Exception:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(b'error')

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
