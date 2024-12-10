from flask import Flask, render_template, send_from_directory, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from functools import wraps 
from werkzeug.utils import secure_filename
import os
import shutil
from datetime import datetime

app = Flask(__name__)
app.secret_key = '1234'

# Admin credentials
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = '1234'

# Configure upload folder and database
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'static', 'project_files')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///projects.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

db = SQLAlchemy(app)

# Models
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(200))
    pdf = db.Column(db.String(100))
    link = db.Column(db.String(200))
    images = db.relationship('ProjectImage', backref='project', lazy=True, cascade="all, delete-orphan")

class ProjectImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            flash('You must be an admin to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():

    # Fetch all projects
    projects = Project.query.all()
    
    # Fetch feedbacks if admin is logged in
    feedbacks = []
    if session.get('is_admin'):
        feedbacks = Feedback.query.order_by(Feedback.timestamp.desc()).all()
    
    is_admin = session.get('is_admin', False)

    return render_template('index.html', 
                           projects=projects, 
                           feedbacks=feedbacks,
                           is_admin=is_admin)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == ADMIN_USERNAME and request.form['password'] == ADMIN_PASSWORD:
            session['is_admin'] = True
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        flash('Invalid credentials', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.')
    return redirect(url_for('home'))

@app.route('/resume')
def resume():
    return send_from_directory('static', 'resume.pdf')


@app.route('/add_project', methods=['POST'])
@admin_required
def add_project():
    try:
        project_name = secure_filename(request.form['project_name'])
        description = request.form['description']
        link = request.form.get('link', '')

        # Create project folder
        project_folder = os.path.join(app.config['UPLOAD_FOLDER'], project_name)
        os.makedirs(project_folder, exist_ok=True)

        # Create new project
        new_project = Project(
            name=project_name,
            description=description,
            link=link
        )
        db.session.add(new_project)
        db.session.flush()

        # Handle images
        # Handle images
        images = request.files.getlist('images')
        existing_images = set()  # Track unique filenames

        for image in images:
            if image and image.filename and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                
                # Skip if this exact filename has already been processed
                if filename in existing_images:
                    continue
                
                image_path = os.path.join(project_folder, filename)
                image.save(image_path)
                
                relative_path = f'project_files/{project_name}/{filename}'
                
                # Set first unique image as main project image
                if not new_project.image:
                    new_project.image = relative_path
                
                # Only add unique images
                new_image = ProjectImage(
                    filename=relative_path,
                    project_id=new_project.id
                )
                db.session.add(new_image)
                
                # Mark this filename as processed
                existing_images.add(filename)

        # Handle PDF
        pdf_file = request.files.get('pdf')
        if pdf_file and pdf_file.filename and allowed_file(pdf_file.filename):
            pdf_filename = secure_filename(pdf_file.filename)
            pdf_path = os.path.join(project_folder, pdf_filename)
            pdf_file.save(pdf_path)
            new_project.pdf = f'project_files/{project_name}/{pdf_filename}'

        db.session.commit()
        flash(f'Project "{project_name}" added successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding project: {str(e)}', 'error')
    
    return redirect(url_for('home'))

@app.route('/delete_project', methods=['POST'])
@admin_required
def delete_project():
    try:
        project_id = request.form.get('project_id')
        project = Project.query.get_or_404(project_id)
        
        # Delete project folder
        project_folder = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(project.name))
        if os.path.exists(project_folder):
            shutil.rmtree(project_folder)
        
        # Delete database record
        db.session.delete(project)
        db.session.commit()
        
        flash(f'Project "{project.name}" deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting project: {str(e)}', 'error')
    
    return redirect(url_for('home'))

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(os.path.join(BASE_DIR, 'static'), filename)

# Create Feedback Model
class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=True)
    feedback_text = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship to Project (optional)
    project = db.relationship('Project', backref=db.backref('feedbacks', lazy=True))

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    try:
        # Get form data
        name = request.form['name']
        email = request.form['email']
        feedback_text = request.form['feedback']
        project_id = request.form.get('project')
        rating = request.form.get('rating')

        # Create new feedback entry
        new_feedback = Feedback(
            name=name,
            email=email,
            feedback_text=feedback_text,
            project_id=project_id if project_id else None,
            rating=int(rating) if rating else None
        )

        # Add to database
        db.session.add(new_feedback)
        db.session.commit()

        # Flash success message
        flash('Thank you for your feedback!', 'success')
    except Exception as e:
        # Handle any errors
        db.session.rollback()
        flash(f'Error submitting feedback: {str(e)}', 'error')

    # Redirect back to home page
    return redirect(url_for('home'))

# Update home route to include feedback display for admin
@app.route('/view_feedback')
@admin_required
def view_feedback():
    # Fetch all feedbacks, optionally filter by project
    feedbacks = Feedback.query.order_by(Feedback.timestamp.desc()).all()
    return render_template('feedback.html', feedbacks=feedbacks)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)