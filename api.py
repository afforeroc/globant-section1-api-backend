# -*- coding: utf-8 -*-

"""
Flask API for Receiving JSON Table Data

This Flask API serves as an endpoint for receiving JSON data containing tables
and validates both the external and internal structures of the input data.
It uses JSON schemas to validate the internal structure of each table type
("hired_employees", "departments", "jobs"). The validated data is then
converted to a Pandas DataFrame and returned as a JSON response.

Endpoints:
- POST /api/receive_table_data: Receives JSON data, validates its structure,
  converts it to a DataFrame, and returns the DataFrame as a JSON response.

Dependencies:
- Flask: Web framework for building the API.
- pandas: Data manipulation library for working with DataFrames.
- jsonschema: Library for validating JSON data against a specified schema.

Note: Ensure that the required dependencies are installed before running the API.

Usage:
1. Run the script.
2. Send a POST request with JSON data to the /api/receive_table_data endpoint.

Example JSON Data:
{
    "table": {
        "hired_employees": {
            "id": [1, 2],
            "name": ["John", "Jane"],
            "datetime": ["2023-01-01", "2023-01-02"],
            "department_id": [1, 2],
            "job_id": [101, 102]
        }
    }
}

Example Response:
{
    "message": "Data was inserted into table 'HIRED_EMPLOYEES'.",
    "status": "success"
}
"""

from flask import Flask, request, jsonify
import pandas as pd
from jsonschema import validate, ValidationError, SchemaError
from dotenv import dotenv_values
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas

app = Flask(__name__)

