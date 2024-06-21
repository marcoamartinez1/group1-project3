import json

# Load your JSON data from a file
with open('cellular_data.json', 'r') as file:
    data = json.load(file)

# Write the pretty-printed JSON to a new file
with open('cellular_data.json', 'w') as file:
    json.dump(data, file, indent=4)
