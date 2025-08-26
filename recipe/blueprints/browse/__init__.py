from flask import Blueprint, render_template

browse_blueprint = Blueprint('home_bp', __name__)

@browse_blueprint.route('/', methods=['GET'])
def browse():
    return render_template()