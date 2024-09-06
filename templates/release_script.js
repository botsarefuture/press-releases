document.addEventListener("DOMContentLoaded", function () {
    const pressReleasesContainer = document.getElementById("pressReleases");

    // Fetch press releases from the backend
    fetch("http://127.0.0.1:5000/api/press-releases", { method: "GET", mode: "no-cors" }) // Removed mode: "no-cors"
        .then(response => response.json())
        .then(data => {
            // Check if press releases exist
            if (data.length > 0) {
                // Iterate over each press release and create HTML elements to display them
                data.forEach(release => {
                    const releaseDiv = document.createElement("div");
                    releaseDiv.classList.add("press-release");

                    const titleHeader = document.createElement("h2");
                    titleHeader.textContent = release.title;

                    const contentParagraph = document.createElement("p");
                    contentParagraph.textContent = release.content;

                    releaseDiv.appendChild(titleHeader);
                    releaseDiv.appendChild(contentParagraph);

                    pressReleasesContainer.appendChild(releaseDiv);
                });
            } else {
                // If no press releases exist, display a message
                pressReleasesContainer.textContent = "No press releases available.";
            }
        })
        .catch(error => console.error('Error fetching press releases:', error));
});
