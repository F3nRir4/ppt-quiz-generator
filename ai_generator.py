import os
import json

from dotenv import load_dotenv
from google import genai


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)


def generate_mcqs(ppt_text, number_of_questions=5, difficulty="Mixed"):

    prompt = f"""
You are an educational multiple-choice question generator.

Use ONLY the PowerPoint content provided below.

Generate exactly {number_of_questions} MCQ questions.

Difficulty level: {difficulty}

Rules:
1. Each question must have exactly 4 options.
2. Only one option must be correct.
3. Questions must be based only on the PowerPoint content.
4. Do not use outside knowledge.
5. Avoid duplicate questions.
6. Give a short explanation for the correct answer.
7. Return only valid JSON.
8. Do not include markdown.
9. Do not include ```json.
10. Do not include any text before or after the JSON.

Return the JSON in this exact format:

{{
    "questions": [
        {{
            "question": "Question text",
            "options": [
                "Option A",
                "Option B",
                "Option C",
                "Option D"
            ],
            "correct_answer": 0,
            "difficulty": "Easy",
            "explanation": "Short explanation"
        }}
    ]
}}

IMPORTANT:
correct_answer must be a number:
0 = first option
1 = second option
2 = third option
3 = fourth option

PowerPoint content:

{ppt_text}
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    response_text = response.text.strip()

    try:
        data = json.loads(response_text)
        return data

    except json.JSONDecodeError:
        return {
            "error": "Gemini did not return valid JSON.",
            "raw_response": response_text
        }