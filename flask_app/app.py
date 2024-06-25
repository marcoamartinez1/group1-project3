from flask import Flask, render_template, jsonify, request, send_file
import json
import logging
from collections import defaultdict, Counter
import os
import zipfile

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

# Construct the path to the ZIP file
zip_file_path = os.path.join(os.path.dirname(__file__), 'cellular_data.json.zip')
json_file_name = 'cellular_data.json'

# Extract the JSON file from the ZIP archive
with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
    zip_ref.extract(json_file_name, os.path.dirname(__file__))

# Construct the path to the extracted JSON file
json_file_path = os.path.join(os.path.dirname(__file__), json_file_name)

# Load data from the JSON file
with open('cellular_data.json') as f:
    cellular_data = json.load(f)
    
# Precompute averages for each operator
operator_averages = defaultdict(lambda: defaultdict(list))
state_carrier_counts = defaultdict(lambda: defaultdict(int))
# Stores averages for each operator and county
operator_county_averages = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
# Stores averages for each operator and state
operator_state_averages = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

for record in cellular_data:
    operator = record['Operator Name'].strip()
    state = record['State'].strip()
    operator_averages[operator]['Average RSSI'].append(record['Average RSSI'])
    operator_averages[operator]['Average Signal Power'].append(record['Average Signal Power'])
    operator_averages[operator]['Average Signal Level'].append(record['Average Signal Level'])
    operator_averages[operator]['Average Signal Quality'].append(record['Average Signal Quality'])
    operator_averages[operator]['Average Signal Strength'].append(record['Average Signal Strength'])
    operator_averages[operator]['Average Cell Strength (ASU)'].append(record['Average Cell Strength (ASU)'])
    
    state_carrier_counts[state][operator] += 1

    # finds average RSSI values for each operator at the county level
    county = record['County'].strip()
    operator_county_averages[operator][county]['Average RSSI'].append(record['Average RSSI'])

    # finds averages RSSI values for each operator at the state level
    operator_state_averages[operator][state]['Average RSSI'].append(record['Average RSSI'])

# Calculate average for each operator
for operator, metrics in operator_averages.items():
    for metric, values in metrics.items():
        operator_averages[operator][metric] = sum(values) / len(values)

# Calculate average for each operator and county
for operator, counties in operator_county_averages.items():
    for county, metrics in counties.items():
        for metric, values in metrics.items():
            operator_county_averages[operator][county][metric] = sum(values) / len(values)

# Calculate average for each operator and state
for operator, states in operator_state_averages.items():
    for state, metrics in states.items():
        for metric, values in metrics.items():
            operator_state_averages[operator][state][metric] = sum(values) / len(values)

# Logging the precomputed averages for debugging
app.logger.debug(f"Precomputed operator averages: {operator_averages}")
app.logger.debug(f"Precomputed operator and county averages: {operator_county_averages}")
app.logger.debug(f"Precomputed operator and state averages: {operator_state_averages}")

# Load the geoJSON files
with open('us-states.json', encoding='utf-8') as f:
    states_geojson = json.load(f)

# Function to merge averages with geoJSON
# def merge_averages_with_geojson(geojson, averages, key):
#     for feature in geojson['features']:
#         name = feature['properties'][key].strip()
#         for operator, data in averages.items():
#             if name in data:
#                 feature['properties'][operator] = data[name]
#     return geojson

def merge_averages_with_geojson(geojson, averages, key):
    for feature in geojson['features']:
        name = feature[key].strip()
        for operator, data in averages.items():
            if name in data:
                feature['properties'][operator] = data[name]
    return geojson

# Merge state averages with geoJSON
states_geojson = merge_averages_with_geojson(states_geojson, operator_state_averages, 'id')

# Save merged geoJSON file for serving
with open('merged_states.geojson', 'w') as f:
    json.dump(states_geojson, f)

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

@app.route('/state-carrier-counts', methods=['GET'])
def get_state_carrier_counts():
    state_totals = {state: sum(carriers.values()) for state, carriers in state_carrier_counts.items()}
    response = {
        'counts': state_carrier_counts,
        'totals': state_totals
    }
    app.logger.debug(f"State Carrier Counts: {response}")
    return jsonify(response)

@app.route('/states', methods=['GET'])
def get_states():
    states = sorted(state_carrier_counts.keys())
    app.logger.debug(f"States: {states}")
    return jsonify(states)

@app.route('/state_averages', methods=['GET'])
def get_state_averages():
    operator_name = request.args.get('operator').strip()
    state_name = request.args.get('state').strip()

    if not operator_name:
        return jsonify({"error": "Operator name is required"}), 400
    
    if not state_name:
        return jsonify({"error": "State name is required"}), 400

    # Log the requested operator and state names for debugging
    app.logger.debug(f"Requested operator name: {operator_name}, state name: {state_name}")

    if operator_name not in operator_state_averages or state_name not in operator_state_averages[operator_name]:
        app.logger.debug(f"No data found for operator: {operator_name} in state: {state_name}")
        return jsonify({"error": "No data found for the specified operator and state"}), 404

    return jsonify(operator_state_averages[operator_name][state_name])


@app.route('/geojson/states')
def get_states_geojson():
    return send_file('merged_states.geojson')

if __name__ == '__main__':
    app.run(debug=True)
