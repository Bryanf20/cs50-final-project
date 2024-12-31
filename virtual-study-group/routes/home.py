from flask import Blueprint, render_template
from models.group import Group

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def home():
    groups = Group.query.all()
    print(groups)
    return render_template('home.html', groups=groups)
