from flask import Flask, request, render_template, redirect, url_for,jsonify
import os
from werkzeug.utils import secure_filename
from threading import Thread
import csv
from Mailer import Mail
import webview
from flask import send_file
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import subprocess


# -------------------------------
# Initialize Flask & Config
# -------------------------------
app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


questions_uploaded = False
emails_uploaded = False
questions_filename = None
emails_filename = None


from temp import assign_randomly


# -------------------------------
# Routes
# -------------------------------

@app.route('/')
def index():
    global questions_uploaded, emails_uploaded
    return render_template('index.html',
                           questions_uploaded=questions_uploaded,
                           emails_uploaded=emails_uploaded)


@app.route('/upload_questions', methods=["POST"])
def upload_questions():
    global questions_uploaded, questions_filename

    file = request.files.get('questions_file')
    if not file:
        return 'No file part', 400

    filename = 'temp.csv'
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

   
    with open(filepath, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        if 'Question_ID' not in reader.fieldnames:
            return render_template('index.html',
                                   questions_uploaded=False,
                                   emails_uploaded=emails_uploaded,
                                   error="Invalid Questions CSV: 'Question_ID' column is missing.")
    
    questions_uploaded = True
    questions_filename = filename

    return render_template('index.html',
                           questions_uploaded=questions_uploaded,
                           emails_uploaded=emails_uploaded)



@app.route('/upload_emails', methods=["POST"])
def upload_emails():
    global emails_uploaded, emails_filename

    file = request.files.get('emails_file')
    if not file:
        return 'No file part', 400

    filename = 'emails.csv'
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    
    with open(filepath, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        if 'Email' not in reader.fieldnames:
            return render_template('index.html',
                                   questions_uploaded=questions_uploaded,
                                   emails_uploaded=False,
                                   error="Invalid Emails CSV: 'Email' column is missing.")

    emails_uploaded = True
    emails_filename = filename

    return render_template('index.html',
                           questions_uploaded=questions_uploaded,
                           emails_uploaded=emails_uploaded)

@app.route('/start_server')
def start_student_server():
    
    try:
        # Path to student module's run.py
        student_script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'student_module', 'run.py'))
        
        # Use subprocess to launch it
        process = subprocess.Popen([sys.executable, student_script_path])
        print('started')
        return "Student server started successfully!"

    except Exception as e:
        print(e)
        return f"Error launching student app: {str(e)}", 500    

@app.route('/assign_questions')
def assign_the_questions():
    global questions_filename, emails_filename,emails_uploaded,questions_uploaded

    if not (questions_filename and emails_filename):
        return "Both files must be uploaded first.", 400

  
    assigned = assign_randomly()
    emails_uploaded = False
    questions_uploaded = False
    with open('assigned_questions.csv','w') as f:
        fieldnames = ['email','question_assigned']
        writer = csv.DictWriter(f,fieldnames=fieldnames)
        print(assigned)
        writer.writeheader()
        for email in assigned:
            writer.writerow({'email':f'{email}','question_assigned':f'{assigned[email]}'})
        

    mail_object = Mail()


    for i in assigned:
        mail_object.send_mail(recipient_email=i,question_id=assigned[i])
        print('mail sucessfully sent to', i)
    
        

    return render_template("results.html", assignments=assigned)
   
@app.route('/download_results')
def download_csv():
    return  send_file('assigned_questions.csv')
    

@app.route('/reset')
def reset_flags():
    global questions_uploaded, emails_uploaded, questions_filename, emails_filename

    questions_uploaded = False
    emails_uploaded = False
    questions_filename = None
    emails_filename = None

    return redirect(url_for('index'))

def start_flask():
    app.run(debug=False, port=5000, use_reloader=False)


if __name__ == '__main__':
    # Start Flask server in a thread
    t = Thread(target=start_flask)
    t.daemon = True
    t.start()

    # Launch WebView window
    webview.create_window("Skill Assess", "http://localhost:5000")
    webview.start()

