from flask import Flask, request, render_template, jsonify,session,url_for,redirect
from code_engine import execute_code
from flask_cors import CORS
import time
from token_handler import decrpyt_token
import pandas as pd
import os
import csv
import json
from datetime import datetime
app = Flask(__name__)
from AI_engine import load_models,predict
CORS(app)
app.secret_key = 'Shaiksh@7'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
Question_folder = os.path.join(BASE_DIR, 'question_folder')
app.config['Questions_folder'] = Question_folder
print(BASE_DIR)

tokenizer, model = load_models()

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

def get_boiler_code_for(email: str, question_id: str) -> str:
    try:
        assigned_csv = os.path.join(BASE_DIR, 'random_question', 'assigned_questions.csv')
        if not os.path.exists(assigned_csv):
            return ""
        with open(assigned_csv, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('email') == email and row.get('question_assigned') == question_id:
                    return row.get('boiler_code', '') or ''
    except Exception as e:
        print('Failed to load boiler code:', e)
    return ""


def get_test_cases_for(email: str, question_id: str):
    """Return a list of {input, expected_output} from assigned_questions.csv for this email+qid."""
    try:
        assigned_csv = os.path.join(BASE_DIR, 'random_question', 'assigned_questions.csv')
        if not os.path.exists(assigned_csv):
            return []
        with open(assigned_csv, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('email') == email and row.get('question_assigned') == question_id:
                    raw = row.get('test_cases', '[]')
                    try:
                        cases = json.loads(raw)
                        norm = []
                        for c in cases:
                            if isinstance(c, dict):
                                norm.append({
                                    'input': str(c.get('input', '')),
                                    'expected_output': str(c.get('expected_output', '')).strip()
                                })
                        return norm
                    except Exception:
                        return []
    except Exception as e:
        print('Failed to load test cases:', e)
    return []


@app.route('/index')
def return_index():
    email = session.get('email')
    question_id = session.get('question_id')
    if email is None or question_id is None:
        return redirect(url_for('index'))

    data = get_question_and_samples(question_id)
    boiler_code = get_boiler_code_for(email, question_id)
    return render_template(
        'index.html',
        name=email,
        question=data['question'],
        question_id=question_id,
        sample_inputs=data['sample_inputs'],
        sample_outputs=data['sample_outputs'],
        boiler_code=boiler_code
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

        email = session.get('email')
        qid = session.get('question_id')
        id = email
        # Evaluate only first available test case
        cases = get_test_cases_for(email, qid)
        test = cases[0] if cases else {'input': '', 'expected_output': ''}
        output, error = execute_code(code, language, id, input_data=test.get('input', ''))
        actual = (output or '').strip()
        expected = (test.get('expected_output', '') or '').strip()
        passed = (error == '' and (expected == '' or actual == expected))
        return jsonify({
            "mode": "single",
            "test": {"input": test.get('input', ''), "expected_output": expected},
            "result": {"output": output, "error": error, "passed": passed}
        })

    except Exception as e:
        return jsonify({"output": "", "error": str(e)}), 500


@app.route('/submit',methods=["POST"]) 
def submit_code():
        data = request.get_json()
        if not data:
            return "Invalid request", 400
        print(data)
        code = data.get("code", "")
        language = data.get("language", "python")

        email = session.get('email')
        qid = session.get('question_id')
        id = email
        cases = get_test_cases_for(email, qid)

        results = []
        passed_count = 0
        for idx, t in enumerate(cases):
            out, err = execute_code(code, language, id, input_data=t.get('input', ''))
            actual = (out or '').strip()
            expected = (t.get('expected_output', '') or '').strip()
            passed = (err == '' and (expected == '' or actual == expected))
            passed_count += 1 if passed else 0
            results.append({
                "index": idx+1,
                "input": t.get('input', ''),
                "expected_output": expected,
                "output": out,
                "error": err,
                "passed": passed
            })

        # Plagiarism detection (evaluation-only)
        try:
            p_class, label = predict(code=code, tokenizer=tokenizer, model=model)
        except Exception as e:
            label = f"plagiarism_check_failed: {e}"

        # Evaluation-only response
        return jsonify({
            "mode": "all",
            "summary": {"total": len(cases), "passed": passed_count},
            "results": results,
            "plagiarism_label": label
        })

@app.route('/final_submit', methods=["POST"]) 
def final_submit():
        data = request.get_json()
        if not data:
            return "Invalid request", 400
        code = data.get("code", "")
        language = data.get("language", "python")

        email = session.get('email')
        qid = session.get('question_id')
        id = email
        cases = get_test_cases_for(email, qid)

        results = []
        passed_count = 0
        for idx, t in enumerate(cases):
            out, err = execute_code(code, language, id, input_data=t.get('input', ''))
            actual = (out or '').strip()
            expected = (t.get('expected_output', '') or '').strip()
            passed = (err == '' and (expected == '' or actual == expected))
            passed_count += 1 if passed else 0
            results.append({
                "index": idx+1,
                "input": t.get('input', ''),
                "expected_output": expected,
                "output": out,
                "error": err,
                "passed": passed
            })

        # Plagiarism detection
        try:
            p_class, label = predict(code=code, tokenizer=tokenizer, model=model)
        except Exception as e:
            label = f"plagiarism_check_failed: {e}"

        # Persist results to CSV
        try:
            csv_path = os.path.join(os.path.dirname(__file__), 'result.csv')
            write_header = not os.path.exists(csv_path)
            with open(csv_path, 'a', newline='', encoding='utf-8') as f:
                fieldnames = [
                    'timestamp','email','question_id','language','total_tests','passed_tests','plagiarism_label','results_json'
                ]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                if write_header:
                    writer.writeheader()
                writer.writerow({
                    'timestamp': datetime.utcnow().isoformat(timespec='seconds') + 'Z',
                    'email': email,
                    'question_id': qid,
                    'language': language,
                    'total_tests': len(cases),
                    'passed_tests': passed_count,
                    'plagiarism_label': label,
                    'results_json': json.dumps(results, ensure_ascii=False)
                })
        except Exception as e:
            print('Failed to persist results:', e)

        return jsonify({
            "mode": "all",
            "summary": {"total": len(cases), "passed": passed_count},
            "results": results,
            "plagiarism_label": label
        })

@app.route('/thankyou')
def thank_you():
    return render_template('thankyou.html')
    
if __name__ == "__main__":
    app.run('0.0.0.0',debug=True,port=5010)
