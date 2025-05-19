import os
import secrets
import hashlib
from functools import wraps
from flask import session, redirect, url_for, abort, request

# Security constants
TOKEN_BYTES = 32  # 256 bits
SESSION_LIFETIME = 3600  # 1 hour in seconds
ALLOWED_EXTENSIONS = {'pdf'}
MAX_UPLOAD_SIZE = 16 * 1024 * 1024  # 16MB

def generate_csrf_token():
    """Generate a secure CSRF token"""
    return secrets.token_hex(TOKEN_BYTES // 2)  # Each hex character is 4 bits

def hash_password(password, salt=None):
    """Hash a password with an optional salt"""
    if salt is None:
        salt = secrets.token_hex(8)
    
    # Use a strong hashing algorithm (SHA-256)
    hash_obj = hashlib.sha256((password + salt).encode())
    password_hash = hash_obj.hexdigest()
    
    return password_hash, salt

def verify_password(password, stored_hash, salt):
    """Verify a password against a stored hash"""
    hash_to_check, _ = hash_password(password, salt)
    return secrets.compare_digest(hash_to_check, stored_hash)

def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def csrf_protected(f):
    """Decorator to protect against CSRF attacks"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method == 'POST':
            token = session.get('csrf_token')
            if not token or token != request.form.get('csrf_token'):
                abort(403)
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    """Check if a file has an allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def secure_headers():
    """Return a dictionary of secure headers to add to responses"""
    return {
        'Content-Security-Policy': "default-src 'self'; script-src 'self' https://cdnjs.cloudflare.com; style-src 'self' https://cdnjs.cloudflare.com https://fonts.googleapis.com; font-src 'self' https://cdnjs.cloudflare.com https://fonts.gstatic.com; img-src 'self' data:;",
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'SAMEORIGIN',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Referrer-Policy': 'strict-origin-when-cross-origin'
    }

def configure_app_security(app):
    """Configure Flask app with security settings"""
    # Set secure session cookie
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['PERMANENT_SESSION_LIFETIME'] = SESSION_LIFETIME
    
    # Set upload limits and allowed extensions
    app.config['MAX_CONTENT_LENGTH'] = MAX_UPLOAD_SIZE
    app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS
    
    # Generate a strong secret key
    app.config['SECRET_KEY'] = secrets.token_hex(TOKEN_BYTES)
    
    # Add security headers to all responses
    @app.after_request
    def add_security_headers(response):
        headers = secure_headers()
        for header, value in headers.items():
            response.headers[header] = value
        return response
    
    # Add CSRF token to session
    @app.before_request
    def csrf_protect():
        if 'csrf_token' not in session:
            session['csrf_token'] = generate_csrf_token()
    
    return app
