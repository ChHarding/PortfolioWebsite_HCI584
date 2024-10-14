from flask import Flask, render_template

app = Flask(__name__, template_folder='flask/templates', static_folder='flask/static')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/project/<int:project_id>')
def project_detail(project_id):
    projects = {
        1: {'name': 'Project One', 'description': 'Description of Project One'},
        2: {'name': 'Project Two', 'description': 'Description of Project Two'}
    }
    project = projects.get(project_id, None)
    if project:
        return render_template('project_detail.html', project=project)
    else:
        return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
