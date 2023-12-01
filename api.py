# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify
import pandas as pd
from jsonschema import validate, ValidationError, SchemaError

app = Flask(__name__)

# JSON schemas for each table "hired_employees", "departments" and "jobs"
table_json_schemas = {
    "hired_employees": {
        "type": "object",
        "properties": {
            "id": {"type": "array", "items": {"type": "integer"}},
            "name": {"type": "array", "items": {"type": "string"}},
            "datetime": {"type": "array", "items": {"type": "string", "format": "date-time"}},
            "department_id": {"type": "array", "items": {"type": "integer"}},
            "job_id": {"type": "array", "items": {"type": "integer"}},
        },
        "required": ["id", "name", "datetime", "department_id", "job_id"]
    },
    "departments": {
        "type": "object",
        "properties": {
            "id": {"type": "array", "items": {"type": "integer"}},
            "department": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["id", "department"]
    },
    "jobs": {
        "type": "object",
        "properties": {
            "id": {"type": "array", "items": {"type": "integer"}},
            "job": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["id", "job"]
    },
}


def validate_table_structure(data):
    """
    Validate the external structure of the input JSON data.

    Parameters:
    - data (dict): Input JSON data.

    Returns:
    - tuple: A tuple containing a boolean indicating validation result and an error message (if any).
    """
    try:
        # Check if the data is a dictionary, has exactly one key, that key is 'table',
        # and the value corresponding to 'table' is also a dictionary.
        if not isinstance(data, dict) or len(data) != 1 or "table" not in data or not isinstance(data["table"], dict):
            raise ValidationError("Invalid external structure. Must contain only one key 'table' with a dictionary value.")
        return True, ""  # Validation successful
    except ValidationError as validation_error:
        return False, str(validation_error)  # Validation failed with an error message


def validate_internal_table_structure(table_data):
    """
    Validate the internal structure of the "table" key.

    Parameters:
    - table_data (dict): Data inside the "table" key.

    Returns:
    - tuple: A tuple containing a boolean indicating validation result and an error message (if any).
    """
    try:
        # Check if the 'table' structure is not empty
        if not table_data:
            raise ValidationError("The 'table' structure must not be empty.")
        
        # Extract the table name and properties from the 'table' structure
        table_name, table_schema = next(iter(table_data.items()))  # Extract the table name and properties

        # Check if the extracted table name is in the predefined JSON schemas
        if table_name not in table_json_schemas:
            valid_table_names = ', '.join([f"'{name}'" for name in table_json_schemas.keys()])
            raise ValidationError(f"Unknown table: '{table_name}'. Valid table names are: {valid_table_names}")
        
        # Check if the properties of the table are represented as a dictionary
        if not isinstance(table_schema, dict):
            raise ValidationError(f"Invalid table structure. Table '{table_name}' must be an object.")

        # Check if the table properties are not empty
        if not table_schema:
            raise ValidationError(f"The table '{table_name}' must not be an empty object. Provide valid properties.")

        try:
            # Validate the schema using jsonschema
            validate(instance=table_schema, schema=table_json_schemas[table_name])
            return True, ""  # Validation successful
        except ValidationError as validation_error:
            # If validation using jsonschema fails, provide a custom error message
            raise ValidationError(f"Verify the columns and data types of the table '{table_name}'.") from validation_error
        except SchemaError as schema_error:
            # If there is an issue with the JSON schema itself, provide a custom error message
            raise ValidationError(f"Invalid JSON schema for table '{table_name}'.") from schema_error
    
    except ValidationError as validation_error:
        return False, str(validation_error) # Validation failed with an error message


@app.route("/api/receive_table_data", methods=["POST"])
def receive_table_data():
    """
    API endpoint to receive JSON data containing a table and return it as a DataFrame.

    Returns:
    - JSON: The DataFrame as a JSON response.
    """
    try:
        # Get the JSON data from the request
        json_data = request.get_json()

        # Validate the table structure
        is_valid_external, external_error_message = validate_table_structure(json_data)
        if not is_valid_external:
            response = {"status": "error", "message": external_error_message}
            return jsonify(response), 400

        # Validate the structure inside of "table"
        is_valid_internal, internal_error_message = validate_internal_table_structure(json_data["table"])
        if not is_valid_internal:
            response = {"status": "error", "message": internal_error_message}
            return jsonify(response), 400

        # Extract the table data from JSON data
        table_dict = json_data["table"]

        # Extract table name key
        table_name = next(iter(table_dict.keys()))

        # Convert the data dictionary to a DataFrame
        df = pd.DataFrame(table_dict[table_name])

        # Return the DataFrame as JSON
        return jsonify(df.to_dict(orient="records"))

    except Exception as exception:
        response = {"status": "error", "message": str(exception)}
        return jsonify(response), 500

if __name__ == "__main__":
    app.run(debug=True)
