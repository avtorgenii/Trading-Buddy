document.addEventListener('DOMContentLoaded', function () {
            const editableCells = document.querySelectorAll('.editable');
            const editModal = new bootstrap.Modal(document.getElementById('editModal'));
            const editValueInput = document.getElementById('editValue');
            const editTradeIdInput = document.getElementById('editTradeId');
            const editFieldInput = document.getElementById('editField');
            const saveChangesButton = document.getElementById('saveChanges');

            editableCells.forEach(cell => {
                cell.addEventListener('click', function () {
                    const tradeId = this.getAttribute('data-trade-id');
                    const field = this.getAttribute('data-field');
                    const currentValue = this.textContent.trim();

                    editTradeIdInput.value = tradeId;
                    editFieldInput.value = field;
                    editValueInput.value = currentValue;

                    editModal.show();
                });
            });

            saveChangesButton.addEventListener('click', function () {
                const tradeId = editTradeIdInput.value;
                const field = editFieldInput.value;
                const newValue = editValueInput.value;

                fetch('/update-trade/', {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ trade_id: tradeId, field: field, value: newValue }),
                })
                .then(response => response.json())
                .then(data => {
                    console.log('Trade updated successfully:', data);
                    // Update the cell with the new value
                    document.querySelector(`.editable[data-trade-id="${tradeId}"][data-field="${field}"]`).textContent = newValue;
                    editModal.hide();
                })
                .catch(error => {
                    console.error('Error updating trade:', error);
                });
            });
        });