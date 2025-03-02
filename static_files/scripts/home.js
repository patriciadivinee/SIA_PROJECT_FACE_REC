var ctx1 = document.getElementById('stockPieChart').getContext('2d');
    var labels1 = JSON.parse('{{ labels1|escapejs }}');
    var data1 = JSON.parse('{{ data1|escapejs }}');
    var colors1 = JSON.parse('{{ colors1|escapejs }}');

    var chartData1 = {
        labels: labels1,
        datasets: [{
            label: 'Stocks by Category',
            data: data1,
            backgroundColor: colors1,
        }]
    };

    var myPieChart1 = new Chart(ctx1, {
        type: 'pie',
        data: chartData1,
        options: {
            // Additional options for the first chart
        }
    });

    var ctx2 = document.getElementById('additionalChart').getContext('2d');
    var labels2 = JSON.parse('{{ labels2|escapejs }}');
    var data2 = JSON.parse('{{ data2|escapejs }}');
    var colors2 = JSON.parse('{{ colors2|escapejs }}');

    var chartData2 = {
        labels: labels2,
        datasets: [{
            label: 'Products by Category',
            data: data2,
            backgroundColor: colors2,
        }]
    };

    var myBarChart = new Chart(ctx2, {
        type: 'pie', // Change to 'bar' or appropriate chart type for the second chart
        data: chartData2,
        options: {
            // Additional options for the second chart
        }
    });

    var ctx3 = document.getElementById('productQtyChart').getContext('2d');
    var labels3 = JSON.parse('{{ labels3|escapejs }}');
    var data3 = JSON.parse('{{ data3|escapejs }}');
    var colors3 = JSON.parse('{{ colors3|escapejs }}');

    var chartData3 = {
        labels: labels3,
        datasets: [{
            label: "Product Quantity",
            data: data3,
            backgroundColor: colors3, // Use the provided colors for bars
        }]
    };

    var myBarChart = new Chart(ctx3, {
        type: 'bar',
        data: chartData3,
        options: {
            scales: {
                y: {
                    beginAtZero: true // Ensure the y-axis starts from zero
                }
            }
            // Additional options for the bar chart (if needed)
        }
    });
    var ctx = document.getElementById('topRequestedItemsChart').getContext('2d');
    var labels = JSON.parse('{{ labels | escapejs }}');
    var data = JSON.parse('{{ data | escapejs }}');

    var topRequestedItemsChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Top Requested Items (Last 30 Days)',
                data: data,
                backgroundColor: 'rgba(75, 192, 192, 0.8)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
    var ctxTotalEmployees = document.getElementById('totalEmployeesChart').getContext('2d');
    var totalEmployeesData = JSON.parse('{{ total_employees|escapejs }}');

    var totalEmployeesChart = new Chart(ctxTotalEmployees, {
        type: 'bar',
        data: {
            labels: ['Number of Staffs'],
            datasets: [{
                label: 'Number of Staffs',
                data: [totalEmployeesData],
                backgroundColor: 'rgba(255, 99, 132, 0.8)',
                borderColor: 'rgba(255, 99, 132, 1)',
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
    var ctxActiveInactive = document.getElementById('activeInactiveEmployeesChart').getContext('2d');
    var activeEmployeesData = JSON.parse('{{ active_employees|escapejs }}');
    var inactiveEmployeesData = JSON.parse('{{ inactive_employees|escapejs }}');

    var activeInactiveEmployeesChart = new Chart(ctxActiveInactive, {
        type: 'bar',
        data: {
            labels: ['Active Employees', 'Inactive Employees'],
            datasets: [{
                data: [activeEmployeesData, inactiveEmployeesData],
                backgroundColor: ['rgba(75, 192, 192, 0.8)', 'rgba(255, 99, 132, 0.8)'],
                borderColor: ['rgba(75, 192, 192, 1)', 'rgba(255, 99, 132, 1)'],
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });