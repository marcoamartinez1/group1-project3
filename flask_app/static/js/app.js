let fetchedData = {};
let selectedOperators = [];

document.addEventListener('DOMContentLoaded', function() {
    fetch('/operators')
        .then(response => response.json())
        .then(data => {
            var operatorCheckboxes = document.getElementById('operator-checkboxes');
            data.forEach(operator => {
                var checkboxDiv = document.createElement('div');
                checkboxDiv.innerHTML = `<input type="checkbox" name="operators" value="${operator}" checked> <label>${operator}</label>`;
                operatorCheckboxes.appendChild(checkboxDiv);
            });
            fetchAllAverages(data);
        });
});

function fetchAllAverages(operators) {
    let promises = operators.map(operator => {
        const encodedOperator = encodeURIComponent(operator);
        return fetch(`/averages?operator=${encodedOperator}`)
            .then(response => response.json())
            .then(data => {
                fetchedData[operator] = data;
            });
    });

    Promise.all(promises).then(updateChart);
}

function updateChart() {
    var selectedMetrics = [];
    document.querySelectorAll('input[name="metrics"]:checked').forEach(checkbox => {
        selectedMetrics.push(checkbox.value);
    });

    selectedOperators = [];
    document.querySelectorAll('input[name="operators"]:checked').forEach(checkbox => {
        selectedOperators.push(checkbox.value);
    });

    var data = [];
    var colors = {
        'AT&T': 'blue',
        'T-Mobile': 'magenta',
        'Verizon': 'red'
        // Add more operators and their colors as needed
    };

    selectedMetrics.forEach(metric => {
        var xValues = [];
        var yValues = [];
        var colorValues = [];
        selectedOperators.forEach(operator => {
            xValues.push(operator);
            yValues.push(fetchedData[operator][metric]);
            colorValues.push(colors[operator] || '#007bff'); // Default color if operator not found
        });

        var trace = {
            x: xValues,
            y: yValues,
            type: 'bar',
            name: metric,
            marker: { color: colorValues },
            text: yValues.map(value => value.toFixed(2)),
            textposition: 'auto'
        };

        data.push(trace);
    });

    var layout = {
        title: 'Averages Comparison',
        barmode: 'stack',
        xaxis: { title: 'Operators' },
        yaxis: { title: 'Values' },
        height: 600,
        width: 900
    };

    Plotly.newPlot('chart-area', data, layout);
}
