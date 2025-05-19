# Personal Website with Automatic Resume Updates

This repository contains a personal website for Sai Balusu that automatically updates based on uploaded resumes. The website is built with Flask and includes a secure admin panel for resume management.

## Features

- Responsive personal website with about, experience, education, portfolio, and contact sections
- Secure admin panel with login authentication
- Automatic resume parsing and website content updates
- Contact form for visitor messages
- Security features including CSRF protection, secure session handling, and input validation

## Project Structure

```
personal_website/
├── src/
│   ├── models/         # Database and business logic
│   │   ├── resume_parser.py  # Resume parsing functionality
│   │   └── security.py       # Security utilities
│   ├── routes/         # Flask blueprint files (if needed)
│   ├── static/         # Static assets
│   │   ├── css/        # Stylesheets
│   │   ├── js/         # JavaScript files
│   │   ├── images/     # Image assets
│   │   └── uploads/    # Uploaded resumes (not tracked in git)
│   ├── templates/      # HTML templates
│   │   ├── layout.html       # Base template
│   │   ├── index.html        # Main website
│   │   ├── admin_login.html  # Admin login page
│   │   └── admin_dashboard.html  # Admin dashboard
│   └── main.py         # Main entry point for the Flask app
├── venv/              # Virtual environment (not tracked in git)
└── requirements.txt   # Python dependencies
```

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/SaiBalusu-usf/personal-website.git
   cd personal-website
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables (for production):
   ```
   export FLASK_APP=src/main.py
   export FLASK_ENV=production
   export SECRET_KEY=your_secret_key_here
   ```

### Running the Application

1. For development:
   ```
   python src/main.py
   ```

2. For production, use a WSGI server like Gunicorn:
   ```
   gunicorn -w 4 -b 0.0.0.0:5000 src.main:app
   ```

## Admin Access

The default admin credentials are:
- Username: admin
- Password: admin123

**Important:** Change these credentials immediately after first login in a production environment.

## Customization

### Updating Content

The website content is automatically updated when you upload a new resume through the admin panel. The system parses the resume and extracts:

- Personal information
- Professional summary
- Education history
- Work experience
- Skills and certifications

### Modifying Design

- CSS styles are in `src/static/css/style.css`
- JavaScript functionality is in `src/static/js/main.js`
- HTML templates are in `src/templates/`

## Security Features

- CSRF protection for all forms
- Secure password hashing
- Session timeout and management
- Input validation and sanitization
- Secure file uploads with type and size restrictions
- Content Security Policy and other security headers

## Deployment

This application can be deployed to any hosting service that supports Python/Flask applications, such as:

- Heroku
- AWS Elastic Beanstalk
- DigitalOcean
- PythonAnywhere

For domain configuration, update your DNS settings to point to your hosting provider.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Sai Balusu
