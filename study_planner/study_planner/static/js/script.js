/**
 * Basic Client-Side Validation
 * Checks if fields are empty before submitting.
 */

function validateLogin() {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    if (email.trim() === "" || password.trim() === "") {
        alert("Please fill in all fields.");
        return false;
    }
    return true;
}

function validateRegister() {
    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm_password').value;

    if (name.trim() === "" || email.trim() === "" || password.trim() === "" || confirmPassword.trim() === "") {
        alert("Please fill in all fields.");
        return false;
    }

    if (password !== confirmPassword) {
        alert("Passwords do not match.");
        return false;
    }

    return true;
}
