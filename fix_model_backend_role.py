#!/usr/bin/env python3
"""Fix model_backend.py to include 'role' in the response"""

import subprocess

# Read current file
result = subprocess.run([
    'docker', 'exec', 'codeagent-scanner-backend',
    'cat', '/app/camel/model_backend.py'
], capture_output=True, text=False)

content = result.stdout.decode('utf-8', errors='ignore')

# Fix the response to include 'role', 'id', and 'finish_reason'
old_text = '''            response = {
                "choices": [{"message": {"role": "assistant", "content": completion.choices[0].message.content}}],
                "usage": {
                    "prompt_tokens": completion.usage.prompt_tokens,
                    "completion_tokens": completion.usage.completion_tokens,
                    "total_tokens": completion.usage.total_tokens
                }
            }'''

new_text = '''            response = {
                "id": completion.id if hasattr(completion, 'id') else "chatcmpl-" + str(hash(completion.choices[0].message.content))[:8],
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": completion.choices[0].message.content
                    },
                    "finish_reason": completion.choices[0].finish_reason if hasattr(completion.choices[0], 'finish_reason') else "stop"
                }],
                "usage": {
                    "prompt_tokens": completion.usage.prompt_tokens,
                    "completion_tokens": completion.usage.completion_tokens,
                    "total_tokens": completion.usage.total_tokens
                }
            }'''

if old_text in content:
    content = content.replace(old_text, new_text)
    print(f"✓ Fixed: Added 'role', 'id', and 'finish_reason' fields")
else:
    print("✗ Could not find the exact text to fix")
    print("Current response structure:")
    for i, line in enumerate(content.split('\n'), 1):
        if 'response = {' in line:
            # Print 10 lines around it
            lines = content.split('\n')
            for j in range(max(0, i-2), min(len(lines), i+10)):
                print(f"Line {j+1}: {lines[j]}")
    exit(1)

# Write to temp file
with open('model_backend_fixed2.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Created: model_backend_fixed2.py")

# Copy to container
result = subprocess.run([
    'docker', 'cp',
    'model_backend_fixed2.py',
    'codeagent-scanner-backend:/app/camel/model_backend.py'
], capture_output=True, text=True)

if result.returncode == 0:
    print("✓ Copied to container")
else:
    print(f"✗ Copy failed: {result.stderr}")
    exit(1)

# Validate
result = subprocess.run([
    'docker', 'exec', 'codeagent-scanner-backend',
    'python3', '-m', 'py_compile', '/app/camel/model_backend.py'
], capture_output=True, text=True)

if result.returncode == 0:
    print("✓ Syntax validated")
    print("\n✓ Fix applied successfully! Restart backend.")
else:
    print(f"✗ Syntax error: {result.stderr}")
    exit(1)
