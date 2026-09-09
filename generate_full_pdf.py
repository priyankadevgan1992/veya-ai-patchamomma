import os
from fpdf import FPDF
from PIL import Image

def get_jpg_path(png_path):
    if not os.path.exists(png_path):
        return None
    jpg_path = png_path.replace('.png', '.jpg')
    if not os.path.exists(jpg_path):
        try:
            im = Image.open(png_path)
            rgb_im = im.convert('RGB')
            rgb_im.save(jpg_path, 'JPEG')
        except Exception as e:
            print(f"Error converting {png_path}: {e}")
            return None
    return jpg_path

class PDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, 'V E Y A A I - Comprehensive Product Concept', 0, 0, 'L')
        self.set_font('Helvetica', '', 10)
        self.cell(0, 10, 'Full Scope Submission', 0, 1, 'R')
        self.set_draw_color(200, 200, 200)
        self.line(10, 20, 200, 20)
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Helvetica', 'B', 18)
        self.set_text_color(20, 30, 60)
        self.cell(0, 10, title, 0, 1, 'L')
        self.set_draw_color(50, 50, 50)
        self.line(10, self.get_y(), 80, self.get_y())
        self.ln(8)

    def section_title(self, title):
        self.set_font('Helvetica', 'B', 14)
        self.set_text_color(40, 40, 40)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(2)

    def body_text(self, text):
        self.set_font('Helvetica', '', 12)
        self.set_text_color(60, 60, 60)
        self.multi_cell(0, 8, text)
        self.ln(5)
        
    def bullet_point(self, title, text):
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(40, 40, 40)
        
        self.cell(5, 8, "-", 0, 0, 'R')
        self.cell(45, 8, title, 0, 0, 'L')
        
        self.set_font('Helvetica', '', 12)
        self.set_text_color(60, 60, 60)
        
        self.multi_cell(0, 8, text)
        self.ln(3)

