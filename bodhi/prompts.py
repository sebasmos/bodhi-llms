"""
BODHI Prompts - v0.1.3

Two-pass prompting strategy for epistemic virtues (curiosity and humility).

Features:
- Specificity enforcement (dosages, frequencies, timeframes)
- Active inquiry pattern ("Are you experiencing X?" vs "If you experience X")
- Explicit alternatives (mention multiple options when they exist)
- Audience detection (PATIENT vs HEALTH_PROFESSIONAL)
- Task type routing (CONVERSATION, TECHNICAL, HYBRID, EMERGENCY)

Changes from v0.1.2:
- Added BE SPECIFIC guidelines (include numbers, dosages, emergency contacts)
- Added ACTIVELY ASK pattern (change conditionals to direct questions)
- Added INCLUDE ALTERNATIVES (mention all options, not just one)s

Reference: PLOS Digital Health (doi: 10.1371/journal.pdig.0001013)
"""

from typing import Dict, Optional


def render_analysis_prompt(case_text: str, domain: str = "medical") -> str:
    """
    Render the Pass 1 analysis prompt.

    Args:
        case_text: The user's input/case to analyze
        domain: The domain context ("medical", "general", etc.)

    Returns:
        The formatted analysis prompt
    """
    if domain == "medical":
        return f"""You are a thoughtful medical AI. Analyze this input carefully.

Input:
{case_text}

Provide your analysis:

1. TASK TYPE: Is this a CONVERSATION (health advice), TECHNICAL (documentation task), HYBRID (technical format + clinical reasoning), or EMERGENCY?

2. AUDIENCE: Who is asking? (PATIENT/CAREGIVER = use simple warm language, HEALTH_PROFESSIONAL = use clinical terminology, UNCLEAR = default to accessible)

3. WHAT I THINK: Your best assessment (be honest about confidence)

4. KEY UNCERTAINTIES: What information is missing that would change your advice?

5. QUESTIONS TO ASK: 1-2 specific clarifying questions (if needed)

6. RED FLAGS: Any urgent warning signs (or "None")

7. SAFE RECOMMENDATIONS: What can you confidently advise regardless of unknowns?

Be genuinely curious and humble - acknowledge what you don't know."""

    else:  # general domain
        return f"""You are a thoughtful AI assistant. Analyze this request with intellectual humility.

Request:
{case_text}

Think carefully and provide:

1. WHAT I THINK: Your best understanding of what's needed
2. WHAT I'M UNSURE ABOUT: Key uncertainties or ambiguities
3. WHAT I NEED TO KNOW: Questions that would help me assist better
4. IMPORTANT CONSIDERATIONS: Any critical factors to keep in mind
5. CONFIDENT ADVICE: What I can reliably help with regardless of uncertainty

Be genuinely curious and humble - don't pretend to know more than you do."""


