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
    takeInputs.forEach(input => input.addEventListener('change', checkAndSubmit));
    stoeInput.addEventListener('change', checkAndSubmit);
    stopPriceInput.addEventListener('change', checkAndSubmit);
    entryPriceInput.addEventListener('change', checkAndSubmit);
    leverageInput.addEventListener('change', checkAndSubmit);
    toolSelect.addEventListener('change', checkAndSubmit);

    function checkAndSubmit() {
        console.log("Processed Trade Data")
        const takes = Array.from(takeInputs).map(input => parseFloat(input.value.replace(",", ".")));
        const stoe = parseInt(stoeInput.value);
        const stopPrice = parseFloat(stopPriceInput.value.replace(",", "."));
        const entryPrice = parseFloat(entryPriceInput.value.replace(",", "."));
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
                body: JSON.stringify({ tool: tool, entry_p: entryPrice, stop_p: stopPrice, leverage: leverage, take_ps: takes, stoe: stoe, volume: 0 }),
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


                    document.getElementById('volume-value').textContent = data.volume;
                    document.getElementById('margin-value').textContent = data.margin;
                    document.getElementById('loss-value').textContent = data.potential_loss;
                    document.getElementById('profit-value').textContent = data.potential_profit;
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


function updateEntryFormState() {
    console.log("Updated form state")
    const stopPriceInput = document.getElementById('stopp').value.replace(",", ".");
    const entryPriceInput = document.getElementById('entryp').value.replace(",", ".");
    const stopPrice = parseFloat(stopPriceInput);
    const entryPrice = parseFloat(entryPriceInput);
    const button = document.getElementById('opent');
    const tradeInfo = document.getElementById('tradeinfo');
    const leverageInput = document.getElementById('leverage');
    const tool = document.getElementById('tool').value;

    console.log('stopPrice:', stopPrice, 'entryPrice:', entryPrice); // Debugging logs

    function fetchMaxLeverage(tool, callback) {
        fetch('/set-default-leverage/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ tool: tool, long_side: entryPrice > stopPrice })
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                callback(data.max_leverage);
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

            tradeInfo.classList.remove('d-none');

            leverageInput.disabled = false;

            // Fetch and update leverage input
            fetchMaxLeverage(tool, updateLeverage);
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

// Event listeners for blur and input events
const entryInput = document.getElementById('entryp');
const stopInput = document.getElementById('stopp');

entryInput.addEventListener('change', updateEntryFormState);
stopInput.addEventListener('change', updateEntryFormState);

// Initial call to set the correct state of the button
updateEntryFormState();


// Adding/Removing tools
document.getElementById('saveAddTool').addEventListener('click', function() {
            const toolName = document.getElementById('toolName').value;
            const starred = document.getElementById('starred').checked;

            if (toolName) {
                fetch('/add-new-tool/', {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ tool_name: toolName, starred: starred })
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

        document.getElementById('saveRemoveTool').addEventListener('click', function() {
            const toolName = document.getElementById('remove_tool').value;

            if (toolName) {
                fetch('/remove-tool/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ tool_name: toolName })
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


// Account Config
function saveAccountData() {
    const riskText = document.getElementById('risk-value');
    const risk = parseFloat(document.getElementById('newRisk').value.replace(",", "."));

    const depositText = document.getElementById('deposit-value');
    const deposit = parseFloat(document.getElementById('newDeposit').value.replace(",", "."));


    if (!isNaN(risk) && !isNaN(deposit)) {
        // Send the request to FastAPI to update the account data in the database
        fetch('/update-account-data/', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ risk: risk, deposit: deposit }),
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                riskText.textContent = `${risk.toFixed(2)}%`;
                depositText.textContent = `${deposit.toFixed(2)}`;



            })
            .catch(error => {

            });

    } else {
        alert('Please enter a valid number for both params.');
    }
}

// Save account data button
document.getElementById('saveAccountData').addEventListener('click', saveAccountData);


// Placing order
document.addEventListener('DOMContentLoaded', function () {
    const opentButton = document.getElementById('opent');
    const submitManualVolumeButton = document.getElementById('submitManualVolume');

    opentButton.addEventListener('click', function () {
        const tool = document.getElementById('tool').value;
        const entryPrice = parseFloat(document.getElementById('entryp').value.replace(",", "."));
        const triggerPrice = parseFloat(document.getElementById('triggerp').value.replace(",", "."));
        const stopPrice = parseFloat(document.getElementById('stopp').value.replace(",", "."));
        const leverage = parseInt(document.getElementById('leverage').value);
        const stoe = parseInt(document.getElementById('stoe').value);
        const volume = parseFloat(document.getElementById('volume-value').textContent);  // Changed from value to textContent

        // Get all take prices
        const takeInputs = document.querySelectorAll('#form-container input[id^="takep"]');
        const takes = Array.from(takeInputs).map(input => parseFloat(input.value.replace(",", ".")));

        const data = {
            tool: tool,
            entryPrice: entryPrice,
            triggerPrice: triggerPrice,
            stopPrice: stopPrice,
            leverage: leverage,
            stoe: stoe,
            takes: takes,
            volume: volume
        };

        fetch('/place-trade/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                if (data.message === "Please enter volume manually") {
                    const manualVolumeModal = new bootstrap.Modal(document.getElementById('manualVolumeModal'));
                    manualVolumeModal.show();
                } else if (data.message === "Volume is too small") {
                    alert('Volume is too small. Cannot place trade.');
                } else {
                    // Refereshing page so trade would appear on pending
                    location.reload();
                }
            })
            .catch(error => {
                alert('Error placing trade', error);
            });
    });

    submitManualVolumeButton.addEventListener('click', function () {
        const manualVolume = parseFloat(document.getElementById('manualVolume').value);

        if (!isNaN(manualVolume)) {
            const tool = document.getElementById('tool').value;
            const entryPrice = parseFloat(document.getElementById('entryp').value.replace(",", "."));
            const triggerPrice = parseFloat(document.getElementById('triggerp').value.replace(",", "."));
            const stopPrice = parseFloat(document.getElementById('stopp').value.replace(",", "."));
            const leverage = parseInt(document.getElementById('leverage').value);
            const stoe = parseInt(document.getElementById('stoe').value);
            const takeInputs = document.querySelectorAll('#form-container input[id^="takep"]');
            const takes = Array.from(takeInputs).map(input => parseFloat(input.value.replace(",", ".")));

            const data = {
                tool: tool,
                entry_p: entryPrice,
                stop_p: stopPrice,
                leverage: leverage,
                stoe: stoe,
                take_ps: takes,
                volume: manualVolume
            };

            fetch('/process-trade-data/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            })
                .then(response => response.json())
                .then(data => {
                    console.log('Trade data processed successfully:', data);

                    // Update the information in the HTML
                    document.getElementById('volume-value').textContent = data.volume;
                    document.getElementById('margin-value').textContent = data.margin;
                    document.getElementById('loss-value').textContent = data.potential_loss;
                    document.getElementById('profit-value').textContent = data.potential_profit;

                    // Close the modal
                    const manualVolumeModal = bootstrap.Modal.getInstance(document.getElementById('manualVolumeModal'));
                    manualVolumeModal.hide();
                })
                .catch(error => {
                    console.error('Error processing trade data:', error);
                });
        } else {
            alert('Please enter a valid number for volume.');
        }
    });
});





// Cancelling trade
document.addEventListener('DOMContentLoaded', function () {
    const cancelTradeButtons = document.querySelectorAll('.cancel-trade-btn');

    cancelTradeButtons.forEach(button => {
        button.addEventListener('click', function () {
            const tool = this.getAttribute('data-tool');
            console.log('Cancelling trade for tool:', tool); // Debugging statement

            fetch('/cancel-trade/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ tool: tool }),
            })
                .then(response => response.json())
                .then(data => {
                    // Refreshing page so trade would disappear from pending
                    location.reload();
                })
                .catch(error => {
                    console.error('Error cancelling trade: ', error);
                    alert('Error cancelling trade');
                });
        });
    });
});




// Cancel levels
document.addEventListener('DOMContentLoaded', function () {
    const cancelButtons = document.querySelectorAll('.cancel-levels-btn');
    const cancelLevelsModal = new bootstrap.Modal(document.getElementById('cancelLevelsModal'));

    cancelButtons.forEach(button => {
        button.addEventListener('click', function () {
            const tool = this.getAttribute('data-tool');
            const posSide = this.getAttribute('data-pos-side');
            const overLabel = document.querySelector('label[for="over"]');

            if (posSide === 'LONG') {
                overLabel.textContent = 'Overlow:';
            } else {
                overLabel.textContent = 'Overhigh:';
            }

            document.getElementById('cancelationTool').value = tool;

            fetch(`/get-cancel-levels/${tool}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                // Update form fields with fetched data
                document.getElementById('over').value = data.over_level;
                document.getElementById('take').value = data.take_profit;
            })
            .catch(error => {
                console.error('Error fetching cancel levels:', error);
            });

            // Show the modal
            cancelLevelsModal.show();
        });
    });

    document.getElementById('saveCancelLevels').addEventListener('click', function () {
        const form = document.getElementById('cancelLevelsForm');
        const formData = new FormData(form);

        // Explicitly add the tool information
        formData.set('tool', document.getElementById('cancelationTool').value.replace(",", "."));

        const data = Object.fromEntries(formData.entries());


        fetch('/update-cancel-levels/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        })
            .then(response => response.json())
            .then(data => {
                console.log('Cancel levels updated successfully:', data);
                cancelLevelsModal.hide();
            })
            .catch(error => {
                console.error('Error updating cancel levels:', error);
            });
    });


});



// Comment and Emotional State
document.addEventListener('DOMContentLoaded', function () {
    console.log('DOM fully loaded and parsed');

    // Add Comment Button Click Event
    document.querySelectorAll('.add-comment-btn').forEach(button => {
        button.addEventListener('click', function () {
            console.log('Add Comment button clicked');
            const tool = this.getAttribute('data-tool');
            console.log('Tool:', tool);
            document.getElementById('commentTool').value = tool;
        });
    });

    // Save Comment Button Click Event
    document.getElementById('saveComment').addEventListener('click', function () {
        console.log('Save Comment button clicked');
        const tool = document.getElementById('commentTool').value;
        const comment = document.getElementById('comment').value;
        console.log('Tool:', tool, 'Comment:', comment);

        fetch('/update-comment/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ tool: tool, comment: comment }),
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                console.log('Comment updated successfully:', data);
                // Hide the modal
                const commentModal = bootstrap.Modal.getInstance(document.getElementById('commentModal'));
                commentModal.hide();
            })
            .catch(error => {
                console.error('Error updating comment:', error);
            });
    });

    // Add Emotion Button Click Event
    document.querySelectorAll('.add-emotion-btn').forEach(button => {
        button.addEventListener('click', function () {
            console.log('Add Emotion button clicked');
            const tool = this.getAttribute('data-tool');
            console.log('Tool:', tool);
            document.getElementById('emotionTool').value = tool;
        });
    });

    // Save Emotion Button Click Event
    document.getElementById('saveEmotion').addEventListener('click', function () {
        console.log('Save Emotion button clicked');
        const tool = document.getElementById('emotionTool').value;
        const emotionalState = document.getElementById('emotionalState').value;
        console.log('Tool:', tool, 'Emotional State:', emotionalState);

        fetch('/update-emotional-state/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ tool: tool, emotional_state: emotionalState }),
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                console.log('Emotional state updated successfully:', data);
                // Hide the modal
                const emotionModal = bootstrap.Modal.getInstance(document.getElementById('emotionModal'));
                emotionModal.hide();
            })
            .catch(error => {
                console.error('Error updating emotional state:', error);
            });
    });
});