def create_pdf():
    pdf = PDF()
    
    # --- PAGE 1: COVER ---
    pdf.add_page()
    pdf.ln(50)
    pdf.set_font('Helvetica', 'B', 48)
    pdf.set_text_color(20, 30, 60)
    pdf.cell(0, 20, 'VeyaAI', 0, 1, 'C')
    
    pdf.set_font('Helvetica', 'I', 16)
    pdf.set_text_color(100, 100, 100)
    pdf.ln(10)
    pdf.cell(0, 10, "A Personal Life Intelligence System.", 0, 1, 'C')
    pdf.cell(0, 10, "Because insight without action is just anxiety.", 0, 1, 'C')
    
    pdf.ln(60)
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 8, 'SUBMITTED FOR: Patchamomma 2026', 0, 1, 'C')
    pdf.cell(0, 8, 'CATEGORY: Personal Life Intelligence', 0, 1, 'C')
    pdf.cell(0, 8, 'SCOPE: Full System Architecture & Product Concept', 0, 1, 'C')

    # --- PAGE 2: EXECUTIVE SUMMARY ---
    pdf.add_page()
    pdf.chapter_title('SECTION 01: Executive Summary')
    
    pdf.section_title('The Core Problem')
    pdf.body_text("In today's hyper-connected world, we juggle complex, intersecting responsibilities: work meetings, caregiving, physical health, and personal anchors. Existing tools like generic calendar apps, fitness trackers, or standard LLM chatbots are fundamentally disconnected. They only look at one slice of data at a time.")
    pdf.body_text("A standard calendar app does not understand that a high-stress client call at 6:00 PM directly ruins a family dinner at 7:00 PM. A fitness tracker tells you your sleep is poor, but it cannot automatically reschedule your 8:00 AM status update to give you an extra hour of rest. Furthermore, most modern AI tools provide 'Dashboards' and 'Analytics'. But giving an overwhelmed user a dashboard showing they are 90% stressed only creates more anxiety.")
    
    pdf.section_title('The VeyaAI Solution')
    pdf.body_text("VeyaAI bridges this gap by acting as a proactive Personal Life Intelligence system. It is a digital twin that observes your life, extracts deep contextual meaning from casual conversations, integrates with live APIs, and most importantly, takes action.")
    pdf.body_text("Instead of just passively chatting, Veya negotiates your calendar, respects your cognitive limits, and actively reshuffles your life before burnout hits. Veya transitions from being a passive chat tool into a persistent, learning co-pilot that fiercely protects your time, mental load, and the people you care about most.")

    # --- PAGE 3: 7-D COGNITIVE MATRIX ---
    pdf.add_page()
    pdf.chapter_title('SECTION 02: Cognitive Decision Matrix')
    pdf.body_text("To act on behalf of a human, VeyaAI cannot just look at free time blocks on a calendar. It uses a sophisticated 7-Dimensional mathematical engine (The PatternAgent) to weigh tradeoffs and prioritize what matters most to the user's holistic well-being.")
    
    pdf.ln(5)
    pdf.bullet_point("1. Chrono-Energy:", "Accounts for peak focus hours and calculates transition lag after hard meetings. Veya knows you need 30 minutes to decompress after a high-stakes pitch.")
    pdf.bullet_point("2. Relational Capital:", "Powered by the Household Orbit profile, this weights the importance (1-100%) of family members and friends. Veya actively tracks if you are in a relational deficit with your spouse or child.")
    pdf.bullet_point("3. Cognitive Load:", "Distinguishes high-stakes preparation from routine execution. Veya will clear small tasks to make room for deep work.")
    pdf.bullet_point("4. Bio Reserves:", "Factors in sleep debt, physical exhaustion, and biological phases (like the menstrual cycle) to adjust daily capacity.")
    pdf.bullet_point("5. Geography:", "Calculates transit buffers and spatial displacement so you aren't booked for a virtual meeting while driving.")
    pdf.bullet_point("6. Resilience:", "Monitors real-time chat for anxiety spikes. If severe stress is detected, Veya abandons standard task-planning and triggers a Voice-Call intervention.")
    pdf.bullet_point("7. Downstream:", "Measures the compounding penalty of delaying an event. Missing a casual sync is fine; missing a doctor's appointment has high downstream costs.")

    # --- PAGE 4: MULTI-AGENT ARCHITECTURE ---
    pdf.add_page()
    pdf.chapter_title('SECTION 03: System Architecture')
    pdf.body_text("VeyaAI's intelligence is not a single, monolithic AI prompt. It is a distributed, multi-agent pipeline built on Google Cloud (Vertex AI / Gemini 2.5) and a FastAPI Python backend.")
    
    pdf.section_title('The 6-Agent Pipeline')
    pdf.body_text("When a user sends a message, it is routed through specialized deterministic agents:")
    
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 8, "1. OnboardingEngine", 0, 1)
    pdf.set_font('Helvetica', '', 12)
    pdf.body_text("A conversational intercept that gently gathers baseline anchors (Name, Role, Life Anchor) without interrogating the user.")
    
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 8, "2. ContextAgent", 0, 1)
    pdf.set_font('Helvetica', '', 12)
    pdf.body_text("The aggregator. It merges Live Google Calendar data with the user's local SQLite profile, Household Orbit, and immediate chat history.")

    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 8, "3. TwinBuilder (RAG Storage)", 0, 1)
    pdf.set_font('Helvetica', '', 12)
    pdf.body_text("Extracts static facts from casual conversation (e.g., 'My son is sick today') and writes them into a long-term vector memory database.")

    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 8, "4. PatternAgent", 0, 1)
    pdf.set_font('Helvetica', '', 12)
    pdf.body_text("The math engine that powers the 7-D Cognitive Matrix, calculating current stress and energy reserves.")

    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 8, "5. ActionAgent", 0, 1)
    pdf.set_font('Helvetica', '', 12)
    pdf.body_text("The negotiator. Computes realistic, 1-tap JSON Action Cards (e.g., Compress Meeting, Reschedule, Delegate).")

    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 8, "6. GeminiEngine (The Voice)", 0, 1)
    pdf.set_font('Helvetica', '', 12)
    pdf.body_text("Uses TF-IDF cosine similarity to pull past relevant memories and synthesize a warm, empathetic reply via Vertex AI.")

    # --- PAGE 5: DATA ECOSYSTEM ---
    pdf.add_page()
    pdf.chapter_title('SECTION 04: Data & The Feedback Loop')
    
    pdf.section_title('Real-World Data Ingestion')
    pdf.body_text("Veya relies on a robust SQLite database (veya_app.db) that manages Identity, Twin Profiles, Short-Term Memory, and Vector Memory. We integrate:")
    pdf.body_text("- Live Google Calendar APIs for bi-directional sync (Take-Action-On-Approval).")
    pdf.body_text("- Household Orbit Maps: A dedicated UI where users add key people, their relation, context, and a 1-100% importance score.")
    pdf.body_text("- Wearables Integration: Tracking physical markers to automatically update the 'Biological Reserves' dimension.")

    pdf.section_title('The Maturity Engine')
    pdf.body_text("Veya gets smarter through telemetry. When Veya proposes an 'Action Card' and the user applies it, the action executes via API. A micro-survey later asks if the intervention helped (Thumbs up/down). This feedback is stored in 'action_outcomes', filtering noise and allowing Veya to eventually auto-execute high-confidence patterns.")

    # --- PAGE 6: FRONTEND UI & INTERVENTIONS ---
    pdf.add_page()
    pdf.chapter_title('SECTION 05: User Experience & UI')
    pdf.body_text("The frontend is a mobile-first, Flutter-inspired web client designed to reduce cognitive friction.")
    
    pdf.section_title('Core UI Components')
    pdf.body_text("1. Home Chat: A conversational interface with Speech-to-Text capabilities. If severe anxiety is detected, a Voice Call Intervention modal triggers, simulating a live empathetic audio call.")
    pdf.body_text("2. Actionable Insights: The Insights Drawer translates static stress scores into contextual nudges (e.g. 'Step onto the balcony') with a 1-tap 'Nudge Me' button to schedule a reminder.")
    pdf.body_text("3. The Tomorrow Planner: Visually separates the user's Rigid Existing Calendar against Veya's Suggestions, displaying them side-by-side or stacked.")
    pdf.body_text("4. Master Control Profile: Total transparency. Users can view and edit everything Veya knows about them, from their baseline stress to their exact biological phase.")
    
    # Images for page 6
    img1_png = r"C:\Users\DELL\.gemini\antigravity\brain\8ce829a2-0cba-49c3-9ee5-e229de673013\.user_uploaded\media_1788471346705.png"
    img2_png = r"C:\Users\DELL\.gemini\antigravity\brain\8ce829a2-0cba-49c3-9ee5-e229de673013\.user_uploaded\media_1788471362086.png"
    
    img1 = get_jpg_path(img1_png)
    img2 = get_jpg_path(img2_png)
    
    y_pos = pdf.get_y() + 5
    try:
        if img1:
            pdf.image(img1, x=20, y=y_pos, w=70)
        if img2:
            pdf.image(img2, x=110, y=y_pos, w=70)
        pdf.set_y(y_pos + 130) # push text down
    except Exception as e:
        print(f"Skipping images due to error: {e}")

    # --- PAGE 7: CONCLUSION & SCREENSHOTS ---
    pdf.add_page()
    pdf.chapter_title('SECTION 06: Application Gallery')
    pdf.body_text("Below are captures demonstrating Veya's conversational interface, the dynamic twin profile drawer, and the household orbit management system.")
    
    img3_png = r"C:\Users\DELL\.gemini\antigravity\brain\8ce829a2-0cba-49c3-9ee5-e229de673013\.user_uploaded\media_1788471362081.png"
    img4_png = r"C:\Users\DELL\.gemini\antigravity\brain\8ce829a2-0cba-49c3-9ee5-e229de673013\.user_uploaded\media_1788471362082.png"
    
    img3 = get_jpg_path(img3_png)
    img4 = get_jpg_path(img4_png)
    
    y_pos = pdf.get_y() + 5
    try:
        if img3:
            pdf.image(img3, x=20, y=y_pos, w=70)
        if img4:
            pdf.image(img4, x=110, y=y_pos, w=70)
    except Exception as e:
        print(f"Skipping images due to error: {e}")
        
    
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

    pdf.add_page()
    pdf.set_y(50)
    pdf.section_title('Conclusion')
    pdf.body_text("VeyaAI represents a paradigm shift from passive analytics to active, empathetic life management. By combining a mathematically rigorous Cognitive Decision Matrix with an approachable, conversational interface, Veya ensures users never have to figure it out alone.")

    output_path = 'veya_data/VeyaAI_FullScope_Submission.pdf'
    pdf.output(output_path)
    print(f"Full PDF successfully generated at: {output_path}")

if __name__ == '__main__':
    create_pdf()
