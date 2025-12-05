# 🍳 Recipes Portal

A web application for browsing and discovering recipes. Built as a team project for COMPSCI 235 (Software Development Methodologies).

**NOTE**: The `.env` file is included in this repository for educational purposes to demonstrate configuration practices. Since this is a classroom project running on localhost with no production deployment, the credentials are non-sensitive placeholders.

## About This Project

Recipes Portal is a web application built with Flask, HTML (with Jinja2), and CSS. It provides an interactive interface for exploring recipes with nutritional insights. The application features a robust domain model with comprehensive unit tests and a clean web interface that displays recipe information, including a custom health star rating system.

### Key Features

- **Recipe Browsing**: Browse and explore recipes with paginated search functionality
- **Filtered Search**: Filter recipes by name, author, or category
- **Save Favorites**: Log in or register to save your favorite recipes for quick access
- **Recipe Reviews**: Read user reviews and ratings for recipes, and log in or register to post your own review (1-5 stars)
- **Detailed Recipe Information**: View complete recipe information including images, ingredients, instructions, and nutrition values
- **Health Star Ratings**: 0–5 health star ratings for each recipe (see [Health Star Rating Formula](#health-star-rating-formula) for details)
- **Automated Testing**: Comprehensive unit, integration, and end-to-end testing
- **Extensible Domain Model**: Well-structured, object-oriented design with support for recipes, users, reviews, favorites, and more
- **Flexible Data Storage**: Works with both an in-memory storage layer and a local SQLite database

## Prerequisites

- Python 3.8+
- pip

## Installation

### Setup Steps

#### Windows
```shell
$ cd <project directory>
$ py -3 -m venv venv
$ venv\Scripts\activate
$ pip install -r requirements.txt
```

#### macOS/Linux
```shell
$ cd <project directory>
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

### Data Storage

This application supports two data storage backends:

- **Memory Repository**: All data is stored in memory during runtime. Useful for testing and development.
- **SQLite Database**: Data is persisted in a local SQLite database. When you run `flask run`, the database will be automatically populated with recipe data on first run.


## Execution

**Running the application**

From the *project directory*, and within the activated virtual environment (see *venv\Scripts\activate* above):

````shell
$ flask run
```` 

## Testing

From a terminal in the root folder of the project (within the activated virtual environment), run the tests with:

```shell
$ python -m pytest -v tests
```

This will run all unit tests with verbose output, showing detailed information about each test. 

## Configuration

The *project directory/.env* file contains variable settings. They are set with appropriate values.

* `FLASK_APP`: Entry point of the application (`wsgi.py`).
* `FLASK_ENV`: The environment in which to run the application (either `development` or `production`).
* `SECRET_KEY`: Secret key used to encrypt session data.
* `TESTING`: Set to False for running the application. Overridden and set to True automatically when testing the application.
* `WTF_CSRF_SECRET_KEY`: Secret key used by the WTForms library.
 
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