
import http.server
import json

def fdir(name:str, extra:str=""):
    directory = '\\'.join(__file__.split('\\')[:-2])
    return f"{directory}\\{extra}{name}"

class userSystem:

    def __init__(self):
        """
        Keeps track of users, roles, and tokens.
        The token variable is a dictionary with the token as the key and the username as the value.
        """
        self.readUsers()

    def readUsers(self):
        with open(fdir("users.json","data\\"), 'r') as f:
            self.users:list[dict[str,str]] = json.load(f)

    def readRoles(self):
        with open(fdir("roles.json","data\\"), 'r') as f:
            self.roles:list[dict[str,]] = json.load(f)
    
    def readTokens(self):
        with open(fdir("tokens.json","data\\"), 'r') as f:
            self.tokens:dict[str,str] = json.load(f)
    
    def readPasswords(self):
        with open(fdir("passwords.json","data\\"), 'r') as f:
            self.passwords = json.load(f)

    def writeUsers(self):
        with open(fdir("users.json","data\\"), 'w') as f:
            json.dump(self.users, f, indent=4)
        
    def writeRoles(self):
        with open(fdir("roles.json","data\\"), 'w') as f:
            json.dump(self.roles, f, indent=4)
        

class Handler(http.server.SimpleHTTPRequestHandler):

    def _401(self):
        self.send_response(401)
        self.end_headers()
        self.wfile.write(b"401 Unauthorized")

    def _404(self, message: str=""):
        if message and message[0]!="\n":
            message = "\n"+message
        self.send_response(404)
        self.end_headers()
        self.wfile.write(f"404 Not Found{message}".encode())

    def redirect(self, url: str):
        self.send_response(301)
        self.send_header('Location', url)
        self.end_headers()

    def _200(self, filename: str=None, content: str=None, public: bool=True):
        """
        Send a 200 response with the content of the file or otherwise specified content.
        
        """
        content_type = "text/html"
        if filename is None and content is None:
            raise ValueError('filename or content must be provided')
        elif filename is not None:
            try:
                if public:
                    with open(fdir(filename, extra="public\\"), 'r') as f:
                        content = f.read()
                else:
                    with open(fdir(filename, extra="static\\"), 'r') as f:
                        content = f.read()
            except FileNotFoundError:
                self._404(f"File not found: {filename}")
                return
            finally:
                if filename.endswith(".js"):
                    content_type = "text/javascript"
                elif filename.endswith(".css"):
                    content_type = "text/css"

        self.send_response(200)
        self.send_header('Content-type', content_type)
        self.end_headers()
        self.wfile.write(content.encode())

    def do_GET(self):
        if self.path=="/":
            self.redirect("/login")
            return

        elif self.path=="/login":
            self._200(filename="login.html")
            return

        self._200(filename=self.path[1:])


if __name__ == '__main__':

    with http.server.HTTPServer(('', 8000), Handler) as httpd:
        print("serving at port", 8000)
        httpd.serve_forever()


