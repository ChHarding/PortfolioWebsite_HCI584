from flask import Flask, render_template, send_from_directory,  redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from functools import wraps 
from werkzeug.utils import secure_filename
import os
import shutil

app = Flask(__name__)

app.secret_key = '1234'

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = '1234'

app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'projects')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        #user = User.query.filter_by(username=username, password=password).first()

        if username == 'admin' and password == '1234':
            session['user_id'] = username
            session['is_admin'] = True    
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials', 'error')

    return render_template('login.html')  # Render login form

@app.route('/logout')
def logout():
    # Clear all session data
    session.clear()
    flash('You have been logged out successfully.')
    return redirect(url_for('home'))


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///projects.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

@app.route('/project_files/<path:filename>')
def project_files(filename):
    return send_from_directory(os.path.join(app.root_path, 'projects'), filename)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

# Define Project model
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(200))
    pdf = db.Column(db.String(100))
    link = db.Column(db.String(200))

    def __repr__(self):
        return f'<Project {self.name}>'


@app.route('/')
def home():
    project_dir = os.path.join(app.root_path, 'projects')

    # Check if the 'projects' directory exists
    if os.path.exists(project_dir):
        # Loop through each subfolder in the projects directory
        for project_folder in os.listdir(project_dir):
            folder_path = os.path.join(project_dir, project_folder)
            
            if os.path.isdir(folder_path):
                # Read project files (e.g., description.txt, image, pdf, link)
                description_path = os.path.join(folder_path, 'description.txt')
                image_filename = 'project_image.jpg'
                pdf_filename = 'project_document.pdf'
                link_path = os.path.join(folder_path, 'link.txt')

                # Check if the project is already in the database
                existing_project = Project.query.filter_by(name=project_folder).first()

                if not existing_project:
                    # Extract description
                    if os.path.exists(description_path):
                        with open(description_path, 'r') as f:
                            description = f.read()
                    else:
                        description = 'No description available.'

                    # Extract link
                    if os.path.exists(link_path):
                        with open(link_path, 'r') as f:
                            link = f.read()
                    else:
                        link = None

                    # Check for image and PDF existence
                    image_path = f'project_files/{project_folder}/{image_filename}' if os.path.exists(os.path.join(folder_path, image_filename)) else None
                    pdf_path = f'project_files/{project_folder}/{pdf_filename}' if os.path.exists(os.path.join(folder_path, pdf_filename)) else None
                    

                    # Add project to database
                    new_project = Project(
                        description=description,
                        link=link,
                        pdf=pdf_path,
                        image=image_path,
                        name=project_folder
                    )
                    db.session.add(new_project)
                    db.session.commit()

    # Fetch all projects from the database to display
    projects = Project.query.all()
    
    is_admin = session.get('is_admin', False)

    return render_template('index.html', projects=projects)

@app.route('/resume')
def resume():
    return render_template('resume.html', title='Resume')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or not session.get('is_admin', False):
            flash('You do not have permission to access this page.', 'error')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/delete_project', methods=['POST'])
def delete_project():
    
    project_id = request.form.get('project_id')
    project = Project.query.get(project_id)
    project_folder = os.path.join(app.config['UPLOAD_FOLDER'], project.name)

    if project:
        # Delete the project from the database
        db.session.delete(project)
        db.session.commit()
        #shutil.rmtree(project_folder)
        print(f"1. Project '{project.name}' has been deleted successfully.", "success")
        print(f"Trying to delete folder: {project_folder}")
        if os.path.exists(project_folder):
            try:
                print(f"2. Folder {project_folder} exists. Attempting to delete it from root.")
                # Remove the project folder and all its contents
                shutil.rmtree(project_folder)
                flash(f'Project "{project_id}" has been deleted successfully.')
                print(f"Successfully deleted folder: {project_folder}")
            except Exception as e:
                print(f"Error deleting project: {str(e)}")
                flash(f'Error deleting project: {str(e)}')
        else:
            flash(f'Project "{project_id}" does not exist.')
    else:
        print("Project not found.", "error")
    

    return redirect(url_for('home'))

@app.route('/add_project', methods=['POST'])
def add_project():
    if not session.get('is_admin'):
        flash('You do not have permission to add projects.')
        return redirect(url_for('home'))

    project_name = request.form['project_name']
    description = request.form['description']
    link = request.form.get('link', '')

    # Create the project directory
    project_folder = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(project_name))
    if not os.path.exists(project_folder):
        os.makedirs(project_folder)

    # Save the description
    with open(os.path.join(project_folder, 'description.txt'), 'w') as f:
        f.write(description)

    # Save the optional link
    if link:
        with open(os.path.join(project_folder, 'link.txt'), 'w') as f:
            f.write(link)

    # Save the image file if uploaded
    image_file = request.files.get('image')
    if image_file:
        image_filename = secure_filename(image_file.filename)
        image_file.save(os.path.join(project_folder, image_filename))

    # Save the PDF file if uploaded
    pdf_file = request.files.get('pdf')
    if pdf_file:
        pdf_filename = secure_filename(pdf_file.filename)
        pdf_file.save(os.path.join(project_folder, pdf_filename))

    flash(f'Project "{project_name}" has been added successfully.')
    return redirect(url_for('home'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables if they don't exist
    app.run(debug=True)
