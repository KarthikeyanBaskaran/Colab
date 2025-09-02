# main.py (Modified for multi-line input with empty line as terminator)

import os
import yaml
import logging
import sys
# from google.colab import userdata  # Not needed since we're using env var
from ReportLabs import load_content, build_pdf  # Assuming this is available or installed in Colab
from google.colab import userdata

# Import modules
from llm_module import get_tailored_resume_content, tailored_projects, apply_hist
from semantic_module import semantic_search, model  # model is global in semantic_module

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load secrets from environment variable (set this in the notebook kernel before running)
GROQ_API_KEY = userdata.get('GROQ_API_KEY')
if not GROQ_API_KEY:
    logging.error("FATAL: GROQ_API_KEY not found in environment variables.")
    sys.exit(1)

def load_config(path: str = "config.yaml") -> dict:
    """Loads the main configuration file."""
    logging.info(f"Loading configuration from '{path}'...")
    try:
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logging.error(f"FATAL: Configuration file not found at '{path}'. Please create it.")
        sys.exit(1)
    except yaml.YAMLError as e:
        logging.error(f"FATAL: Error parsing YAML configuration file: {e}")
        sys.exit(1)

def main():
    """Main function to run the resume generation process."""
    config = load_config()

    # Load initial base resume
    try:
        input_resume_path = "Resume.yaml"
        
        logging.info(f"Loading raw resume text from '{input_resume_path}'...")
        with open(input_resume_path, 'r') as f:
            resume_data = yaml.safe_load(f)
    
    except FileNotFoundError as e:
        logging.error(f"FATAL: A required base resume file was not found: {e.filename}")
        return
    

    # Parse the base file
    try:
        vestas_bullets = resume_data['Professional Experience']['Vestas Wind Technology']
        manpower_bullets = resume_data['Professional Experience']['ManpowerGroup Services']
        valeo_bullets = resume_data['Professional Experience']['Valeo India']
        projects_bullets = resume_data['projects']
    except:
        logging.error(f"FATAL: A required base resume is not in parsable YAML format")
        return

    # Modified input for job description: Read lines until an empty line
    print("Paste the Job Description below. End with an empty line (just press Enter).")
    jd_lines = []
    while True:
        try:
            line = input()
            if line.strip() == "":
                break
            jd_lines.append(line)
        except EOFError:
            break
    job_description = "\n".join(jd_lines).strip()
    
    if not job_description:
        logging.warning("Job description is empty. Exiting.")
        return
    
    try:
        logging.info("Semantic matching in progress")
        jd_embedding = model.encode(job_description, convert_to_tensor=True)
        sem_vestas = semantic_search(jd_embedding, vestas_bullets)
        sem_manpower = semantic_search(jd_embedding, manpower_bullets)
        sem_valeo = semantic_search(jd_embedding, valeo_bullets)
        sem_projects = semantic_search(jd_embedding, projects_bullets)

        vestas = [j for i, j in sem_vestas]
        manpower = [j for i, j in sem_manpower]
        valeo = [j for i, j in sem_valeo]
        projects = [j for i, j in sem_projects]
        
    except Exception as e:
        logging.error(f"Semantic matching failed: {e}")
        return

    # --- Initial Tailored Resume Generation  ---
    tailored_yaml = get_tailored_resume_content(vestas, manpower, valeo, job_description, GROQ_API_KEY)
    if not tailored_yaml:
        logging.error("Could not get initial content from LLM. Aborting PDF generation.")
        return
        
    resume_data = None

    try:
        # First attempt to parse the YAML
        resume_data = yaml.safe_load(tailored_yaml)
        logging.info("Initial YAML from LLM is valid.")
    except yaml.YAMLError as e:
        logging.error(f"The llm output is not in suitable YAML format {e}")

    
    # adding projects in the yaml output
    llm_tailored_projects = tailored_projects(resume_data, job_description, projects, GROQ_API_KEY)

    # --- Initial Tailored Projects Generation  ---
    try:
        # First attempt to parse the YAML
        projects_data = yaml.safe_load(llm_tailored_projects)
        new_projects = projects_data['projects']
        logging.info("Initial YAML from LLM is valid.")
    except yaml.YAMLError as e:
        logging.error(f"The llm output is not in suitable YAML format {e}")
        return

    jd_embedding = model.encode(job_description, convert_to_tensor=True)  # Re-encode if needed
    SemProjectFinalList = semantic_search(jd_embedding, new_projects + projects)
    ProjectFinalList = [j for i, j in SemProjectFinalList]
    resume_data['projects'] = ProjectFinalList
    
    if resume_data:
        output_yaml_path = config['paths']['output_yaml']
        logging.info(f"Saving final tailored YAML to '{output_yaml_path}'...")
        with open(output_yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(resume_data, f, sort_keys=False, default_flow_style=False)
        
        content = load_content("output.yaml")
        build_pdf(content, config['paths']['output_pdf'])

    apply_hist(job_description, config, GROQ_API_KEY)

if __name__ == "__main__":
    main()