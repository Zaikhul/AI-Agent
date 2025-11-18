import os
import subprocess
import tempfile
from pathlib import Path

class SafeCodeExecutor:
    def __init__(self, workspace="workspace"):
        self.workspace = Path(workspace)
        self.workspace.mkdir(exist_ok=True)
    
    def execute_python(self, code, filename="temp_script.py"):
        """Execute Python code safely"""
        filepath = self.workspace / filename
        
        # Write code to file
        with open(filepath, "w") as f:
            f.write(code)
        
        try:
            # Execute dengan timeout
            result = subprocess.run(
                ["python", str(filepath)],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=self.workspace
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Execution timeout (30s)"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def run_tests(self, test_file="test_*.py"):
        """Run pytest tests"""
        try:
            result = subprocess.run(
                ["pytest", str(self.workspace / test_file), "-v"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "errors": result.stderr
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def lint_code(self, filename):
        """Run pylint untuk code quality check"""
        filepath = self.workspace / filename
        
        try:
            result = subprocess.run(
                ["pylint", str(filepath)],
                capture_output=True,
                text=True
            )
            
            return {
                "score": self._extract_pylint_score(result.stdout),
                "output": result.stdout
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _extract_pylint_score(self, output):
        """Extract score dari pylint output"""
        for line in output.split("\n"):
            if "Your code has been rated at" in line:
                score = line.split("rated at ")[1].split("/")[0]
                return float(score)
        return 0.0

# Integration dengan AutoGen
def create_executor_agent():
    executor = SafeCodeExecutor()
    
    def execute_code_function(code: str, filename: str = "script.py") -> str:
        """Function yang bisa dipanggil oleh agent"""
        result = executor.execute_python(code, filename)
        
        if result["success"]:
            return f"✓ Execution successful\n\nOutput:\n{result['stdout']}"
        else:
            return f"✗ Execution failed\n\nError:\n{result['stderr']}"
    
    return execute_code_function