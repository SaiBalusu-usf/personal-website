from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, abort, send_from_directory
import os
import sys
import json
import datetime
from werkzeug.utils import secure_filename
import PyPDF2

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import security module
from src.models.security import configure_app_security, login_required, csrf_protected, allowed_file, hash_password, verify_password

# Create Flask app
app = Flask(__name__)

# Configure security
app = configure_app_security(app)

# Set upload folder
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Admin credentials - in production, these would be stored securely in environment variables
# For demo purposes, we'll use a simple hash with salt
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD_HASH, ADMIN_SALT = hash_password('admin123')

# Resume storage
RESUME_DATA_FILE = os.path.join(app.config['UPLOAD_FOLDER'], 'resume_data.json')

# Import resume parser
from src.models.resume_parser import extract_resume_content, parse_resume, update_website_from_resume

def load_resume_data():
    if os.path.exists(RESUME_DATA_FILE):
        with open(RESUME_DATA_FILE, 'r') as f:
            return json.load(f)
    return {'resumes': []}

def save_resume_data(data):
    with open(RESUME_DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# Routes
@app.route('/')
def index():
    # Load website data if it exists
    website_data_file = os.path.join(app.config['UPLOAD_FOLDER'], 'website_data.json')
    website_data = {}
    if os.path.exists(website_data_file):
        with open(website_data_file, 'r') as f:
            website_data = json.load(f)
    
    return render_template('index.html', data=website_data)

@app.route('/contact', methods=['POST'])
@csrf_protected
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        # Validate inputs
        if not all([name, email, subject, message]):
            return jsonify({'success': False, 'message': 'All fields are required'})
        
        # In a real application, you would save this to a database
        # and/or send an email notification
        
        # For now, we'll just save to a JSON file
        contact_file = os.path.join(app.config['UPLOAD_FOLDER'], 'contact_messages.json')
        
        # Load existing messages
        messages = []
        if os.path.exists(contact_file):
            with open(contact_file, 'r') as f:
                try:
                    messages = json.load(f)
                except:
                    messages = []
        
        # Add new message
        messages.append({
            'name': name,
            'email': email,
            'subject': subject,
            'message': message,
            'date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
        # Save messages
        with open(contact_file, 'w') as f:
            json.dump(messages, f, indent=4)
        
        return jsonify({'success': True, 'message': 'Your message has been sent successfully!'})
    
    return jsonify({'success': False, 'message': 'Invalid request method'})

@app.route('/admin')
def admin():
    return redirect(url_for('admin_login'))

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.content_type == 'application/json':
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
        else:
            username = request.form.get('username')
            password = request.form.get('password')
        
        # Check credentials
        if username == ADMIN_USERNAME and verify_password(password, ADMIN_PASSWORD_HASH, ADMIN_SALT):
            session['logged_in'] = True
            session['last_activity'] = datetime.datetime.now().timestamp()
            
            if request.content_type == 'application/json':
                return jsonify({'success': True})
            return redirect(url_for('admin_dashboard'))
        else:
            if request.content_type == 'application/json':
                return jsonify({'success': False, 'message': 'Invalid credentials'})
            flash('Invalid credentials', 'error')
    
    return render_template('admin_login.html', csrf_token=session.get('csrf_token', ''))

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    # Check session timeout
    last_activity = session.get('last_activity', 0)
    if datetime.datetime.now().timestamp() - last_activity > app.config['PERMANENT_SESSION_LIFETIME']:
        session.clear()
        return redirect(url_for('admin_login'))
    
    # Update last activity
    session['last_activity'] = datetime.datetime.now().timestamp()
    
    # Load resume data
    resume_data = load_resume_data()
    return render_template('admin_dashboard.html', 
                          resumes=resume_data.get('resumes', []),
                          csrf_token=session.get('csrf_token', ''))

@app.route('/admin/upload-resume', methods=['POST'])
@login_required
@csrf_protected
def upload_resume():
    # Check session timeout
    last_activity = session.get('last_activity', 0)
    if datetime.datetime.now().timestamp() - last_activity > app.config['PERMANENT_SESSION_LIFETIME']:
        session.clear()
        return redirect(url_for('admin_login'))
    
    # Update last activity
    session['last_activity'] = datetime.datetime.now().timestamp()
    
    if 'resume' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('admin_dashboard'))
    
    file = request.files['resume']
    
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('admin_dashboard'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        new_filename = f"{timestamp}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
        file.save(file_path)
        
        # Extract and parse resume content
        content = extract_resume_content(file_path)
        if content:
            parsed_data = parse_resume(content)
            
            # Save resume metadata
            resume_data = load_resume_data()
            resume_id = len(resume_data.get('resumes', [])) + 1
            
            resume_entry = {
                'id': resume_id,
                'filename': filename,
                'stored_filename': new_filename,
                'upload_date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'parsed': True if parsed_data else False
            }
            
            resume_data.setdefault('resumes', []).append(resume_entry)
            save_resume_data(resume_data)
            
            # Save parsed data
            if parsed_data:
                parsed_data_file = os.path.join(app.config['UPLOAD_FOLDER'], f"parsed_{resume_id}.json")
                with open(parsed_data_file, 'w') as f:
                    json.dump(parsed_data, f, indent=4)
            
            flash('Resume uploaded successfully', 'success')
        else:
            flash('Failed to extract content from the resume', 'error')
    else:
        flash('Invalid file type. Only PDF files are allowed.', 'error')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/view-resume/<int:resume_id>')
@login_required
def view_resume(resume_id):
    # Check session timeout
    last_activity = session.get('last_activity', 0)
    if datetime.datetime.now().timestamp() - last_activity > app.config['PERMANENT_SESSION_LIFETIME']:
        session.clear()
        return redirect(url_for('admin_login'))
    
    # Update last activity
    session['last_activity'] = datetime.datetime.now().timestamp()
    
    resume_data = load_resume_data()
    resume = next((r for r in resume_data.get('resumes', []) if r['id'] == resume_id), None)
    
    if not resume:
        abort(404)
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], resume['stored_filename'])
    return send_from_directory(os.path.dirname(file_path), os.path.basename(file_path))

@app.route('/admin/apply-resume/<int:resume_id>')
@login_required
def apply_resume(resume_id):
    # Check session timeout
    last_activity = session.get('last_activity', 0)
    if datetime.datetime.now().timestamp() - last_activity > app.config['PERMANENT_SESSION_LIFETIME']:
        session.clear()
        return redirect(url_for('admin_login'))
    
    # Update last activity
    session['last_activity'] = datetime.datetime.now().timestamp()
    
    resume_data = load_resume_data()
    resume = next((r for r in resume_data.get('resumes', []) if r['id'] == resume_id), None)
    
    if not resume:
        abort(404)
    
    # Check if parsed data exists
    parsed_data_file = os.path.join(app.config['UPLOAD_FOLDER'], f"parsed_{resume_id}.json")
    if not os.path.exists(parsed_data_file):
        # Try to parse it now
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], resume['stored_filename'])
        content = extract_resume_content(file_path)
        if content:
            parsed_data = parse_resume(content)
            with open(parsed_data_file, 'w') as f:
                json.dump(parsed_data, f, indent=4)
        else:
            flash('Failed to extract content from the resume', 'error')
            return redirect(url_for('admin_dashboard'))
    
    # Load parsed data
    with open(parsed_data_file, 'r') as f:
        parsed_data = json.load(f)
    
    # Update website with parsed data
    success = update_website_from_resume(parsed_data, app.config['UPLOAD_FOLDER'])
    
    if success:
        flash('Website updated successfully with the selected resume', 'success')
    else:
        flash('Failed to update website with the selected resume', 'error')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete-resume/<int:resume_id>')
