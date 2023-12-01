# Backend for Section 1: API of Globant's Data Engineering Coding Challenge

## Instructions to configure the API in local way

## Install Python and update PIP
> PowerShell
* Install [Python 3.9.0](https://www.python.org/downloads/release/python-390/)
* Check Python version: `python --version`
* Install and upgrade PIP: `python -m pip install --upgrade pip`

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
* Run python file: `python .\api.py`
* Deactivate the virtual environment: `deactivate`

## Dependencies
```
flask
pandas
```