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

class ResumeParserTool:
    """Tool for parsing resumes using Azure OpenAI through Moya."""
    
    def __init__(self):
        self.name = "resume_parser"
        self.description = "Parses resume text to extract structured information using AI"
        
    def parse_resume(self, resume_text: str) -> Dict[str, Any]:
        """
        Parse resume text using Azure OpenAI through Moya.
        
        Args:
            resume_text: The text content of the resume
            
        Returns:
            Dict containing parsed resume information
        """
        # Prepare the prompt for the AI model
        prompt = f"""You are an expert resume parser. Your task is to extract structured information from the given resume.

INSTRUCTIONS:
1. Carefully analyze the resume text
2. Extract all relevant information
3. Format the response as a valid JSON object
4. Ensure all fields are properly filled
5. Use "N/A" for missing information
6. Keep the response concise and accurate

RESUME TEXT:
{resume_text}

REQUIRED OUTPUT FORMAT:
{{
    "name": "full name of the candidate",
    "contact_info": {{
        "email": "email address (if found)",
        "phone": "phone number (if found)",
        "location": "location (if found)"
    }},
    "summary": "brief professional summary",
    "skills": [
        "skill1",
        "skill2",
        ...
    ],
    "experience": [
        {{
            "company": "company name",
            "title": "job title",
            "dates": "employment period",
            "responsibilities": [
                "key responsibility 1",
                "key responsibility 2",
                ...
            ]
        }},
        ...
    ],
    "education": [
        {{
            "degree": "degree name",
            "institution": "school name",
            "dates": "education period"
        }},
        ...
    ],
    "certifications": [
        "certification1",
        "certification2",
        ...
    ]
}}

IMPORTANT:
- The response must be a valid JSON object
- Do not include any explanatory text outside the JSON structure
- Use arrays [] for multiple items
- Include all sections even if empty (use empty arrays [] or "N/A")
- Ensure proper JSON formatting with quotes around keys and string values

Please process the resume and return the structured JSON data:"""
        
        return prompt


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
