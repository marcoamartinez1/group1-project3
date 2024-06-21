from flask import Flask, render_template, jsonify, request
import json
import logging
from collections import defaultdict

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

# Load data from the JSON file
with open('cellular_data.json') as f:
    cellular_data = json.load(f)

# Precompute averages for each operator
operator_averages = defaultdict(lambda: defaultdict(list))

for record in cellular_data:
    operator = record['Operator Name'].strip()
    operator_averages[operator]['Average RSSI'].append(record['Average RSSI'])
    operator_averages[operator]['Average Signal Power'].append(record['Average Signal Power'])
    operator_averages[operator]['Average Signal Level'].append(record['Average Signal Level'])
    operator_averages[operator]['Average Signal Quality'].append(record['Average Signal Quality'])
    operator_averages[operator]['Average Signal Strength'].append(record['Average Signal Strength'])
    operator_averages[operator]['Average Cell Strength (ASU)'].append(record['Average Cell Strength (ASU)'])

# Calculate average for each operator
for operator, metrics in operator_averages.items():
    for metric, values in metrics.items():
        operator_averages[operator][metric] = sum(values) / len(values)

# Log the precomputed averages for debugging
app.logger.debug(f"Precomputed operator averages: {operator_averages}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/operators', methods=['GET'])
def get_operators():
    operators = sorted(operator_averages.keys())
    return jsonify(operators)

@app.route('/averages', methods=['GET'])
def get_averages():
    operator_name = request.args.get('operator').strip()

    if not operator_name:
        return jsonify({"error": "Operator name is required"}), 400

    # Log the requested operator name for debugging
    app.logger.debug(f"Requested operator name: {operator_name}")

    if operator_name not in operator_averages:
        app.logger.debug(f"No data found for operator: {operator_name}")
        return jsonify({"error": "No data found for the specified operator"}), 404

    return jsonify(operator_averages[operator_name])

if __name__ == '__main__':
    app.run(debug=True)
