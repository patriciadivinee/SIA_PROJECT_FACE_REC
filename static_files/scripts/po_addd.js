$("#buttones").click(function (event) {
    event.preventDefault();

    var id = $('#search_id').val().trim();

    if (id !== '') {
        $.ajax({
            type: 'POST',
            url: '/supplier/search',  // Ensure this URL matches your Django URL configuration
            data: {
                'search_id': id,
                'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val(),
            },
            dataType: 'json',
            success: function (data) {
                if ('error' in data) {
                    window.alert('Error: Product not found');
                } else {
                    // Assuming data is a list of dictionaries
                    var tableBody = $('#resultTable tbody');
                    tableBody.empty(); // Clear existing rows

                    for (var i = 0; i < data.length; i++) {
                        var productData = data[i];

                        // Create a new row for each product
                        var newRow = '<tr>' +
                            '<td class="marquee">' + productData.Ide + '</td>' +
                            '<td class="marquee">' + productData.brand + '</td>' +
                            '<td class="marquee">' + productData.name + '</td>' +
                            '<td class="marquee">' + productData.desc + '</td>' +
                            '<td class="marquee">' + productData.price + '</td>' +
                            '<td class="marquee">' + productData.packsize + '</td>' +
                            '<td>' +
                            '<button type="button" data-id=' + productData.Ide + ' class="btn btn-sm btn-primary" onclick="transferData(this, ' + productData.Ide + ')">' +
                            '<i class="fa-solid fa-plus"></i>' +
                            '</button>' +
                            '</td>' +
                            '</tr>';

                        // Append the new row to the table body
                        tableBody.append(newRow);
                    }
                }
            }
        });
    } else {
        window.alert('Select supplier');
    }
});
function deleteRow(button) {
  // Get the parent row of the clicked delete button
  var rowToDelete = button.parentNode.parentNode;

  // Remove the row from the table
  rowToDelete.remove();

  // Re-enable the corresponding "Add" button in the source table
  var productId = button.getAttribute('data-id');
  var addButton = document.querySelector('button[data-id="' + productId + '"]');
  if (addButton) {
      addButton.disabled = false;
  }
}
function transferData(button, productId) {
  // Get the parent row of the clicked button
  var sourceRow = button.parentNode.parentNode;

  // Get reference to destination table
  var destinationTable = document.getElementById("destinationTable");
  var destinationTbody = destinationTable.querySelector('tbody');
  button.disabled = true;

  // Create a new row in the destination table
  var newRow = destinationTbody.insertRow();

  // Loop through each cell in the source row and copy data to the destination row
  for (var i = 0; i < sourceRow.cells.length - 1; i++) {
      var cellValue = sourceRow.cells[i].innerHTML;

      // Create a new cell in the destination row
      var newCell = newRow.insertCell();

      // Set the value of the new cell to the value of the corresponding cell in the source row
      newCell.innerHTML = cellValue;
  }

  // Add a new cell for "Input Number" with an input field
  var inputCell = newRow.insertCell();
  inputCell.innerHTML = '<input type="number" class="req_qty" value="" min="1" style="width: 50px" required>';


  // Add a new cell for "Delete" button
  var deleteCell = newRow.insertCell();
  deleteCell.innerHTML = '<button class="btn btn-danger btn-sm" onclick="deleteRow(this)"><i class="fa-regular fa-trash-can"></i></button>';
  deleteCell.querySelector('button').disabled = false; // Enable the delete button

  // Pass the product ID to the deleteRow function for re-enabling the corresponding "Add" button
  deleteCell.querySelector('button').setAttribute('data-id', productId);
}
function validateInputs() {
// Get all quantity input elements
var qtyInputs = document.getElementsByClassName('req_qty');

// Check if there are no products in the requisition
if (qtyInputs.length === 0) {
  alert('Please add at least one product to the requisition');
  return false;
}

// Loop through each quantity input
for (var i = 0; i < qtyInputs.length; i++) {
  var qtyInput = qtyInputs[i];

  // Check if the quantity is empty or zero or below zero
  var quantity = parseInt(qtyInput.value, 10);

  if (isNaN(quantity) || quantity <= 0) {
    alert('Please enter a valid quantity greater than zero for all products');
    return false;
  }
}

// If the loop completes, all inputs are valid
return true;
}

$("#add_po").click(function (event) {
event.preventDefault();

if (!validateInputs()) {
    return; // Stop execution if validation fails
}

var table = $('#destinationTable');
var idColumnIndex = 0;
var brandInputClassName = 'req_qty';

var tableContent = [];
var edd = $('#edd').val();
var sup_id = $('#search_id').val().trim(); ; // Replace this with the actual sup_id

table.find('tbody tr').each(function () {
    var cellsInCurrentRow = $(this).find('td');
    var rowContent = {};

    var idCellValue = cellsInCurrentRow.eq(idColumnIndex).text();
    var brandInput = $(this).find('.' + brandInputClassName);
    var brandInputValue = brandInput.val();

    tableContent.push({
      'id': idCellValue,
      'qty': brandInputValue
  });

});

// Include sup_id in the payload sent to Django
var requestData = {
    'table_data': tableContent,
    'edd': edd,
    'sup_id': sup_id  // Add sup_id to the payload
};

$.ajax({
    url: '/purchase/order/add',
    type: 'POST',
    contentType: 'application/json',
    data: JSON.stringify(requestData), // Include sup_id in the payload
    success: function (response) {
      console.log(response);
      // Check if the response indicates success
      if ('message' in response && response.message === 'Purchase Order added successfully') {
          // Redirect to the PO.html page
          window.location.href = '/purchase/order/pending';
      } else {
          // Handle other cases if needed
          console.error('Unexpected response:', response);
      }
  },
  error: function (error) {
      console.error(error);
  }
});
});

function hasText() {
    let text = document.getElementById("search_input").value;
    let clearBtn = document.getElementById("clear_btn");
    
    if (text.trim() !== "") {
        clearBtn.style.display = "block";
    } else {
        clearBtn.style.display = "none";
    }
  }

  function clearText() {
    document.getElementById('search_input').value = '';
    document.getElementById("clear_btn").style.display = "none";
  }