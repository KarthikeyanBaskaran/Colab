# llm_module.py (No changes needed, as it's already suitable)

import os
import yaml
import logging
from datetime import datetime
from groq import Groq

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_llm_response(prompt: str, GROQ_API_KEY: str) -> str:
    """Generic function to get a response from the Groq LLM."""
    try:
        client = Groq(api_key=GROQ_API_KEY)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional career coach and resume-writing assistant. Your task is to craft strong, impactful, and industry-relevant resume bullet points that make my profile stand out for data analytics, data engineering roles and other type of analyst roles"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=1,
            max_tokens=1024,
            top_p=1,
            stream=True,
            stop=None,
        )
        content = ""
        for chunk in response:
            c = chunk.choices[0].delta.content if chunk.choices[0].delta.content else ""
            content += c
        return content
    except Exception as e:
        logging.error(f"An error occurred while communicating with the Groq API: {e}")
        return ""

def get_tailored_resume_content(resume: dict, job_description: str, GROQ_API_KEY: str) -> str:
    logging.info("Contacting Groq API to generate tailored resume experience content...")
    prompt = (f"""
    Rewrite the below points resume to suit the job description in resume suited quantifiable points with problem solution and impact type sentences. Maintain same yaml format and headings job
    ---
    My Resume:
    {resume}

    ---
    Job Description:
    {job_description}

    NO PREAMBLE only yaml
    """
    )
    
    yaml_output = get_llm_response(prompt, GROQ_API_KEY)
    if yaml_output:
        logging.info("Successfully received initial experience content from Groq.")
        with open("llmexp.txt", "w", encoding="utf-8") as file:
            file.write(yaml_output)
    return yaml_output

# def tailored_projects(resume, job_description, projects, GROQ_API_KEY: str):
#     logging.info("2. Contacting Groq API to generate tailored project content...")
#     prompt = (f"""
              
#     **Projects :**
#     * Generate 2 ATS friendly new projects when some mandatory keywords or technology from the job description is missing in my work experience and projects. 
     
    
#     Project Generation Guidelines:
#         Instructions:
#         1.The project can be built from data freely available content online by a college graduate.
#         2. The graduate has ability to learn new technology from online tutorials such as youtube
#         3. projects with difficulty level easy
       
       
#         ---
#         Output Format (YAML - directly parsable):       
#         projects: 
#         - project_name: <Project Title in 3 words>
#             description: <Short idea in one line>
#             keywords: [<keyword1>, <keyword2>, <keyword3>] # Include relevant keywords for each project.
              
#         My Resume:
#         {resume}

#         ---
#         Job Description:
#         {job_description}

#         projects:
#         {projects}
                

#         NO PREAMBLE only yaml

#         """)
#     yaml_output = get_llm_response(prompt, GROQ_API_KEY)
#     return yaml_output

def apply_hist(job_description: str, config: dict, GROQ_API_KEY: str):
    logging.info("Extracting company and position names")
    prompt = f"""What is the name of the company based on the below job description? If it does not contain a name return null

        {job_description}
        
        Output format as valid yaml format
       company: 
        - company name
       position_name:
        - position name
        
        NO PREAMBLE 
        """
    output = get_llm_response(prompt, GROQ_API_KEY)
    compos = yaml.safe_load(output)
    output_pdf_file = config['paths']['output_pdf']

    # Check for company name
    if compos['company'] is None:
        company = input("Enter the company name manually: ")
    else:
        company = compos['company'][0]

    # Check for position name
    if compos['position_name'] is None:
        position = input("Enter the position name manually: ")
    else:
        position = compos['position_name'][0].replace("/", "_")

    # Simplify for Colab: Save in current directory with position name
    new_pdf_filename = f"{position}_Resume.pdf"
    jd_filename = "job_description.txt"

    # Copy and rename PDF (assuming output_pdf is generated)
    import shutil
    shutil.copy2(output_pdf_file, new_pdf_filename)

    # Save job description
    with open(jd_filename, "w") as file:
        file.write(job_description)

    print(f"Resume saved as: {new_pdf_filename}")
    print(f"Job description saved as: {jd_filename}")