import os
import json
from dotenv import load_dotenv

load_dotenv()

def load_llm_config(config_name="gpt_config"):
    with open("config/llm_config.json", "r") as f:
        configs = json.load(f)
    
    config = configs[config_name]
    
    # Replace environment variables
    for key, value in config.items():
        if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
            env_var = value[2:-1]
            config[key] = os.getenv(env_var)
    
    return {
        "config_list": [config],
        "timeout": 120,
    }

# Untuk GLM API (custom endpoint)
def get_glm_config():
    return {
        "config_list": [{
            "model": "glm-4-flash",
            "api_key": os.getenv("GLM_API_KEY"),
            "base_url": os.getenv("GLM_API_BASE"),
            "api_type": "openai",  # GLM compatible dengan OpenAI API
        }],
        "timeout": 120,
    }