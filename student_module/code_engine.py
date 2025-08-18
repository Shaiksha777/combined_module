import subprocess
import uuid
import os 
from collections import deque

UPLOAD_FOLDER = "code_templates"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
Queue = deque()
def execute_code(code, language,id):
    
    
    
    filename = os.path.join(UPLOAD_FOLDER, f"code_{id}")
    
    try:
        if language == "python":
            filename += ".py"
            with open(filename, "w") as f:
                f.write(code)
            result = subprocess.run(["python", filename], capture_output=True, text=True, timeout=5)
            print(result)

        elif language == "c":
            filename_c = filename + ".c"
            output_exe = filename + ".exe"
            with open(filename_c, "w") as f:
                f.write(code)
            compile = subprocess.run(["gcc", filename_c, "-o", output_exe], capture_output=True, text=True,timeout=1)
            if compile.returncode != 0:
                return "", compile.stderr
            result = subprocess.run([output_exe], capture_output=True, text=True, timeout=5)

        elif language == "cpp":
            filename_cpp = filename + ".cpp"
            output_exe = filename + ".exe"
            with open(filename_cpp, "w") as f:
                f.write(code)
            compile = subprocess.run(["g++", filename_cpp, "-o", output_exe], capture_output=True, text=True)
            if compile.returncode != 0:
                return "", compile.stderr
            result = subprocess.run([output_exe], capture_output=True, text=True, timeout=5)

        elif language == "java":
            filename_java = filename + ".java"
            classname = "Main"
            with open(filename_java, "w") as f:
                f.write(code.replace("Main", classname))
            compile = subprocess.run(["javac", filename_java], capture_output=True, text=True)
            if compile.returncode != 0:
                return "", compile.stderr
            result = subprocess.run(["java", "-cp", UPLOAD_FOLDER, classname], capture_output=True, text=True, timeout=5)

        elif language == "javascript":
            filename += ".js"
            with open(filename, "w") as f:
                f.write(code)
            result = subprocess.run(["node", filename], capture_output=True, text=True, timeout=5)

        else:
            return "", "Unsupported language"
        
        return result.stdout, result.stderr

    except subprocess.TimeoutExpired:
        return "", "Execution timed out"
    except Exception as e:
        return "", str(e)
    finally:
        # Optional: Clean up temp files if needed
        os.remove(filename)
        print('file removed sucessfully')
        