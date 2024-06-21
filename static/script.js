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


// Updating trade info after update of the trade form
document.addEventListener('DOMContentLoaded', () => {
    const takeInputs = document.querySelectorAll('#form-container input[id^="takep"]');
    const stoeInput = document.getElementById('stoe');
    const stopPriceInput = document.getElementById('stopp');
    const entryPriceInput = document.getElementById('entryp');
    const leverageInput = document.getElementById('leverage');
    const toolSelect = document.getElementById('tool');

    // Add event listeners to each input field
    takeInputs.forEach(input => input.addEventListener('input', checkAndSubmit));
    stoeInput.addEventListener('input', checkAndSubmit);
    stopPriceInput.addEventListener('input', checkAndSubmit);
    entryPriceInput.addEventListener('input', checkAndSubmit);
    leverageInput.addEventListener('input', checkAndSubmit);
    toolSelect.addEventListener('change', checkAndSubmit);

    function checkAndSubmit() {
        const takes = Array.from(takeInputs).map(input => parseFloat(input.value));
        const stoe = parseInt(stoeInput.value);
        const stopPrice = parseFloat(stopPriceInput.value);
        const entryPrice = parseFloat(entryPriceInput.value);
        const leverage = parseInt(leverageInput.value);
        const tool = toolSelect.value;

        // Check if all fields have valid numbers
        if (takes.every(value => !isNaN(value)) && !isNaN(stoe) && !isNaN(stopPrice) && !isNaN(entryPrice) && !isNaN(leverage) && tool) {
            // Send the request to FastAPI to process the data
            fetch('/process-trade-data/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ tool: tool, entry_p: entryPrice, stop_p: stopPrice, leverage: leverage, take_ps: takes, stoe: stoe }),
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                console.log('Data processed successfully:', data);

                // Update the trade info in the HTML
                const tradeInfoDiv = document.getElementById('tradeinfo');
                tradeInfoDiv.classList.remove('d-none');

                // Assuming you have <span> tags inside your <p> tags to update values
                document.getElementById('volume-info').textContent = `Volume: ${data.volume}`;
                document.getElementById('margin-info').textContent = `Margin: ${data.margin}`;
                document.getElementById('loss-info').textContent = `Potential Loss: ${data.potential_loss}`;
                document.getElementById('profit-info').textContent = `Potential Profit: ${data.potential_profit}`;
            })
            .catch(error => {
                console.error('There was a problem with the fetch operation:', error);
            });
        }
    }
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
document.getElementById('entryp').addEventListener('blur', function () {
    updateEntryFormState();
});

document.getElementById('stopp').addEventListener('blur', function () {
    updateEntryFormState();
});



function updateEntryFormState() {
    const stopPrice = parseFloat(document.getElementById('stopp').value);
    const entryPrice = parseFloat(document.getElementById('entryp').value);
    const button = document.getElementById('opent');
    const tradeInfo = document.getElementById('tradeinfo');
    const leverageInput = document.getElementById('leverage');
    const tool = document.getElementById('tool').value;

    function fetchMaxLeverage(tool, callback) {
        fetch('/set-default-leverage/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ tool: tool, long_side: entryPrice > stopPrice})
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            callback(data.max_leverage)
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
        });
    }

    function updateLeverage(maxLeverage) {
        leverageInput.value = maxLeverage;
        leverageInput.disabled = false;
        leverageInput.max = maxLeverage;

        leverageInput.addEventListener('input', () => {
            if (leverageInput.value > maxLeverage || leverageInput.value <= 0) {
                leverageInput.value = maxLeverage;
            }
        });
    }

    if (!isNaN(stopPrice) && !isNaN(entryPrice)) {
        if (stopPrice < entryPrice) {
            button.classList.remove('btn-danger', 'btn-secondary', 'disabled');
            button.classList.add('btn-success');
            button.textContent = 'Open Long';

            tradeInfo.classList.remove('d-none');

            leverageInput.disabled = false;

            // Fetch and update leverage input
            fetchMaxLeverage(tool, updateLeverage);

        } else if (stopPrice > entryPrice) {
            button.classList.remove('btn-success', 'btn-secondary', 'disabled');
            button.classList.add('btn-danger');
            button.textContent = 'Open Short';

            leverageInput.disabled = true;

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
updateEntryFormState();


function saveRisk() {
    const riskText = document.getElementById('risk-value');
    const risk = parseFloat(document.getElementById('newRisk').value);

    console.log(`New risk value: ${risk}`); // Debugging statement

    if (!isNaN(risk)) {
        // Send the request to FastAPI to update the risk value in the database
        fetch('/update-risk/', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ risk: risk }),
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                const updatedRisk = parseFloat(data.risk).toFixed(1);
                riskText.textContent = `${updatedRisk}%`;
            })
            .catch(error => {

            });

    } else {
        alert('Please enter a valid number for risk.');
    }
}

// Save risk button
document.getElementById('saveRisk').addEventListener('click', saveRisk);
