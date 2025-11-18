import autogen
from config.agent_config import load_llm_config

class CodingAgent:
    def __init__(self, model_config="coding_config"):
        self.llm_config = load_llm_config(model_config)
        
        self.agent = autogen.AssistantAgent(
            name="Senior_Python_Developer",
            system_message="""You are a senior Python developer with expertise in:
            - Writing clean, efficient, and well-documented code
            - Following PEP 8 style guidelines
            - Implementing best practices and design patterns
            - Error handling and edge cases
            - Writing comprehensive docstrings
            
            When writing code:
            1. Always include proper error handling
            2. Add clear comments for complex logic
            3. Use type hints
            4. Write modular and reusable code
            5. Consider performance and scalability
            """,
            llm_config=self.llm_config,
        )
    
    def get_agent(self):
        return self.agent

if __name__ == "__main__":
    coder = CodingAgent()
    
    user_proxy = autogen.UserProxyAgent(
        name="User",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=10,
        code_execution_config={
            "work_dir": "coding_workspace",
            "use_docker": False,
        }
    )
    
    # Test agent
    user_proxy.initiate_chat(
        coder.get_agent(),
        message="Create a Python function to calculate Fibonacci sequence with memoization."
    )