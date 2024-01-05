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