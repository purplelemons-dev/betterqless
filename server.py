
import http.server
import json
from random import getrandbits as rand
from hashlib import sha256

def fdir(name:str, extra:str=""):
    directory = '\\'.join(__file__.split('\\')[:-1])
    return f"{directory}\\{extra}{name}"

class userSystem:

    def __init__(self):
        """
        Keeps track of users, roles, and tokens.
        The token variable is a dictionary with the token as the key and the username as the value.
        """
        self.readUsers()
        self.readRoles()
        self.readTokens()
        self.readPasswords()

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
            self.passwords:dict[str,str] = json.load(f)

    def writeUsers(self):
        with open(fdir("users.json","data\\"), 'w') as f:
            json.dump(self.users, f, indent=4)

    def writeRoles(self):
        with open(fdir("roles.json","data\\"), 'w') as f:
            json.dump(self.roles, f, indent=4)

    def writeTokens(self):
        with open(fdir("tokens.json","data\\"), 'w') as f:
            json.dump(self.tokens, f, indent=4)

    def writePasswords(self):
        with open(fdir("passwords.json","data\\"), 'w') as f:
            json.dump(self.passwords, f, indent=4)

    def authenticate(self, username:str, password:str)->int:
        """
        Checks if the password is correct and returns a new token.\n
        Returns `-1` if the password is incorrect.\n
        Returns `-2` if the user does not exist.
        """
        username = username.lower()
        if username in self.passwords:
            hashed = sha256(password.encode()).hexdigest()
            if self.passwords[username] == hashed:
                token = str(rand(100))
                if username in self.tokens.values():
                    for key, value in self.tokens.copy().items():
                        if value == username: del self.tokens[key]
                self.tokens[token] = username
                self.writeTokens()
                return token
            return -1
        return -2

class Handler(http.server.SimpleHTTPRequestHandler):

    def read_post(self):
        """
        Reads the post data from the request.
        """
        length = int(self.headers['Content-Length'])
        data = self.rfile.read(length).decode()
        return data

    def _401(self):
        self.send_response(401)
        self.end_headers()
        self.wfile.write(b"401 Unauthorized")

    def _404(self, message: str=""):
        if message and message[0]!="\n": message = "\n"+message
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
                    with open(fdir(filename, extra="public\\"), 'r') as f: content = f.read()
                else:
                    with open(fdir(filename, extra="static\\"), 'r') as f: content = f.read()
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

        elif self.path=="/favicon.ico":
            self._200("favico.png", public=False)
            return
        elif self.path=="/login":
            self._200(filename="login.html")
            return

        # If all other paths are not found, return something in the public directory
        self._200(filename=self.path[1:])

    def do_POST(self):
        if self.path=="/login":
            if self.headers["Content-Type"]!="application/json":
                self._404("Content-Type must be application/json")
                return
            data:dict|list = json.loads(self.read_post())
            token = usersys.authenticate(data["username"], data["password"])
            if token == -1:
                self._401()
                return
            elif token == -2:
                self._404("User not found")
                return
            # send the token as a cookie
            self.send_response(200)
            self.send_header("Set-Cookie", f"token={token};SameSite=Strict;")
            self.end_headers()
            return

        self._404()

if __name__ == '__main__':

    usersys = userSystem()

    with http.server.HTTPServer(('', 8000), Handler) as httpd:
        print("serving at port", 8000)
        httpd.serve_forever()