def render_response_prompt(case_text: str, analysis: str, domain: str = "medical") -> str:
    """
    Render the Pass 2 response prompt.

    v0.1.3: Integrated completeness, simplified structure.

    Args:
        case_text: The original user input
        analysis: The Pass 1 analysis output
        domain: The domain context

    Returns:
        The formatted response prompt
    """
    # Detect task type from analysis
    task_type = _detect_task_type(analysis)

    if domain == "medical":
        if task_type == "TECHNICAL":
            # Strict TECHNICAL mode - format only, no questions
            return f"""Based on your analysis, this is a TECHNICAL/DOCUMENTATION task.

Your analysis:
{analysis}

Original request:
{case_text}

INSTRUCTIONS (Follow exactly):
- Provide ONLY the specific output format requested (SOAP note, ICD codes, summary, etc.)
- Match the user's formatting instructions precisely
- Use professional medical documentation style
- Do NOT add conversational advice
- Do NOT add clarifying questions
- Do NOT add disclaimers or caveats unless part of standard documentation

If the request asks for a specific format, provide ONLY that format.

Provide the requested output:"""

        elif task_type == "EMERGENCY":
            return f"""Based on your analysis, this may be an EMERGENCY situation.

Your analysis:
{analysis}

Original request:
{case_text}

PROVIDE EMERGENCY GUIDANCE:
1. First, state what to check (responsiveness, breathing, pulse) in order
2. Give clear, step-by-step instructions
3. Say when to call emergency services
4. Keep it brief and actionable

Respond now:"""

        elif task_type == "HYBRID":
            # HYBRID: Technical format + clinical reasoning
            return f"""This task requires BOTH technical format AND clinical reasoning.

Your analysis:
{analysis}

Original request:
{case_text}

HYBRID RESPONSE GUIDELINES:

1. PRIMARY OUTPUT:
   - Provide the requested format (SOAP note, ICD codes, etc.) as the main output
   - Follow formatting instructions precisely

2. EMBEDDED CLINICAL REASONING:
   - WITHIN that format, include appropriate uncertainty markers
   - For SOAP notes: In Assessment, note differentials and uncertainties
   - For ICD codes: Provide codes, then note "If [condition], also consider [code]"

3. BE COMPLETE:
   - Address all aspects of the request
   - Don't just defer - provide information for each scenario
   - Include relevant differentials

4. OPTIONAL FOLLOW-UP:
   If helpful, add a brief note about what additional context would refine the plan.

Provide the formatted response with embedded clinical reasoning:"""

        else:  # CONVERSATION (default)
            # Detect audience from analysis
            audience = _detect_audience(analysis)

            if audience == "PATIENT":
                # PATIENT PATH: v0.1.3 - specificity + active inquiry
                return f"""Write a warm, helpful response for this patient/caregiver.

Your analysis:
{analysis}

Original request:
{case_text}

RESPONSE GUIDELINES:
- First, directly answer their main question
- Address ALL parts of what they asked

BE SPECIFIC:
- Include specific numbers: dosages, frequencies, timeframes
- Example: "Take ibuprofen 200-400mg every 4-6 hours, max 1200mg per day"
- Mention emergency numbers: "Call 911 (in the US)" when relevant

ACTIVELY ASK about concerning symptoms:
- Don't say "if you experience X" - instead ASK "Are you experiencing X right now?"
- Example: "Are you having any chest pain, shortness of breath, or fever?"

INCLUDE ALTERNATIVES when they exist:
- Don't just give one option - mention alternatives
- Example: "See a doctor within 24-48 hours, or sooner if symptoms worsen"

Include warning signs and when to see a doctor.
Use warm, simple language. Be reassuring but honest.

Write your response:"""

            elif audience == "HEALTH_PROFESSIONAL":
                # PROFESSIONAL PATH: v0.1.3 - specificity + active inquiry
                return f"""Write a helpful response for this health professional.

Your analysis:
{analysis}

Original request:
{case_text}

RESPONSE GUIDELINES:
- Directly address their clinical question first
- Address ALL aspects of what they asked

BE SPECIFIC:
- Include specific dosing, frequencies, lab values when relevant
- Provide concrete differential diagnoses with distinguishing features
- Suggest specific workup: "Consider CBC, CMP, imaging with CT/MRI"

INCLUDE ALTERNATIVES:
- "If X is confirmed, consider Y; if Z instead, consider W"
- Mention multiple management options where appropriate

If key info is missing, ask directly: "Is the patient currently experiencing [symptom]?"

Write your response:"""

            else:  # UNCLEAR audience
                # GENERAL PATH: v0.1.3 - specificity + active inquiry
                return f"""Write a helpful response to the user.

Your analysis:
{analysis}

Original request:
{case_text}

RESPONSE GUIDELINES:
- Lead with a clear, direct answer to their main question
- Address ALL parts of what they asked

BE SPECIFIC:
- Include specific numbers, dosages, timeframes when relevant
- Mention emergency contacts: "Call 911 (US) or your local emergency number"

ACTIVELY ASK about concerning symptoms:
- Don't say "if you experience" - ASK directly: "Are you having [symptom] right now?"

INCLUDE ALTERNATIVES:
- When multiple options exist, mention all of them

Include what to monitor and when to seek care.
Use accessible language - explain any medical terms.

Write your response:"""

    else:  # general domain
        return f"""Now respond to the user helpfully.

Your analysis:
{analysis}

Request:
{case_text}

Write a helpful, natural response:"""


