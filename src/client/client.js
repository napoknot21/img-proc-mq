// Add an event listener to handle image upload when the button is clicked
document.getElementById('uploadButton').addEventListener('click', async () => {

    const fileInput = document.getElementById('imageInput'); // Input element for file selection
    const statusDiv = document.getElementById('status'); // Status message display element
    const downloadLink = document.getElementById('downloadLink'); // Link to download the processed image

    // Reset previous status and hide the download link
    statusDiv.textContent = '';
    statusDiv.className = 'status';
    downloadLink.style.display = 'none';

    // Validate that a file is selected
    if (!fileInput.files[0]) {

        updateStatus('Please select an image before uploading.', 'error', statusDiv);
        return;

    }

    // Prepare the file for upload
    const formData = new FormData();
    formData.append('image', fileInput.files[0]);

    try {
        // Update the user interface
        statusDiv.textContent = 'Uploading...';
        statusDiv.classList.add('status');

        // Send the file to the server
        const response = await fetch('http://localhost:5000/upload', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (response.ok) {

            statusDiv.textContent = `Upload successful! Task ID: ${result.file_path}`;
            statusDiv.classList.add('success');

            // Start checking the status of the task
            checkStatus(result.file_path, statusDiv, downloadLink);

        } else {

            statusDiv.textContent = `Error: ${result.message}`;
            statusDiv.classList.add('error');

        }

    } catch (error) {

        statusDiv.textContent = `Error: ${error.message}`;
        statusDiv.classList.add('error');

    }

});


/**
 * Poll the server for the status of the image processing task.
 * @param {string} fileName - The name of the uploaded file.
 * @param {HTMLElement} statusDiv - The element to display status messages.
 * @param {HTMLElement} downloadLink - The element to display the download link.
 */
async function checkStatus (fileName, statusDiv, downloadLink) {

    try {
        // Poll the status endpoint
        const response = await fetch(`http://localhost:5000/status?file_name=${fileName}`);
        const result = await response.json();

        if (response.ok && result.status === 'completed') {

            statusDiv.textContent = 'Image processing completed! You can now download the file.';
            statusDiv.classList.add('success');

            // Update and show the download link
            downloadLink.href = result.download_url;
            downloadLink.style.display = 'block';
            downloadLink.textContent = 'Download Processed Image';

        } else if (result.status === 'processing') {

            // Keep checking until the task is completed
            statusDiv.textContent = 'Processing... Please wait.';
            setTimeout(() => checkStatus(fileName, statusDiv, downloadLink), 5000);

        } else {

            statusDiv.textContent = 'Error checking status.';
            statusDiv.classList.add('error');

        }

    } catch (error) {

        statusDiv.textContent = `Error checking status: ${error.message}`;
        statusDiv.classList.add('error');
        
    }
}
