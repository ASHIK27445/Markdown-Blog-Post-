from flask import Flask, render_template, request, redirect, url_for
import json
import os
from markdown import markdown

app = Flask(__name__)

BLOGS_FILE = 'blogs.json'
GROUPS_FILE = 'groups.json'

def load_blogs():
    if os.path.exists(BLOGS_FILE):
        with open(BLOGS_FILE, 'r') as f:
            return json.load(f)
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

def safe_markdown(text):
    """Convert markdown to HTML with GitHub-like styling"""
    html = markdown(text, extensions=[
        'fenced_code',
        'tables',
        'toc'
    ])
    return html

@app.context_processor
def inject_data():
    return {
        'blogs': load_blogs(),
        'groups': load_groups()
    }

@app.route('/')
def index():
    blogs = load_blogs()
    groups = load_groups()
    return render_template('index.html', blogs=blogs, groups=groups)

@app.route('/blog/<blog_id>')
def blog_detail(blog_id):
    blogs = load_blogs()
    blog = blogs.get(blog_id)
    if not blog:
        return "Blog not found", 404
    
    # Convert markdown to HTML using our safe function
    blog['content_html'] = safe_markdown(blog['content'])
    for subsection in blog.get('subsections', []):
        subsection['content_html'] = safe_markdown(subsection['content'])
    
    return render_template('blog_detail.html', blog=blog, blog_id=blog_id)

@app.route('/admin')
def admin():
    blogs = load_blogs()
    groups = load_groups()
    return render_template('admin.html', blogs=blogs, groups=groups)

# New route for groups management
@app.route('/manage_groups')
def manage_groups():
    blogs = load_blogs()
    groups = load_groups()
    return render_template('manage_groups.html', blogs=blogs, groups=groups)

# Group Management Routes
@app.route('/create_group', methods=['POST'])
def create_group():
    groups = load_groups()
    
    group_id = str(len(groups) + 1)
    group_name = request.form['group_name']
    group_description = request.form.get('group_description', '')
    
    groups[group_id] = {
        'name': group_name,
        'description': group_description,
        'blogs': []  # List of blog IDs in this group
    }
    
    save_groups(groups)
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

# Existing blog management routes (unchanged)
@app.route('/create_blog', methods=['POST'])
def create_blog():
    blogs = load_blogs()
    
    blog_id = str(len(blogs) + 1)
    title = request.form['title']
    content = request.form['content']
    
    blogs[blog_id] = {
        'title': title,
        'content': content,
        'subsections': []
    }
    
    save_blogs(blogs)
    return redirect(url_for('admin'))

@app.route('/edit_blog/<blog_id>')
def edit_blog(blog_id):
    blogs = load_blogs()
    blog = blogs.get(blog_id)
    if not blog:
        return "Blog not found", 404
    return render_template('edit_blog.html', blog=blog, blog_id=blog_id)

@app.route('/update_blog/<blog_id>', methods=['POST'])
def update_blog(blog_id):
    blogs = load_blogs()
    
    if blog_id in blogs:
        blogs[blog_id]['title'] = request.form['title']
        blogs[blog_id]['content'] = request.form['content']
        save_blogs(blogs)
    
    return redirect(url_for('admin'))

@app.route('/delete_blog/<blog_id>')
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))