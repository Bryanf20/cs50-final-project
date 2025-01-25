# Virtual Study Group Web Application

## Video Demo: [YouTube](https://youtu.be/_KAktPEzHAg?si=3nJ0fjs6SWEgKL4-)

## Overview

This web application is designed to help students create, manage, and collaborate in virtual study groups. It provides a comprehensive platform for academic collaboration, resource sharing, and group study coordination.

## Features

- **User Authentication**
  - Secure sign-up and login system
  - Role-based access control
  - User profile management

- **Group Management**
  - Create and join study groups
  - Invite members via email
  - Manage group settings

- **Meeting Scheduler**
  - Schedule group study sessions
  - Meeting link generation (google meet/ zoom)

- **Resource Sharing**
  - Upload and share study materials
  - Easy resource discovery

- **Communication Tools**
  - Group chat and discussion forum
  - Collaborative communication

- **Progress Tracking**
  - Individual and group study goal tracking
  - Performance insights

- **Notifications**
  - In-app notifications

## Tech Stack

### Backend

- Flask and its associated libraries

### Frontend

- HTML
- CSS
- Bootstrap
- JavaScript

### Database

- SQLite3 (SQLAlchemy)

### File Storage

- Local Storage

## Files

### Forms

This folder contains the forms I will use on my HTML templates. The idea is to do this for all the forms on my HTML pages. Organizing forms this way improves maintainnability, enhances functionality and reusability. Here are the various forms I created

- accept_invite_form.py - For users to accept group invites after they recieve an email invite
- edit_group_form.py - To edit group details
- group_form.py - For the creation of groups
- login_form.py - For Loggin in
- registration_form.py - For user registration
- resource_form.py - For uploading group resources (e.g. pdf files)
- schedule_meeting_form.py - For scheduling group meetings

### Models

Instead of hard coding my database, i opted to use models with Flask SQLAlchemy, this method simplifies db management, for example it enhances scalability, maintainability, security, less error prone. I created seperate python files to group related models within each. Below is a description of each

- chat.py - Contains the db model for the group chat feature. It cotains a relationship with the group model and the user model.

- group.py - This file contains 3 models, the group model, the group_member model and the group invite model. The group model will createt the table to store all created groups, meanwhile the group_member model has a relationship with the group model. As for the groupInvite model, this will create the table to store all group invites.

- meeting.py - This file contains the meeting model. This models contains a method to create a notification and to create a reminder when the due date draws close. The reminder method creates a reminder when the meeting is due within a day and another two hours before it is due.

- notification.py - This file contains the model to create the table to store notifications.

- resource.py - This file contains the model to create the table to store all uploaded resources. Note that, the resource table only stores the link to the resource and not the actual resource.

- task_progress.py - This file contains the model to create the table to store tasks and their due dates. It also contains methods to checke due dates, create notifications and notify members. The check_due_date method check for upcomming task due dates and then notify the members assign to said task. For task without members assigned to, every gets to receive a notification.

- user.py - Contains model to create user table. This user model has some methods and properties. The properties are, is_active, is_authenticated and is_anonymous. For the methods, we have a method to set_password, to check_password and a method that uses the group relationship to know if a user is a member osf a specific group.

### Routes

- auth.py - Contains my register, login, delete account, change password and logout methods. I use Flask-login library for authentication.

- chat.py - This contains the functions for viewing and posting group chat messages. I used flask-socketio library for this.

- groups.py - This file contains majority of the methods for this app. It has methods to handle CRUD operations for the groups. Also has an invite function that sends emails to people who vave been invited to join a group. Once you follow this invite link you can then create an account(if you don't have one) then join the group. We also have methods to handle meeting operations, a method to upload resourses, a method for users to leave a group and a method for the admin to remove group members.

- home.py - Has a function that renders my home page.

- notification.py - Has a function to mark notifications as read.

- progress.py - This file contains methods to monitor task progres, add task, delete task, and edit task. It also has a method to update task status.

### Static

This folder contains the custom css files i wrote for my project to handle toast notifications. It also conntains a chat.css file used by the view_chat.html file to style the chat page. This folde also contains an upload folder for all files uploaded from a group.

### Templates

The templates folder has all the HTML files for this project. I divide them into, sub folders to ease troubleshooting. I have a base.html template that has elements that i import to all other templates.

### Other files

- app.py - This is the main file of the project. Without this the project won't run.

- config.py - contains my database, email and upload configurations.

- scheduler.py - This file contains task that are supposed to run at a particular time. I created a scheduler fo notifications and to delete meetins that have passed.

- requirements.txt - Has all the necessary libraries to run this project.

## Prerequisites

- Python 3.8+
- pip
- Virtual environment (recommended)

## Installation

1. Clone the repository

   ```bash
   git clone https://github.com/Bryanf20/cs50-final-project.git
   cd virtual-study-group
   ```

2. Create a virtual environment

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install dependencies

   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables
   - Create a `.env` file
   - Add necessary configuration variables
   - Use the example below for your `.env` file

   ```bash
    FLASK_ENV=development
    FLASK_APP=app.py
    FLASK_DEBUG=1

    SECRET_KEY=your secret key(random number)
    DATABASE_URL=sqlite:///study_group.db
    MAIL_SERVER=your mail server
    MAIL_PORT=587
    MAIL_USE_TLS=True
    MAIL_USE_SSL=False
    MAIL_USERNAME=youremail@email.com
    MAIL_PASSWORD=your password
    MAIL_SENDER_NAME="Virtual Study Group"
    MAIL_SENDER_EMAIL=youremail@email.com

    UPLOADED_FILES_DEST='static/uploads'  # Folder to store uploaded files
    UPLOADED_FILES_ALLOW=['pdf', 'docx', 'txt', 'jpg', 'png', 'md']
   ```

5. Initialize the database

   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

6. Run the application

   ```bash
   cd virtual-study-group
   flask run
   ```

## Configuration

- Configure database settings in `.env`
- Set up email services for notifications
- Configure file storage options

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Future Works

### Deployment

- Recommended platforms: Heroku, AWS, DigitalOcean
- Use PostgreSQL for production
- Configure environment-specific settings

### Security Considerations

- Implement HTTPS
- Use strong password hashing
- Implement proper access controls
- Regular security audits

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Contact

Bryan .F - <fongangbryan@gmail.com>

Project Link: [https://github.com/Bryanf20/cs50-final-project](https://github.com/Bryanf20/cs50-final-project)

## Acknowledgements

- Flask
- Bootstrap
- SQLAlchemy
- ChatGPT
