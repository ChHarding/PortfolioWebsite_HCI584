# PortfolioWebsite_HCI584
 This project is to build a personal portfolio website using the Flask framework. The website will showcase the admin's professional projects, personal information, and an image gallery.
User's Guide

# 1. Overview
This is a Flask-based web application that serves as a portfolio and personal website. It allows the user to showcase their projects, resume, and other relevant information.

# 2. Installation and Setup

To run the portfolio/website application, follow these steps:

1. **Clone or Download the Repository**
   - Clone the project repository from GitHub.

2. **Set up the Development Environment**
   - Install the required Python packages:
     ```
     pip install -r requirements.txt
     ```

4. **Create the Database (if applicable)**
   This project uses a SQLite database to store the user's project information.
   To create the initial projects.db file, run the following command in your terminal:
     ```
     python main.py
     ```
   - This will generate the `projects.db` file in the project's root directory.

6. **Run the Application**
   - To start the Flask application, run the following command in your terminal:
     ```
     python main.py
     ```
   - The application should now be running, and you can access it in your web browser at `http://localhost:5000`.

## Using the Portfolio/Website

### Home Page
When you first access the application, you'll see the home page, which provides a general introduction and navigation to other sections of the website.
![image](https://github.com/user-attachments/assets/dbc62a56-63f8-4403-8f76-b5a3af4ac5ba)


### Project Showcase
You can view a list of the portfolio owner's projects on the project showcase page. Each project is represented by a set of files in the `project_files` directory.
![image](https://github.com/user-attachments/assets/e9590f1a-5bd9-4c78-9eb7-de4de2300ddd)


### Login (if applicable)
If the portfolio owner needs to update their information, they can log in to the system using the login page.
![Uploading image.png…]()


## Troubleshooting
These are some errors you may encounter while running the application

**Error: "SQLite database file does not exist"**
- Run `python main.py` to generate the initial `projects.db` file.


## Limitations and Future Enhancements

The current version of the portfolio/website application has the following limitations:

- The login functionality is basic and does not include advanced security measures.
- The project showcase section is limited to displaying a list of projects and does not support features like sorting, filtering, or pagination.
- Admin users are not able to edit the projects that are uploaded. 

