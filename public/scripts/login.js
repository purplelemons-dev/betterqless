const loginButton = document.getElementById('login');

loginButton.onclick = () => {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const data = { username, password };
    fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    }).then(res => res.json()).then(data => {
        console.log(data);
    });
}
