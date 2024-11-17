from flask import Flask, render_template, send_from_directory, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from functools import wraps 
from werkzeug.utils import secure_filename
import os
import shutil

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
    projects = Project.query.all()
    return render_template('index.html', projects=projects)

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
        images = request.files.getlist('images')
        for i, image in enumerate(images):
            if image and image.filename and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                image_path = os.path.join(project_folder, filename)
                image.save(image_path)
                
                relative_path = f'project_files/{project_name}/{filename}'
                
                if i == 0:  # Set first image as main project image
                    new_project.image = relative_path
                
                new_image = ProjectImage(
                    filename=relative_path,
                    project_id=new_project.id
                )
                db.session.add(new_image)

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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)