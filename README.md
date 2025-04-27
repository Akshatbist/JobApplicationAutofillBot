📄 README.md Job Application Autofill Bot 🚀 An AI-powered automation tool that intelligently fills out job applications, generates custom cover letters, and streamlines your job hunting process.

📚 Features ✍️ Resume Parsing: Automatically extracts important details from your resume.

🧠 AI-Powered Answers: Uses OpenAI to answer application questions smartly.

📝 Auto-Generated Cover Letters: Creates customized cover letters on the fly.

🌐 Web Automation: Autofills job applications using Selenium.

🛡️ Error Handling: Detects and handles missing or invalid information gracefully.

⚙️ Tech Stack Python 🐍

Selenium (Web browser automation)

OpenAI API (LLM integration)

FastAPI (optional backend server)

python-dotenv (environment variable management)

PyPDF2 (reading resumes from PDF files)

scikit-learn (TF-IDF keyword extraction)

🚀 Setup Instructions Clone this repository:

bash git clone https://github.com/yourusername/job-application-autofill-bot.git cd job-application-autofill-bot Install dependencies:

nginx pip install -r requirements.txt

Create a .env file:

Inside the root folder, create a file named .env and add:

OPENAI_API_KEY=your-openai-key-here

Run the bot: python main.py

🗂️ Project Structure bash

job-application-autofill-bot/ ├── AnswerDatabase.py ├── AnsweringBot.py ├── main.py ├── .env ├── requirements.txt ├── savedResumeAndCV/ ├── README.md └── other project files... 💡 Future Improvements Add support for more job platforms (LinkedIn, Indeed, Workday, etc.)

Chrome Extension for direct form filling

Improved AI resume matching system

OCR support for scanned documents

🤝 Contributing Contributions are welcome! Feel free to submit a pull request or open an issue.

📄 License This project is licensed under the MIT License.
