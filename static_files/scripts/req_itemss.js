function markReceived(reqId) {
    // AJAX call to mark requisition as received
    $.ajax({
        url: "{% url 'mark_received' %}", // Replace with your URL for marking received
        type: 'POST',
        data: {
            req_id: reqId,
            action: 'receive' // Indicate action as 'receive'
        },
        success: function (response) {
            // Reload or update the necessary content on success
            window.location.reload(); // Reload the page for simplicity; you can update content dynamically instead
        },
        error: function (error) {
            console.error('Error:', error);
            // Handle errors if necessary
        }
    });
}

function printToPDF() {
    // Select the element to be converted to PDF
    const element = document.getElementById("content");

    // Use html2pdf library
    html2pdf(element);
}