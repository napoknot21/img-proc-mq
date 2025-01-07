document.getElementById('uploadButton').addEventListener('click', async () => {

    const fileInput = document.getElementById('imageInput');
    const statusDiv = document.getElementById('status');

    // Clear previous status
    statusDiv.textContent = '';
    statusDiv.className = 'status';

    if (!fileInput.files[0]) {

        statusDiv.textContent = 'Please select an image before uploading.';
        statusDiv.classList.add('error');
        return;
    
    }

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
            statusDiv.textContent = `Upload successful! Task ID: ${result.task_id}`;
            statusDiv.classList.add('success');
        } else {
            statusDiv.textContent = `Error: ${result.message}`;
            statusDiv.classList.add('error');
        }
    
    } catch (error) {
    
        statusDiv.textContent = `Error: ${error.message}`;
        statusDiv.classList.add('error');
    
    }

});
