import autogen
from agents.specialist_agents import CodeSpecialists

class CodingWorkflow:
    def __init__(self):
        self.specialists = CodeSpecialists()
        
        # Setup group chat
        self.group_chat = autogen.GroupChat(
            agents=self.specialists.get_all_agents(),
            messages=[],
            max_round=20,
            speaker_selection_method="round_robin",
        )
        
        self.manager = autogen.GroupChatManager(
            groupchat=self.group_chat,
            llm_config=load_llm_config("gpt_config"),
        )
    
    def execute_coding_task(self, task_description):
        """
        Workflow lengkap:
        1. Architect merancang struktur
        2. Developer mengimplementasi
        3. Reviewer melakukan code review
        4. Tester membuat unit tests
        5. Executor menjalankan code dan tests
        """
        
        initial_message = f"""
        New coding task: {task_description}
        
        Workflow:
        1. Software_Architect: Design the solution architecture
        2. Python_Developer: Implement the code based on design
        3. Code_Reviewer: Review the implementation
        4. QA_Engineer: Write unit tests
        5. Code_Executor: Run the code and tests
        
        Let's begin!
        """
        
        self.specialists.executor.initiate_chat(
            self.manager,
            message=initial_message
        )

# Sequential Workflow (lebih terstruktur)
class SequentialCodingWorkflow:
    def __init__(self):
        self.specialists = CodeSpecialists()
    
    def execute(self, task):
        """Workflow sequential untuk kontrol lebih baik"""
        
        print("=== PHASE 1: ARCHITECTURE DESIGN ===")
        design = self._get_design(task)
        
        print("\n=== PHASE 2: IMPLEMENTATION ===")
        code = self._implement_code(design)
        
        print("\n=== PHASE 3: CODE REVIEW ===")
        review = self._review_code(code)
        
        print("\n=== PHASE 4: TESTING ===")
        tests = self._create_tests(code)
        
        print("\n=== PHASE 5: EXECUTION ===")
        self._execute_code(code, tests)
        
        return {
            "design": design,
            "code": code,
            "review": review,
            "tests": tests
        }
    
    def _get_design(self, task):
        user_proxy = autogen.UserProxyAgent(
            name="user",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=1,
        )
        
        user_proxy.initiate_chat(
            self.specialists.architect,
            message=f"Design architecture for: {task}"
        )
        
        return user_proxy.last_message()["content"]
    
    def _implement_code(self, design):
        user_proxy = autogen.UserProxyAgent(
            name="user",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=1,
        )
        
        user_proxy.initiate_chat(
            self.specialists.coder,
            message=f"Implement this design:\n\n{design}"
        )
        
        return user_proxy.last_message()["content"]
    
    def _review_code(self, code):
        user_proxy = autogen.UserProxyAgent(
            name="user",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=1,
        )
        
        user_proxy.initiate_chat(
            self.specialists.reviewer,
            message=f"Review this code:\n\n{code}"
        )
        
        return user_proxy.last_message()["content"]
    
    def _create_tests(self, code):
        user_proxy = autogen.UserProxyAgent(
            name="user",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=1,
        )
        
        user_proxy.initiate_chat(
            self.specialists.tester,
            message=f"Write unit tests for:\n\n{code}"
        )
        
        return user_proxy.last_message()["content"]
    
    def _execute_code(self, code, tests):
        self.specialists.executor.initiate_chat(
            self.specialists.executor,
            message=f"Execute this code and tests:\n\n{code}\n\n{tests}"
        )