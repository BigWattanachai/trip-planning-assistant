import os
import re

def remove_google_search(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    
    # Remove the import for google_search
    content = re.sub(r'from google\.adk\.tools import google_search\n', '', content)
    
    # Remove google_search from the tools list
    content = re.sub(r', google_search', '', content)
    
    with open(file_path, 'w') as file:
        file.write(content)
    
    print(f"Removed Google search from {file_path}")

# Update all agent files
agent_dir = "backend/agents"
for filename in os.listdir(agent_dir):
    if filename.endswith(".py"):
        remove_google_search(os.path.join(agent_dir, filename))
