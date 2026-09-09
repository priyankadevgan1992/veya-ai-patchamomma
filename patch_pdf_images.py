import os

with open('generate_full_pdf.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace the old image paths with the new ones
text = text.replace(
    r"img1_png = r'C:\Users\DELL\.gemini\antigravity\brain\8ce829a2-0cba-49c3-9ee5-e229de673013\.user_uploaded\media_1788468059100.png'",
    r"img1_png = r'C:\Users\DELL\.gemini\antigravity\brain\8ce829a2-0cba-49c3-9ee5-e229de673013\.user_uploaded\media_1788471346705.png'"
)
text = text.replace(
    r'img1_png = r"C:\Users\DELL\.gemini\antigravity\brain\8ce829a2-0cba-49c3-9ee5-e229de673013\.user_uploaded\media_1788468059100.png"',
    r'img1_png = r"C:\Users\DELL\.gemini\antigravity\brain\8ce829a2-0cba-49c3-9ee5-e229de673013\.user_uploaded\media_1788471346705.png"'
)

text = text.replace(
    r"img2_png = r'C:\Users\DELL\.gemini\antigravity\brain\8ce829a2-0cba-49c3-9ee5-e229de673013\.user_uploaded\media_1788462985901.png'",
    r"img2_png = r'C:\Users\DELL\.gemini\antigravity\brain\8ce829a2-0cba-49c3-9ee5-e229de673013\.user_uploaded\media_1788471362086.png'"
)
text = text.replace(
    r'img2_png = r"C:\Users\DELL\.gemini\antigravity\brain\8ce829a2-0cba-49c3-9ee5-e229de673013\.user_uploaded\media_1788462985901.png"',
    r'img2_png = r"C:\Users\DELL\.gemini\antigravity\brain\8ce829a2-0cba-49c3-9ee5-e229de673013\.user_uploaded\media_1788471362086.png"'
)

text = text.replace(
    r"img3_png = r'C:\Users\DELL\.gemini\antigravity\brain\8ce829a2-0cba-49c3-9ee5-e229de673013\.user_uploaded\media_1788460683262.png'",
    r"img3_png = r'C:\Users\DELL\.gemini\antigravity\brain\8ce829a2-0cba-49c3-9ee5-e229de673013\.user_uploaded\media_1788471362081.png'"
)
text = text.replace(
    r'img3_png = r"C:\Users\DELL\.gemini\antigravity\brain\8ce829a2-0cba-49c3-9ee5-e229de673013\.user_uploaded\media_1788460683262.png"',
    r'img3_png = r"C:\Users\DELL\.gemini\antigravity\brain\8ce829a2-0cba-49c3-9ee5-e229de673013\.user_uploaded\media_1788471362081.png"'
)

text = text.replace(
    r"img4_png = r'C:\Users\DELL\.gemini\antigravity\brain\8ce829a2-0cba-49c3-9ee5-e229de673013\.user_uploaded\media_1787834578506.png'",
    r"img4_png = r'C:\Users\DELL\.gemini\antigravity\brain\8ce829a2-0cba-49c3-9ee5-e229de673013\.user_uploaded\media_1788471362082.png'"
)
text = text.replace(
    r'img4_png = r"C:\Users\DELL\.gemini\antigravity\brain\8ce829a2-0cba-49c3-9ee5-e229de673013\.user_uploaded\media_1787834578506.png"',
    r'img4_png = r"C:\Users\DELL\.gemini\antigravity\brain\8ce829a2-0cba-49c3-9ee5-e229de673013\.user_uploaded\media_1788471362082.png"'
)

# Add the 5th image (Voice calling)
new_code = r'''
    img5_png = r"C:\Users\DELL\.gemini\antigravity\brain\8ce829a2-0cba-49c3-9ee5-e229de673013\.user_uploaded\media_1788471362133.png"
    img5 = get_jpg_path(img5_png)
    
    pdf.add_page()
    pdf.chapter_title('SECTION 07: Voice Fallback')
    pdf.body_text("When severe anxiety is detected in the chat log, Veya bypasses normal actionable interventions and triggers a simulated live audio call to de-escalate the situation.")
    y_pos = pdf.get_y() + 5
    try:
        if img5:
            pdf.image(img5, x=65, y=y_pos, w=80)
    except Exception as e:
        print(f"Skipping image 5 due to error: {e}")
'''

if 'SECTION 07: Voice Fallback' not in text:
    text = text.replace("pdf.set_y(230)\n    pdf.section_title('Conclusion')", new_code + "\n    pdf.add_page()\n    pdf.set_y(50)\n    pdf.section_title('Conclusion')")

with open('generate_full_pdf.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("generate_full_pdf.py patched with new screenshots")
