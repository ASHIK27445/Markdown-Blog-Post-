from flask import Flask, render_template, request, redirect, url_for, session , flash
import json
import os
from markdown import markdown
from werkzeug.security import generate_password_hash, check_password_hash
from collections import defaultdict
from datetime import datetime, timedelta
import hashlib
from functools import wraps
import secrets
from dotenv import load_dotenv
import hashlib
import secrets
import string

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)


app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(32))
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)
app.config['SESSION_COOKIE_SECURE'] = True  # HTTPS only
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection

# Admin credentials file
ADMIN_FILE = 'admin_credentials.json'

BLOGS_FILE = 'blogs.json'
GROUPS_FILE = 'groups.json'
VISITORS_FILE = 'visitors.json'
TEMP_USERS_FILE = 'temp_users.json'

def load_blogs():
    if os.path.exists(BLOGS_FILE):
        try:
            with open(BLOGS_FILE, 'r') as f:
                blogs = json.load(f)
            
            # Clean up any malformed blog entries
            cleaned_blogs = {}
            for blog_id, blog_data in blogs.items():
                if (isinstance(blog_data, dict) and 
                    blog_data.get('title') and 
                    isinstance(blog_data['title'], str) and 
                    blog_data['title'].strip() != ''):
                    
                    # Ensure subsections exists and is a list
                    if 'subsections' not in blog_data or not isinstance(blog_data['subsections'], list):
                        blog_data['subsections'] = []
                    
                    # Ensure content exists
                    if 'content' not in blog_data:
                        blog_data['content'] = ''
                    
                    cleaned_blogs[blog_id] = blog_data
                else:
                    print(f"Warning: Skipping malformed blog entry {blog_id}: {blog_data}")
            
            # Save cleaned data back to file if we made changes
            if len(cleaned_blogs) != len(blogs):
                print(f"Cleaned blogs data: removed {len(blogs) - len(cleaned_blogs)} malformed entries")
                save_blogs(cleaned_blogs)
            
            return cleaned_blogs
        except (json.JSONDecodeError, Exception) as e:
            print(f"Error loading blogs: {e}")
            return {}
    return {}

def save_blogs(blogs):
    with open(BLOGS_FILE, 'w') as f:
        json.dump(blogs, f, indent=4)

