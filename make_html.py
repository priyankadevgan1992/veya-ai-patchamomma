import markdown
import os
import re

md_path = r'C:\Users\DELL\.gemini\antigravity\brain\8ce829a2-0cba-49c3-9ee5-e229de673013\veya_tech_documentation.md'
html_path = r'C:\patchamomma\prac1\veya_tech_documentation.html'

with open(md_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Replace the mermaid code block with an image tag pointing to our new high-res PNG
mermaid_regex = r'```mermaid.*?```'
text = re.sub(mermaid_regex, r'<img src="file:///C:/patchamomma/prac1/architecture.png" style="width: 100%; max-width: 800px; display: block; margin: 20px auto; border: 1px solid #eaeaea; border-radius: 8px;">', text, flags=re.DOTALL)

html = markdown.markdown(text, extensions=['fenced_code', 'tables'])

full_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Veya AI Technical Documentation</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }}
        h1, h2, h3 {{ color: #333; }}
        code {{ background-color: #f4f4f4; padding: 2px 5px; border-radius: 3px; }}
        pre {{ background-color: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto; }}
    </style>
</head>
<body>
{html}
</body>
</html>
"""

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(full_html)
print(f"Successfully created: {html_path}")
