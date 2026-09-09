import os
from fpdf import FPDF
import datetime

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, 'V E Y A A I - Product Concept Document', 0, 0, 'L')
        self.set_font('Arial', '', 10)
        self.cell(0, 10, 'Phase 2 Submission', 0, 1, 'R')
        self.set_draw_color(200, 200, 200)
        self.line(10, 20, 200, 20)
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'R')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 16)
        self.set_text_color(33, 37, 41)
        self.cell(0, 10, title, 0, 1, 'L')
        self.set_draw_color(50, 50, 50)
        self.line(10, self.get_y(), 60, self.get_y())
        self.ln(5)

    def section_title(self, title):
        self.set_font('Arial', 'B', 14)
        self.set_text_color(50, 50, 50)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(2)

    def body_text(self, text):
        self.set_font('Arial', '', 11)
        self.set_text_color(80, 80, 80)
        self.multi_cell(0, 7, text.encode('latin-1', 'replace').decode('latin-1'))
        self.ln(3)
        
    def bullet_point(self, text):
        self.set_font('Arial', '', 11)
        self.set_text_color(80, 80, 80)
        self.cell(5, 7, "-", 0, 0, 'R')
        self.multi_cell(0, 7, text.encode('latin-1', 'replace').decode('latin-1'))

def create_pdf():
    pdf = PDF()
    pdf.add_page()

    # Cover
    pdf.set_font('Arial', 'B', 36)
    pdf.set_text_color(20, 30, 60)
    pdf.ln(40)
    pdf.cell(0, 20, 'VeyaAI', 0, 1, 'L')
    pdf.set_font('Arial', 'I', 16)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, "A Personal AI who understands your life,", 0, 1, 'L')
    pdf.cell(0, 10, "so you don't have to figure it out alone.", 0, 1, 'L')
    
    pdf.ln(50)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(60, 5, 'SUBMITTED FOR', 0, 0)
    pdf.cell(70, 5, 'CATEGORY', 0, 0)
    pdf.cell(60, 5, 'PHASE', 0, 1)
    
    pdf.set_font('Arial', '', 10)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(60, 5, 'Patchamomma 2026', 0, 0)
    pdf.cell(70, 5, 'Personal Life Intelligence', 0, 0)
    pdf.cell(60, 5, 'Phase 2 (Integration & Action)', 0, 1)

    pdf.add_page()

    # Section 1
    pdf.chapter_title('SECTION 01: The Evolution')
    pdf.section_title('The Problem / Gap (Phase 2 Focus)')
    pdf.body_text("In Phase 1, we successfully proved that a Personal Digital Twin could observe a user's life and extract deep contextual meaning. However, we discovered a crucial gap: Insight without action creates anxiety.")
    pdf.body_text("Users do not want another dashboard telling them they are stressed. They want a system that negotiates their calendar, respects their limits, and actively reshuffles their life before burnout hits. Most tools stop at analytics; VeyaAI Phase 2 crosses the threshold into execution.")

    pdf.section_title('The 7-Dimensional Cognitive Decision Matrix')
    pdf.body_text("To act on behalf of a human, VeyaAI uses a sophisticated 7-D mathematical engine to weigh tradeoffs, prioritizing what matters most:")
    pdf.bullet_point("1. Chrono-Energy: Accounting for peak focus hours and transition lag after hard meetings.")
    pdf.bullet_point("2. Relational Capital: Dynamic 'Household Orbit' mapping, weighting the importance (1-100%) of family members to prevent relational deficit.")
    pdf.bullet_point("3. Cognitive Load: Distinguishing high-stakes preparation from routine execution.")
    pdf.bullet_point("4. Biological Reserves: Factor in sleep debt and physiological rhythms.")
    pdf.bullet_point("5. Physical Geography: Transit buffers and spatial displacement.")
    pdf.bullet_point("6. Psychological Resilience: Voice-intervention fallback triggers when high anxiety is detected.")
    pdf.bullet_point("7. Downstream Costs: Measuring the compounding penalty of delaying an event.")

    pdf.add_page()
    
    # Section 2
    pdf.chapter_title('SECTION 02: Data & The Feedback Loop')
    pdf.section_title('Enriched Real-World Data Sources')
    pdf.body_text("Phase 2 deepens Veya's intelligence by connecting to robust, real-world data streams:")
    pdf.bullet_point("Household Orbit Profile (New): Explicit 1-100% importance weighting for key people in the user's life, driving relational prioritization.")
    pdf.bullet_point("Health Connect / Wearables: Integrating real-time sleep debt and physiological stress markers directly into the Cognitive Matrix.")
    pdf.bullet_point("Live Google Calendar API: Moving beyond read-only to bi-directional sync (Take-Action-On-Approval).")
    
    pdf.section_title('The Maturity Engine (Feedback Loop)')
    pdf.body_text("VeyaAI gets smarter through telemetry. When Veya proposes an 'Action Card' (e.g., 'Compress meeting to 15 mins'), and the user applies it, the action executes via API. A micro-survey later asks if the intervention helped. This feedback loop is stored in the 'action_outcomes' database, filtering noise and allowing Veya to eventually auto-execute high-confidence patterns.")

    pdf.add_page()

    # Section 3
    pdf.chapter_title('SECTION 03: Technology & Multi-Agent Architecture')
    pdf.section_title('6-Agent Orchestration Pipeline')
    pdf.body_text("VeyaAI's intelligence is distributed across highly specialized, deterministic agents routed by an Orchestrator:")
    pdf.bullet_point("1. OnboardingEngine: Conversational intercept to gather baseline anchors gently.")
    pdf.bullet_point("2. ContextAgent: Aggregates Live Calendar APIs with the local SQLite Household Orbit profiles.")
    pdf.bullet_point("3. TwinBuilder: Extracts and writes static facts to long-term vector memory.")
    pdf.bullet_point("4. PatternAgent: The math engine powering the 7-D Cognitive Matrix.")
    pdf.bullet_point("5. ActionAgent: The Negotiator. Computes realistic, 1-tap JSON Action Cards.")
    pdf.bullet_point("6. RagAgent / GeminiEngine: The voice. Uses TF-IDF cosine similarity to pull past relevant memories and synthesize an empathetic reply via Vertex AI.")

    pdf.section_title('Frontend Interventions')
    pdf.body_text("The Flutter-inspired web client brings the intelligence to life:")
    pdf.bullet_point("Tomorrow Planner: A split view contrasting the user's rigid existing calendar against Veya's flexible suggestions--actionable blocks optimized for cognitive focus.")
    pdf.bullet_point("Actionable Insights: Translating static stress scores into contextual nudges (e.g. 'Step onto the balcony') with a 1-tap 'Nudge Me' reminder integration.")
    pdf.bullet_point("Voice Fallback: A real-time anxiety detection system that interrupts text chat to offer a live audio-call intervention.")

    output_path = 'veya_data/VeyaAI_Phase2_Submission.pdf'
    pdf.output(output_path)
    print(f"PDF successfully generated at: {output_path}")

if __name__ == '__main__':
    create_pdf()