# JSON schemas for each table "hired_employees", "departments" and "jobs"
table_json_schemas = {
    "hired_employees": {
        "type": "object",
        "properties": {
            "id": {"type": "array", "items": {"type": "integer"}},
            "name": {"type": "array", "items": {"type": ["string", "null"] }},
            "datetime": {"type": "array", "items": {"type": ["string", "null"], "format": "date-time"}},
            "department_id": {"type": "array", "items": {"type": ["integer", "null"]}},
            "job_id": {"type": "array", "items": {"type": ["integer", "null"]}},
        },
        "required": ["id", "name", "datetime", "department_id", "job_id"],
        "additionalProperties": False
    },
    "departments": {
        "type": "object",
        "properties": {
            "id": {"type": "array", "items": {"type": "integer"}},
            "department": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["id", "department"],
        "additionalProperties": False
    },
    "jobs": {
        "type": "object",
        "properties": {
            "id": {"type": "array", "items": {"type": "integer"}},
            "job": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["id", "job"],
        "additionalProperties": False
    }
}


def create_snowflake_connection(snowflake_credentials):
    """
    Connects to Snowflake using the provided credentials from the .env file.

    Returns:
    snowflake.connector.connection.SnowflakeConnection: A Snowflake connection object.

    Raises:
    snowflake.connector.errors.DatabaseError: If there is an error connecting to Snowflake.
    """
    try:
        snowflake_connection = snowflake.connector.connect(
            user=snowflake_credentials["user_login"],
            password=snowflake_credentials["password"],
            account=snowflake_credentials["account"],
            warehouse=snowflake_credentials["warehouse"],
            database=snowflake_credentials["database"],
            schema=snowflake_credentials["schema"]
        )
        return snowflake_connection
    except snowflake.connector.errors.DatabaseError as snowflake_error:
        print(f"Error connecting to Snowflake: {str(snowflake_error)}")


def delete_records_by_id_for_snowflake(conn, table_name, id_values):
    """
    Delete records from Snowflake table based on the specified IDs.

    Parameters:
    - conn (snowflake.connector.connection): Snowflake connection object.
    - table_name (str): The name of the Snowflake table.
    - id_values (list): List of IDs to be deleted.

    Returns:
    - None
    """
    # Create a cursor object
    cursor = conn.cursor()
    try:
        # Generate a comma-separated string of IDs for the WHERE clause
        id_string = ', '.join(map(str, id_values))
        # Construct the DELETE query
        delete_query = f"DELETE FROM {table_name} WHERE ID IN ({id_string})"
        # Execute the DELETE query
        cursor.execute(delete_query)
        # Commit the changes
        conn.commit()
        # print(f"Records with IDs {id_string} deleted successfully.")
    except Exception as e:
        # Handle the exception (you can modify this part based on your requirements)
        print(f"Error deleting records with IDs {id_string}. {str(e)}")
    finally:
        # Close the cursor
        cursor.close()


def validate_dictionary_with_unique_key(data, key_list):
    """
    Validate if data is a dictionary with only one key and the value is not empty.

    Parameters:
    - data (dict): Dictionary data.
    - key_list (array): List of keys.

    Returns:
    - tuple: A tuple containing a boolean indicating validation result and an error message (if any).
    """
    try:
        # Check if the data is a dictionary
        if not isinstance(data, dict):
            raise ValidationError("Invalid input. Must be a dictionary.")

        # Check if there is exactly one key in the dictionary
        if len(data) != 1:
            raise ValidationError("The dictionary must have exactly one key.")

        # Check if the specified key is present in the dictionary
        dict_key = next(iter(data))
        if dict_key not in key_list:
            valid_keys = ', '.join(map(lambda key: f"'{key}'", key_list))
            raise ValidationError(f"The dictionary key '{dict_key}' should be: {valid_keys}")

        # Check if the value corresponding to the specified key is a non-empty dictionary
        if not data[dict_key] or not isinstance(data[dict_key], dict):
            raise ValidationError(f"The dictionary associated with key '{dict_key}' must not be empty and should be a valid dictionary.")

        return True, ""  # Validation successful
    except ValidationError as validation_error:
        return False, str(validation_error)  # Validation failed with an error message


def validate_table_data(table_data, table_name):
    """
    Validate the schema (column names and the data types) of the table data.

    Parameters:
    - table_data (dict): Data inside of "hired_employees", "departments", "jobs".
    - table_name (str): Name of table.

    Returns:
    - tuple: A tuple containing a boolean indicating validation result and an error message (if any).
    """
    try:
        # Validate the schema of table data
        try:
            # Validate the schema using jsonschema
            validate(instance=table_data, schema=table_json_schemas[table_name])
            return True, ""  # Validation successful
        except ValidationError as validation_error:
            # If validation using jsonschema fails, provide a custom error message
            raise ValidationError(f"Verify the columns and data types of the table '{table_name}'.") from validation_error
        except SchemaError as schema_error:
            # If there is an issue with the JSON schema itself, provide a custom error message
            raise ValidationError(f"Invalid JSON schema for table '{table_name}'.") from schema_error

    except ValidationError as validation_error:
        return False, str(validation_error)  # Validation failed with an error message


def validate_record_count(table_data):
    """
    Validate the number of records of table data.

    Parameters:
    - table_data (dict): Data inside of "hired_employees", "departments", "jobs"

    Returns:
    - tuple: A tuple containing a boolean indicating validation result and an error message (if any).
    """
    try:
        expected_record_count = None

        for column_name, records in table_data.items():
            record_count = len(records)
            if not 1 <= record_count <= 1000:
                raise ValidationError(f"Invalid number of records for column '{column_name}'. "
                                      f"Expected between 1 and 1000 records, but got {record_count}.")

            if expected_record_count is None:
                # Set the expected record count for the first column
                expected_record_count = record_count
            elif record_count != expected_record_count:
                # Check if the current column has the same number of records as the first column
                raise ValidationError(f"Mismatched record count for column '{column_name}'. "
                                      f"Expected {expected_record_count} records, but got {record_count}.")

        return True, ""  # Validation successful
    except ValidationError as validation_error:
        return False, str(validation_error)  # Validation failed with an error message


@app.route("/api/receive-table-data", methods=["POST"])
def receive_table_data():
    """
    API endpoint to receive JSON data containing a table and return it as a DataFrame.

    Returns:
    - JSON: The DataFrame as a JSON response.
    """
    try:
        # Get the JSON data from the request
        json_data = request.get_json()

        # Validate JSON data
        entry_key_list = ["table"]
        is_valid_entry_dict, entry_dict_error_message = validate_dictionary_with_unique_key(json_data, entry_key_list)
        if not is_valid_entry_dict:
            response = {"status": "error", "message": entry_dict_error_message}
            return jsonify(response), 400

        # Extract the entry key and entry data
        entry_key = next(iter(json_data))
        entry_data = json_data[entry_key]

        # Validate the entry data
        table_name_list = ["hired_employees", "departments", "jobs"]
        is_valid_table_dict, table_dict_error_message = validate_dictionary_with_unique_key(entry_data, table_name_list)
        if not is_valid_table_dict:
            response = {"status": "error", "message": table_dict_error_message}
            return jsonify(response), 400

        # Extract the table name and table data
        table_name = next(iter(entry_data))
        table_data = entry_data[table_name]

        # Validate the schema (column names and the data types) of the table data
        is_valid_table_data, table_data_error_message = validate_table_data(table_data, table_name)
        if not is_valid_table_data:
            response = {"status": "error", "message": table_data_error_message}
            return jsonify(response), 400

        # Validate record count of table data
        is_valid_record_count, record_count_error_message = validate_record_count(table_data)
        if not is_valid_record_count:
            response = {"status": "error", "message": record_count_error_message}
            return jsonify(response), 400

        # Convert the data dictionary to a DataFrame
        try:
            df = pd.DataFrame(table_data)
            # print(df)
        except Exception as exception:
            response = {"status": "error", "message": f"Error creating Pandas DataFrame: {str(exception)}"}
            return jsonify(response), 500

        # Uppercase table name
        table_name = table_name.upper()
        
        # Uppercase all column names
        df.columns = [col.upper() for col in df.columns]
        
        # Extract unique IDs from the DataFrame
        unique_ids = df['ID'].unique().tolist()

        # Load JSON data from the .env file
        snowflake_credentials = dotenv_values(".env")
        
        # Snowflake connection
        conn = create_snowflake_connection(snowflake_credentials)
        try:
            # Delete existing records with the same IDs
            delete_records_by_id_for_snowflake(conn, table_name, unique_ids)
            # Write new data to Snowflake
            success, nchunks, nrows, _ = write_pandas(conn, df, table_name)
            # Success response
            response = {"status": "success", "message": f"Data was inserted into table '{table_name}'."}
            return jsonify(response), 200
        except Exception as _:
            response = {"status": "error", "message": f"Error inserting data into  table '{table_name}'."}
            return jsonify(response), 500

    except Exception as exception:
        response = {"status": "error", "message": str(exception)}
        return jsonify(response), 500


if __name__ == "__main__":
    app.run(debug=True)
