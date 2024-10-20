from flask import Flask, render_template, send_from_directory
import os

app = Flask(__name__)

@app.route('/project_files/<path:filename>')
def project_files(filename):
    # Serve files from the 'projects' directory
    return send_from_directory(os.path.join(app.root_path, 'projects'), filename)


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
@app.route('/resume')
def resume():
    return render_template('resume.html', title='Resume')

if __name__ == '__main__':
    app.run(debug=True)
