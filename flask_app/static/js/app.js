let fetchedData = {};
let selectedOperators = [];

// gets operator names to create interactive box
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

            var operatorSelect = document.getElementById('carrier-select');
            data.forEach(operator => {
                var option = document.createElement('option');
                option.value = operator;
                option.text = operator;
                operatorSelect.appendChild(option);
            });
            updateMap(data[0]);
        });

    document.getElementById('carrier-select').addEventListener('change', function() {
        updateMap(this.value);
    });
});

// gets averages for metrics for chart
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

// Function to update the map
function updateMap(carrier) {
    fetch('/geojson/states')
        .then(response => response.json())
        .then(data => {
            // Ensure each feature has a property for the average RSSI for the selected carrier
            data.features.forEach(feature => {
                feature.properties.averageRSSI = feature.properties[carrier]?.['Average RSSI'] || null;
            });

            // Filter out Alaska for T-Mobile
            if (carrier === 'T-Mobile') {
                data.features = data.features.filter(feature => feature.id !== 'AK');
            }

            // Collect all averageRSSI values for the selected carrier from filtered data
            var averageRSSIValues = data.features.map(feature => feature.properties.averageRSSI).filter(value => value !== null);

            // Calculate new min and max for the selected carrier
            var minRSSI = Math.min(...averageRSSIValues);
            var maxRSSI = Math.max(...averageRSSIValues);

            // Define the colorscale
            var colorscale = [
                [0, '#FFFFFF'],  // Lighter color for less negative values
                [1, '#0000FF']   // Darker color for more negative values
            ];

            // Define the trace for the choropleth map
            var trace = {
                type: 'choropleth',
                locationmode: 'USA-states',
                locations: data.features.map(feature => feature.id),
                z: data.features.map(feature => feature.properties.averageRSSI),
                text: data.features.map(feature => feature.properties.name),
                zmin: minRSSI,
                zmax: maxRSSI,
                colorscale: colorscale,
                colorbar: {
                    title: `Average RSSI (${carrier})`
                },
                marker: {
                    line: {
                        color: 'rgb(255,255,255)',
                        width: 2
                    }
                }
            };

            // Define the layout for the map
            var layout = {
                title: `Average RSSI by State (${carrier})`,
                geo: {
                    scope: 'usa',
                    projection: {
                        type: 'albers usa'
                    },
                    showlakes: true,
                    lakecolor: 'rgb(255,255,255)'
                }
            };

            // Create the plot for the selected carrier
            Plotly.newPlot('map', [trace], layout);
        });
}

// updates the chart when a new operator or metric is selected
function updateChart() {
    var selectedMetric = $('#metrics-select').val();

    selectedOperators = [];
    document.querySelectorAll('input[name="operators"]:checked').forEach(checkbox => {
        selectedOperators.push(checkbox.value);
    });

    if (!selectedMetric) {
        // Clear the chart if no metric is selected
        Plotly.newPlot('chart-area', [], {});
        return;
    }

    var xValues = [];
    var yValues = [];
    var barColors = [];
    var colors = {
        'AT&T': 'blue',
        'T-Mobile': 'magenta',
        'Verizon': 'red'
        // Add more operators and their colors as needed
    };

    selectedOperators.forEach(operator => {
        xValues.push(operator);
        yValues.push(fetchedData[operator][selectedMetric]);
        barColors.push(colors[operator] || '#007bff'); // Default color if operator not found
    });

    var trace = {
        x: xValues,
        y: yValues,
        type: 'bar',
        name: selectedMetric,
        marker: {
            color: barColors,
            line: {
                width: 1.5
            }
        },
        text: yValues.map(value => value.toFixed(2)),
        textposition: 'auto'
    };

    var layout = {
        title: {
            text: `Average ${selectedMetric} Comparison`,
            font: {
                family: 'Arial, sans-serif',
                size: 24
            }
        },
        xaxis: {
            title: {
                text: 'Operators',
                font: {
                    family: 'Arial, sans-serif',
                    size: 18
                }
            },
            tickangle: -45
        },
        yaxis: {
            title: {
                text: 'Values',
                font: {
                    family: 'Arial, sans-serif',
                    size: 18
                }
            },
            gridcolor: 'rgba(200, 200, 200, 0.2)',
            zerolinecolor: 'rgba(200, 200, 200, 0.5)'
        },
        margin: {
            l: 50,
            r: 50,
            b: 100,
            t: 50,
            pad: 4
        },
        legend: {
            font: {
                family: 'Arial, sans-serif',
                size: 14
            },
            bgcolor: 'rgba(255, 255, 255, 0.7)',
            bordercolor: 'rgba(200, 200, 200, 0.5)',
            borderwidth: 1
        },
        paper_bgcolor: 'rgba(245, 245, 245, 1)',
        plot_bgcolor: 'rgba(245, 245, 245, 1)',
        hovermode: 'closest',
        autosize: true,
        height: document.querySelector('.chart-container').clientHeight,
        width: document.querySelector('.chart-container').clientWidth
    };

    Plotly.newPlot('chart-area', [trace], layout, {responsive: true});
}

