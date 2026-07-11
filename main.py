from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from groq import Groq
from dotenv import load_dotenv
from fastapi import UploadFile, File
import pdfplumber
from docx import Document
import tempfile
import os

load_dotenv()

app = FastAPI(title="BizPilot AI Backend")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Groq Client
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# Request Model
class ChatRequest(BaseModel):
    message: str

@app.get("/")
def home():
    return {
        "status": "online",
        "app": "BizPilot AI Backend"
    }

# ===========================
# CHAT ENDPOINT
# ===========================

@app.post("/chat")
async def chat(request: ChatRequest):

    try:

        response = client.chat.completions.create(

            model="openai/gpt-oss-20b",

            messages=[

                {
                    "role": "system",
                    "content": """
You are BizPilot AI.

You are a professional AI Business Assistant.

Help users with:
- Business Ideas
- Startups
- Marketing
- Sales
- Emails
- Business Plans
- Finance
- Productivity
- Customer Support
- HR
- Content Writing

Always answer professionally.

"""
                },

                {
                    "role": "user",
                    "content": request.message
                }

            ],

            temperature=0.7,

            max_tokens=1500

        )

        return {

            "success": True,

            "reply": response.choices[0].message.content

        }

    except Exception as e:

        return {

            "success": False,

            "error": str(e)

        }

@app.post("/email")
async def generate_email(data: dict):

    prompt = f"""
Write a professional email.

Subject: {data['subject']}
Type: {data['type']}
Tone: {data['tone']}

Details:
{data['details']}
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role":"user","content":prompt}
        ]
    )

    return {
        "success": True,
        "email": response.choices[0].message.content
    }

@app.post("/document")
async def analyze_document(file: UploadFile = File(...)):

    try:

        text = ""

        # Save uploaded file temporarily
        suffix = os.path.splitext(file.filename)[1]

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp:
            temp.write(await file.read())
            temp_path = temp.name

        # Read PDF
        if suffix.lower() == ".pdf":

            with pdfplumber.open(temp_path) as pdf:

                for page in pdf.pages:

                    page_text = page.extract_text()

                    if page_text:
                        text += page_text + "\n"

        # Read DOCX
        elif suffix.lower() == ".docx":

            doc = Document(temp_path)

            for para in doc.paragraphs:

                text += para.text + "\n"

        else:

            os.remove(temp_path)

            return {
                "success": False,
                "error": "Only PDF and DOCX files are supported."
            }

        os.remove(temp_path)

        prompt = f"""
Analyze the following document.

Generate:

1. Executive Summary

2. Key Points

3. Important Dates

4. Important Numbers

5. Action Items

6. Final Conclusion

Document:

{text}
"""

        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return {
            "success": True,
            "analysis": response.choices[0].message.content
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }


