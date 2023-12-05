# Backend for Section 1: API of Globant's Data Engineering Coding Challenge

## Dependencies
```
python-dotenv
pandas
jsonschema
flask
snowflake-connector-python[secure-local-storage,pandas]
```

## Steps to use the API locally

## Install Python and update PIP
> PowerShell
* Install [Python 3.10.0](https://www.python.org/downloads/release/python-3100/)
* Check Python version: `python --version`
* Install and upgrade PIP: `python -m pip install --upgrade pip`

## Install Postman
* Install [Postman](https://www.postman.com/downloads/)

## Configure the virtual environment
> PowerShell
* Allow execute scripts to activate a virtual environment: `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`
* Install the virtual environment package: `pip install virtualenv`
* Access the repository folder: `cd .\globant-section1-api-backend\`
* Create a virtual environment: `python -m virtualenv venv`
* Activate the virtual environment: `.\venv\Scripts\activate`
* Install the libraries required: `pip install -r requirements.txt`

## How to use

## How to use the API with virtual env
> PowerShell
* Access the repository folder: `cd .\globant-section1-api-backend\`
* Activate the virtual environment: `.\venv\Scripts\activate`
* Run the Flask App: `python .\api.py`
* Deactivate the virtual environment: `deactivate`

## How to test the API with unit tests
> PowerShell
* Access the repository folder: `cd .\globant-section1-api-backend\`
* Activate the virtual environment: `.\venv\Scripts\activate`
* Run the Flask App: `python .\test_api.py`
* Deactivate the virtual environment: `deactivate`

## How to use the API using Postman
> Postman
* Run Flask App: `python .\api.py`
* Open Postman
* Create a New Request:
    - Click on the "New" button in Postman to create a new request.
* Set Request Details:
    - Choose the HTTP method as POST.
    - Enter the URL of your Flask app, e.g., `http://127.0.0.1:5000/api/receive-table-data`
    - Go to the "Body" tab.
* Add JSON Data:
    - Select the raw option.
    - Choose the content type as JSON (application/json).
    - In the body, enter your JSON data. For example:

    hired_employees e.g.
    ```
    {
        "table": {
            "hired_employees": {
                "id": [1, 2],
                "name": ["Harold Vogt", "Ty Hofer"],
                "datetime": ["2021-11-07T02:48:42Z", "2021-05-30T05:43:46Z"],
                "department_id": [2, 8],
                "job_id": [96, null]
            }
        }
    }
    ```
    departments e.g.
    ```
    
    {
        "table": {
            "departments": {
                "id": [1, 2],
                "department": ["Product Management", "Sales"]
            }
        }
    }
    ```
    jobs e.g.
    ```
    {
        "table": {
            "jobs": {
                "id": [1, 2],
                "job": ["Marketing Assistant", "VP Sales"]
            }
        }
    }
    ```
* Look into `json_samples/` folder to use JSON samples of each table.
* Send the Request:
    - Click on the "Send" button to send the POST request to your Flask API.
* View Response:
    - Postman will display the response from your Flask API.
    - The Flask app should respond with a JSON representation of the Pandas DataFrame.
