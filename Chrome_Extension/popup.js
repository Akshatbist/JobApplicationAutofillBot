const dropZone = document.getElementById("dropZone");
const statusElement = document.getElementById("status");
const submitButton = document.getElementById("submitButton");
let uploadedFile = null;

// Highlight the drop zone when a file is dragged over it
dropZone.addEventListener("dragover", (event) => {
    event.preventDefault();
    dropZone.classList.add("dragover");
});

// Remove highlight when the drag leaves the drop zone
dropZone.addEventListener("dragleave", () => {
    dropZone.classList.remove("dragover");
});

// Handle the file drop
dropZone.addEventListener("drop", (event) => {
    event.preventDefault();
    dropZone.classList.remove("dragover");

    const file = event.dataTransfer.files[0];
    if (!file) {
        statusElement.textContent = "No file dropped.";
        return;
    }

    uploadedFile = file;
    statusElement.textContent = `File "${file.name}" ready for upload.`;
    
});

submitButton.addEventListener("click", () => {
  if (!uploadedFile) {
    statusElement.textContent = "Please upload a resume first.";
    return;
  }

  const backendUrlResume = "http://127.0.0.1:8000/scan_resume";
  const backendUrlQuestion = "http://127.0.0.1:8000/scan_question";
  const formData = new FormData();
  formData.append("file", uploadedFile);

  statusElement.textContent = "Bot in progress...";

  // Force the DOM update before continuing
  setTimeout(() => {
    fetch(backendUrlResume, {
      method: "POST",
      body: formData
    })
      .then(response => response.json())
      .then(data => {
        if (data.status === "success") {
          statusElement.textContent = "Resume uploaded and processed successfully!";

          // Trigger scan_question
          return fetch(backendUrlQuestion, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url: "YOUR_JOB_URL_HERE" })
          });
        } else {
          throw new Error(data.message);
        }
      })
      .then(response => response.json())
      .then(data => {
        //Not rendering the emoji
        statusElement.textContent = `✅ Job form scanned: ${data.message}`;
      })
      .catch(err => {
        statusElement.textContent = `❌ Error: ${err.message}`;
      });
  }, 50); // Let the browser paint first
});
