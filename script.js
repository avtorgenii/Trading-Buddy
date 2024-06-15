const tooltips = document.querySelectorAll('.tt')
tooltips.forEach(t => {
    new bootstrap.Tooltip(t)
});

document.getElementById('add-form-button').addEventListener('click', function () {
    // Get the form container
    const formContainer = document.getElementById('form-container');

    // Get the first form group as a template
    const firstFormGroup = formContainer.querySelector('.form-group');

    // Clone the template
    const newFormGroup = firstFormGroup.cloneNode(true);

    // Update the label and input ID for the new form group
    const formCount = formContainer.querySelectorAll('.form-group').length + 1;
    newFormGroup.querySelector('label').setAttribute('for', 'takep' + formCount);
    newFormGroup.querySelector('label').textContent = 'Take №' + formCount + ' Price:';
    newFormGroup.querySelector('input').setAttribute('id', 'takep' + formCount);
    newFormGroup.querySelector('input').value = '';

    // Append the new form group to the container
    formContainer.appendChild(newFormGroup);

    // Show the remove button if there is more than one form group
    toggleRemoveButton();

    // Show the stop-to-entry form if there are two or more take forms
    toggleStopToEntryForm();
});

document.getElementById('remove-form-button').addEventListener('click', function () {
    // Get the form container
    const formContainer = document.getElementById('form-container');

    // Get all form groups
    const formGroups = formContainer.querySelectorAll('.form-group');

    // Remove the last form group if there's more than one
    if (formGroups.length > 1) {
        formContainer.removeChild(formGroups[formGroups.length - 1]);
    }

    // Hide the remove button if there is only one form group left
    toggleRemoveButton();

    // Show/hide the stop-to-entry form based on the number of take forms
    toggleStopToEntryForm();
});

function toggleRemoveButton() {
    const formGroups = document.getElementById('form-container').querySelectorAll('.form-group');
    const removeButton = document.getElementById('remove-form-button');
    if (formGroups.length > 1) {
        removeButton.style.display = 'inline-block';
    } else {
        removeButton.style.display = 'none';
    }
}

function toggleStopToEntryForm() {
    const formGroups = document.getElementById('form-container').querySelectorAll('.form-group');
    const stopToEntryForm = document.getElementById('stop-to-entry-form');
    if (formGroups.length >= 2) {
        stopToEntryForm.style.display = 'block';
    } else {
        stopToEntryForm.style.display = 'none';
    }
}

// Initial call to set the correct state of the remove button and stop-to-entry form
toggleRemoveButton();
toggleStopToEntryForm();


// Open position button
document.getElementById('entryp').addEventListener('click', function() {
    updateButtonState();
});

document.getElementById('stopp').addEventListener('input', function() {
    updateButtonState();
});

function updateButtonState() {
    const stopPrice = parseFloat(document.getElementById('stopp').value);
    const entryPrice = parseFloat(document.getElementById('entryp').value);
    const button = document.getElementById('opent');
    const tradeInfo = document.getElementById('tradeinfo');

    if (!isNaN(stopPrice) && !isNaN(entryPrice)) {
        if (stopPrice < entryPrice) {
            button.classList.remove('btn-danger', 'btn-secondary', 'disabled');
            button.classList.add('btn-success');
            button.textContent = 'Open Long';

            tradeInfo.classList.remove('d-none');
        } else if (stopPrice > entryPrice) {
            button.classList.remove('btn-success', 'btn-secondary', 'disabled');
            button.classList.add('btn-danger');
            button.textContent = 'Open Short';

            tradeInfo.classList.remove('d-none');
        } else {
            button.classList.remove('btn-success', 'btn-danger', 'disabled');
            button.classList.add('btn-secondary');
            button.textContent = 'Open';

            tradeInfo.classList.add('d-none');
        }
    } else {
        button.classList.remove('btn-success', 'btn-danger');
        button.classList.add('btn-secondary', 'disabled');
        button.textContent = 'Open';

        tradeInfo.classList.add('d-none');
    }
}

// Initial call to set the correct state of the button
updateButtonState();
