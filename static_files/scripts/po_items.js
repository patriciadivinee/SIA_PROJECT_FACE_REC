$(document).ready(function() {
    $('#toReceived').on('click', function() {
      // Toggle the display property of the target element
      $('.receivedQty').toggle();
      $('.itemStatus').toggle();
      $('#CancelReceive').toggle();
      $('#completePO').toggle();
      $('#total').attr('colspan', 1);
      $('#billtxt').attr('colspan', 5);
      $('#amnt').attr('colspan', 1);
      $('#toReceived').hide();
      $('#printBtn').hide();
    });
});

$(document).ready(function() {
    $('#CancelReceive').on('click', function() {
      // Toggle the display property of the target element
      $('.receivedQty').hide();
      $('.itemStatus').hide();
      $('#CancelReceive').hide();
      $('#completePO').hide();
      $('#total').attr('colspan', 1);
      $('#billtxt').attr('colspan', 4);
      $('#amnt').attr('colspan', 2);
      $('#toReceived').toggle();
      $('#printBtn').toggle();
    });
});
