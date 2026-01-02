import re
with open('/app/integration/camel_bridge.py', 'r') as f:
    content = f.read()
    
# Replace the post_processing line with try-except
content = re.sub(
    r'(\s+)chat_chain\.post_processing\(\)',
    r'\1try:\n\1    chat_chain.post_processing()\n\1except Exception as e:\n\1    logger.warning(f"post_processing failed: {e}")',
    content
)

with open('/app/integration/camel_bridge.py', 'w') as f:
    f.write(content)
print('Fixed camel_bridge.py')
