const users = fetch("/api/users", {
    credentials: "include"
})
.then(response => response.json())
.then(data => {
    const table = document.getElementById("users");
    for (let user of data) {
        const row = table.insertRow();
        const username = row.insertCell(0);
        const department = row.insertCell(1);
        const actions = row.insertCell(2);
        username.innerText = user.name;
        department.innerText = user.department;
        actions.innerHTML = `<a id="edit${user.name}"><img src="images/pencil.png" alt="Edit User"></a>
                             <a id="delete${user.name}"><img src="images/trash.png" alt="Delete User"></a>`;
        document.getElementById(`edit${user.name}`).addEventListener("click", () => {
            // Edit user
        });
        document.getElementById(`delete${user.name}`).addEventListener("click", () => {
            // Delete user
        });
    }
});


