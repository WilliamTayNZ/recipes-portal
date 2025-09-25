from flask import Blueprint, request, render_template, abort, session, redirect, url_for

from better_profanity import profanity
from flask_wtf import FlaskForm
from wtforms import TextAreaField, HiddenField, SubmitField, RadioField
from wtforms.validators import DataRequired, Length, ValidationError, Optional
from wtforms.validators import DataRequired, Length, ValidationError

import recipe.adapters.repository as repo
import recipe.blueprints.browse.services as browse_services
import recipe.blueprints.recipe.services as recipe_services

from recipe.blueprints.authentication.authentication import login_required

recipe_blueprint = Blueprint('recipe_bp', __name__)

@recipe_blueprint.route('/recipe/<int:recipe_id>', methods=['GET'])
def recipe(recipe_id):
    # Get the recipe from the repository
    recipe_obj = repo.repo_instance.get_recipe_by_id(recipe_id)
    
    if recipe_obj is None:
        abort(404)  # Recipe not found

    # Create an instance of the review form
    form = ReviewForm()

    # Ensure favourite state is annotated
    try:
        browse_services.annotate_is_favourite([recipe_obj], repo.repo_instance)
    except Exception:
        pass

    return render_template('recipe.html', recipe=recipe_obj, form=form)

@recipe_blueprint.route('/recipe/<int:recipe_id>/review', methods=['POST'])
@login_required
def review_on_recipe(recipe_id):
    # Get the recipe from the repository
    recipe_obj = repo.repo_instance.get_recipe_by_id(recipe_id)
    
    if recipe_obj is None:
        abort(404)  # Recipe not found

    # Get form data
    user_name = session['user_name']
    form = ReviewForm()

    if form.validate_on_submit():

        try:
            recipe_services.add_review(recipe_id, form.review.data or "", float(form.rating.data), user_name, repo.repo_instance)
            return redirect(url_for('recipe_bp.recipe', recipe_id=recipe_id) + '#reviews')
        except Exception as e:
            form.review.errors.append(str(e))

    # If we get here, either form validation failed or there was an error
    
    # Ensure favourite state is annotated
    try:
        browse_services.annotate_is_favourite([recipe_obj], repo.repo_instance)
    except Exception:
        pass

    # When re-rendering with errors, include anchor in the response
    return render_template('recipe.html', recipe=recipe_obj, form=form), 422


class ProfanityFree:
    def __init__(self, message=None):
        if not message:
            message = u'Field must not contain profanity'
        self.message = message

    def __call__(self, form, field):
        if profanity.contains_profanity(field.data):
            raise ValidationError(self.message)

class ReviewForm(FlaskForm):
    rating = RadioField('Rating', 
        choices=[(str(i), str(i)) for i in range(1, 6)],
        validators=[DataRequired(message='Please select a rating')])
    review = TextAreaField('Review (optional)', [
        Optional(),
        Length(min=4, message='If providing a review, it must be at least 4 characters'),
        ProfanityFree(message='Your review must not contain profanity')])
    recipe_id = HiddenField("Recipe id")
    submit = SubmitField('Submit')