from typing import Dict, Any, List
from veya_agents.cognitive_matrix import cognitive_matrix

class PatternAgent:
    """
    Pattern Detection Agent:
    Evaluates multi-dimensional cognitive fatigue, biological rhythms, and second-order carryover risks.
    """

    def detect_patterns(self, internal_uuid: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        patterns = []
        eval_state = cognitive_matrix.evaluate_cognitive_state(internal_uuid, context)

        # 1. Downstream Second-Order Carryover Pattern
        if eval_state["downstream_carryover_risk"] >= 80:
            patterns.append({
                "pattern_id": "pat_downstream_carryover",
                "title": "Second-Order Downstream Fatigue Risk",
                "confidence_score": f"{eval_state['downstream_carryover_risk']}%",
                "provenance": "Calculated from back-to-back meeting residue and evening household solo caregiving load.",
                "dimension": "TEMPORAL_AND_RELATIONAL"
            })

        # 2. Biological Somatic Recovery Pattern
        if eval_state["biological"]["is_luteal"] and eval_state["biological"]["somatic_fatigue_index"] >= 70:
            patterns.append({
                "pattern_id": "pat_luteal_somatic_fatigue",
                "title": "Biological Energy Depletion (Luteal Phase)",
                "confidence_score": f"{eval_state['biological']['somatic_fatigue_index']}%",
                "provenance": "Luteal progesterone dip combined with high cognitive synthesis creates higher fatigue.",
                "dimension": "BIOLOGICAL_SOMATIC"
            })

        # 3. High Stakes Preparation Runway Deficit
        if eval_state["cognitive"]["prep_runway_deficit"]:
            patterns.append({
                "pattern_id": "pat_prep_runway_deficit",
                "title": "Pre-Pitch Focus Buffer Depletion",
                "confidence_score": "86%",
                "provenance": "High-stakes presentation detected without sufficient 45-min deep focus preparation runway.",
                "dimension": "COGNITIVE_LOAD"
            })

        return patterns
