setTimeout(function() {
    bootstrap.Alert.getOrCreateInstance(document.querySelector(".alert")).close();
}, 3000)

document.querySelectorAll('.edit-btn').forEach(function(button) {
    button.addEventListener('click', function() {
        var id = this.value;
        var name = this.closest('.categories').querySelector('.cat_name').textContent;

        document.getElementById("catid").value = id;
        document.getElementById("editCatName").value = name;

    });
});

function clear_input() {
    document.getElementById("edit_cat").reset();
}

document.addEventListener('DOMContentLoaded', function () {
    var myModal = new bootstrap.Modal(document.getElementById('exampleModal'));

    myModal._element.addEventListener('hidden.bs.modal', function () {
        clear_input();
    });
});


$(document).ready(function () {
    var oTable = $('#prod_table_list').DataTable({
        // Your DataTable options here
        scrollX: true,
        scrollY: '338px',
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
        }
    });

    // Handle dropdown change event
    $('#category_list').on('change', function () {
        var selectedValue = $(this).val();
        console.log(selectedValue)

        // Apply the selected filter to the DataTable
        if (selectedValue === 'all') {
            oTable.search('').columns().search('').draw(); // all data from table
        } else {
            oTable.column(4).search(selectedValue).draw();
        }
    });
});

$(document).ready(function () {
    var oTable = $('#cat_list').DataTable({
        // Your DataTable options here
        searching: false,
        scrollX: true,
        scrollY: '205px',
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
    });
});
