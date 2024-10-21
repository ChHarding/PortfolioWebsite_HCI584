from flask import Flask, render_template, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///projects.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

@app.route('/project_files/<path:filename>')
def project_files(filename):
    return send_from_directory(os.path.join(app.root_path, 'projects'), filename)

# Define Project model
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(100))
    pdf = db.Column(db.String(100))
    link = db.Column(db.String(200))

    def __repr__(self):
        return f'<Project {self.name}>'

#@app.route('/project_files/<path:filename>')
#def project_files(filename):
#    # Serve files from the 'projects' directory
#    return send_from_directory(os.path.join(app.root_path, 'projects'), filename)


'''
@app.route('/')
def home():
    project_dir = os.path.join(app.root_path, 'projects')
    projects = []

    # Loop through each subfolder in the projects directory
    if os.path.exists(project_dir):
        for project_folder in os.listdir(project_dir):
            folder_path = os.path.join(project_dir, project_folder)
            if os.path.isdir(folder_path):
                # Read project files (e.g., description.txt, image, pdf)
                description_path = os.path.join(folder_path, 'description.txt')
                image_filename = 'project_image.jpg'
                pdf_filename = 'project_document.pdf'
                link_path = os.path.join(folder_path, 'link.txt')

                if os.path.exists(description_path):
                    with open(description_path, 'r') as f:
                        description = f.read()
                else:
                    description = 'No description available.'

                if os.path.exists(link_path):
                    with open(link_path, 'r') as f:
                        link = f.read()

                # Check for image and PDF existence
                image_path = f'project_files/{project_folder}/{image_filename}' if os.path.exists(os.path.join(folder_path, image_filename)) else None
                pdf_path = f'project_files/{project_folder}/{pdf_filename}' if os.path.exists(os.path.join(folder_path, pdf_filename)) else None

                # Add to projects list
                projects.append({
                    'name': project_folder,
                    'description': description,
                    'image': image_path,
                    'link': link,
                    'pdf': pdf_path
                })

    return render_template('index.html', projects=projects)
'''

@app.route('/')
def home():
    project_dir = os.path.join(app.root_path, 'projects')

    # Step 1: Check if the 'projects' directory exists
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

    # Step 2: Fetch all projects from the database to display
    projects = Project.query.all()
    
    return render_template('index.html', projects=projects)

@app.route('/resume')
def resume():
    return render_template('resume.html', title='Resume')



if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables if they don't exist
    app.run(debug=True)
