from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'


UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


users = {
    'student': {'password': 'student', 'role': 'student'},
    'instructor': {'password': 'instructor', 'role': 'instructor'},
    'admin': {'password': 'admin', 'role': 'admin'}
}


courses = []  

@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username]['password'] == password:
            session['username'] = username
            session['role'] = users[username]['role']
            return redirect(url_for('dashboard'))
        else:
            return "Login Failed. Please check your credentials."
    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    role = session.get('role')
    if role == 'student':
        return render_template('dashboard.html', role=role, courses=courses)
    elif role == 'instructor':
        return render_template('dashboard.html', role=role, courses=courses)
    elif role == 'admin':
        return render_template('dashboard.html', role=role, users=users, courses=courses)
    return redirect(url_for('login'))


@app.route('/upload_course', methods=['GET', 'POST'])
def upload_course():
    if 'role' not in session or session['role'] != 'instructor':
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        course_name = request.form['course_name']
        file = request.files['file']
        if file:
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            courses.append({'name': course_name, 'filename': filename})
            return redirect(url_for('dashboard'))
    return render_template('course_upload.html')


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/browse_courses')
def browse_courses():
    if 'role' not in session or session['role'] != 'student':
        return redirect(url_for('login'))
    return render_template('browse_courses.html', courses=courses)


@app.route('/view_course/<filename>')
def view_course(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/manage_users')
def manage_users():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    return render_template('manage_users.html', users=users)


@app.route('/manage_courses')
def manage_courses():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    return render_template('manage_courses.html', courses=courses)


@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
