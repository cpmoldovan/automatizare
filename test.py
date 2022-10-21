# -*- coding: utf8 -*-
"""Simple HTTP Server.
This module builds on BaseHTTPServer by implementing the standard GET
and HEAD requests in a fairly straightforward manner.
"""

'''
This version of HTTPServer supports unicode and also serves files
from different directories. This version is by Ryan Marvin and is free to use.(marvinryan@ymail.com)
All you have to do is create an instance of this Handler, add the files you'd like to
serve in the paths list and set the flag to a value greater than 1.
In windows if you have files in a different disk partition, it'd be best to
create a symbolic link and use that to access that partition. See
example below
___________________________________________________________________
EXAMPLE:
import MySimpleHTTPServer as SimpleHTTPServer
class MyHttpRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    paths = [
    u"C:/Pictures/vacation.png",
    u"C:/Python27/LICENSE.txt",
    u"C:/D_Drive/Music/awesome.mp3",
    ]
    flag = 1
___________________________________________________________________
How it works:
Since the flag has been turned on, the list_directory() function which has been
changed, takes a different path and changes var list to self.paths.
Once set, the links of the files in the generated html page are now set
not relative to the current directory, but stating the full path to the
file.
'''

__version__ = "0.6"

__all__ = ["SimpleHTTPRequestHandler"]

import os
import posixpath
from http.server import SimpleHTTPRequestHandler
import urllib
import cgi
import shutil
import mimetypes
from io import StringIO
from web_server import HOST_NAME

HOST_NAME = "0.0.0.0"
PORT = 8080
class SimpleHTTPRequestHandler(SimpleHTTPRequestHandler):

    """Simple HTTP request handler with GET and HEAD commands.
    This serves files from the current directory and any of its
    subdirectories.  The MIME type for files is determined by
    calling the .guess_type() method.
    The GET and HEAD requests are identical except that the HEAD
    request omits the actual contents of the file.
    
    """

    server_version = "SimpleHTTP/" + __version__
    #this will be modified by you to set the files from different
    #directories you want
    paths = [
        u"C:/Users/Cristi/scoala/automatizare/documente_create/",
        ]

    #this is a flag signaling to override the default behaviour 
    #i.e serving only the current directory
    #change this to any other number
    
    flag = 1
    
    def do_GET(self):
        """Serve a GET request."""
        f = self.send_head()
        if f:
            try:
                self.copyfile(f, self.wfile)
            finally:
                f.close()

    def do_HEAD(self):
        """Serve a HEAD request."""
        f = self.send_head()
        if f:
            print(str(f))
            f.close()

    def send_head(self):
        """Common code for GET and HEAD commands.
        This sends the response code and MIME headers.
        Return value is either a file object (which has to be copied
        to the outputfile by the caller unless the command was HEAD,
        and must be closed by the caller under all circumstances), or
        None, in which case the caller has nothing further to do.
        """
        path = self.translate_path(self.path)
        f = None
        if os.path.isdir(path):
            parts = urllib.parse.urlsplit(self.path)
            if not parts.path.endswith('/'):
                # redirect browser - doing basically what apache does
                self.send_response(301)
                new_parts = (parts[0], parts[1], parts[2] + '/',
                             parts[3], parts[4])
                new_url = urllib.parse.urlunsplit(new_parts)
                self.send_header("Location", new_url)
                self.end_headers()
                return None
            for index in "index.html", "index.htm":
                index = os.path.join(path, index)
                if os.path.exists(index):
                    path = index
                    break
            else:
                return self.list_directory(path)
        ctype = self.guess_type(path)
        try:
            # Always read in binary mode. Opening files in text mode may cause
            # newline translations, making the actual size of the content
            # transmitted *less* than the content-length!
            f = open(path.decode("utf8"), 'rb')
        except IOError:
            self.send_error(404, "File not found")
            return None
        try:
            self.send_response(200)
            self.send_header("Content-type", ctype)
            fs = os.fstat(f.fileno())
            self.send_header("Content-Length", str(fs[6]))
            self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
            self.end_headers()
            return f
        except:
            f.close()
            raise

    def list_directory(self, path):
        """Helper to produce a directory listing (absent index.html).
        Return value is either a file object, or None (indicating an
        error).  In either case, the headers are sent, making the
        interface the same as for send_head().
        """
        if self.flag == 0:
            try:
                list = os.listdir(path.decode("utf8"))
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
        f = StringIO()
        displaypath = "Requested Files"
        f.write('<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">')
        f.write("<html>\n<title>Directory listing for %s</title>\n" % displaypath)
        f.write("<body>\n<h2>Directory listing for %s</h2>\n" % displaypath)
        f.write("<hr>\n<ul>\n")
        for dirname in list:
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
            
            f.write('<li><a href="%s">%s</a>\n'
                    % (urllib.quote(fullname), cgi.escape(displayname)))
        f.write("</ul>\n<hr>\n</body>\n</html>\n")
        length = f.tell()
        f.seek(0)
        self.send_response(200)
        encoding = "utf-8"
        self.send_header("Content-type", "text/html; charset=%s" % encoding)
        self.send_header("Content-Length", str(length))
        self.end_headers()
        return f

    def translate_path(self, path):
        """Translate a /-separated PATH to the local filename syntax.
        Components that mean special things to the local file system
        (e.g. drive or directory names) are ignored.  (XXX They should
        probably be diagnosed.)
        """
        # abandon query parameters
        path = path.split('?',1)[0]
        path = path.split('#',1)[0]
        # Don't forget explicit trailing slash when normalizing. Issue17324
        trailing_slash = path.rstrip().endswith('/')
        path = posixpath.normpath(urllib.unquote(path))
        words = path.split('/')
        words = filter(None, words)
        path = os.getcwd()
        for word in words:
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            if word in (os.curdir, os.pardir): continue
            path = os.path.join(path, word)
        if trailing_slash:
            path += '/'
        return path

    def copyfile(self, source, outputfile):
        """Copy all data between two file objects.
        The SOURCE argument is a file object open for reading
        (or anything with a read() method) and the DESTINATION
        argument is a file object open for writing (or
        anything with a write() method).
        The only reason for overriding this would be to change
        the block size or perhaps to replace newlines by CRLF
        -- note however that this the default server uses this
        to copy binary data as well.
        """
        shutil.copyfileobj(source, outputfile)

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
        '.py': 'text/plain',
        '.c': 'text/plain',
        '.h': 'text/plain',
        })


def test(HandlerClass = SimpleHTTPRequestHandler,
         ServerClass = SimpleHTTPRequestHandler):
   SimpleHTTPRequestHandler.test(HandlerClass, ServerClass)


if __name__ == '__main__':
    test()

if __name__ == "__main__":
    server = HTTPServer((HOST_NAME, PORT), PythonServer)
    print(f"Server started http://{HOST_NAME}:{PORT}")