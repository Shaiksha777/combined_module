import subprocess

def run_python_code(code: str, stdin: str = ""):
    try:
        # Save the code to a temporary file
        with open("temp_user_code.py", "w") as f:
            f.write(code)

        # Run it using subprocess
        result = subprocess.run(
            ["python", "temp_user_code.py"],
            input=stdin.encode(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5  # timeout in seconds
        )

        return {
            "stdout": result.stdout.decode(),
            "stderr": result.stderr.decode(),
            "status": "success" if result.returncode == 0 else "error"
        }

    except subprocess.TimeoutExpired:
        return {
            "stdout": "",
            "stderr": "Execution timed out",
            "status": "timeout"
        }

# Example usage
user_code = """
for i in range(100):
    print(i)
"""
stdin_input = "0 7"

output = run_python_code(user_code, stdin_input)
print(output)
