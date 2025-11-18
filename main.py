from workflows.coding_workflow import SequentialCodingWorkflow
from tools.code_executor import SafeCodeExecutor
import sys

def main():
    print("=== AI Coding Agent System ===\n")
    
    # Initialize workflow
    workflow = SequentialCodingWorkflow()
    
    # Example task
    task = """
    Create a Python class for a simple REST API client with:
    - GET, POST, PUT, DELETE methods
    - Error handling for network errors
    - Retry logic with exponential backoff
    - Request/response logging
    - Type hints and docstrings
    """
    
    print(f"Task: {task}\n")
    print("Starting workflow...\n")
    
    try:
        result = workflow.execute(task)
        
        print("\n=== WORKFLOW COMPLETE ===")
        print("\nDesign:", result["design"][:200], "...")
        print("\nCode generated successfully!")
        print("\nReview:", result["review"][:200], "...")
        print("\nTests created!")
        
    except Exception as e:
        print(f"\nError during execution: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()