def load_groups():
    if os.path.exists(GROUPS_FILE):
        with open(GROUPS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_groups(groups):
    with open(GROUPS_FILE, 'w') as f:
        json.dump(groups, f, indent=4)

def load_visitors():
    """Load visitor data with proper default structure and error handling"""
    default_visitors = {
        'total_visits': 0,
        'unique_visitors': {},
        'blog_visits': {},
        'daily_visits': {},
        'daily_unique_visitors': {}
    }
    
    # If file doesn't exist, return default structure
    if not os.path.exists(VISITORS_FILE):
        return default_visitors.copy()
    
    try:
        # Check if file is empty
        if os.path.getsize(VISITORS_FILE) == 0:
            return default_visitors.copy()
            
        with open(VISITORS_FILE, 'r') as f:
            data = json.load(f)
            
        # Ensure all required keys exist with proper defaults
        for key, default_value in default_visitors.items():
            if key not in data:
                data[key] = default_value
        
        return data
        
    except (json.JSONDecodeError, Exception) as e:
        print(f"Error loading visitors file: {e}. Using default structure.")
        # If there's any error reading the file, return default structure
        return default_visitors.copy()

def save_visitors(visitors):
    """Save visitor data with error handling"""
    try:
        with open(VISITORS_FILE, 'w') as f:
            json.dump(visitors, f, indent=4)
    except Exception as e:
        print(f"Error saving visitors file: {e}")

def get_client_ip():
    """Get client IP address considering proxy headers"""
    if request.headers.get('X-Forwarded-For'):
        ip = request.headers.get('X-Forwarded-For').split(',')[0]
    elif request.headers.get('X-Real-IP'):
        ip = request.headers.get('X-Real-IP')
    else:
        ip = request.remote_addr
    return ip.strip()

def hash_ip(ip_address):
    """Hash IP address for privacy while maintaining uniqueness"""
    return hashlib.sha256(ip_address.encode()).hexdigest()[:16]

def track_visit(blog_id=None):
    visitors = load_visitors()
    today = datetime.now().strftime('%Y-%m-%d')
    client_ip = get_client_ip()
    ip_hash = hash_ip(client_ip)
    
    # Update total visits
    visitors['total_visits'] += 1
    
    # Update daily visits
    if today not in visitors['daily_visits']:
        visitors['daily_visits'][today] = 0
    visitors['daily_visits'][today] += 1
    
    # Track unique visitors
    is_new_visitor = ip_hash not in visitors['unique_visitors']
    if is_new_visitor:
        visitors['unique_visitors'][ip_hash] = 1
    else:
        visitors['unique_visitors'][ip_hash] += 1
    
    # Track daily unique visitors
    if today not in visitors['daily_unique_visitors']:
        visitors['daily_unique_visitors'][today] = 0
    if is_new_visitor:
        visitors['daily_unique_visitors'][today] += 1
    
    # Update blog-specific visits if blog_id provided
    if blog_id:
        if blog_id not in visitors['blog_visits']:
            visitors['blog_visits'][blog_id] = 0
        visitors['blog_visits'][blog_id] += 1
    
    save_visitors(visitors)
    
    # Return visitor stats for display
    return {
        'total_visits': visitors['total_visits'],
        'unique_visitors': len(visitors['unique_visitors']),
        'today_visits': visitors['daily_visits'].get(today, 0),
        'today_unique_visitors': visitors['daily_unique_visitors'].get(today, 0),
        'blog_visits': visitors['blog_visits'].get(blog_id, 0) if blog_id else 0
    }

def get_visitor_stats():
    """Get comprehensive visitor statistics"""
    visitors = load_visitors()
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Get most popular blog
    most_popular_blog = None
    if visitors['blog_visits']:
        most_popular_blog = max(visitors['blog_visits'].items(), key=lambda x: x[1])
    
    return {
        'total_visits': visitors.get('total_visits', 0),
        'unique_visitors': len(visitors.get('unique_visitors', {})),
        'today_visits': visitors.get('daily_visits', {}).get(today, 0),
        'today_unique_visitors': visitors.get('daily_unique_visitors', {}).get(today, 0),
        'most_popular_blog': most_popular_blog,
        'blog_visits': visitors.get('blog_visits', {}),
        'daily_visits': visitors.get('daily_visits', {})
    }

def safe_markdown(text):
    """Convert markdown to HTML with GitHub-like styling"""
    html = markdown(text, extensions=[
        'fenced_code',
        'tables',
        'toc'
    ])
    return html

def init_admin():
    """Initialize admin credentials if not exists"""
    if not os.path.exists(ADMIN_FILE):
        # Default admin credentials (CHANGE THESE!)
        default_admin = {
            'username': 'admin',
            'password': generate_password_hash('admin123', method='pbkdf2:sha256'),
            'email': 'admin@example.com',
            'failed_attempts': 0,
            'locked_until': None
        }
        with open(ADMIN_FILE, 'w') as f:
            json.dump(default_admin, f, indent=4)

def load_admin():
    """Load admin credentials"""
    if os.path.exists(ADMIN_FILE):
        with open(ADMIN_FILE, 'r') as f:
            return json.load(f)
    return None

def save_admin(admin_data):
    """Save admin credentials"""
    with open(ADMIN_FILE, 'w') as f:
        json.dump(admin_data, f, indent=4)

def login_required(f):
    """Decorator to protect routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            flash('Please login to access this page', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Helper functions for temp users
def load_temp_users():
    """Load temporary users data"""
    if os.path.exists(TEMP_USERS_FILE):
        try:
            with open(TEMP_USERS_FILE, 'r') as f:
                temp_users = json.load(f)
                
                # Replace codes from environment variables if available
                for username in temp_users:
                    env_code = os.getenv(f'{username.upper()}_CODE')
                    if env_code:
                        temp_users[username]['code'] = env_code
                
                return temp_users
        except (json.JSONDecodeError, Exception) as e:
            print(f"Error loading temp users: {e}")
            return {}
    return {}

def save_temp_users(temp_users):
    """Save temporary users data"""
    with open(TEMP_USERS_FILE, 'w') as f:
        json.dump(temp_users, f, indent=4)

def generate_access_code(length=8):
    """Generate a random access code"""
    characters = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))

def is_temp_user_valid(username, code):
    """Check if temp user credentials are valid and not expired"""
    temp_users = load_temp_users()
    
    if username not in temp_users:
        return False, None
    
    user = temp_users[username]
    
    # Check if code matches
    if user['code'] != code:
        return False, None
    
    # Check if expired
    expiration = datetime.fromisoformat(user['expiration'])
    if datetime.now() > expiration:
        return False, None
    
    return True, user

def temp_login_required(f):
    """Decorator to protect routes for temp users"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if admin is logged in
        if 'admin_logged_in' in session:
            return f(*args, **kwargs)
        
        # Check if temp user is logged in
        if 'temp_user_logged_in' not in session:
            flash('Please login to access this content', 'error')
            return redirect(url_for('temp_login'))
        
        # Verify temp user is still valid
        username = session.get('temp_username')
        code = session.get('temp_code')
        
        is_valid, user = is_temp_user_valid(username, code)
        if not is_valid:
            session.clear()
            flash('Your access has expired. Please login again.', 'error')
            return redirect(url_for('temp_login'))
        
        return f(*args, **kwargs)
    return decorated_function

@app.context_processor
def inject_data():
    is_temp_user = 'temp_user_logged_in' in session
    temp_username = session.get('temp_username', '')
    
    return {
        'blogs': load_blogs(),
        'groups': load_groups(),
        'visitor_stats': get_visitor_stats(),
        'is_temp_user': is_temp_user,
        'temp_username': temp_username
    }

@app.route('/')
def index():
    track_visit()
    blogs = load_blogs()
    groups = load_groups()
    
    # Check if temp user can see all hidden content
    temp_can_see_all = session.get('temp_can_see_all_hidden', False)
    
    # Filter out hidden content for users without permission
    if 'admin_logged_in' not in session:
        if not temp_can_see_all:
            # Filter hidden blogs
            blogs = {blog_id: blog for blog_id, blog in blogs.items() 
                    if not blog.get('hidden', False)}
            
            # Filter hidden groups
            groups = {group_id: group for group_id, group in groups.items() 
                     if not group.get('hidden', False)}
    
    return render_template('index.html', blogs=blogs, groups=groups)

@app.route('/blog/<blog_id>')
def blog_detail(blog_id):
    visit_data = track_visit(blog_id)
    blogs = load_blogs()
    blog = blogs.get(blog_id)
    
    if not blog:
        return "Blog not found", 404
    
    # Check if blog is hidden
    if blog.get('hidden', False):
        # Allow admin
        if 'admin_logged_in' in session:
            pass  # Admin can see
        # Check if temp user has permission
        elif 'temp_user_logged_in' in session:
            if not session.get('temp_can_see_all_hidden', False):
                flash('This blog post is not available', 'error')
                return redirect(url_for('index'))
        # Block normal users
        else:
            flash('This blog post is not available', 'error')
            return redirect(url_for('index'))
    
    # Convert markdown to HTML
    blog['content_html'] = safe_markdown(blog['content'])
    for subsection in blog.get('subsections', []):
        subsection['content_html'] = safe_markdown(subsection['content'])
    
    return render_template('blog_detail.html', blog=blog, blog_id=blog_id, visit_data=visit_data)

#Authentication System
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page with security features"""
    if 'admin_logged_in' in session:
        return redirect(url_for('admin'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        admin = load_admin()
        
        if not admin:
            flash('Admin account not found. Please contact system administrator.', 'error')
            return render_template('login.html')
        
        # Check if account is locked
        if admin.get('locked_until'):
            from datetime import datetime
            locked_until = datetime.fromisoformat(admin['locked_until'])
            if datetime.now() < locked_until:
                remaining = (locked_until - datetime.now()).seconds // 60
                flash(f'Account locked. Try again in {remaining} minutes.', 'error')
                return render_template('login.html')
            else:
                # Unlock account
                admin['locked_until'] = None
                admin['failed_attempts'] = 0
                save_admin(admin)
        
        # Validate credentials
        if username == admin['username'] and check_password_hash(admin['password'], password):
            # Successful login
            session.permanent = True
            session['admin_logged_in'] = True
            session['username'] = username
            
            # Reset failed attempts
            admin['failed_attempts'] = 0
            admin['locked_until'] = None
            save_admin(admin)
            
            flash('Login successful!', 'success')
            return redirect(url_for('admin'))
        else:
            # Failed login
            admin['failed_attempts'] = admin.get('failed_attempts', 0) + 1
            
            # Lock account after 5 failed attempts
            if admin['failed_attempts'] >= 5:
                from datetime import datetime, timedelta
                admin['locked_until'] = (datetime.now() + timedelta(minutes=30)).isoformat()
                save_admin(admin)
                flash('Too many failed attempts. Account locked for 30 minutes.', 'error')
            else:
                save_admin(admin)
                remaining = 5 - admin['failed_attempts']
                flash(f'Invalid credentials. {remaining} attempts remaining.', 'error')
            
            return render_template('login.html')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout admin"""
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change admin password"""
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        admin = load_admin()
        
        # Verify current password
        if not check_password_hash(admin['password'], current_password):
            flash('Current password is incorrect', 'error')
            return render_template('change_password.html')
        
        # Validate new password
        if len(new_password) < 8:
            flash('Password must be at least 8 characters long', 'error')
            return render_template('change_password.html')
        
        if new_password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('change_password.html')
        
        # Update password
        admin['password'] = generate_password_hash(new_password, method='pbkdf2:sha256')
        save_admin(admin)
        
        flash('Password changed successfully', 'success')
        return redirect(url_for('admin'))
    
    return render_template('change_password.html')
#-------------------------------------------------------------------

#Admin
@app.route('/admin')
@login_required
def admin():
    blogs = load_blogs()
    groups = load_groups()
    visitor_stats = get_visitor_stats()
    return render_template('admin.html', blogs=blogs, groups=groups, visitor_stats=visitor_stats)

@app.route('/visitor_stats')
@login_required
def visitor_stats():
    """Detailed visitor statistics page"""
    stats = get_visitor_stats()
    blogs = load_blogs()
    
    # Add blog titles to stats
    blog_stats = []
    for blog_id, visits in stats['blog_visits'].items():
        blog_title = blogs.get(blog_id, {}).get('title', 'Unknown Blog') if blog_id else 'Homepage'
        blog_stats.append({
            'id': blog_id,
            'title': blog_title,
            'visits': visits
        })
    
    # Sort by visits descending
    blog_stats.sort(key=lambda x: x['visits'], reverse=True)
    
    # Limit to top 6 posts only
    blog_stats = blog_stats[:6]
    
    return render_template('visitor_stats.html', 
                         stats=stats, 
                         blog_stats=blog_stats,
                         blogs=blogs)
    """Detailed visitor statistics page"""
    stats = get_visitor_stats()
    blogs = load_blogs()
    
    # Add blog titles to stats
    blog_stats = []
    for blog_id, visits in stats['blog_visits'].items():
        blog_title = blogs.get(blog_id, {}).get('title', 'Unknown Blog') if blog_id else 'Homepage'
        blog_stats.append({
            'id': blog_id,
            'title': blog_title,
            'visits': visits
        })
    
    # Sort by visits descending
    blog_stats.sort(key=lambda x: x['visits'], reverse=True)
    
    return render_template('visitor_stats.html', 
                         stats=stats, 
                         blog_stats=blog_stats,
                         blogs=blogs)

# New route for groups management
@app.route('/manage_groups')
@login_required
def manage_groups():
    blogs = load_blogs()
    groups = load_groups()
    return render_template('manage_groups.html', blogs=blogs, groups=groups)

# Group Management Routes
@app.route('/create_group', methods=['POST'])
@login_required
def create_group():
    groups = load_groups()
    
    group_id = str(len(groups) + 1)
    group_name = request.form['group_name']
    group_description = request.form.get('group_description', '')
    
    groups[group_id] = {
        'name': group_name,
        'description': group_description,
        'blogs': [],
        'hidden': False  # Default to visible
    }
    
    save_groups(groups)
    flash(f'Group "{group_name}" created successfully', 'success')
    return redirect(url_for('manage_groups'))

@app.route('/add_blog_to_group', methods=['POST'])
def add_blog_to_group():
    groups = load_groups()
    group_id = request.form['group_id']
    blog_id = request.form['blog_id']
    
    if group_id in groups and blog_id not in groups[group_id]['blogs']:
        groups[group_id]['blogs'].append(blog_id)
        save_groups(groups)
    
    return redirect(url_for('manage_groups'))

@app.route('/remove_blog_from_group', methods=['POST'])
def remove_blog_from_group():
    groups = load_groups()
    group_id = request.form['group_id']
    blog_id = request.form['blog_id']
    
    if group_id in groups and blog_id in groups[group_id]['blogs']:
        groups[group_id]['blogs'].remove(blog_id)
        save_groups(groups)
    
    return redirect(url_for('manage_groups'))

@app.route('/delete_group/<group_id>')
def delete_group(group_id):
    groups = load_groups()
    
    if group_id in groups:
        del groups[group_id]
        save_groups(groups)
    
    return redirect(url_for('manage_groups'))

# Existing blog management routes
@app.route('/create_blog', methods=['POST'])
@login_required
def create_blog():
    blogs = load_blogs()
    
    blog_id = str(len(blogs) + 1)
    title = request.form['title']
    content = request.form['content']
    
    blogs[blog_id] = {
        'title': title,
        'content': content,
        'subsections': [],
        'hidden': False  # Default to visible
    }
    
    save_blogs(blogs)
    flash(f'Blog "{title}" created successfully', 'success')
    return redirect(url_for('admin'))

@app.route('/edit_blog/<blog_id>')
@login_required
def edit_blog(blog_id):
    blogs = load_blogs()
    blog = blogs.get(blog_id)
    if not blog:
        return "Blog not found", 404
    return render_template('edit_blog.html', blog=blog, blog_id=blog_id)

@app.route('/update_blog/<blog_id>', methods=['POST'])
@login_required
def update_blog(blog_id):
    blogs = load_blogs()
    
    if blog_id in blogs:
        blogs[blog_id]['title'] = request.form['title']
        blogs[blog_id]['content'] = request.form['content']
        save_blogs(blogs)
    
    return redirect(url_for('admin'))

@app.route('/delete_blog/<blog_id>')
@login_required
def delete_blog(blog_id):
    blogs = load_blogs()
    
    if blog_id in blogs:
        del blogs[blog_id]
        save_blogs(blogs)
    
    return redirect(url_for('admin'))

@app.route('/add_subsection/<blog_id>', methods=['POST'])
def add_subsection(blog_id):
    blogs = load_blogs()
    
    if blog_id in blogs:
        subsection_title = request.form['subsection_title']
        subsection_content = request.form['subsection_content']
        
        subsection = {
            'title': subsection_title,
            'content': subsection_content
        }
        
        blogs[blog_id]['subsections'].append(subsection)
        save_blogs(blogs)
    
    return redirect(url_for('edit_blog', blog_id=blog_id))

@app.route('/edit_subsection/<blog_id>/<int:subsection_index>', methods=['POST'])
def edit_subsection(blog_id, subsection_index):
    blogs = load_blogs()
    
    if blog_id in blogs and 0 <= subsection_index < len(blogs[blog_id]['subsections']):
        blogs[blog_id]['subsections'][subsection_index]['title'] = request.form['subsection_title']
        blogs[blog_id]['subsections'][subsection_index]['content'] = request.form['subsection_content']
        save_blogs(blogs)
    
    return redirect(url_for('edit_blog', blog_id=blog_id))

@app.route('/delete_subsection/<blog_id>/<int:subsection_index>')
def delete_subsection(blog_id, subsection_index):
    blogs = load_blogs()
    
    if blog_id in blogs and 0 <= subsection_index < len(blogs[blog_id]['subsections']):
        blogs[blog_id]['subsections'].pop(subsection_index)
        save_blogs(blogs)
    
    return redirect(url_for('edit_blog', blog_id=blog_id))

@app.route('/add_multiple_blogs_to_group', methods=['POST'])
def add_multiple_blogs_to_group():
    groups = load_groups()
    blogs = load_blogs()
    group_id = request.form['group_id']
    blog_ids = request.form.getlist('blog_ids')  # Get all blog_ids
    
    if group_id in groups:
        added_blogs = []
        already_in_group = []
        
        for blog_id in blog_ids:
            # Check if blog exists
            if blog_id in blogs:
                if blog_id not in groups[group_id]['blogs']:
                    groups[group_id]['blogs'].append(blog_id)
                    added_blogs.append(blog_id)
                else:
                    already_in_group.append(blog_id)
        
        save_groups(groups)
        
        # Optional: You can add flash messages here to show results
        print(f"Added {len(added_blogs)} blogs to group. {len(already_in_group)} were already in the group.")
    
    return redirect(url_for('manage_groups'))

@app.route('/cleanup_blogs')
def cleanup_blogs():
    """Clean up malformed blog entries"""
    blogs = load_blogs()  # This will now clean the data
    return redirect(url_for('admin'))

# Toggle Blog Visibility (Hide/Show)
@app.route('/toggle_blog_visibility/<blog_id>')
@login_required
def toggle_blog_visibility(blog_id):
    """Toggle blog visibility between hidden and visible"""
    blogs = load_blogs()
    
    if blog_id in blogs:
        # Toggle the hidden status
        current_status = blogs[blog_id].get('hidden', False)
        blogs[blog_id]['hidden'] = not current_status
        save_blogs(blogs)
        
        status = "hidden" if not current_status else "visible"
        flash(f'Blog "{blogs[blog_id]["title"]}" is now {status}', 'success')
    
    return redirect(request.referrer or url_for('admin'))

# Toggle Group Visibility (Hide/Show)
@app.route('/toggle_group_visibility/<group_id>')
@login_required
def toggle_group_visibility(group_id):
    """Toggle group visibility between hidden and visible"""
    groups = load_groups()
    
    if group_id in groups:
        # Toggle the hidden status
        current_status = groups[group_id].get('hidden', False)
        groups[group_id]['hidden'] = not current_status
        save_groups(groups)
        
        status = "hidden" if not current_status else "visible"
        flash(f'Group "{groups[group_id]["name"]}" is now {status}', 'success')
    
    return redirect(request.referrer or url_for('manage_groups'))


# ============================================
# TEMP USER ROUTES
# ============================================

@app.route('/temp_login', methods=['GET', 'POST'])
def temp_login():
    """Temporary user login page"""
    if 'temp_user_logged_in' in session or 'admin_logged_in' in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        code = request.form.get('code', '').strip().upper()
        
        is_valid, user = is_temp_user_valid(username, code)
        
        if is_valid:
            # Successful login
            session.permanent = True
            session['temp_user_logged_in'] = True
            session['temp_username'] = username
            session['temp_code'] = code
            session['temp_can_see_all_hidden'] = user.get('can_see_all_hidden', False)
            
            flash(f'Welcome, {username}! Access valid until {user["expiration"][:10]}', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or access code, or your access has expired.', 'error')
    
    return render_template('temp_login.html')

@app.route('/temp_logout')
def temp_logout():
    """Logout temporary user"""
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

@app.route('/manage_temp_users')
@login_required
def manage_temp_users():
    """Admin page to manage temporary users"""
    temp_users = load_temp_users()
    
    # Add status to each user
    now = datetime.now()
    for username, user in temp_users.items():
        expiration = datetime.fromisoformat(user['expiration'])
        user['is_expired'] = now > expiration
        user['days_remaining'] = (expiration - now).days if not user['is_expired'] else 0
    
    return render_template('manage_temp_users.html', temp_users=temp_users)

@app.route('/create_temp_user', methods=['POST'])
@login_required
def create_temp_user():
    """Create a new temporary user"""
    temp_users = load_temp_users()
    
    username = request.form.get('username', '').strip()
    duration_days = int(request.form.get('duration_days', 7))
    can_see_all_hidden = request.form.get('can_see_all_hidden') == 'on'
    
    # Validate username
    if not username:
        flash('Username is required', 'error')
        return redirect(url_for('manage_temp_users'))
    
    if username in temp_users:
        flash('Username already exists', 'error')
        return redirect(url_for('manage_temp_users'))
    
    # Generate access code
    code = generate_access_code()
    
    # Calculate expiration
    expiration = datetime.now() + timedelta(days=duration_days)
    
    # Create temp user
    temp_users[username] = {
        'code': code,
        'created_at': datetime.now().isoformat(),
        'expiration': expiration.isoformat(),
        'can_see_all_hidden': can_see_all_hidden,
        'duration_days': duration_days
    }
    
    save_temp_users(temp_users)
    
    flash(f'Temp user created! Username: {username}, Code: {code}', 'success')
    return redirect(url_for('manage_temp_users'))

@app.route('/extend_temp_user/<username>', methods=['POST'])
@login_required
def extend_temp_user(username):
    """Extend temporary user expiration"""
    temp_users = load_temp_users()
    
    if username not in temp_users:
        flash('User not found', 'error')
        return redirect(url_for('manage_temp_users'))
    
    additional_days = int(request.form.get('additional_days', 7))
    
    # Get current expiration
    current_expiration = datetime.fromisoformat(temp_users[username]['expiration'])
    
    # If already expired, extend from now
    if datetime.now() > current_expiration:
        new_expiration = datetime.now() + timedelta(days=additional_days)
    else:
        new_expiration = current_expiration + timedelta(days=additional_days)
    
    temp_users[username]['expiration'] = new_expiration.isoformat()
    temp_users[username]['duration_days'] = temp_users[username].get('duration_days', 0) + additional_days
    
    save_temp_users(temp_users)
    
    flash(f'Extended {username}\'s access by {additional_days} days', 'success')
    return redirect(url_for('manage_temp_users'))

@app.route('/toggle_temp_user_permission/<username>')
@login_required
def toggle_temp_user_permission(username):
    """Toggle temp user permission to see all hidden content"""
    temp_users = load_temp_users()
    
    if username not in temp_users:
        flash('User not found', 'error')
        return redirect(url_for('manage_temp_users'))
    
    current_permission = temp_users[username].get('can_see_all_hidden', False)
    temp_users[username]['can_see_all_hidden'] = not current_permission
    
    save_temp_users(temp_users)
    
    status = "CAN" if not current_permission else "CANNOT"
    flash(f'{username} {status} now see all hidden content', 'success')
    return redirect(url_for('manage_temp_users'))

@app.route('/delete_temp_user/<username>')
@login_required
def delete_temp_user(username):
    """Delete a temporary user"""
    temp_users = load_temp_users()
    
    if username in temp_users:
        del temp_users[username]
        save_temp_users(temp_users)
        flash(f'Temp user {username} deleted', 'success')
    
    return redirect(url_for('manage_temp_users'))

@app.route('/regenerate_temp_code/<username>')
@login_required
def regenerate_temp_code(username):
    """Regenerate access code for temp user"""
    temp_users = load_temp_users()
    
    if username not in temp_users:
        flash('User not found', 'error')
        return redirect(url_for('manage_temp_users'))
    
    new_code = generate_access_code()
    temp_users[username]['code'] = new_code
    
    save_temp_users(temp_users)
    
    flash(f'New code for {username}: {new_code}', 'success')
    return redirect(url_for('manage_temp_users'))

if __name__ == "__main__":
    init_admin()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))