"""Initialize Flask app."""
from datetime import datetime
from flask import Flask, render_template

from recipe.blueprints.home.home import home_blueprint
# TODO: Access to the recipe should be implemented via the repository pattern and using blueprints, so this can not
#  stay here!

from recipe.domainmodel.recipe import Recipe
from recipe.domainmodel.author import Author


# TODO: Access to the recipe should be implemented via the repository pattern and using blueprints, so this can not
#  stay here!
def create_some_recipe():
    some_author = Author(1752, "Bob Ross")
    some_recipe = Recipe(221, "Chocolate Chip Muffins", some_author)
    some_recipe.description = "When I find my bananas getting too ripe I freeze them for later use.  Just thaw them in the microwave when you want to use.  Here is a recipe for chocolate chip muffins that uses one banana. They even taste healthy :-)"
    some_recipe.images = ['https://img.sndimg.com/food/image/upload/w_555,h_416,c_fit,fl_progressive,q_95/v1/img/recipes/22/1/picmE4uiZ.jpg',
     'https://img.sndimg.com/food/image/upload/w_555,h_416,c_fit,fl_progressive,q_95/v1/img/recipes/22/1/picjXaLFo.jpg']
    return some_recipe


def create_app():
    """Construct the core application."""

    # Create the Flask app object.
    app = Flask(__name__)

    with app.app_context():
        # Register blueprints.
        from .blueprints.home.home import home_blueprint
        app.register_blueprint(home_blueprint)



    return app
