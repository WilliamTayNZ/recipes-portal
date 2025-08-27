from flask import Blueprint, render_template

browse_blueprint = Blueprint('browse_bp', __name__)

@browse_blueprint.route('/browse', methods=['GET'])
def browse():
    return render_template('browse.html')