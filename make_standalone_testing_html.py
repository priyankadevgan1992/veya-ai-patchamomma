import markdown

md_path = r'C:\Users\DELL\.gemini\antigravity\brain\8ce829a2-0cba-49c3-9ee5-e229de673013\testing_instructions.md'
html_path = r'c:\patchamomma\prac1\Testing_Instructions_Standalone.html'

with open(md_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Convert markdown to HTML
html = markdown.markdown(text, extensions=['fenced_code', 'tables'])

# Wrapping in HTML with highly professional, standalone styling
full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Veya AI Testing Instructions</title>
    <style>
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; 
            line-height: 1.7; 
            color: #333; 
            background-color: #f7f9fc; 
            margin: 0; 
            padding: 40px 20px; 
        }}
        .container {{ 
            max-width: 900px; 
            margin: 0 auto; 
            background-color: #ffffff; 
            padding: 50px 60px; 
            border-radius: 16px; 
            box-shadow: 0 4px 30px rgba(0,0,0,0.05); 
        }}
        h1 {{ 
            color: #111827; 
            font-size: 2.2em; 
            border-bottom: 3px solid #f3f4f6; 
            padding-bottom: 15px; 
            margin-bottom: 30px; 
        }}
        h2 {{ 
            color: #1f2937; 
            font-size: 1.5em; 
            margin-top: 40px; 
            border-bottom: 1px solid #e5e7eb; 
            padding-bottom: 10px; 
        }}
        h3 {{ color: #374151; font-size: 1.25em; }}
        p {{ font-size: 16px; margin-bottom: 20px; }}
        ul, ol {{ font-size: 16px; margin-bottom: 20px; padding-left: 25px; display: block; }}
        li {{ margin-bottom: 10px; display: list-item; line-height: 1.6; }}
        strong {{ color: #000; font-weight: 600; }}
        em {{ color: #4b5563; }}
        a {{ color: #2563eb; text-decoration: none; font-weight: bold; }}
        a:hover {{ text-decoration: underline; }}
        code {{ 
            background-color: #f3f4f6; 
            padding: 3px 6px; 
            border-radius: 4px; 
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; 
            font-size: 14px; 
            color: #db2777; 
        }}
        @media (max-width: 768px) {{
            .container {{ padding: 30px 25px; }}
            h1 {{ font-size: 1.8em; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        {html}
    </div>
</body>
</html>"""

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(full_html)
print(f'HTML generated successfully at {html_path}')
