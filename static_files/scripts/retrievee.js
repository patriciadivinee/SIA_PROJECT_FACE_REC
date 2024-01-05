$(document).ready(function () {
    // Handle the click event on the eye icon button
    $('.btn-info').on('click', function () {
        var empId = $(this).data('emp-id');
        // Perform an AJAX request to get employee details
        $.ajax({
            url: '/employee_details/' + empId, // Update the URL as per your Django URL configuration
            type: 'GET',
            success: function (data) {
                // Update the modal body with the employee details
                $('#employeeDetailsBody').html(data);
                // Show the modal
                $('#EmployeeModal').modal('show');
            },
            error: function (error) {
                console.log('Error fetching employee details:', error);
            }
        });
    });
});

function confirmDelete(empId) {
    Swal.fire({
        title: 'Are you sure?',
        text: 'You won\'t be able to revert this!',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Yes, delete it!'
    }).then((result) => {
        if (result.isConfirmed) {
            // If the user clicks "Yes", redirect to the delete URL
            window.location.href = `/delete_permanently/${empId}`;
        }
    });
}

function confirmRetrieve(empId) {
    Swal.fire({
        title: 'Are you sure?',
        text: 'This will retrieve the employee account!',
        icon: 'info',
        showCancelButton: true,
        confirmButtonColor: '#28a745',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Yes, retrieve it!'
    }).then((result) => {
        if (result.isConfirmed) {
            // If the user clicks "Yes", redirect to the retrieve URL
            window.location.href = `/retrieve/${empId}`;
        }
    });
}

$(document).ready(function() {
    var oTable = $('#prod_list').DataTable({
         // Disable DataTables search input
        "columnDefs": [
            { "orderable": false, "targets": 7 }
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
  
        //"dom": '<"top"f>rt<"bottom"flp><"clear">', // Place the custom search input at the top
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
  
  setTimeout(function() {
    bootstrap.Alert.getOrCreateInstance(document.querySelector(".alert")).close();
  }, 3000)
  
  function clearText() {
    document.getElementById('search_input').value = '';
    document.getElementById("clear_btn").style.display = "none";
  }