def _detect_task_type(analysis: str) -> str:
    """
    Detect the task type from the analysis.

    Returns: "TECHNICAL", "HYBRID", "EMERGENCY", or "CONVERSATION"

    Note: Be CONSERVATIVE - default to CONVERSATION unless clearly technical/emergency.
    HYBRID is for technical format requests that also need clinical reasoning.
    """
    analysis_lower = analysis.lower()

    # Check for explicit task type declaration from Pass 1
    if "task type:" in analysis_lower:
        after_type = analysis_lower.split("task type:")[1][:80]
        if "hybrid" in after_type:
            return "HYBRID"
        elif "technical" in after_type:
            return "TECHNICAL"
        elif "emergency" in after_type:
            return "EMERGENCY"

    # Emergency detection - only for truly urgent situations
    emergency_phrases = [
        "someone collapse", "collapsed", "unconscious", "not breathing",
        "stopped breathing", "choking", "severe bleeding", "call 911"
    ]
    for phrase in emergency_phrases:
        if phrase in analysis_lower:
            return "EMERGENCY"

    # Technical/Hybrid detection - for documentation requests
    doc_types = ["soap note", "icd code", "cpt code", "mychart note", "discharge summary"]
    action_words = ["write a", "create a", "provide the", "edit this", "rewrite", "correct this"]

    has_doc_type = any(doc in analysis_lower for doc in doc_types)
    has_action = any(action in analysis_lower for action in action_words)

    if has_doc_type and has_action:
        # Check if this also needs clinical reasoning (HYBRID) or is pure format (TECHNICAL)
        clinical_reasoning_signals = [
            "differential", "uncertainty", "rule out", "consider",
            "unclear", "depends on", "need more information", "clinical reasoning"
        ]
        has_clinical_reasoning = any(signal in analysis_lower for signal in clinical_reasoning_signals)

        if has_clinical_reasoning:
            return "HYBRID"
        else:
            return "TECHNICAL"

    # Default to CONVERSATION - this preserves context-seeking behavior
    return "CONVERSATION"


def _detect_audience(analysis: str) -> str:
    """
    Detect the audience type from the analysis.

    Returns: "PATIENT", "HEALTH_PROFESSIONAL", or "UNCLEAR"
    """
    analysis_lower = analysis.lower()

    # Check for explicit audience declaration from Pass 1
    if "audience:" in analysis_lower:
        after_audience = analysis_lower.split("audience:")[1][:60]
        if "health_professional" in after_audience or "professional" in after_audience:
            return "HEALTH_PROFESSIONAL"
        elif "patient" in after_audience or "caregiver" in after_audience:
            return "PATIENT"

    # Heuristic detection
    professional_signals = [
        "as a nurse", "as a physician", "as a doctor", "medical student",
        "clinical question", "differential diagnosis", "treatment protocol",
        "icd code", "cpt code", "soap note", "chart note"
    ]

    patient_signals = [
        "my symptom", "i have", "my child", "my husband", "my wife",
        "should i", "is it normal", "worried about", "scared", "anxious"
    ]

    has_professional = any(signal in analysis_lower for signal in professional_signals)
    has_patient = any(signal in analysis_lower for signal in patient_signals)

    if has_professional and not has_patient:
        return "HEALTH_PROFESSIONAL"
    elif has_patient and not has_professional:
        return "PATIENT"

    return "UNCLEAR"


# Legacy functions kept for backwards compatibility

def _extract_missing_context(analysis: str) -> str:
    """
    Extract critical missing information identified in Pass 1.
    NOTE: Kept for backwards compatibility.
    """
    lines = analysis.split('\n')
    missing = []

    in_questions_section = False
    for line in lines:
        lower = line.lower().strip()

        if 'questions to ask' in lower or 'need to know' in lower or 'key uncertainties' in lower:
            in_questions_section = True
            continue

        if in_questions_section and lower and lower[0].isdigit() and '.' in lower[:3]:
            in_questions_section = False

        if in_questions_section and line.strip() and len(line.strip()) > 15:
            clean_line = line.strip().lstrip('-').lstrip('•').strip()
            if clean_line and not clean_line.lower().startswith('none'):
                missing.append(clean_line)

    if missing:
        items = "\n".join(f"- {m}" for m in missing[:3])
        return f"""KEY INFORMATION GAPS FROM YOUR ANALYSIS:
{items}

IMPORTANT: Address these gaps explicitly."""
    return ""


def _get_audience_style(audience: str) -> str:
    """
    Get styling instructions based on detected audience.
    NOTE: Kept for backwards compatibility.
    """
    if audience == "HEALTH_PROFESSIONAL":
        return """COMMUNICATION STYLE (Health Professional):
- Use clinical terminology appropriately
- Be concise and efficient
- Focus on clinical decision-making points"""

    elif audience == "PATIENT":
        return """COMMUNICATION STYLE (Patient/Caregiver):
- Use warm, simple language
- Be reassuring while remaining honest
- Explain the "why" behind recommendations"""

    else:
        return """COMMUNICATION STYLE (General):
- Use accessible language
- Explain medical terms when introduced
- Balance warmth with professionalism"""


def _extract_response_hints(analysis: str) -> list:
    """
    Extract response hints from the analysis.
    NOTE: Kept for backwards compatibility.
    """
    hints = []
    analysis_lower = analysis.lower()

    if 'safe' in analysis_lower and 'recommend' in analysis_lower:
        hints.append("Start with safe, helpful recommendations")

    if 'red flag' in analysis_lower and 'none' not in analysis_lower:
        hints.append("Include guidance on when to seek immediate care")

    return hints
