from typing import Dict, Any, Optional, List, Callable
import os
import re
import spacy
from dotenv import load_dotenv
from moya.agents.base_agent import Agent, AgentConfig
from moya.tools.base_tool import BaseTool

# Load environment variables if .env exists
ENV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
if os.path.exists(ENV_PATH):
    load_dotenv(dotenv_path=ENV_PATH)

class ResumeParserTool(BaseTool):
    """Tool for parsing resumes using spaCy"""
    
    name = "resume_parser"
    description = "Extracts structured information from resume text using NLP"
    function = "parse_resume"
    
    def __init__(self):
        """Initialize the resume parser tool"""
        super().__init__(name=self.name, function=self.function)
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            # If the spaCy model isn't found, print a helpful message
            print("Spacy model not found. Please run: python -m spacy download en_core_web_sm")
            raise
    
    def parse_resume(self, resume_text: str) -> Dict[str, Any]:
        """Parse a resume and extract structured information
        
        Args:
            resume_text: The text content of the resume
            
        Returns:
            A dictionary containing the extracted resume information
        """
        return self.extract_data(resume_text)
    
    def extract_data(self, resume_text: str) -> Dict[str, Any]:
        """Extract information from resume text"""
        # Clean the input text
        resume_text = resume_text.strip()
        doc = self.nlp(resume_text)
        
        # Initialize extracted data structure
        extracted_data = {
            "name": None,
            "skills": [],
            "experience": [],
            "education": [],
            "contact_info": {
                "email": None,
                "phone": None
            }
        }
        
        # Split text into sections based on headers and blank lines
        sections = {}
        current_section = "header"  # Default section for the top of the resume
        sections[current_section] = []
        
        lines = resume_text.split('\n')
        for i, line in enumerate(lines):
            line = line.strip()
            # Skip empty lines
            if not line:
                continue
            
            # Check if this is a section header (all caps, or followed by blank line)
            if line.upper() == line and len(line) > 3:
                current_section = line.lower()
                sections[current_section] = []
            # Check for common section headers
            elif any(header in line.lower() for header in ["education", "experience", "skills", "work history", "contact"]):
                current_section = next(h for h in ["education", "experience", "skills", "work history", "contact"] 
                                     if h in line.lower())
                sections[current_section] = []
            else:
                sections[current_section].append(line)
        
        # Extract name (typically first line of resume)
        if "header" in sections and sections["header"]:
            extracted_data["name"] = sections["header"][0]
        
        # Extract contact information using regex
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        phone_pattern = r'\b(?:\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b'
        
        # Look for email and phone in the entire text
        emails = re.findall(email_pattern, resume_text)
        phones = re.findall(phone_pattern, resume_text)
        
        if emails:
            extracted_data["contact_info"]["email"] = emails[0]
        if phones:
            extracted_data["contact_info"]["phone"] = phones[0]
        
        # Extract skills
        skill_keywords = {
            "python": ["python", " py ", "py,"],
            "java": ["java", "java se", "java ee"],
            "javascript": ["javascript", " js ", "js,", "ecmascript"],
            "typescript": ["typescript", " ts ", "ts,"],
            "react": ["react", "react.js", "reactjs"],
            "node.js": ["node.js", "nodejs", "node"],
            "sql": ["sql", "mysql", "postgresql", "oracle"],
            "machine learning": ["machine learning", " ml ", "ml,", "deep learning", " dl ", "dl,"],
            "ai": ["ai", "artificial intelligence"],
            "docker": ["docker", "containerization"],
            "kubernetes": ["kubernetes", "k8s"],
            "aws": ["aws", "amazon web services"],
            "azure": ["azure", "microsoft azure"],
            "gcp": ["gcp", "google cloud"],
            "devops": ["devops", "devsecops"],
            "ci/cd": ["ci/cd", "continuous integration", "continuous deployment"],
            "html": ["html", "html5"],
            "css": ["css", "css3", "scss", "sass"],
            "angular": ["angular", "angularjs"],
            "vue.js": ["vue.js", "vuejs", "vue"],
            "django": ["django"],
            "flask": ["flask"],
            "fastapi": ["fastapi"],
            "mongodb": ["mongodb", "mongo"],
            "redis": ["redis"],
            "elasticsearch": ["elasticsearch", "elk"]
        }
        
        found_skills = set()
        text_lower = " " + resume_text.lower() + " "  # Add spaces to help with word boundary detection
        
        # Process skills section specifically if it exists
        for section_key in sections.keys():
            if "skill" in section_key:
                section_text = " ".join(sections[section_key])
                section_lower = " " + section_text.lower() + " "
                
                for skill, variations in skill_keywords.items():
                    if any(var in section_lower for var in variations):
                        found_skills.add(skill)
        
        # Also look for skills in the entire document
        for skill, variations in skill_keywords.items():
            if any(var in text_lower for var in variations):
                found_skills.add(skill)
        
        extracted_data["skills"] = sorted(list(found_skills))
        
        # Extract education
        education_keywords = [
            "bachelor", "master", "phd", "degree", "university", "college",
            "diploma", "certification", "b.tech", "m.tech", "b.e.", "m.e.",
            "b.sc", "m.sc", "mba"
        ]
        
        # Process education section if it exists
        for section_key in sections.keys():
            if "education" in section_key:
                education_lines = []
                current_entry = []
                
                for line in sections[section_key]:
                    if line and len(line) > 3:
                        if any(keyword in line.lower() for keyword in education_keywords) and current_entry:
                            # This is a new education entry
                            education_lines.append(" ".join(current_entry))
                            current_entry = [line]
                        else:
                            current_entry.append(line)
                
                if current_entry:
                    education_lines.append(" ".join(current_entry))
                
                extracted_data["education"] = education_lines
        
        # Extract experience
        for section_key in sections.keys():
            if any(exp_key in section_key for exp_key in ["experience", "work history", "employment"]):
                exp_entries = []
                current_entry = []
                
                for line in sections[section_key]:
                    if line and len(line) > 3:
                        # Heuristic: a date or "present" often indicates a new job entry
                        if (re.search(r'\b(19|20)\d{2}\b', line) or "present" in line.lower()) and current_entry:
                            exp_entries.append(" ".join(current_entry))
                            current_entry = [line]
                        else:
                            current_entry.append(line)
                
                if current_entry:
                    exp_entries.append(" ".join(current_entry))
                
                # If we found structured entries, use them
                if exp_entries:
                    extracted_data["experience"] = exp_entries
                # Otherwise, just use the raw section text
                else:
                    extracted_data["experience"] = [" ".join(sections[section_key])]
        
        return extracted_data


