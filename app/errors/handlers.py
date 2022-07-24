from turtle import title
from flask import render_template
from app import db
from app.errors import bp

"""
Each of these routes is associated with an error code
If the user encounters an error they will be shown the respective URL
This avoids showing the user default error pages which can be a security risk
"""
@bp.app_errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html', title="ERROR"), 404


@bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html', title="ERROR"), 500


@bp.app_errorhandler(403)
def internal_error(error):
    return render_template('errors/403.html', title="ERROR"), 403


@bp.app_errorhandler(405)
def internal_error(error):
    return render_template('errors/405.html', title="ERROR"), 405

    