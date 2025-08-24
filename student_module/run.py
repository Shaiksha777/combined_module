from flask import Flask, request, render_template, jsonify,session,url_for,redirect
from code_engine import execute_code
from flask_cors import CORS
import time
from token_handler import decrpyt_token
import pandas as pd
import os
app = Flask(__name__)

CORS(app)
app.secret_key = 'Shaiksh@7'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
Question_folder = os.path.join(BASE_DIR, 'question_folder')
app.config['Questions_folder'] = Question_folder
print(BASE_DIR)


class Person:
    def __init__(self,name,roll_no,question_assigned=102):

        self.name = name
        self.roll_no = roll_no
        self.question_assigned = question_assigned


    def save_code(self,code):
        self.code = code

    
    
     

@app.route("/")
def index():
    name = session.get('name')
    if name:
        return redirect(url_for('return_index'))
    return render_template("first.html")

def get_question_and_samples(question_id):
    df = pd.read_csv(f'{Question_folder}\\questions.csv')
    if question_id not in df['Question_ID'].values:
        return {
            "question": "Question not found",
            "sample_inputs": [],
            "sample_outputs": []
        }

    row = df.loc[df['Question_ID'] == question_id].iloc[0]
    question_text = row['Question']

    # Split testcases by '||'
    sample_inputs = row.get('Sample_Input', '')
    sample_outputs = row.get('Sample_Output', '')

    sample_inputs_list = [x.strip() for x in sample_inputs.split('||')] if sample_inputs else []
    sample_outputs_list = [x.strip() for x in sample_outputs.split('||')] if sample_outputs else []

    return {
        "question": question_text,
        "sample_inputs": sample_inputs_list,
        "sample_outputs": sample_outputs_list
    }

@app.route('/index')
def return_index():
    email = session.get('email')
    question_id = session.get('question_id')
    if email is None or question_id is None:
        return redirect(url_for('index'))

    data = get_question_and_samples(question_id)
    return render_template(
        'index.html',
        name=email,
        question=data['question'],
        question_id=question_id,
        sample_inputs=data['sample_inputs'],
        sample_outputs=data['sample_outputs']
    )


"""
@app.route('/index')
def return_index():
    
    email = session.get('email')
    question_id = session.get('question_id')
    question = get_question(question_id)
    if email == None:
        return redirect(url_for('index'))
    
    return render_template('index.html',name = email,question = question,question_id = question_id)
"""

@app.route('/test/<token>')
def extract_data(token):
    encrypted_token = token
    try:
        value = decrpyt_token(encrypted_token)
    except Exception as e:
        return f'invalid URL {e}'
    

    print(value)
    question_id = value['question_id']
    email = value['email']
    session['question_id'] = question_id
    session['email'] = email

    return redirect(url_for('return_index'))




@app.route('/save_details',methods = ['POST'])
def save_details():
    data = request.get_json()
    name = data.get('name','')
    roll_no = data.get('roll_no','')

    session['name'] = name
    session['roll_no'] = roll_no
    

    student = Person(name=name,roll_no=roll_no)
    print(student.name)
    

    return jsonify({"redirect": "/index"})


@app.route("/run", methods=["POST"])


def run_code():
    try:
        data = request.get_json()
        if not data:
            return "Invalid request", 400
        print(data)
        code = data.get("code", "")
        language = data.get("language", "python")

        id = session.get('email')
        output, error = execute_code(code, language,id)
        return jsonify({"output": output, "error": error})

    except Exception as e:
        return jsonify({"output": "", "error": str(e)}), 500

    
    
if __name__ == "__main__":
    app.run('0.0.0.0',debug=True,port=5010)
