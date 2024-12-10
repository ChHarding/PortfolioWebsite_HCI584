# Developer's Guide 

## 1. Overview
 This is a Flask-based web application that serves as a portfolio/personal website. It allows the admin user to showcase their projects, resumes and non-admin users to view it.

 The current implementation includes the following key features and components:
    - Web pages: index.html, login.html, resume.html
    - Database: projects.db and  to store instances of project information
    - Python modules: main.py
    - External libraries: Flask web framework, SQLite database
   
 The project was built using Flask, a Python web framework, along with HTML, CSS, and JavaScript for the front end. The admin user's project data is stored in a SQLite database, which is accessed and managed through the Python modules. 

## 2. Condensed version
  All task vignettes, including Admin Login and Logout, project upload and deletion by admin users, project viewing, the feedback feature, and project display, have been implemented and are fully functional.

## 3. Install and Deployment
   - Login as an admin user and add project details.
   - Run main.py file and then open this link: http://127.0.0.1:5000/ where the file runs locally in your server

## 4. User Interaction & Code Flow
   - Upon opening the link, the user can see a navigation bar with options to log in (as admin), view project details (images, links, PDFs), and even give feedback and ratings to the portfolio owner.
   - Upon logging in, the admin can view an additional section where they can add more projects and delete existing projects.
   - The functions in the ```main.py``` and what it does is as follows:
     ### Authentication and Access Control Functions
    1. admin_required(f):
    - A decorator function that wraps route handlers
    - Checks if the user is logged in as an admin
    - If not logged in, redirects to login page with an error message
    - Protects admin-only routes by checking session['is_admin']
    
    2. login():
    - Handles both GET and POST requests to the login route
    - On GET  : Displays the login page
    - On POST : Validates credentials against hardcoded ADMIN_USERNAME and ADMIN_PASSWORD
                If credentials are correct: 
                  Sets session['is_admin'] to True
                  Flashes a success message
                  Redirects to home page
                  
   3. logout(): 
      - Clears the entire session
      - Flashes a logout success message
      - Redirects to the home page

   ### File Handling Functions
    4. allowed_file(filename):
      - Checks if a file has an allowed extension
      - Verifies the file extension is in the ALLOWED_EXTENSIONS set
      - Returns True if the file is allowed, False otherwise

   ### Route Handlers
   5. home():
    - Retrieves all projects from the database
    - If admin is logged in, also fetches all feedback
    - Passes projects and (optionally) feedbacks to the home template
    - Includes a flag indicating admin status

   6. add_project():
    - Protected by @admin_required decorator
    - Handles project creation with multiple steps:
         - Creates a secure project folder
         - Creates a new Project database record
         - Handles image uploads: 
             - Saves images to project folder
             - Tracks unique images
             - Sets first image as project's main image
               
  7. delete_project():
    - Protected by @admin_required decorator
    - Retrieves project by ID
    - Deletes project folder from file system
    - Removes project record from database
    - Handles potential errors with database rollback
    - Flashes success or error messages

  8. submit_feedback():
    - Receives feedback form submission
    - Creates a new Feedback database record
    - Handles optional project and rating associations
    - Commits feedback to database
    - Flashes success or error messages

 9. view_feedback():
    - Protected by @admin_required decorator
    - Retrieves all feedbacks, ordered by timestamp
    - Renders feedback template for admin review

   ### Utility Routes
  10. serve_static(filename):
      - Serves static files (like images, PDFs) from the static directory
      - Ensures secure file serving from a specific directory

  ### Initialization and Configuration
  11. if __name__ == '__main__'::
    - Creates database tables if they don't exist
    - Runs the Flask application in debug mode

  ### Classes
  1. ```Project```
      - Created when admin adds a new project via /add_project route
      - Stores core project information:
         - Allows displaying projects on the home page
         - Tracks project details like name, description, main image
         - Supports optional PDF documentation and external links 
     - Manages multiple project images through its images relationship
  2. ```ProjectImage```
      - Stores additional images beyond the main project image
      - Ensures each image is linked to a specific project
      - Allows storing multiple image paths for a single project
  3. ```Feedback```
      - Created when a user submits feedback via /submit_feedback route
      - Optional association with a specific project
      - Stores:
          - User's name and email
          - Feedback text
          - Optional project-specific rating
          - Timestamp of feedback submission
      - Enables admin to view all feedbacks via /view_feedback route

## 5. Known Issues
   - Username and password are hardcoded in the main.py
   - No option to edit the submitted project
   - When multiple images are uploaded, loading the last image will take quite some time; a feature that shows all the uploaded images in a grid layout will solve this. 

## 6. Future Work
   Future improvements may include adding an edit project features and adding testimonials. 

## TLDR: 
This Flask web application is a personal portfolio management system designed to showcase projects with a simple, secure admin interface. Administrators can add, delete, and manage projects by uploading multiple images, PDFs, and providing detailed descriptions. The application uses SQLAlchemy for database management, allowing flexible storage of project information with support for multiple images per project and optional documentation.

The system includes a straightforward authentication mechanism that allows admin-only access to project management features. Users can browse projects and submit feedback, which administrators can review. Each project can have multiple images, an optional PDF, and external links, providing a comprehensive way to display professional work. The feedback system enables visitors to provide comments and ratings, giving project owners insights into their work.

Built with Flask and SQLite, the application prioritizes simplicity and functionality. It includes basic security measures like file upload restrictions, input sanitization, and session-based authentication. While the current implementation is relatively simple, it provides a solid foundation for a personal portfolio website that can be easily expanded with additional features like more robust user management, enhanced authentication, and advanced project tracking. 
