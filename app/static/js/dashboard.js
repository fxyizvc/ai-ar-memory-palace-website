document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.querySelector('.drop-zone');
    const fileInput = document.getElementById('file-input');
    const previewContainer = document.getElementById('file-preview-container');
    const uploadForm = document.getElementById('upload-form');
    const submitBtn = document.getElementById('submit-btn');

    // Handle file selection via click
    dropZone.addEventListener('click', () => fileInput.click());

    // Handle drag and drop events
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length) {
            fileInput.files = files;
            updateFilePreview();
        }
    });

    // Handle file selection from input
    fileInput.addEventListener('change', updateFilePreview);
    
    // Form submission
    submitBtn.addEventListener('click', () => {
        // Here you would typically use AJAX to submit the form
        // For now, we'll just submit it normally.
        uploadForm.submit();
    });

    function updateFilePreview() {
        previewContainer.innerHTML = ''; // Clear existing previews
        const files = fileInput.files;

        if (files.length === 0) {
            submitBtn.style.display = 'none';
            return;
        }

        submitBtn.style.display = 'block';

        for (const file of files) {
            const previewElement = document.createElement('div');
            previewElement.classList.add('file-preview');
            previewElement.textContent = file.name;

            const removeBtn = document.createElement('button');
            removeBtn.classList.add('remove-file');
            removeBtn.textContent = 'x';
            removeBtn.onclick = () => {
                removeFileFromFileList(file.name);
            };

            previewElement.appendChild(removeBtn);
            previewContainer.appendChild(previewElement);
        }
    }
    
    function removeFileFromFileList(fileName) {
        const dt = new DataTransfer();
        const files = fileInput.files;
        
        for (let i = 0; i < files.length; i++) {
            if (files[i].name !== fileName) {
                dt.items.add(files[i]);
            }
        }
        
        fileInput.files = dt.files;
        updateFilePreview();
    }
});