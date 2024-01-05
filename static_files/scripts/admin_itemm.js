function markReceived() {
    // AJAX call to mark requisition as received
    let reqId = document.getElementById("receivedBtn").value;
    console.log(reqId);

    $.ajax({
        url: "/requisition/received", // Replace with your URL for marking received
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