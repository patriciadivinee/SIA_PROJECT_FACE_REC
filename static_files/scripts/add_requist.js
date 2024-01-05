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
    deleteCell.innerHTML = '<button class="btn btn-sm btn-danger" onclick="deleteRow(this)"><i class="fa-solid fa-trash-can"></i></button>';
    deleteCell.querySelector('button').disabled = false; // Enable the delete button

    // Pass the product ID to the deleteRow function for re-enabling the corresponding "Add" button
    deleteCell.querySelector('button').setAttribute('data-id', productId);
}


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

document.getElementById("add_req").addEventListener("click", function (event) {
    event.preventDefault();

    // Show a confirmation dialog
    var confirmation = confirm("Do you want to create this requisition?");

    // Check user's choice in the confirmation dialog
    if (confirmation) {
        if (!validateInputs()) {
            return; // Stop execution if validation fails
        }

        var table = $('#destinationTable');
        var idColumnIndex = 0;
        var brandInputClassName = 'req_qty';

        var tableContent = {};
        var edd = $('#edd').val();
        var empId = 1; // Replace this with the actual emp_id

        table.find('tbody tr').each(function (i) {
            var cellsInCurrentRow = $(this).find('td');
            var rowContent = {};

            var idCellValue = cellsInCurrentRow.eq(idColumnIndex).text();
            var brandInput = $(this).find('.' + brandInputClassName);
            var brandInputValue = brandInput.val();

            rowContent['id'] = idCellValue;
            rowContent['qty'] = brandInputValue;

            tableContent['row' + (i + 1)] = rowContent;
        });

        // Include empId in the payload sent to Django
        var requestData = {
            'table_data': tableContent,
            'edd': edd,
            'emp_id': empId  // Add emp_id to the payload
        };

        $.ajax({
            url: '/add_req',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(requestData), // Include emp_id in the payload
            success: function (response) {
                console.log(response);
                // Handle the response from Django if needed
            },
            error: function (error) {
                console.error(error);
            }
        });
    } else {
        // If user clicks 'Cancel' (false), stay on the page or perform other actions
        // For example, you can return to the previous page:
        /*window.history.back();*/
    }
});

function validateInputs() {
    var edd = document.getElementById('edd').value;
    var today = new Date();

    if (edd === '') {
        alert('Please enter the Estimated Date of Delivery');
        return false;
    }

    var eddDate = new Date(edd);

    if (isNaN(eddDate.getTime())) {
        alert('Please enter a valid date');
        return false;
    }

    if (eddDate <= today) {
        alert('Please enter a date onward');
        return false;
    }

    var qtyInputs = document.getElementsByClassName('req_qty');
    var rows = document.getElementById('destinationTable').getElementsByTagName('tr');

    if (rows.length <= 1) {
        alert('Please add at least one product to the requisition');
        return false;
    }

    var shouldUpdateDatabase = false;
    var updateData = [];

    for (var i = 0; i < qtyInputs.length; i++) {
        var quantity = parseInt(qtyInputs[i].value);
        var Inv_QOH = parseInt(qtyInputs[i].parentNode.previousElementSibling.textContent); // Fetch Inv_QOH from the table

        if (isNaN(quantity) || quantity < 1) {
            alert('Please enter a valid quantity greater than 0');
            return false;
        }

        if (quantity >= Inv_QOH) {
            // Quantity greater than or equal to QOH - proceed with database update
            shouldUpdateDatabase = true;
            updateData.push({
                productIndex: i + 1,
                quantity: quantity
            });
        } 
    }

    if (shouldUpdateDatabase) {
       
        fetch('/updateRequisition', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(updateData)
        })
            .then(response => {
                // Handle response from the server
                // Perhaps show a success message or perform additional actions
                console.log('Requisition updated successfully');
            })
            .catch(error => {
                console.error('Error updating requisition:', error);
                // Handle errors here
            });
    }

    return true;
}


function validateAndRedirect() {
    if (!validateInputs()) {
        return false; // Stop execution if validation fails
    }

    // Validation successful, redirect to another page
    window.location.href = '/employee/requisition/pending';
    // Replace '/your_redirect_url/' with the URL of the page you want to redirect to
    return true; // Return true to indicate successful validation
}

// Attach click event handler to the button
document.getElementById('add_req').addEventListener('click', function (event) {
    event.preventDefault(); // Prevent the default form submission

    // Call validateAndRedirect function on button click
    var validationPassed = validateAndRedirect();
    if (!validationPassed) {
        // Validation failed, stay on the current page
        console.log('Validation failed. Stay on the current page.');
    }
});

$(document).ready(function() {
    var oTable = $('#prod_list').DataTable({
         // Disable DataTables search input
        "columnDefs": [
            { "orderable": false, "targets": 4 }
        ],
        "language": {
            'paginate': {
                'previous': '<span class="fa fa-chevron-left"></span>',
                'next': '<span class="fa fa-chevron-right"></span>'
            },
            "lengthMenu": '<div class="d-flex align-items-center">Display'+
              '<div class="input-group input-group-sm my-3 mx-2 p-0 border border-dark" style="border-radius: 20px;">'+
                '<select class="form-select border border-0" style="border-radius: 20px;">'+
                '<option value="5">5</option>'+
                '<option value="10">10</option>'+
                '<option value="20">20</option>'+
                '<option value="30">30</option>'+
                '<option value="50">50</option>'+
                '<option value="-1">All</option>'+
                '</select></div> Results</div>',
        },
  
              "initComplete": function(settings, json) {
                  // Bind existing input to DataTable search
                  $('#clear_btn').on('click', function() {
                    $('#search_input').val('');
                    $('#clear_btn').css('display', 'none');
  
                    oTable.search('').draw();
                });
  
                  $('#search_input').on('keyup change', function() {
                    oTable.search(this.value).draw();
                  });
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

  $(document).ready(function() {
    // Get the height of the source div
    var sourceHeight = $('#products').height();

    // Set the minimum height of the target div
    $('#to_purchase').css('min-height', sourceHeight + 32 + 'px');
});