document.addEventListener('DOMContentLoaded', function () {
    const editableCells = document.querySelectorAll('.editable');
    const editableScreenCells = document.querySelectorAll('.editableScreen');
    const editTextModal = new bootstrap.Modal(document.getElementById('editTextModal'));
    const editScreenModal = new bootstrap.Modal(document.getElementById('editScreenModal'));
    const editValueInput = document.getElementById('editValue');
    const editTradeIdInput = document.getElementById('editTradeId');
    const editFieldInput = document.getElementById('editField');
    const saveChangesButton = document.getElementById('saveChanges');

    const editScreenTradeIdInput = document.getElementById('editScreenTradeId');
    const editScreenFieldInput = document.getElementById('editScreenField');
    const saveScreenChangesButton = document.getElementById('saveScreenChanges');

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

            editTextModal.show();
        });
    });

    editableScreenCells.forEach(cell => {
        cell.addEventListener('click', function () {
            const tradeId = this.getAttribute('data-trade-id');
            const field = this.getAttribute('data-field');

            editScreenTradeIdInput.value = tradeId;
            editScreenFieldInput.value = field;

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

            editScreenModal.show();
        });
    });

    saveChangesButton.addEventListener('click', function () {
        const tradeId = editTradeIdInput.value;
        const field = editFieldInput.value;
        const newValue = editValueInput.value;

        fetch('/update-trade/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ trade_id: tradeId, field: field, value: newValue }),
        })
            .then(response => response.json())
            .then(data => {
                console.log('Trade updated successfully:', data);
                document.querySelector(`.editable[data-trade-id="${tradeId}"][data-field="${field}"]`).textContent = newValue;
                editTextModal.hide();
            })
            .catch(error => {
                console.error('Error updating trade:', error);
            });
    });

    saveScreenChangesButton.addEventListener('click', function () {
        const tradeId = editScreenTradeIdInput.value;
        const field = editScreenFieldInput.value;
        const screenFile = document.getElementById('screen').files[0];
        const screenZoomedFile = document.getElementById('screenZoomed').files[0];

        const formData = new FormData();
        formData.append('trade_id', tradeId);
        formData.append('field', field);
        if (screenFile) {
            formData.append('screen', screenFile);
        }
        if (screenZoomedFile) {
            formData.append('screen_zoomed', screenZoomedFile);
        }

        fetch('/update-trade-screens/', {
            method: 'POST',
            body: formData
        })
            .then(response => response.json())
            .then(data => {
                console.log('Trade updated successfully:', data);
                editScreenModal.hide();
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

    const editTextModalElement = document.getElementById('editTextModal');
    editTextModalElement.addEventListener('shown.bs.modal', function () {
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

    // Function to convert Unix time to readable date format
    const convertUnixToDate = (unixTime) => {
        const date = new Date(unixTime * 1000); // Convert to milliseconds
        return date.toUTCString().replace(' GMT', ''); // Convert to UTC string and remove GMT
    };

    const unixFields = document.querySelectorAll('td[data-unix]');
    unixFields.forEach(field => {
        const unixTime = parseInt(field.getAttribute('data-unix'), 10);
        if (!isNaN(unixTime)) {
            field.textContent = convertUnixToDate(unixTime);
        } else {
            field.textContent = '';
        }
    });
});

// Removing Trade
document.getElementById('saveRemoveTrade').addEventListener('click', function() {
            const tradeId = document.getElementById('removeTradeId').value;

            if (tradeId) {
                fetch('/remove-trade', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ trade_id: tradeId})
                })
                .then(response => response.json())
                .then(data => {
                    location.reload()
                })
                .catch(error => {
                    console.error('Error:', error);
                });
            }
});
