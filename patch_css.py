def patch_css():
    with open('veya_web/index.html', 'r', encoding='utf-8') as f:
        html = f.read()
    
    old_css = '''    <style>
      .fval:disabled, .o-fval:disabled {
        color: #888;
        background: transparent;
        border: 1px solid transparent;
        appearance: none;
        -webkit-appearance: none;
      }
      .fval:not(:disabled), .o-fval:not(:disabled) {
        background: #fff;
        border: 1px solid #ccc;
        border-radius: 4px;
        padding: 4px 8px;
        color: #000;
      }
      .orbit-row {
        display: flex;
        gap: 8px;
        margin-bottom: 8px;
        align-items: center;
      }
      .orbit-row input {
        flex: 1;
      }
    </style>'''

    new_css = '''    <style>
      .form-row .fval:disabled, .form-row input:disabled, .orbit-row .o-fval:disabled {
        color: #aaa !important;
        background: transparent !important;
        border: 1px solid transparent !important;
        appearance: none;
        -webkit-appearance: none;
        opacity: 1; /* For iOS */
      }
      .form-row .fval:not(:disabled), .form-row input:not(:disabled), .orbit-row .o-fval:not(:disabled) {
        background: #fff !important;
        border: 1px solid #ccc !important;
        border-radius: 4px !important;
        padding: 4px 8px !important;
        color: #000 !important;
      }
      .orbit-row {
        display: flex;
        gap: 8px;
        margin-bottom: 8px;
        align-items: center;
      }
      .orbit-row input {
        flex: 1;
      }
    </style>'''

    if old_css in html:
        html = html.replace(old_css, new_css)
        with open('veya_web/index.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print("CSS patched!")
    else:
        print("Old CSS not found!")

if __name__ == '__main__':
    patch_css()
