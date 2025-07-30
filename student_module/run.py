from flask import Flask, request, render_template, jsonify
from code_engine import execute_code
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes



@app.route("/")
def index():
    return render_template("index.html")

@app.route("/run", methods=["POST"])
def run_code():
    try:
        data = request.get_json()
        code = data.get("code", "")
        language = data.get("language", "python")

        output, error = execute_code(code, language)
        return jsonify({"output": output, "error": error})

    except Exception as e:
        return jsonify({"output": "", "error": str(e)}), 500

if __name__ == "__main__":
    app.run('0.0.0.0',debug=True,port=5010)
