
import json
from hashlib import sha256
from random import getrandbits as rand


def fdir(name:str, extra:str=""):
    directory = '\\'.join(__file__.split('\\')[:-1])
    return f"{directory}\\{extra}{name}"

class userSystem:

    def __init__(self):
        """
        Keeps track of users, roles, and tokens.\n
        The token variable is a dictionary with the token as the key and the username as the value.
        """
        self.readUsers()
        self.readRoles()
        self.readPasswords()
        self.tokens:dict[str,str] = {}

    def readUsers(self):
        with open(fdir("users.json","data\\"), 'r') as f:
            self.users:list[dict[str,str]] = json.load(f)

    def readRoles(self):
        with open(fdir("roles.json","data\\"), 'r') as f:
            self.roles:list[dict[str,]] = json.load(f)

    def readPasswords(self):
        with open(fdir("passwords.json","data\\"), 'r') as f:
            self.passwords:dict[str,str] = json.load(f)

    def writeUsers(self):
        with open(fdir("users.json","data\\"), 'w') as f:
            json.dump(self.users, f, indent=4)

    def writeRoles(self):
        with open(fdir("roles.json","data\\"), 'w') as f:
            json.dump(self.roles, f, indent=4)

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
                return token
            return -1
        return -2

    def getUserRole(self,username:str)->str:
        """
        Returns the role of the user.
        """
        for user in self.users:
            if user["name"] == username:
                return user["department"]
        return None
