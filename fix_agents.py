import os
import re

def fix_function_params(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    
    # Replace 'str = None' with 'str = ""'
    content = re.sub(r'(\w+: str) = None', r'\1 = ""', content)
    
    # Replace 'if parameter:' with 'if parameter and parameter.strip():'
    content = re.sub(r'if (\w+):', r'if \1 and \1.strip():', content)
    
    with open(file_path, 'w') as file:
        file.write(content)
    
    print(f"Fixed {file_path}")

# Fix all agent files
agent_dir = "backend/agents"
for filename in os.listdir(agent_dir):
    if filename.endswith(".py"):
        fix_function_params(os.path.join(agent_dir, filename))
