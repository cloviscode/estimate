function addMaterialRow() {
    const tbody = document.getElementById('materials');
    const newRow = tbody.querySelector('.material-row').cloneNode(true);
    const rowCount = tbody.children.length + 1;
    
    // Reset input values
    newRow.querySelectorAll('input').forEach(input => {
        input.value = '';
        input.addEventListener('input', updateRowTotal);
    });
    newRow.querySelectorAll('select').forEach(select => select.selectedIndex = 0);
    newRow.querySelector('td:first-child').textContent = rowCount;
    newRow.querySelector('.total').textContent = '$0.00';
    
    tbody.appendChild(newRow);
}

function removeMaterialRow(button) {
    if (document.getElementById('materials').children.length > 1) {
        button.closest('tr').remove();
        updateRowNumbers();
        updateGrandTotal();
    }
}

function updateRowNumbers() {
    const rows = document.getElementById('materials').children;
    Array.from(rows).forEach((row, index) => {
        row.querySelector('td:first-child').textContent = index + 1;
    });
}

function updateRowTotal(event) {
    const row = event.target.closest('tr');
    const quantity = parseFloat(row.querySelector('input[name="quantity[]"]').value) || 0;
    const unitPrice = parseFloat(row.querySelector('input[name="unit_price[]"]').value) || 0;
    const total = quantity * unitPrice;
    row.querySelector('.total').textContent = `$${total.toFixed(2)}`;
    updateGrandTotal();
}

function updateGrandTotal() {
    const totals = Array.from(document.querySelectorAll('.total'))
        .map(el => parseFloat(el.textContent.replace('$', '')) || 0);
    const grandTotal = totals.reduce((sum, val) => sum + val, 0);
    const laborCost = parseFloat(document.querySelector('input[name="labor_cost"]').value) || 0;
    document.getElementById('grandTotal').textContent = `$${(grandTotal + laborCost).toFixed(2)}`;
}

// Add event listeners when document loads
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('input[name="quantity[]"], input[name="unit_price[]"]')
        .forEach(input => input.addEventListener('input', updateRowTotal));
    document.querySelector('input[name="labor_cost"]')
        .addEventListener('input', updateGrandTotal);
});
