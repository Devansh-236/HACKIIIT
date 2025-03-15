import sys
import os
from dotenv import load_dotenv
from moya import MoyaAgent
from app.agents.resume_parser import ResumeParserTool
from app.agents.job_matcher import match_jobs

# Load API keys from .env file
ENV_PATH = "/home/mehulagarwal/Documents/hackIIIt/try/moya/ai_recruitment_system/.env"  # Change this to the actual path
load_dotenv(dotenv_path=ENV_PATH)

def main():
    if len(sys.argv) < 2:
        print("Usage: python orchestrator.py <resume_file>")
        sys.exit(1)

    resume_file = sys.argv[1]

    try:
        with open(resume_file, "r", encoding="utf-8") as file:
            resume_text = file.read()

        # Initialize Moya agent
        agent = MoyaAgent(api_key=os.getenv("OPENAI_API_KEY"))

        # Register ResumeParserTool in Moya
        parser_tool = ResumeParserTool()
        agent.register_tool(parser_tool)

        # Parse resume and store in Moya's memory
        extracted_data = parser_tool.run(resume_text, agent.memory)

        # Retrieve parsed resume from Moya memory
        parsed_resume = agent.memory.get("resume_data")

        print("\n📄 Parsed Resume Data:")
        print(parsed_resume)

        # Sample job descriptions
        job_descriptions = [
            {"title": "AI Engineer", "skills": ["Machine Learning", "Deep Learning", "Python"]},
            {"title": "Software Developer", "skills": ["Python", "Java"]},
            {"title": "Data Scientist", "skills": ["Machine Learning", "Data Analysis"]}
        ]

        # Match jobs based on parsed resume data
        matched_jobs = match_jobs(job_descriptions, parsed_resume)

        print("\n🎯 Matched Jobs:")
        for job in matched_jobs:
            print(f"- {job['title']}")

    except FileNotFoundError:
        print(f"❌ Error: File '{resume_file}' not found.")
    except Exception as e:
        print(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    main()
