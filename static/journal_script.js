document.addEventListener('DOMContentLoaded', function () {
    const editableCells = document.querySelectorAll('.editable');
    const editModal = new bootstrap.Modal(document.getElementById('editModal'));
    const editValueInput = document.getElementById('editValue');
    const editTradeIdInput = document.getElementById('editTradeId');
    const editFieldInput = document.getElementById('editField');
    const saveChangesButton = document.getElementById('saveChanges');

    const handleFileSelect = (event, previewId) => {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function (e) {
                showImagePreview(previewId, e.target.result);
            };
            reader.readAsDataURL(file);
        }
    };

    const showImagePreview = (previewId, src) => {
        const previewArea = document.getElementById(previewId);
        previewArea.innerHTML = `<img src="${src}" class="img-fluid" alt="Image Preview" />`;
    };

    editableCells.forEach(cell => {
        cell.addEventListener('click', function () {
            const tradeId = this.getAttribute('data-trade-id');
            const field = this.getAttribute('data-field');
            const currentValue = this.textContent.trim();

            editTradeIdInput.value = tradeId;
            editFieldInput.value = field;
            editValueInput.value = currentValue;

            // Fetch existing images for the trade and show them in the modal
            fetch(`/get-trade-images/${tradeId}`)
                .then(response => response.json())
                .then(data => {
                    if (data.screen) {
                        showImagePreview('screenPreview', `data:image/png;base64,${data.screen}`);
                    } else {
                        document.getElementById('screenPreview').innerHTML = 'Drag and drop an image here or click to select.';
                    }
                    if (data.screen_zoomed) {
                        showImagePreview('screenZoomedPreview', `data:image/png;base64,${data.screen_zoomed}`);
                    } else {
                        document.getElementById('screenZoomedPreview').innerHTML = 'Drag and drop an image here or click to select.';
                    }
                });

            editModal.show();
        });
    });

    saveChangesButton.addEventListener('click', function () {
        const tradeId = editTradeIdInput.value;
        const field = editFieldInput.value;
        const newValue = editValueInput.value;
        const screenFile = document.getElementById('screen').files[0];
        const screenZoomedFile = document.getElementById('screenZoomed').files[0];

        const formData = new FormData();
        formData.append('trade_id', tradeId);
        formData.append('field', field);
        formData.append('value', newValue);
        if (screenFile) {
            formData.append('screen', screenFile);
        }
        if (screenZoomedFile) {
            formData.append('screen_zoomed', screenZoomedFile);
        }

        fetch('/update-trade/', {
            method: 'POST',
            body: formData
        })
            .then(response => response.json())
            .then(data => {
                console.log('Trade updated successfully:', data);
                document.querySelector(`.editable[data-trade-id="${tradeId}"][data-field="${field}"]`).textContent = newValue;
                editModal.hide();
            })
            .catch(error => {
                console.error('Error updating trade:', error);
            });
    });

    const textarea = document.getElementById('editValue');

    const adjustHeight = (el) => {
        el.style.height = 'auto';
        el.style.height = (el.scrollHeight + 5) + 'px';
    };

    textarea.addEventListener('input', function () {
        adjustHeight(textarea);
    });

    const editModalElement = document.getElementById('editModal');
    editModalElement.addEventListener('shown.bs.modal', function () {
        adjustHeight(textarea);
    });

    adjustHeight(textarea);

    document.getElementById('screen').addEventListener('change', function (event) {
        handleFileSelect(event, 'screenPreview');
    });

    document.getElementById('screenZoomed').addEventListener('change', function (event) {
        handleFileSelect(event, 'screenZoomedPreview');
    });

    const screenDropArea = document.getElementById('screenDropArea');
    screenDropArea.addEventListener('click', () => document.getElementById('screen').click());
    screenDropArea.addEventListener('dragover', (event) => {
        event.preventDefault();
        screenDropArea.classList.add('dragging');
    });
    screenDropArea.addEventListener('dragleave', () => screenDropArea.classList.remove('dragging'));
    screenDropArea.addEventListener('drop', (event) => {
        event.preventDefault();
        screenDropArea.classList.remove('dragging');
        const file = event.dataTransfer.files[0];
        document.getElementById('screen').files = event.dataTransfer.files;
        handleFileSelect({ target: { files: [file] } }, 'screenPreview');
    });

    const screenZoomedDropArea = document.getElementById('screenZoomedDropArea');
    screenZoomedDropArea.addEventListener('click', () => document.getElementById('screenZoomed').click());
    screenZoomedDropArea.addEventListener('dragover', (event) => {
        event.preventDefault();
        screenZoomedDropArea.classList.add('dragging');
    });
    screenZoomedDropArea.addEventListener('dragleave', () => screenZoomedDropArea.classList.remove('dragging'));
    screenZoomedDropArea.addEventListener('drop', (event) => {
        event.preventDefault();
        screenZoomedDropArea.classList.remove('dragging');
        const file = event.dataTransfer.files[0];
        document.getElementById('screenZoomed').files = event.dataTransfer.files;
        handleFileSelect({ target: { files: [file] } }, 'screenZoomedPreview');
    });
});

