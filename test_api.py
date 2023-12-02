# -*- coding: utf-8 -*-

"""
Unit tests for the Flask API in the 'api' module, focusing on the '/api/receive_table_data' endpoint.
Scenarios cover positive cases with valid data for tables like 'hired_employees,' 'departments,' and 'jobs.'
Error handling is tested for empty dictionaries, invalid keys, non-dictionary inputs, tables with missing
columns, invalid columns, extra columns, mismatched record counts, empty records, and data type inconsistencies.
Additional tests involve large datasets, checking successful processing with 1000 records and proper error
handling with 1001 records. The goal is to ensure the API's robustness and correctness when handling diverse table data.
"""

import unittest
import json
from api import app


def generate_large_data(n=100):
    large_data = {
        "table": {
            "hired_employees": {
                "id": list(range(1, n + 1)),
                "name": ["Name" + str(i) for i in range(1, n + 1)],
                "datetime": ["2023-01-01"] * n,
                "department_id": list(range(1, n + 1)),
                "job_id": list(range(1, n + 1))
            }
        }
    }
    return large_data


class TestFlaskAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_receive_valid_table_data_hired_employees(self):
        data = {
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

        response = self.app.post('/api/receive_table_data', data=json.dumps(data), content_type='application/json')
        result = json.loads(response.data.decode('utf-8'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(result['status'], 'success')

    def test_receive_valid_table_data_departments(self):
        data = {
            "table": {
                "departments": {
                    "id": [1, 2],
                    "department": ["HR", "Finance"]
                }
            }
        }

        response = self.app.post('/api/receive_table_data', data=json.dumps(data), content_type='application/json')
        result = json.loads(response.data.decode('utf-8'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(result['status'], 'success')

    def test_receive_valid_table_data_jobs(self):
        data = {
            "table": {
                "jobs": {
                    "id": [101, 102],
                    "job": ["Manager", "Developer"]
                }
            }
        }

        response = self.app.post('/api/receive_table_data', data=json.dumps(data), content_type='application/json')
        result = json.loads(response.data.decode('utf-8'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(result['status'], 'success')

    def test_receive_table_data_empty_dict(self):
        data = {"table": {}}

        response = self.app.post('/api/receive_table_data', data=json.dumps(data), content_type='application/json')
        result = json.loads(response.data.decode('utf-8'))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(result['status'], 'error')
        self.assertIn("The dictionary associated with key 'table' must not be empty and should be a valid dictionary.", result['message'])

    def test_receive_table_data_invalid_entry_dict(self):
        data = {"invalid_key": {"hired_employees": {}}}

        response = self.app.post('/api/receive_table_data', data=json.dumps(data), content_type='application/json')
        result = json.loads(response.data.decode('utf-8'))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(result['status'], 'error')
        self.assertIn("The dictionary key 'invalid_key' should be:", result['message'])

    def test_receive_table_data_non_dict(self):
        data = {"table": "not_a_dict"}

        response = self.app.post('/api/receive_table_data', data=json.dumps(data), content_type='application/json')
        result = json.loads(response.data.decode('utf-8'))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(result['status'], 'error')
        self.assertIn("The dictionary associated with key 'table' must not be empty and should be a valid dictionary.", result['message'])

    def test_receive_table_data_invalid_table_dict(self):
        data = {"table": {"invalid_table": {}}}

        response = self.app.post('/api/receive_table_data', data=json.dumps(data), content_type='application/json')
        result = json.loads(response.data.decode('utf-8'))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(result['status'], 'error')
        self.assertIn("The dictionary key 'invalid_table' should be:", result['message'])

    def test_receive_table_data_with_missing_column(self):
        data = {
            "table": {
                "hired_employees": {
                    "id": [1, 2],
                    "name": ["John", "Jane"],
                    "department_id": [1, 2],
                    "job_id": [101, 102]
                }
            }
        }

        response = self.app.post('/api/receive_table_data', data=json.dumps(data), content_type='application/json')
        result = json.loads(response.data.decode('utf-8'))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(result['status'], 'error')
        self.assertIn("Verify the columns and data types of the table 'hired_employees'.", result['message'])

    def test_receive_table_data_with_invalid_column(self):
        data = {
            "table": {
                "hired_employees": {
                    "id": [1, 2],
                    "name": ["John", "Jane"],
                    "invalid_column": ["2023-01-01", "2023-01-02"],  # Invalid column
                    "department_id": [1, 2],
                    "job_id": [101, 102]
                }
            }
        }

        response = self.app.post('/api/receive_table_data', data=json.dumps(data), content_type='application/json')
        result = json.loads(response.data.decode('utf-8'))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(result['status'], 'error')
        self.assertIn("Verify the columns and data types of the table 'hired_employees'.", result['message'])

    def test_receive_table_data_with_extra_column(self):
        data = {
            "table": {
                "hired_employees": {
                    "id": [1, 2],
                    "name": ["John", "Jane"],
                    "datetime": ["2023-01-01", "2023-01-02"],
                    "department_id": [1, 2],
                    "job_id": [101, 102],
                    "extra_column": [1, 2],  # Extra record
                }
            }
        }

        response = self.app.post('/api/receive_table_data', data=json.dumps(data), content_type='application/json')
        result = json.loads(response.data.decode('utf-8'))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(result['status'], 'error')
        self.assertIn("Verify the columns and data types of the table 'hired_employees'.", result['message'])

    def test_receive_table_data_different_record_count(self):
        data = {
            "table": {
                "hired_employees": {
                    "id": [1, 2, 3],
                    "name": ["John", "Jane"],
                    "datetime": ["2023-01-01", "2023-01-02"],
                    "department_id": [1, 2],
                    "job_id": [101, 102]
                }
            }
        }

        response = self.app.post('/api/receive_table_data', data=json.dumps(data), content_type='application/json')
        result = json.loads(response.data.decode('utf-8'))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(result['status'], 'error')
        self.assertIn("Mismatched record count for column", result['message'])

    def test_receive_table_data_with_empty_records(self):
        data = {
            "table": {
                "hired_employees": {
                    "id": [],
                    "name": [],
                    "datetime": [],
                    "department_id": [],
                    "job_id": []
                }
            }
        }

        response = self.app.post('/api/receive_table_data', data=json.dumps(data), content_type='application/json')
        result = json.loads(response.data.decode('utf-8'))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(result['status'], 'error')
        self.assertIn("Invalid number of records for column 'id'. Expected between 1 and 1000 records, but got 0.", result['message'])

    def test_receive_table_data_1000_records(self):
        large_data = generate_large_data(n=1000)

        response = self.app.post('/api/receive_table_data', data=json.dumps(large_data), content_type='application/json')
        result = json.loads(response.data.decode('utf-8'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(result['status'], 'success')
        self.assertIn("Pandas DataFrame created for table 'hired_employees'.", result['message'])

    def test_receive_table_data_1001_records(self):
        large_data = generate_large_data(n=1001)

        response = self.app.post('/api/receive_table_data', data=json.dumps(large_data), content_type='application/json')
        result = json.loads(response.data.decode('utf-8'))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(result['status'], 'error')
        self.assertIn("Invalid number of records for column 'id'. Expected between 1 and 1000 records, but got 1001.", result['message'])

    def test_receive_table_data_with_different_data_types(self):
        data = {
            "table": {
                "hired_employees": {
                    "id": [1, "2"],
                    "name": ["John", "Jane"],
                    "datetime": ["2023-01-01", "2023-01-02"],
                    "department_id": [1, 2],
                    "job_id": [101, 102]
                }
            }
        }

        response = self.app.post('/api/receive_table_data', data=json.dumps(data), content_type='application/json')
        result = json.loads(response.data.decode('utf-8'))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(result['status'], 'error')
        self.assertIn("Verify the columns and data types of the table", result['message'])


if __name__ == '__main__':
    unittest.main()
