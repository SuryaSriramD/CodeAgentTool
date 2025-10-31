#!/usr/bin/env python3
"""Fix ChatMessage constructor call in chat_agent.py"""

import subprocess

# Read the current file
result = subprocess.run([
    'docker', 'exec', 'codeagent-scanner-backend',
    'cat', '/app/camel/agents/chat_agent.py'
], capture_output=True, text=False)

content = result.stdout.decode('utf-8', errors='ignore')

# Find and replace the broken ChatMessage call
# The issue is that ChatMessage needs explicit role parameter
old_code = '''            output_messages = [
                ChatMessage(role_name=self.role_name, role_type=self.role_type,
                            meta_dict=dict(), **dict(choice["message"]))
                for choice in response["choices"]
            ]'''

new_code = '''            output_messages = [
                ChatMessage(role_name=self.role_name, role_type=self.role_type,
                            meta_dict=dict(), role=choice["message"]["role"], 
                            content=choice["message"]["content"])
                for choice in response["choices"]
            ]'''

if old_code in content:
    content = content.replace(old_code, new_code)
    print("✓ Found and fixed ChatMessage constructor")
else:
    print("✗ Could not find the exact code to replace")
    print("Trying alternative fix...")
    # Try a more flexible replacement
    import re
    pattern = r'(output_messages = \[\s*ChatMessage\(role_name=self\.role_name, role_type=self\.role_type,\s*meta_dict=dict\(\),) \*\*dict\(choice\["message"\]\)\)'
    replacement = r'\1 role=choice["message"]["role"], content=choice["message"]["content"])'
    content, count = re.subn(pattern, replacement, content)
    if count > 0:
        print(f"✓ Fixed {count} occurrence(s) using regex")
    else:
        print("✗ Could not apply fix")
        exit(1)

# Write fixed content to temp file
with open('chat_agent_fixed.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Created fixed file: chat_agent_fixed.py")

# Copy to container
result = subprocess.run([
    'docker', 'cp',
    'chat_agent_fixed.py',
    'codeagent-scanner-backend:/app/camel/agents/chat_agent.py'
], capture_output=True, text=True)

if result.returncode == 0:
    print("✓ Copied fixed file to container")
else:
    print(f"✗ Error copying: {result.stderr}")
    exit(1)

# Validate syntax
result = subprocess.run([
    'docker', 'exec', 'codeagent-scanner-backend',
    'python3', '-m', 'py_compile', '/app/camel/agents/chat_agent.py'
], capture_output=True, text=True)

if result.returncode == 0:
    print("✓ Python syntax validated")
else:
    print(f"✗ Syntax error: {result.stderr}")
    exit(1)

print("\n✓ ChatAgent fix applied successfully!")
print("Restart the backend to apply changes.")
