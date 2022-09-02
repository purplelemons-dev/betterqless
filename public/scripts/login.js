const loginButton = document.getElementById('login');
const passwordField = document.getElementById('password');
const usernameField = document.getElementById('username');

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
    }).then(res => {
        if (res.status === 200) {
            window.location.href = '/dashboard';
        } else {
            alert('Invalid username or password');
        }
    });
}

passwordField.onkeydown = usernameField.onkeydown = (e) => {
    if (e.key === 'Enter') {
        loginButton.click();
    }
}
