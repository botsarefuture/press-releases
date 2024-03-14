document.addEventListener("DOMContentLoaded", function() {
    const loginForm = document.getElementById("loginForm");
    const createReleaseForm = document.getElementById("createReleaseForm");
    const addReleaseForm = document.getElementById("addReleaseForm");

    // Event listener for submitting the login form
    loginForm.addEventListener("submit", function(event) {
        event.preventDefault();
        
        const username = document.getElementById("username").value;
        const password = document.getElementById("password").value;

        // Send login request to backend
        fetch("http://127.0.0.1:5000/api/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ username, password })
        })
        .then(response => {
            if (response.ok) {
                // Redirect to main page if login successful
                window.location.href = "/";
            } else {
                alert("Invalid credentials. Please try again.");
            }
        })
        .catch(error => console.error('Error logging in:', error));
    });

    // Event listener for submitting the add release form
    addReleaseForm.addEventListener("submit", function(event) {
        event.preventDefault();

        // Get release details from form inputs
        const title = document.getElementById("releaseTitle").value;
        const content = document.getElementById("releaseContent").value;

        // Send POST request to add new release
        fetch("/api/new-release", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ title, content })
        })
        .then(response => {
            if (response.ok) {
                alert("Press release added successfully.");
                // Clear form inputs
                document.getElementById("releaseTitle").value = "";
                document.getElementById("releaseContent").value = "";
            } else {
                alert("Error adding press release. Please try again.");
            }
        })
        .catch(error => console.error('Error adding new release:', error));
    });
});
