from typing import Dict, List, Any, Optional
import datetime
import json
import uuid
import os
from dotenv import load_dotenv
from moya.agents.base_agent import Agent, AgentConfig
from moya.tools.base_tool import BaseTool

# Load environment variables if .env exists
ENV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
if os.path.exists(ENV_PATH):
    load_dotenv(dotenv_path=ENV_PATH)

class CandidateAssessorTool:
    """Tool for assessing candidates and generating interview questions using Azure OpenAI through Moya."""
    
    def __init__(self):
        self.name = "candidate_assessor"
        self.description = "Assesses candidate qualifications and generates customized assessments using AI"
        
    def generate_assessment(self, data: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        """Generate a prompt for Azure OpenAI to create an assessment for a candidate
        
        Args:
            data: Dictionary containing candidate_profile and job_info
            **kwargs: Alternative way to pass candidate_profile and job_info directly
                
        Returns:
            A prompt for Azure OpenAI to create an assessment
        """
        # Extract candidate_profile and job_info from either data dict or kwargs
        candidate_profile = None
        job_info = None
        
        if data and isinstance(data, dict):
            candidate_profile = data.get("candidate_profile", {})
            job_info = data.get("job_info", {})
        else:
            candidate_profile = kwargs.get("candidate_profile", {})
            job_info = kwargs.get("job_info", {})
        
        # Validate required fields
        if not candidate_profile:
            return {"error": "Candidate profile is required"}
        
        if not job_info:
            return {"error": "Job information is required"}
            
        # Create a unique assessment ID
        assessment_id = f"ASM-{uuid.uuid4().hex[:8].upper()}"
        
        # Prepare the prompt for the AI model
        prompt = f"""You are an expert technical recruiter specialized in creating candidate assessments.

Please create a comprehensive assessment for a candidate based on their profile and the job requirements.

ASSESSMENT ID: {assessment_id}

CANDIDATE PROFILE:
{json.dumps(candidate_profile, indent=2)}

JOB INFORMATION:
{json.dumps(job_info, indent=2)}

INSTRUCTIONS:
1. Analyze the candidate's skills and experience against the job requirements
2. Create a personalized assessment with appropriate technical and behavioral questions
3. Include a coding challenge if the role is technical
4. Provide detailed evaluation criteria

REQUIRED OUTPUT FORMAT:
{{
    "assessment_id": "{assessment_id}",
    "candidate_name": "{candidate_profile.get('name', 'Unknown Candidate')}",
    "job_title": "{job_info.get('title', 'Unknown Position')}",
    "company": "{job_info.get('company', 'Unknown Company')}",
    "skills_assessed": [List of skills being assessed],
    "technical_questions": [
        {{
            "question_id": "TQ-1",
            "skill": "skill name",
            "question": "Detailed technical question text",
            "type": "technical"
        }},
        ... (5-8 questions total)
    ],
    "behavioral_questions": [
        {{
            "question_id": "BQ-1",
            "question": "Detailed behavioral question text",
            "type": "behavioral"
        }},
        ... (3-5 questions total)
    ],
    "coding_challenge": {{  // Optional, include only if job is technical
        "title": "Challenge title",
        "description": "Detailed description of the coding task",
        "requirements": [
            "Requirement 1",
            "Requirement 2",
            ...
        ],
        "time_limit": "Suggested time limit",
        "language": "Suggested programming language"
    }},
    "evaluation_criteria": {{
        "technical_knowledge": "Criteria for evaluating technical knowledge",
        "problem_solving": "Criteria for evaluating problem solving",
        "communication": "Criteria for evaluating communication",
        ...
    }},
    "scoring_guide": {{
        "1": "Does not meet expectations",
        "2": "Partially meets expectations",
        "3": "Meets expectations",
        "4": "Exceeds expectations",
        "5": "Significantly exceeds expectations"
    }},
    "passing_threshold": 70,
    "created_at": "{datetime.datetime.now().isoformat()}"
}}

IMPORTANT GUIDELINES:
1. Generate challenging but fair questions that match the candidate's skill level
2. Create technical questions specific to the technologies in their profile
3. Make behavioral questions relevant to the job role and seniority
4. Be specific and detailed in all questions
5. Ensure your response is valid JSON with proper formatting
6. Do not include any explanation or text outside the JSON structure

The output MUST be a valid JSON object with all the required fields.
"""
        
        return prompt
    
    def evaluate_submission(self, data: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        """Generate a prompt for Azure OpenAI to evaluate a candidate's assessment submission
        
        Args:
            data: Dictionary containing assessment_id, assessment_details, submission, and evaluator_notes
            **kwargs: Alternative way to pass parameters directly
                
        Returns:
            A prompt for Azure OpenAI to evaluate the submission
        """
        # Extract parameters from either data dict or kwargs
        assessment_id = None
        assessment_details = None
        submission = None
        evaluator_notes = None
        
        if data and isinstance(data, dict):
            assessment_id = data.get("assessment_id")
            assessment_details = data.get("assessment_details", {})
            submission = data.get("submission", {})
            evaluator_notes = data.get("evaluator_notes", {})
        else:
            assessment_id = kwargs.get("assessment_id")
            assessment_details = kwargs.get("assessment_details", {})
            submission = kwargs.get("submission", {})
            evaluator_notes = kwargs.get("evaluator_notes", {})
        
        # Validate required fields
        if not assessment_id:
            return {"error": "Assessment ID is required"}
        
        if not submission:
            return {"error": "Submission data is required"}
        
        if not assessment_details:
            return {"error": "Assessment details are required"}
        
        # Prepare the prompt for the AI model
        prompt = f"""You are an expert technical evaluator specialized in assessing candidate submissions.

Please evaluate the candidate's assessment submission based on the original assessment and any evaluator notes.

ASSESSMENT ID: {assessment_id}

ORIGINAL ASSESSMENT:
{json.dumps(assessment_details, indent=2)}

CANDIDATE SUBMISSION:
{json.dumps(submission, indent=2)}

EVALUATOR NOTES (if any):
{json.dumps(evaluator_notes or {}, indent=2)}

INSTRUCTIONS:
1. Analyze the candidate's answers against the assessment questions
2. Evaluate technical accuracy, problem-solving approach, and communication
3. Provide scores and detailed feedback for each area
4. Make an overall recommendation based on the scores

REQUIRED OUTPUT FORMAT:
{{
    "assessment_id": "{assessment_id}",
    "scores": {{
        "technical_knowledge": score (0-100),
        "problem_solving": score (0-100),
        "communication": score (0-100),
        "cultural_fit": score (0-100),
        "experience": score (0-100)
    }},
    "overall_score": calculated_overall_score,
    "feedback": {{
        "technical_knowledge": "Detailed feedback on technical knowledge",
        "problem_solving": "Detailed feedback on problem solving",
        "communication": "Detailed feedback on communication",
        "cultural_fit": "Detailed feedback on cultural fit",
        "experience": "Detailed feedback on experience"
    }},
    "strengths": [
        "Key strength 1",
        "Key strength 2",
        ...
    ],
    "areas_for_improvement": [
        "Area for improvement 1",
        "Area for improvement 2",
        ...
    ],
    "evaluator_notes": {{ // Include any provided notes here
        ...
    }},
    "status": "passed" or "failed",
    "recommendation": "Your recommendation about this candidate",
    "next_steps": [
        "Suggested next step 1",
        "Suggested next step 2",
        ...
    ],
    "evaluated_at": "{datetime.datetime.now().isoformat()}"
}}

IMPORTANT GUIDELINES:
1. Be objective and fair in your evaluation
2. Base scores on demonstrated skills, not assumptions
3. Provide constructive feedback, even for high scores
4. Consider the job requirements when making recommendations
5. Use a 70% threshold for passing
6. Ensure your response is valid JSON with proper formatting
7. Do not include any explanation or text outside the JSON structure

The output MUST be a valid JSON object with all the required fields.
"""
        
        return prompt


class CandidateAssessorAgent(Agent):
    """Agent for assessing candidates and generating interview questions"""
    
    def __init__(self, config: AgentConfig = None):
        """Initialize the candidate assessor agent"""
        if config is None:
            config = AgentConfig(
                agent_name="candidate_assessor",
                agent_type="candidate_assessor",
                description="Assesses candidates and generates customized interview questions",
                system_prompt="You are a candidate assessment assistant that creates comprehensive assessments based on candidate profiles and job requirements."
            )
        super().__init__(config)
        self.assessor_tool = CandidateAssessorTool()
        
    async def handle_message(self, message: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Handle incoming messages for candidate assessment
        
        Args:
            message: Message dictionary containing candidate profile and job info
            
        Returns:
            The assessment prompt for Azure OpenAI
        """
        try:
            # Extract candidate profile and job info from the message
            candidate_profile = message.get("candidate_profile", {})
            job_info = message.get("job_info", {})
            
            # Generate the assessment prompt
            return self.assessor_tool.generate_assessment(data={"candidate_profile": candidate_profile, "job_info": job_info})
        except Exception as e:
            return {"error": f"Failed to generate assessment: {str(e)}"}
            
    async def handle_message_stream(self, message: str, **kwargs):
        """Stream the assessment generation process"""
        yield "Streaming is not supported for assessment generation. Please use handle_message instead."


# Helper functions for standalone use
async def generate_assessment(candidate_profile: Dict[str, Any], job_info: Dict[str, Any]) -> Dict[str, Any]:
    """Generate an assessment prompt for a candidate
    
    Args:
        candidate_profile: Information about the candidate
        job_info: Information about the job
        
    Returns:
        A prompt for Azure OpenAI to create an assessment
    """
    assessor_tool = CandidateAssessorTool()
    return assessor_tool.generate_assessment(data={"candidate_profile": candidate_profile, "job_info": job_info})


async def evaluate_submission(assessment_id: str, assessment_details: Dict[str, Any], 
                           submission: Dict[str, Any], evaluator_notes: Dict[str, Any] = None) -> Dict[str, Any]:
    """Generate a prompt to evaluate a candidate's assessment submission
    
    Args:
        assessment_id: ID of the assessment
        assessment_details: The original assessment
        submission: Candidate's answers and solutions
        evaluator_notes: Notes from the evaluator (optional)
        
    Returns:
        A prompt for Azure OpenAI to evaluate the submission
    """
    assessor_tool = CandidateAssessorTool()
    return assessor_tool.evaluate_submission(data={
        "assessment_id": assessment_id, 
        "assessment_details": assessment_details, 
        "submission": submission, 
        "evaluator_notes": evaluator_notes
    })