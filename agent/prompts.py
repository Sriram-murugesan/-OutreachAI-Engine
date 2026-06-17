PERSONA_PROMPT = """
You are a sales research analyst. Based on the research below about a potential lead, 
build a concise persona profile.

Lead name: {name}
Company: {company}
Research data: {research}

Write a 3-4 sentence persona covering:
- Their role and responsibilities
- Their likely pain points
- A recent signal or event you can reference
- Their likely goal right now

Be specific. No generic filler. Output only the persona, no headings.
"""

EMAIL_PROMPT = """
You are an expert cold email writer. Write a short, personalized cold email.

Product being sold: AI-powered workflow automation tools for sales teams
Sender name: Alex

Lead persona:
{persona}

Rules:
- Max 5 sentences total
- First sentence must reference something specific from their persona
- No "I hope this email finds you well" openers
- End with a soft CTA (15 min call, not "buy now")
- Sound human, not salesy
- Subject line on the first line prefixed with "Subject:"

Output only the email. No extra commentary.
"""

QUALITY_PROMPT = """
You are a cold email quality checker.

Email to evaluate:
{email_body}

Score this email from 1 to 10 based on:
- Personalization (does it reference something specific?)
- Brevity (is it under 5 sentences?)
- Soft CTA (does it end with a low-pressure ask?)
- Human tone (does it sound like a real person?)

Respond in this exact format and nothing else:
SCORE: <number>
REASON: <one sentence>
"""