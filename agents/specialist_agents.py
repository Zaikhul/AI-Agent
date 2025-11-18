import autogen
from config.agent_config import load_llm_config, get_glm_config

class CodeSpecialists:
    def __init__(self):
        # Architect menggunakan GPT-4
        self.architect = autogen.AssistantAgent(
            name="Software_Architect",
            system_message="""You are a software architect responsible for:
            - Designing system architecture
            - Defining module structure
            - Planning scalable solutions
            - Identifying design patterns
            - Creating technical specifications
            
            Provide high-level design before implementation.
            """,
            llm_config=load_llm_config("gpt_config"),
        )
        
        # Coder menggunakan GPT-4 (lebih fokus pada implementasi)
        self.coder = autogen.AssistantAgent(
            name="Python_Developer",
            system_message="""You are an expert Python developer:
            - Implement code based on architectural design
            - Write clean, efficient code
            - Follow PEP 8 standards
            - Add comprehensive docstrings
            - Handle errors properly
            - Use type hints
            """,
            llm_config=load_llm_config("coding_config"),
        )
        
        # Reviewer menggunakan GLM-4 (cost-effective untuk review)
        self.reviewer = autogen.AssistantAgent(
            name="Code_Reviewer",
            system_message="""You are a code reviewer focusing on:
            - Code quality and readability
            - Bug detection
            - Performance issues
            - Security vulnerabilities
            - Best practices compliance
            
            Provide constructive feedback with specific suggestions.
            """,
            llm_config=get_glm_config(),
        )
        
        # Tester menggunakan GLM-4
        self.tester = autogen.AssistantAgent(
            name="QA_Engineer",
            system_message="""You are a QA engineer responsible for:
            - Writing comprehensive unit tests
            - Creating test cases for edge cases
            - Using pytest framework
            - Ensuring code coverage
            - Testing error handling
            """,
            llm_config=get_glm_config(),
        )
        
        # User proxy untuk eksekusi code
        self.executor = autogen.UserProxyAgent(
            name="Code_Executor",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=0,
            code_execution_config={
                "work_dir": "workspace",
                "use_docker": False,
                "last_n_messages": 3,
            }
        )

    def get_all_agents(self):
        return [
            self.architect,
            self.coder,
            self.reviewer,
            self.tester,
            self.executor
        ]