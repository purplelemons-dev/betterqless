
const express = require("express");
const app = express();
const http = require("http").Server(app);
const { createHash } = require("crypto");
const fs = require("fs");
const port = 3000;
app.use(express.json());

let users;
fs.readFile("data/users.json", "utf8", (err, data) => {
    if (err) {
        throw err;
    } else {
        users = JSON.parse(data);
    }
});
let passwords;
fs.readFile("data/passwords.json", "utf8", (err, data) => {
    if (err) {
        throw err;
    } else {
        passwords = JSON.parse(data);
    }
});
let tokens;
fs.readFile("data/tokens.json", "utf8", (err, data) => {
    if (err) {
        throw err;
    } else {
        tokens = JSON.parse(data);
    }
});

const hash = (str) => createHash("sha256").update(str).digest("hex");

app.get("/", (req, res) => {
    res.redirect("/login");
});

app.get("/login", (req, res) => {
    res.sendFile(__dirname + "/login.html");
});

app.post("/login", (req, res) => {
    const { username, password } = req.body;
    if (username in users) {
        if (passwords[username] === hash(password)) {
            const token = hash(username + password);
            tokens[token] = username;
            res.cookie("token", token, { maxAge: 900000, httpOnly: true });
            res.redirect("/home");
        }
    }
});

app.get("/home", (req, res) => {
    const token = req.cookies.token;
    if (token in tokens) {
        res.sendFile(__dirname + "/home.html");
    } else {
        res.redirect("/login");
    }
});

app.get("/admindash", (req, res) => {
    if (req.query.key === hash(process.env.ADMIN_KEY)) {
        res.sendFile(__dirname + "/public/admindash.html");
    } else {
        res.status(401).sendFile(__dirname + "/public/errors/401.html");
    }
});

http.listen(port, () => {
    console.log("listening on *:3000");
});