@login_required
def delete_resume(resume_id):
    # Check session timeout
    last_activity = session.get('last_activity', 0)
    if datetime.datetime.now().timestamp() - last_activity > app.config['PERMANENT_SESSION_LIFETIME']:
        session.clear()
        return redirect(url_for('admin_login'))
    
    # Update last activity
    session['last_activity'] = datetime.datetime.now().timestamp()
    
    resume_data = load_resume_data()
    resume = next((r for r in resume_data.get('resumes', []) if r['id'] == resume_id), None)
    
    if not resume:
        abort(404)
    
    # Delete the file
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], resume['stored_filename'])
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # Delete parsed data if exists
    parsed_data_file = os.path.join(app.config['UPLOAD_FOLDER'], f"parsed_{resume_id}.json")
    if os.path.exists(parsed_data_file):
        os.remove(parsed_data_file)
    
    # Update resume data
    resume_data['resumes'] = [r for r in resume_data.get('resumes', []) if r['id'] != resume_id]
    save_resume_data(resume_data)
    
    flash('Resume deleted successfully', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/logout')
@login_required
def logout():
    session.clear()
    flash('You have been logged out', 'success')
    return redirect(url_for('admin_login'))

@app.route('/admin/view-messages')
@login_required
def view_messages():
    # Check session timeout
    last_activity = session.get('last_activity', 0)
    if datetime.datetime.now().timestamp() - last_activity > app.config['PERMANENT_SESSION_LIFETIME']:
        session.clear()
        return redirect(url_for('admin_login'))
    
    # Update last activity
    session['last_activity'] = datetime.datetime.now().timestamp()
    
    # Load contact messages
    contact_file = os.path.join(app.config['UPLOAD_FOLDER'], 'contact_messages.json')
    messages = []
    if os.path.exists(contact_file):
        with open(contact_file, 'r') as f:
            try:
                messages = json.load(f)
            except:
                messages = []
    
    return render_template('admin_messages.html', 
                          messages=messages,
                          csrf_token=session.get('csrf_token', ''))

@app.route('/admin/change-password', methods=['GET', 'POST'])
@login_required
@csrf_protected
def change_password():
    # Check session timeout
    last_activity = session.get('last_activity', 0)
    if datetime.datetime.now().timestamp() - last_activity > app.config['PERMANENT_SESSION_LIFETIME']:
        session.clear()
        return redirect(url_for('admin_login'))
    
    # Update last activity
    session['last_activity'] = datetime.datetime.now().timestamp()
    
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate inputs
        if not all([current_password, new_password, confirm_password]):
            flash('All fields are required', 'error')
            return redirect(url_for('change_password'))
        
        if new_password != confirm_password:
            flash('New passwords do not match', 'error')
            return redirect(url_for('change_password'))
        
        # Verify current password
        if not verify_password(current_password, ADMIN_PASSWORD_HASH, ADMIN_SALT):
            flash('Current password is incorrect', 'error')
            return redirect(url_for('change_password'))
        
        # Update password - in a real application, this would update a database
        # For this demo, we'll just show a success message
        flash('Password changed successfully', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin_change_password.html', csrf_token=session.get('csrf_token', ''))

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
