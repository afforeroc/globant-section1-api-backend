from flask import Flask, request, jsonify
import pandas as pd
from collections import Counter

app = Flask(__name__)

# CONSTANTS
tables_columns_dict = {
    "hired_employees": {"id", "name", "datetime", "department_id", "job_id"},
    "departments_columns": {"id", "department"},
    "jobs_columns": {"id", "job"}
}

def validate_json_structure(json_data):
    # Validate JSON structure
    if not isinstance(json_data, dict):
        return False, "JSON structure is not a dictionary."
    # General Structure JSON data is correct
    return True, "JSON structure is valid."


def validate_table_name(json_data):
    # Validate that JSON document has only one key
    if len(json_data.keys()) != 1:
        error = "The JSON document does not have a key or has more than one. The JSON document has requires only one key."
        return False, error

    # Validate that JSON document has a key and this key is the name of table: "hired_employees", "departments", "jobs"
    table_name = (list(json_data.keys()))[0]
    if table_name not in ["hired_employees", "departments", "jobs"]:
        error = f"The JSON document has a invalid key: '{table_name}'. This key must be a table name: 'hired_employees', 'departments' or 'jobs'."
        return False, error
    
    # The key for table name is correct
    return True, "The JSON document has the required key (table name)."


def validate_json_data_inside_of_table_name(json_data, table_name):
    inside_table_name = json_data[table_name]
    # Validate inside JSON structure of table name
    if not isinstance(inside_table_name, dict):
        error = f"Invalid JSON structure inside of '{table_name}'."
        return False, error

    # Validate if inside of table_name has data
    if not len(inside_table_name):
        error = f"The data inside of '{table_name}' is empty. The data inside must be columns and records."
        return False, error

    # Validate column names of table_name
    received_columns = (list(inside_table_name.keys())).sort()
    stablished_columns = (list(tables_columns_dict[table_name].keys())).sort()
    # print(received_columns)
    # print(stablished_columns)
    if received_columns != stablished_columns:
        error = f"The columns for {table_name} are not valid. Please verify the column names."
        return False, error

    # Validate that each column has a list and the list has 1 to 1000 records
    for column, values in inside_table_name.items():
        # Check if values is a list
        if not isinstance(values, list):
            error = f"The values for column '{column}' inside of {table_name} should be a list."
            return False, error

        # Check the number of records
        if not (1 <= len(values) <= 1000):
            error = f"The number of records for column '{column}' inside of {table_name} should be between 1 and 1000."
            return False, error
    
    # JSON data inside is correct
    return True, f"The JSON data inside of {table_name} is correct."


@app.route('/api/receive_json', methods=['POST'])
def receive_json():
    try:
        # Get the JSON data from the request
        json_data = request.get_json()

        # Validate JSON structure
        valid_json, error = validate_json_structure(json_data)
        if not valid_json:
            response = {'status': 'error', 'message': f'{error}'}
            return jsonify(response), 400

        # Validate the 'table_name' key of the JSON
        valid_json, error = validate_table_name(json_data)
        if not valid_json:
            response = {'status': 'error', 'message': f'{error}'}
            return jsonify(response), 400

        # Validate the internal structure inside of 'table_name'
        table_name = (list(json_data.keys()))[0]
        valid_json, error = validate_json_data_inside_of_table_name(json_data, table_name)
        if not valid_json:
            response = {'status': 'error', 'message': f'{error}'}
            return jsonify(response), 400

        # Extract the data dictionary from the JSON
        data_dict = json_data['data']

        # Convert the data dictionary to a DataFrame
        df = pd.DataFrame(data_dict)

        # Return the DataFrame as JSON
        return jsonify(df.to_dict(orient='records'))

    except Exception as e:
        response = {'status': 'error', 'message': str(e)}
        return jsonify(response), 500

if __name__ == '__main__':
    app.run(debug=True)
