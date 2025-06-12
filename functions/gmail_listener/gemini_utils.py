import base64
from typing import List, Optional
from pydantic import BaseModel
from google import genai
from google.genai.types import Part, GenerateContentConfig
import os

# --- Gemini Config ---
MODEL_ID = "gemini-2.0-flash"
PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = "us-central1"

client = genai.Client(
    vertexai=True,
    project=PROJECT_ID,
    location=LOCATION
)

# --- Pydantic Models for Structured Output ---

class EmailSummary(BaseModel):
    subject: str
    sender: str
    summary: str
    tag: str
    action_required: str
    next_action: Optional[str]
    suggested_reply: Optional[str]


class AttachmentAnalysis(BaseModel):
    type: str
    summary: str
    total: Optional[str] = ""
    date: Optional[str] = ""
    

def summarize_email_structured(msg) -> EmailSummary:
    try:
        message_json = Part.from_text(text=str(msg))

        response = client.models.generate_content(
            model=MODEL_ID,
            contents=[
                message_json,
                "Summarize this email and respond with: summary (one line), one main gmail tag, action (if required yes/no and what), suggested reply (one line)"
            ],
            config=GenerateContentConfig(
                response_schema=EmailSummary,
                response_mime_type="application/json"
            )
        )

        return response.parsed.model_dump() # Pydantic object

    except Exception as e:
        print(f"❌ Error in summarize_email_structured: {e}")
        return EmailSummary(
            summary="(Error generating summary)",
            tags=[],
            action_required="unknown"
        ).model_dump()


def analyze_attachment(data: bytes, filename: str, mime_type: str) -> AttachmentAnalysis:
    try:
        prompt = (
            f"Analyze the attached file '{filename}' and make a summarized description of line (or 2 only if needed)," \
            " make a macro classification of the type of document. Include total amount ($) and date if available."
        )

        response = client.models.generate_content(
            model=MODEL_ID,
            contents=[
                Part.from_bytes(data=data, mime_type=mime_type),
                prompt
            ],
            config=GenerateContentConfig(
                response_schema=AttachmentAnalysis,
                response_mime_type="application/json"
            )
        )

        return response.parsed.model_dump()

    except Exception as e:
        print(f"❌ Error analyzing attachment: {e}")
        return AttachmentAnalysis(
            type="unknown",
            summary="Unable to analyze"
        ).model_dump()