class ResumeParserAgent(Agent):
    """Agent for parsing and analyzing resumes"""
    
    def __init__(self, config: AgentConfig = None):
        """Initialize the resume parser agent"""
        if config is None:
            config = AgentConfig(
                agent_name="resume_parser",
                agent_type="resume_parser",
                description="Extracts and analyzes information from resumes",
                system_prompt="You are a resume parsing assistant that extracts structured information from resumes."
            )
        super().__init__(config)
        self.parser_tool = ResumeParserTool()
        
    async def handle_message(self, message: str, **kwargs) -> Dict[str, Any]:
        """Handle incoming resume text and extract information
        
        Args:
            message: The resume text to parse
            
        Returns:
            The extracted resume data as a dictionary
        """
        try:
            extracted_data = self.parser_tool.parse_resume(message)
            return extracted_data
        except Exception as e:
            return {"error": f"Failed to parse resume: {str(e)}"}
            
    async def handle_message_stream(self, message: str, **kwargs):
        """Stream is not supported for resume parsing"""
        yield "Streaming is not supported for resume parsing. Please use handle_message instead."


# Helper function for standalone use
async def extract_resume_data(resume_text: str) -> Dict[str, Any]:
    """Extract structured data from a resume text using the ResumeParserAgent
    
    Args:
        resume_text: The text content of the resume
        
    Returns:
        A dictionary containing the extracted resume information
    """
    config = AgentConfig(
        agent_name="resume_parser",
        agent_type="resume_parser",
        description="Extracts and analyzes information from resumes",
        system_prompt="You are a resume parsing assistant that extracts structured information from resumes."
    )
    agent = ResumeParserAgent(config)
    return await agent.handle_message(resume_text)
