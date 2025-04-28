from AnsweringBot import AnsweringBot
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile
from io import BytesIO
from PyPDF2 import PdfReader
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


bot = AnsweringBot()

@app.get("/")
async def root():
    return {"message": "Welcome to the AnsweringBot API!"}

@app.post("/scan_resume")
async def scan_resume(file: UploadFile = File(...)):
    global latest_resume_path
    try:

        file_content = await file.read()
        pdf_reader = PdfReader(BytesIO(file_content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()

        # Get the directory of the current file
        save_dir = os.path.join(r"C:\Users\aksha\ALL_PROJECTS\Mass_Apply\backend", "savedResumeAndCV")
        os.makedirs(save_dir, exist_ok=True)

        # Save the file in the savedResumeAndCV folder
        save_path = os.path.join(save_dir, file.filename)
        with open(save_path, "wb") as f:
            f.write(file_content)

        latest_resume_path = save_path

        bot.scan_resume(text)


        bot.scan_resume(text)
        return {"status": "success", "message": "Resume scanned successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/scan_question")
async def scan_question():
    global latest_resume_path
    try:
        print("Received request for /scan_question")
        url = input("Type or paste url:")
        data = {"url": url.strip()}
        url = data["url"]
        print(f"Scanning questions from URL: {url}")

        print("Latest resume path:", latest_resume_path)
        bot.scan_question(url, latest_resume_path)
        print("Finished scanning questions")
        return {"status": "success", "message": f"Questions scanned from {url}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}






