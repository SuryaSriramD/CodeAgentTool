#!/usr/bin/env python3
"""Fix post_processing error handling in camel_bridge.py"""

import subprocess

# Read current file
result = subprocess.run([
    'docker', 'exec', 'codeagent-scanner-backend',
    'cat', '/app/integration/camel_bridge.py'
], capture_output=True, text=False)

content = result.stdout.decode('utf-8', errors='ignore')

# Fix post_processing call
old_code = '''            chat_chain.execute_chain()
            chat_chain.post_processing()
            
            # Extract recommendations from the generated output'''

new_code = '''            chat_chain.execute_chain()
            
            # post_processing() may fail if log file doesn't exist, but that's okay
            try:
                chat_chain.post_processing()
            except FileNotFoundError as e:
                logger.warning(f"post_processing failed (non-critical): {e}")
            
            # Extract recommendations from the generated output'''

if old_code in content:
    content = content.replace(old_code, new_code)
    print("✓ Fixed post_processing error handling")
else:
    print("✗ Could not find the code to replace")
    exit(1)

# Write to temp file
with open('camel_bridge_fixed.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Created: camel_bridge_fixed.py")

# Copy to container
result = subprocess.run([
    'docker', 'cp',
    'camel_bridge_fixed.py',
    'codeagent-scanner-backend:/tmp/camel_bridge.py'
], capture_output=True, text=True)

if result.returncode != 0:
    print(f"✗ Copy failed: {result.stderr}")
    exit(1)

# Move it into place (as root)
result = subprocess.run([
    'docker', 'exec', '-u', 'root', 'codeagent-scanner-backend',
    'mv', '/tmp/camel_bridge.py', '/app/integration/camel_bridge.py'
], capture_output=True, text=True)

if result.returncode == 0:
    print("✓ File deployed")
else:
    print(f"✗ Move failed: {result.stderr}")
    exit(1)

print("\n✓ Fix applied! Restart backend.")
