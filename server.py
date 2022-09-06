
import http.server
import json
from userSystem import userSystem, fdir

def parseCookie(cookie:str):
    return {item.split('=')[0]:item.split('=')[1] for item in cookie.split('; ')}

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

    def _500(self, message: str=""):
        if message and message[0]!="\n": message = "\n"+message
        self.send_response(500)
        self.end_headers()
        self.wfile.write(f"500 Internal Server Error{message}".encode())

    def redirect(self, url: str):
        self.send_response(301)
        self.send_header('Location', url)
        self.end_headers()

    def _200(self, filename: str=None, content: str=None, custom_headers:dict[str,str]={}, **replace:str):
        """
        Send a 200 response with the content of the file or otherwise specified content.
        Will replace any variables in the form of `{{var}}` with the value of the `var` key in the `replace` dictionary.
        """
        content_type = "text/html"
        if filename is None and content is None:
            raise ValueError('filename or content must be provided')
        elif filename is not None:
            try:
                with open(fdir(filename, extra="public\\"), 'r') as f:
                    content = f.read()
            except FileNotFoundError:
                self._404(f"File not found: {filename}")
                return
            finally:
                if filename.endswith(".js"):
                    content_type = "text/javascript"
                elif filename.endswith(".css"):
                    content_type = "text/css"
                elif filename.endswith(".png"):
                    content_type = "image/png"

        for key, value in replace.items():
            content = content.replace("{{"+key+"}}", str(value))

        self.send_response(200)
        self.send_header('Content-type', content_type)
        for key, value in custom_headers.items(): self.send_header(key, value)
        self.end_headers()
        self.wfile.write(content.encode())

    def userInfo(self)->tuple[str,dict[str,str]]:
        """
        Gets the user info from the request cookie.
        """
        try:
            cookie = self.headers.get("Cookie")
            token = parseCookie(cookie)["token"]
        except KeyError: return None, None
        try: username = usersys.tokens[token]
        except KeyError: return None, None

        for user in usersys.users:
            if user["name"] == username:
                return token, user
        return None, None

    def isAdmin(self)->bool:
        """
        Checks if the user is an admin.
        """
        token, user = self.userInfo()
        if user is None: return False
        return user["department"] == "admin"

    def do_GET(self):
        if self.path=="/":
            self.redirect("/login")
            return

        elif self.path.startswith("/api/") and self.isAdmin():
            if self.path=="/api/roles":
                self._200(content=json.dumps(usersys.roles))
            elif self.path=="/api/users":
                self._200(content=json.dumps(usersys.users))
            else:
                self._404()
            return

        elif self.path.startswith("/login"):
            # Check if the logout=true query is present
            if "logout=true" in self.path:
                # Delete the token cookie
                self._200(filename="login.html", custom_headers={"Set-Cookie": "token=;SameSite=Strict;Expires=Thu, 01 Jan 1970 00:00:00 GMT;"})
                return
            token, user = self.userInfo()
            if token is not None:
                self.redirect("/dashboard")
                return
            self._200(filename="login.html")
            return

        elif self.path=="/dashboard":
            # validate token via request cookie
            token, user = self.userInfo()
            if token is None and user is None:
                self.redirect("/login")
                return
            username = user["name"]
            role=usersys.getUserRole(username)
            if role is None:
                self._500(f"Problem getting {username}'s department")
                return

            if role=="admin":
                self._200(filename="admindash.html", username=username)
                return
            elif role=="student_worker":
                self._200(filename="workerdash.html", username=username)
                return

        elif self.path=="/admin":
            token, user = self.userInfo()
            if token not in usersys.tokens:
                self.redirect("/login")
                return

            role = user["department"]

            if role=="admin":
                self._200(filename="adminpanel.html", username=user["name"], users=usersys.users)
                return
            else:
                self._401()
                return

        # If all other paths are not found, return something in the public directory
        try: self._200(filename=self.path[1:])
        except ValueError: self._404()
        except: self._500()

    def do_POST(self):
        if self.path=="/login":
            if self.headers["Content-Type"]!="application/json":
                self._404("Content-Type must be application/json")
                return
            data:dict = json.loads(self.read_post())
            token = usersys.authenticate(data["username"], data["password"])
            if token == -1:
                self._401()
                return
            elif token == -2:
                self._404("User not found")
                return
            # send the token as a cookie
            self._200(content="", custom_headers={"Set-Cookie": f"token={token};SameSite=Strict;"})
            return

        self._404()

if __name__ == '__main__':

    usersys = userSystem()

    with http.server.HTTPServer(('', 8000), Handler) as httpd:
        print("serving at port", 8000)
        httpd.serve_forever()
