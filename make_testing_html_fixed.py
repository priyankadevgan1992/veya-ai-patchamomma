import markdown

md_path = r'C:\Users\DELL\.gemini\antigravity\brain\8ce829a2-0cba-49c3-9ee5-e229de673013\testing_instructions.md'
html_path = r'c:\patchamomma\prac1\Testing_Instructions.html'

with open(md_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Convert markdown to HTML
html = markdown.markdown(text, extensions=['fenced_code', 'tables'])

# Wrapping in HTML with explicit styles to force list items to block layout
full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Veya AI Testing Instructions</title>
    <style>
        body {{ font-family: sans-serif; line-height: 1.7; padding: 40px; max-width: 900px; margin: 0 auto; }}
        h1, h2, h3 {{ color: #111827; }}
        p {{ margin-bottom: 15px; }}
        /* Explicitly force lists to block with margin to ensure new lines */
        ul, ol {{ display: block; margin-top: 10px; margin-bottom: 20px; padding-left: 30px; }}
        li {{ display: list-item; margin-bottom: 10px; line-height: 1.6; }}
    </style>
</head>
<body>
{html}
</body>
</html>"""

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(full_html)
print('HTML updated')
