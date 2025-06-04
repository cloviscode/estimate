function addMaterialRow() {
    const tbody = document.getElementById('materials');
    const newRow = tbody.querySelector('.material-row').cloneNode(true);
    const rowCount = tbody.children.length + 1;
    
    newRow.querySelectorAll('input').forEach(input => {
        input.value = '';
        input.addEventListener('input', updateRowTotal);
    });
    newRow.querySelectorAll('select').forEach(select => select.selectedIndex = 0);
    newRow.querySelector('td:first-child').textContent = rowCount;
    newRow.querySelector('.total').textContent = 'XAF 0';
    
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

function formatXAF(amount) {
    return `XAF ${amount.toLocaleString('fr-FR', { maximumFractionDigits: 0 })}`;
}

function updateRowTotal(event) {
    const row = event.target.closest('tr');
    const quantity = parseFloat(row.querySelector('input[name="quantity[]"]').value) || 0;
    const unitPrice = parseFloat(row.querySelector('input[name="unit_price[]"]').value) || 0;
    const total = quantity * unitPrice;
    row.querySelector('.total').textContent = formatXAF(total);
    updateGrandTotal();
}

function addAdditionalCost() {
    const table = document.getElementById('additional-costs');
    const newRow = table.querySelector('.additional-cost-row').cloneNode(true);
    newRow.querySelectorAll('input').forEach(input => {
        input.value = '';
        if (input.name === 'cost_amount[]') {
            input.addEventListener('input', updateGrandTotal);
        }
    });
    table.appendChild(newRow);
}

function removeAdditionalCost(button) {
    const table = document.getElementById('additional-costs');
    if (table.children.length > 2) {  // Keep header row and at least one cost row
        button.closest('tr').remove();
        updateGrandTotal();
    }
}

function updateGrandTotal() {
    const materialTotals = Array.from(document.querySelectorAll('.total'))
        .map(el => parseFloat(el.textContent.replace('XAF', '').replace(/\s/g, '').replace(/\./g, '').replace(',', '.')) || 0);
    const materialTotal = materialTotals.reduce((sum, val) => sum + val, 0);
    
    const laborCost = parseFloat(document.querySelector('input[name="labor_cost"]').value) || 0;
    
    const additionalCosts = Array.from(document.querySelectorAll('input[name="cost_amount[]"]'))
        .map(input => parseFloat(input.value) || 0)
        .reduce((sum, val) => sum + val, 0);

    const grandTotal = materialTotal + laborCost + additionalCosts;
    document.getElementById('grandTotal').textContent = formatXAF(grandTotal);
}

// Add event listeners when document loads
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('input[name="quantity[]"], input[name="unit_price[]"]')
        .forEach(input => input.addEventListener('input', updateRowTotal));
    document.querySelector('input[name="labor_cost"]')
        .addEventListener('input', updateGrandTotal);
});