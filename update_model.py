import os
import re

def update_model(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    
    # Replace 'model="gemini-2.0-flash"' with 'model="gemini-1.5-flash"'
    content = re.sub(r'model="gemini-2.0-flash"', r'model="gemini-1.5-flash"', content)
    
    with open(file_path, 'w') as file:
        file.write(content)
    
    print(f"Updated model in {file_path}")

# Update all agent files
agent_dir = "backend/agents"
for filename in os.listdir(agent_dir):
    if filename.endswith(".py"):
        update_model(os.path.join(agent_dir, filename))
