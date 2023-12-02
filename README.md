# Backend for Section 1: API of Globant's Data Engineering Coding Challenge

## Dependencies
```
flask
pandas
jsonschema
python-dotenv
SQLAlchemy
snowflake-sqlalchemy
```

## Instructions to configure the API in local way

## Install Python and update PIP
> PowerShell
* Install [Python 3.9.0](https://www.python.org/downloads/release/python-390/)
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

## How to use virtual env
> PowerShell
* Access the repository folder: `cd .\globant-section1-api-backend\`
* Activate the virtual environment: `.\venv\Scripts\activate`
* Run the Flask App: `python .\api.py`
* Deactivate the virtual environment: `deactivate`

## How to use the API using Postman
> Postman
* Run Flask App: `python .\api.py`
* Open Postman
* Create a New Request:
    - Click on the "New" button in Postman to create a new request.
* Set Request Details:
    - Choose the HTTP method as POST.
    - Enter the URL of your Flask app, e.g., `http://127.0.0.1:5000/api/receive_json`
    - Go to the "Body" tab.
* Add JSON Data:
    - Select the raw option.
    - Choose the content type as JSON (application/json).
    - In the body, enter your JSON data. For example:
    ```
    {   "jobs": {
            "id": [1, 2, 3],
            "job": ["Marketing Assistant", "VP Sales", "Biostatistician IV"]
        }
    }
    ```
* Send the Request:
    - Click on the "Send" button to send the POST request to your Flask API.
* View Response:
    - Postman will display the response from your Flask API.
    - The Flask app should respond with a JSON representation of the Pandas DataFrame.
