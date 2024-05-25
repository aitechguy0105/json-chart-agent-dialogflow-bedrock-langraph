import csv
import json

# Open the double-encoded CSV file
with open('Responses (1).csv', 'rb') as file:
    # Decode the file twice to get the original data
    content = file.read().decode('utf-8-sig').encode('latin-1').decode('utf-8')

# Create a CSV reader object
reader = csv.DictReader(content.splitlines())

# Convert the CSV data to a list of dictionaries
data = list(reader)

# Write the data to a JSON file
with open('output.json', 'w', encoding='utf-8') as json_file:
    json.dump(data, json_file, ensure_ascii=False, indent=4)
