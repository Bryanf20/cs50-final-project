import os

class Config:
    DEBUG = True
    SECRET_KEY = os.environ.get('SECRET_KEY', '12345678')  # Use an environment variable in production
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///study_group.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TEMPLATES_AUTO_RELOAD = True

    # Flask-Mail Configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT'))  # Convert to integer
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') == 'True'  # Convert to boolean
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL') == 'True'  # Convert to boolean
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = (
        os.environ.get('MAIL_SENDER_NAME', ''),
        os.environ.get('MAIL_SENDER_EMAIL', '')
    )
    # Configure file upload settings
    UPLOADED_FILES_DEST = os.environ.get('UPLOADED_FILES_DEST')  # Folder to store uploaded files
    UPLOADED_FILES_ALLOW = os.environ.get('UPLOADED_FILES_ALLOW')
