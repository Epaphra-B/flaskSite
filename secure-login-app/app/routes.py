from flask import Blueprint, render_template, redirect, url_for, flash, request, session, send_file
from .forms import RegistrationForm, LoginForm
from .models import User
from .utils import hash_password, verify_password, save_user_photo
from . import db
from werkzeug.exceptions import NotFound
from io import BytesIO
import imghdr

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return redirect(url_for('main.login'))

@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user_photo_data = save_user_photo(form.user_photo.data)
        hashed_password = hash_password(form.password.data)
        
        user = User(
            first_name=form.first_name.data,
            middle_name=form.middle_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            password_hash=hashed_password,
            user_photo=user_photo_data
        )
        
        try:
            db.session.add(user)
            db.session.commit()
            flash(f'Account created! Your username is {user.user_id}. Please log in.', 'success')
            return redirect(url_for('main.login'))
        except:
            db.session.rollback()
            flash('An error occurred. Please try again.', 'danger')
    
    return render_template('register.html', form=form)

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        identifier = form.email_or_username.data.lower()
        user = User.query.filter((User.email == identifier) | (User.user_id == identifier)).first()
        
        if user and verify_password(user.password_hash, form.password.data):
            session['user_id'] = user.user_id
            flash('Login successful!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid email/username or password.', 'danger')
    
    return render_template('login.html', form=form)

@main.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please log in to access the dashboard.', 'danger')
        return redirect(url_for('main.login'))
    
    user = User.query.filter_by(user_id=session['user_id']).first()
    return render_template('dashboard.html', user=user)

@main.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('main.login'))

@main.route('/user_photo/<user_id>')
def user_photo(user_id):
    # Check if user is logged in
    if 'user_id' not in session:
        flash('Please log in to view this photo.', 'danger')
        return redirect(url_for('main.login'))
    
    # # Check if the logged-in user is authorized to view this photo
    if session['user_id'] != user_id:
        # raise Forbidden('URL not found or you do not have permission to access this resource.')
        return redirect(url_for('main.dashboard'))
    
    # Fetch the user
    user = User.query.filter_by(user_id=user_id).first()
    if not user or not user.user_photo:
        raise NotFound('Photo not found.')
    
    # Create a BytesIO object from the photo data
    photo_io = BytesIO(user.user_photo)
    
    # Detect image format
    image_format = imghdr.what(None, h=user.user_photo)
    if image_format not in ['jpeg', 'jpg', 'png']:
        raise ValueError('Unsupported image format')
        
    # Set the appropriate MIME type based on the image format
    mime_type = f'image/{image_format if image_format != "jpg" else "jpeg"}'
    
    # Return the photo with the detected MIME type
    return send_file(
        photo_io,
        mimetype=mime_type,
        as_attachment=False
    )

