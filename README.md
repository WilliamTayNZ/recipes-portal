# COMPSCI 235 - Starter Repository for the CS235 Recipe Portal
This is a starter repository for the recipes webapp project of CompSci 235 in Semester 2, 2025.

## Description

This repository contains a partial implementation of the domain model. It contains unit tests which can be run through pytest. It also contains a simple Flask application that renders content of a Recipe object instance from our domain model on a blank HTML page. You'll be expanding the domain model implementation, and you have the freedom to add, modify or remove test cases as needed.

## Installation

**Installation via requirements.txt**

**Windows**
```shell
$ cd <project directory>
$ py -3 -m venv venv
$ venv\Scripts\activate
$ pip install -r requirements.txt
```

**MacOS**
```shell
$ cd <project directory>
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

When using PyCharm, set the virtual environment using 'File or PyCharm'->'Settings' and select your project from the left menu. Select 'Project Interpreter', click on the gearwheel button and select 'Add Interpreter'. Click the 'Existing environment' radio button to select the virtual environment. 

## Execution

**Running the application**

From the *project directory*, and within the activated virtual environment (see *venv\Scripts\activate* above):

````shell
$ flask run
```` 

## Testing

After you have configured pytest as the testing tool for PyCharm (File - Settings - Tools - Python Integrated Tools - Testing), you can then run tests from within PyCharm by right-clicking the tests folder and selecting "Run pytest in tests".

Alternatively, from a terminal in the root folder of the project, you can also call 'python -m pytest tests' to run all the tests. PyCharm also provides a built-in terminal, which uses the configured virtual environment. 

## Configuration

The *project directory/.env* file contains variable settings. They are set with appropriate values.

* `FLASK_APP`: Entry point of the application (should always be `wsgi.py`).
* `FLASK_ENV`: The environment in which to run the application (either `development` or `production`).
* `SECRET_KEY`: Secret key used to encrypt session data.
* `TESTING`: Set to False for running the application. Overridden and set to True automatically when testing the application.
* `WTF_CSRF_SECRET_KEY`: Secret key used by the WTForm library.
 
## Data sources

The data files are modified excerpts downloaded from:

https://www.kaggle.com/datasets/irkaal/foodcom-recipes-and-reviews/

## Health Star Rating Formula

Each recipe in this application is given a **Health Star Rating (0–5 stars)** based on its per-serving nutritional values.  
The formula is designed to reward nutrients that are generally considered beneficial, while penalizing those that are linked to less healthy outcomes when consumed in excess.

- **Starting point:** Every recipe begins with a baseline of **5 stars**.  
- **Deductions (penalties):**  
  - Saturated fat: `-0.5 stars per 5g`  
  - Sugar: `-0.3 stars per 10g`  
  - Sodium: `-0.5 stars per 1000mg`  
- **Additions (bonuses):**  
  - Fiber: `+0.4 stars per 5g`  
  - Protein: `+0.3 stars per 10g`  

**Final rating:**  
The result is rounded to one decimal place and **clamped between 0 and 5 stars**.  

If a recipe is missing key nutrition data (calories, sugar, saturated fat, sodium, fiber, or protein), the health star rating is shown as: “Health star rating unavailable”.






