document.addEventListener('DOMContentLoaded', function() {
    // Assign our HTML elements to JS variables
    var tradeSelector = document.getElementById('trade-type-selector');
    var submitButton = document.getElementById('trade-submit-btn');
    var reminder = document.getElementById('reminder');
    var tradeValueField = document.getElementById('trade-value-field');
    var funds = parseFloat(document.getElementById('funds').innerHTML);

    // "Confirm Trade" button is disabled by default
    submitButton.disabled = true;

    // When the user selects either the "Buy" or "Sell" option, the button is enabled and reminder message disappears
    // If they select the placeholder option again, it will be disabled again and reminder will re-appear
    tradeSelector.addEventListener('change', () => {
        if (tradeSelector.value == 'null') {
            submitButton.disabled = true;
            reminder.innerHTML = 'Please select a trade option from the drop-down menu above'
            reminder.style.display = 'block'
        }
        else if ((tradeSelector.value == 'BUY') && (tradeValueField.value > funds)) {
            submitButton.disabled = true;
            reminder.innerHTML = 'You have insufficient funds to make this purchase';
            reminder.style.display = 'block';
        }
        else {
            submitButton.disabled = false;
            reminder.style.display = 'none';
        }
    });

    // Check if user has enough funds before trying to make a 'Buy' transaction, disable button if they enter an amount
    // greater than their available funds
    tradeValueField.addEventListener('input', () => {
        if ((tradeSelector.value == 'BUY') && (tradeValueField.value > funds)) {
            submitButton.disabled = true;
            reminder.innerHTML = 'You have insufficient funds to make this purchase';
            reminder.style.display = 'block';
        }
        else if (tradeSelector.value == 'null') {
            submitButton.disabled = true;
            reminder.innerHTML = 'Please select a trade option from the drop-down menu above'
            reminder.style.display = 'block'
        }
        else if ((tradeSelector.value == 'BUY') && (tradeValueField.value <= funds)) {
            submitButton.disabled = false;
            reminder.style.display = 'none';
            reminder.innerHTML = 'Please select a trade option from the drop-down menu above';

        }
    });



});