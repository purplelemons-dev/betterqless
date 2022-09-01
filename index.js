
const app = require('express')();
const http = require('http').Server(app);
const { createHash } = require('crypto');

const hash = (str) => createHash('sha256').update(str).digest('hex');

app.get('/', (req, res) => {
    res.sendFile(__dirname + "/public/index.html");
});

app.get("/admindash", (req, res) => {
    if (req.query.key === hash(process.env.ADMIN_KEY)) {
        res.sendFile(__dirname + "/public/admindash.html");
    } else {
        res.status(401).sendFile(__dirname + "/public/errors/401.html");
    }
});

http.listen(3000, () => {
    console.log("listening on *:3000");
});

