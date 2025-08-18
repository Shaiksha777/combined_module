from flask import Flask, request, render_template, jsonify,session,url_for,redirect
from code_engine import execute_code
from flask_cors import CORS
import time


app = Flask(__name__)

CORS(app)
app.secret_key = 'Shaiksh@7'

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

@app.route('/index')
def return_index():
    
    name = session.get('name')
    if name == None:
        return redirect(url_for('index'))
    
    return render_template('index.html',name = name)

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
        code = data.get("code", "")
        language = data.get("language", "python")
        roll_no = session.get('roll_no')

        length = len(roll_no) - 5
        id = roll_no[length:]

        output, error = execute_code(code, language,id)
    
        return jsonify({"output": output, "error": error})

    except Exception as e:
        return jsonify({"output": "", "error": str(e)}), 500

if __name__ == "__main__":
    app.run('0.0.0.0',debug=True,port=5010)
