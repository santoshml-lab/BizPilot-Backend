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

from fastapi import UploadFile, File, Form
from docx import Document
import pdfplumber
import tempfile
import os

@app.post("/document")
async def analyze_document(

    file: UploadFile = File(...),

    task: str = Form(...)

):

    try:

        text = ""

        suffix = os.path.splitext(file.filename)[1].lower()

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp:

            temp.write(await file.read())

            temp_path = temp.name

        # ==========================
        # READ PDF
        # ==========================

        if suffix == ".pdf":

            with pdfplumber.open(temp_path) as pdf:

                for page in pdf.pages:

                    page_text = page.extract_text()

                    if page_text:

                        text += page_text + "\n"

        # ==========================
        # READ DOCX
        # ==========================

        elif suffix == ".docx":

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

        # ==========================
        # PROMPT
        # ==========================

        prompt = f"""
You are BizPilot AI.

Perform ONLY the following task:

Task:
{task}

Document:

{text}

Instructions:

- If task is Summarize Document → Create a professional summary.
- If task is Explain Document → Explain in simple language.
- If task is Extract Key Points → Give bullet points.
- If task is Translate Document → Translate professionally.
- If task is Create Notes → Create revision notes.
- If task is Generate Questions → Create important interview/exam questions.

Use proper headings and formatting.
"""

        # ==========================
        # AI
        # ==========================

        response = client.chat.completions.create(

            model="openai/gpt-oss-20b",

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0.5,

            max_tokens=2000

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
                                      
    

from pydantic import BaseModel

class InvoiceRequest(BaseModel):
    prompt: str


@app.post("/invoice-ai")
async def invoice_ai(req: InvoiceRequest):

    try:

        prompt = f"""
You are BizPilot AI.

Create a PREMIUM professional business invoice.

User Request:
{req.prompt}

IMPORTANT RULES:

- Return ONLY HTML.
- Do NOT use Markdown.
- Do NOT use ```html.
- Use inline CSS only.
- Background should be white.
- Text color should be dark.
- Blue header (#2563EB).
- Rounded corners.
- Nice shadows.
- Professional spacing.

Invoice must contain:

• Company Name
• INVOICE title
• Invoice Number
• Date
• Bill To
• Service
• Description
• Quantity
• Price
• GST
• Grand Total
• Payment Terms
• Notes
• Thank You Message

Create a beautiful table.

Grand Total should be highlighted.

Finish with:

"Thank you for choosing our services ❤️"

Return ONLY HTML.
"""

        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional invoice designer."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.4,
            max_tokens=2000
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

class PlannerRequest(BaseModel):
    prompt: str

@app.post("/planner")
async def planner(req: PlannerRequest):

    try:

        prompt = f"""
You are BizPilot AI.

Create a professional action plan.

Goal:
{req.prompt}

Return:

- Daily Tasks
- Weekly Goals
- Timeline
- Priority
- Tips
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
            "reply": response.choices[0].message.content
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }

from pydantic import BaseModel

# ===========================
# Analytics Request
# ===========================

class AnalyticsRequest(BaseModel):
    pass


# ===========================
# Analytics Endpoint
# ===========================

@app.post("/analytics")
async def analytics(req: AnalyticsRequest):

    return {

        "success": True,

        "requests": 245,

        "emails": 61,

        "documents": 18,

        "invoices": 29,

        "plans": 41,

        "productivity": 96,

        "tool": "🤖 AI Chat",

        "activity": [

            "AI Chat completed successfully",

            "Professional Email Generated",

            "Document Analyzed",

            "Invoice Created",

            "Smart Planner Generated",

            "Dashboard Accessed"

        ]

    }






