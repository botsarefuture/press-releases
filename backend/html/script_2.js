document.addEventListener("DOMContentLoaded", function () {
    const createReleaseForm = document.getElementById("createReleaseForm");
    // Event listener for submitting the add release form
    createReleaseForm.addEventListener("submit", function (event) {
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
