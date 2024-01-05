$(document).ready(function() {
    var oTable = $('#sup_list').DataTable({
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
    $.fn.dataTable.ext.search.push(
      function(settings, searchData, index, rowData, counter) {
          // Get the search value
          var searchTerm = oTable.column(7).search();

          // If the search term is empty, no filtering is needed
          if (searchTerm === '') {
              return true;
          }

          // Remove HTML tags from the data before searching
          var columnContent = oTable.cell(index, 7).nodes().to$().html();

          // Perform the search on the cleaned data
          return columnContent.includes(searchTerm);
      }
  );

  $('#category_list').on('change', function () {
      var selectedValue = $(this).val();
      console.log(selectedValue)
  
      // Apply the selected filter to the DataTable
      if (selectedValue === 'all') {
          oTable.search('').columns().search('').draw(); // all data from table
      } else {
          oTable.columns(7).search(selectedValue).draw();
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