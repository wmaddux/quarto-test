__version__ = "1.4.0"
import os
import re

rules_dir = "rules"
for filename in os.listdir(rules_dir):
    if filename.endswith(".py") and filename != "__init__.py":
        filepath = os.path.join(rules_dir, filename)
        with open(filepath, 'r') as f:
            content = f.read()

        # Matches "name": "4.a: Hot Key Detection"
        pattern = r'"name":\s*"(\d+\.[a-z]):\s*(.*?)"'
        
        if re.search(pattern, content):
            # Replaces with "id": "4.a", "name": "Hot Key Detection"
            new_content = re.sub(pattern, r'"id": "\1", "name": "\2"', content)
            with open(filepath, 'w') as f:
                f.write(new_content)
            print(f"✅ Updated {filename}")
