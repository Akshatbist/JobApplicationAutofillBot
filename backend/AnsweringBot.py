from PyPDF2 import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from AnswerDatabase import AnswerDatabase
from openai import OpenAI
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
import re
import time
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from fpdf import FPDF
from datetime import datetime
import os
import unicodedata
from selenium.common.exceptions import InvalidSessionIdException
from dotenv import load_dotenv
import os

load_dotenv()
#once inside apply now(will be done manually for now), work on a better autofiller than simplify that generates a cover letter as well

#make it a chrome extension
#get answers from resume, then makes the user fill in questions that it doesn't know the answer to so it can automatically fill it later
#rag application

#Using Greenhouse Layout to build this, might not work with other platforms

class AnsweringBot():
    def __init__(self):
         self.today = datetime.today().strftime("%B %d, %Y")
         self.resume_text = ""
         self.db = AnswerDatabase()
         self.options = Options()
         self.driver = None
         #Store this as an env variable later
         self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def initialize_driver(self):
        print("Initializing WebDriver...")
        options = self.options
        options.add_experimental_option("detach", True)
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        
    def scan_resume(self, text):

        self.db.store_qa(
                    question = "Full_resume",
                    context = text
            )
        print("Resume stored in vector database")

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                {
                    "role": "system",
                    "content": "Extract structured personal information from the resume text. Only provide the fields listed."
                },
                {
                    "role": "user",
                    "content": f"From the following resume:\n\n{text}\n\nExtract:\n- first_name\n- last_name\n- email\n- phone\n- linkedin\n- github (if available)\n- location\n- degree\n- portfolio (if available)\n- Work_experience\n- All_work_experience_details\n- skills\n- certifications\n- languages\n- interests\n- projects\n- All_projects_details\n- summary\n- education\n- location\n- awards\n- publications\n- volunteer_experience\n- hobbies\n- references\n"
                }
             ]
            )
            structured_output = response.choices[0].message.content.strip()
            
            print(f"Structured Output:{structured_output}")

            data = {}
            for line in structured_output.splitlines():
                key_val = line.split(":", 1)
                if len(key_val) == 2:
                    key, val = key_val
                    data[key.strip()] = val.strip()

            for key, value in data.items():
                self.db.store_qa(question=key, context=value)

            print("✅ Structured resume fields stored in vector DB.")

        except Exception as e:
            print("❌ Error during structured resume processing:", e)
            
        finally:
            print("Processing complete")
           

        try:
            all_entries = self.db.collection.get()
            for doc, meta in zip(all_entries['documents'], all_entries['metadatas']):
                print(f"📝 Document: {doc}")
                print(f"📌 Metadata: {meta}")
                print("------")
        except Exception as e:
            print("❌ Error printing DB entries:", e)
                  
    
    def scan_question(self, website_url, save_path):
        try:
            #ask all the variables here and pass them in llm
            
            #how do i make sure the users are only answering whats expected
            #Use some sort of nlp or ai to make sure users are answering with expected answers
            howDidYouHear = input("How did you hear about this job? (e.g., LinkedIn, Referral, etc.): ").strip()

            eligibleToWork = input("Are you eligible to work in the US? (Yes/No): ").strip()
            eligibleToWork = f"Are you eligible to work in the US? {eligibleToWork}"

            sponsorship = input("Do you need sponsorship? (Yes/No): ").strip()
            sponsorship  = f"Do you need sponsorship? {sponsorship}"

            gender = input("Male/Female/Non-Binary/Other/Prefer to self describe/Rather not say: ").strip()

            sexuality = input("What is your sexuality? (e.g., Heterosexual, Homosexual, Bisexual, Asexual, Pansexual, etc.): ").strip()

            identity = input("Cisgender/Transgender/Other/Rather Not Say: ").strip()

            ethnicity = input("What is your ethnicity? (e.g., Asian, Black or African American, Hispanic or Latino, White, etc.): ").strip()

            disability_status = input("Do you have a disability? (Yes/No/Prefer not to say): ").strip()
            disability_status = f"Do you have a disability? {disability_status}"

            veteran_status = input("Are you a veteran? (Yes/No/Prefer not to say): ").strip()
            veteran_status = f"Are you a veteran? {veteran_status}"



            self.initialize_driver()
            print("WebDriver initialized")

            print(f"Starting scan_question for URL: {website_url}")
            try:
                self.driver.get(website_url)
            except InvalidSessionIdException:
                print("Session expired or not initialized. Restarting WebDriver...")
                self.initialize_driver() 
                self.driver.get(website_url)
            print("Website loaded successfully")

            WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//input | //textarea | //select"))
            )
            print("Found input elements")

            self.handle_text_inputs(howDidYouHear)
            print("Handled text inputs")

            self.handle_file_uploads(save_path)
            print("Handled file uploads")

            self.handle_dropdowns(eligibleToWork,sponsorship, gender, sexuality, identity, ethnicity, disability_status, veteran_status)
            print("Handled dropdowns")

            self.handle_checkboxes()
            print("Handled checkboxes")

            print("Finished scan_question")
        except Exception as e:
            print(f"Error in scan_question: {e}")
        finally:
            input("🛑 Press Enter to exit and close browser manually...")




    def handle_text_inputs(self, howDidYouHear):
        input_elements = self.driver.find_elements(By.XPATH, "//input[@type='text'] | //textarea")

        for input_elem in input_elements:
            question = self.driver.execute_script("""
                let input = arguments[0];
                let label = document.querySelector(`label[for='${input.id}']`) || input.closest('div')?.querySelector('label');
                return label ? label.innerText.trim() : "";
            """, input_elem)

            if not question:
                continue

            print(f"📄 Text Question: {question}")
            similar_qs, metadatas = self.db.query_similar(question)

            if not metadatas:
                self.db.store_qa(question, "PENDING_USER_INPUT")
                continue

            answer = metadatas[0][0]['answer'].strip()
            if not answer or answer.upper() == "PENDING_USER_INPUT":
                self.db.store_qa(question, "PENDING_USER_INPUT")
                continue

            try:
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are an AI assistant helping a user complete a job application using answers from their resume and profile.\n\n"
                                "Use the provided database answer if it directly answers the question.\n"
                                "Otherwise, respond with only 'SKIP' (no punctuation or explanation).\n"
                                f"If the question is about 'how did you hear about the job?', respond with: {howDidYouHear}.\n"
                                "If it's a phone number, include the country code (+1 for U.S.).\n"
                                "Do not fabricate or assume information that is not in the database."
                            )
                        },
                        {
                            "role": "user",
                            "content": f"Database answer:\n{answer}\n\nApplication question:\n{question}\n\nAnswer:"
                        }
                    ]
                )

                final_answer = response.choices[0].message.content.strip()
                if "skip" in final_answer.lower():
                    print(f"🤖 LLM skipped: {question}")
                    self.db.store_qa(question, "PENDING_USER_INPUT")
                    continue

                if input_elem.is_displayed() and input_elem.is_enabled():
                    input_elem.clear()
                    input_elem.send_keys(final_answer)
                    print(f"✍️ Filled: {final_answer}")

            except Exception as e:
                print(f"❌ Error answering '{question}': {e}")



    def handle_dropdowns(self,eligible,needSponsorship, gender, sexuality, identity, ethnicity, disability_status, veteran_status):
        try:
            input_fields = self.driver.find_elements(By.CLASS_NAME, "select__input")

            for input_field in input_fields:
                try:
                    question = self.driver.execute_script("""
                        let input = arguments[0];
                        let label = document.querySelector(`label[for='${input.id}']`) || input.closest('div')?.querySelector('label');
                        return label ? label.innerText.trim() : "";
                    """, input_field)

                    if not question:
                        continue

                    print(f"\U0001F55D️ Dropdown Question: {question}")

                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", input_field)
                    self.driver.execute_script("arguments[0].click();", input_field)

                    input_field.send_keys(Keys.ARROW_DOWN)
                    print("✅ Sent ARROW_DOWN to trigger dropdown")

                    WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "select__menu"))
                    )
                    print("✅ Menu rendered")

                    options = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_all_elements_located((By.CLASS_NAME, "select__option"))
                    )
                    option_texts = [opt.text.strip() for opt in options]
                    print(f"🧾 Options: {option_texts}")

                    response = self.client.chat.completions.create(
                        model="gpt-4",
                        messages=[
                            {"role": "system", "content": (
                                "You are selecting answers to demographic and employment questions on a job application form.\n\n"
                                "User details:\n"
                                f"- Eligible to work in the US: {eligible}\n"
                                f"- Needs sponsorship: {needSponsorship}\n"
                                f"- Gender: {gender}\n"
                                f"- Sexuality: {sexuality}\n"
                                f"- Gender Identity: {identity}\n"
                                f"- Ethnicity: {ethnicity}\n"
                                f"- Disability Status: {disability_status}\n"
                                f"- Veteran Status: {veteran_status}\n\n"
                                "From the given options below, select the one that most exactly matches the user's information.\n"
                                "If no good match is available, respond only with 'SKIP'."

                            )},
                            {"role": "user", "content": f"Question: {question}\nOptions:\n- " + "\n- ".join(option_texts)}
                        ]
                    )

                    answer = response.choices[0].message.content.strip()
                    print(f"🤖 LLM Answer: {answer}")

                    if answer.lower() == "skip":
                        self.db.store_qa(question, "PENDING_USER_INPUT")
                        continue
                    else:
                        self.db.store_qa(question, answer)

                    best_idx = self.get_best_matching_option_index(answer, option_texts)

                    if best_idx is not None:
                        fresh_options = self.driver.find_elements(By.CLASS_NAME, "select__option")
                        best_option = fresh_options[best_idx]

                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", best_option)
                        self.driver.execute_script("arguments[0].click();", best_option)
                        print(f"✅ NLP Match Selected: {best_option.text}")

                       

                        time.sleep(0.3)
                    else:
                        print(f"❌ No NLP match found for '{question}' ➡️ '{answer}'")
                        self.db.store_qa(question, "PENDING_USER_INPUT")
                #this exception is always getting triggered but the try back is working
                except Exception as e:
                    pass
      

        except Exception as e:
            print(f"❌ Dropdown handler error: {e}")

    def get_best_matching_option_index(self, answer, option_texts):
        try:
            inputs = [answer] + option_texts
            response = self.client.embeddings.create(
                model="text-embedding-ada-002",
                input=inputs
            )

            vectors = [np.array(e.embedding) for e in response.data]
            answer_vector = vectors[0]
            option_vectors = vectors[1:]

            similarities = cosine_similarity([answer_vector], option_vectors)[0]
            best_idx = int(np.argmax(similarities))
            best_score = similarities[best_idx]

            print(f"🧠 Best match: {option_texts[best_idx]} (score: {best_score:.4f})")

            if best_score < 0.65:
                print("⚠️ Similarity score too low, skipping selection.")
                return None

            return best_idx

        except Exception as e:
            print(f"❌ Similarity match error: {e}")
            return None
   
    def handle_checkboxes(self):
        try:

            checkbox = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "gdpr_demographic_data_consent_given_1"))
            )

            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkbox)
            time.sleep(0.3)

            self.driver.execute_script("arguments[0].click();", checkbox)
            print("✅ Checkbox clicked")

        except Exception as e:
            print(f"❌ Error clicking checkbox: {e}")

    

    def cover_letter_generator(self):
        
        uls = self.driver.find_elements(By.TAG_NAME, "ul")
        ps = self.driver.find_elements(By.TAG_NAME, "p")
        job_description = "\n".join([e.text.strip() for e in (uls + ps) if e.text.strip()])
        print(f"🧾 Job Descriptions: {job_description}")

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert cover letter writer. "
                        "Your job is to generate concise, tailored, and professional cover letters "
                        "that highlight the candidate's qualifications for the specific job."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"Generate a personalized cover letter using the following:\n\n"
                        f"🔹 Job Description:\n{job_description}\n\n"
                        f"🔹 Resume Text:\n{self.resume_text}\n\n"
                        "📄 The cover letter should use the format below:\n\n"
                        "Akshat Bist\n"
                        "+1 510-513-1854 | abist@cpp.edu\n"
                        "linkedin.com/in/akshat-bist | github.com/Akshatbist\n"
                        f"{self.today}\n\n"
                        "[Start of Cover Letter: 3–5 paragraphs]\n"
                        "- Tailor the letter to the job\n"
                        "- Highlight relevant skills/projects\n"
                        "- Maintain a professional and enthusiastic tone\n"
                        "- Keep it under 400 words\n\n"
                        "Close the letter with a thank you and a signature-style ending (e.g., Sincerely, Akshat)"
                    )
                }
            ]
        )

        final_answer = response.choices[0].message.content.strip()
        normal_final_answer = unicodedata.normalize('NFKD', final_answer).encode('ascii', 'ignore').decode('ascii')
        print(f"🤖 LLM Cover Letter:\n {normal_final_answer}")
        #TODO: Convert the text from the final answer into a pdf and save it to local machine
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_margins(left=10, top=10, right=10)
        pdf.add_page()
        pdf.set_font("Times", size=12)

        for line in normal_final_answer.splitlines():
            pdf.multi_cell(0, 6, line)

        full_path = os.path.join("C:/Users/aksha/ALL_PROJECTS/Mass_Apply/backend", "CV.pdf")
        pdf.output(full_path)
        print(f"✅ PDF saved to: {full_path}")
        #TODO: Additional improvements to the cover letter like mentioning the company name, and their location

        #When building this for users, will need to store pdf in database 

#TODO: Make sure that the bot is submiting the resume that you are uploading into chrome extension
    def handle_file_uploads(self, save_path):
        try:
           
            upload_resume = self.driver.find_element(By.ID, "resume")
            upload_cover_letter = self.driver.find_element(By.ID, "cover_letter")

           
            if upload_resume:
                print("📄 Uploading resume...")
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", upload_resume)
                upload_resume.send_keys(save_path)
                print("✅ Resume uploaded via visually-hidden input")

            if upload_cover_letter:
                self.cover_letter_generator()
                time.sleep(10)  # Wait for file to be written

                print("📄 Uploading cover letter...")
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", upload_cover_letter)
                upload_cover_letter.send_keys(r"C:\Users\aksha\ALL_PROJECTS\Mass_Apply\backend\CV.pdf")
                print("✅ Cover letter uploaded")

        except Exception as e:
            print(f"❌ Error during file uploads: {e}")


