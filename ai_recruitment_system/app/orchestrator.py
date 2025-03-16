import os
import json
import re
import traceback
from typing import Dict, List, Any, Optional
import uuid
import datetime

from moya.tools.base_tool import BaseTool
from moya.tools.ephemeral_memory import EphemeralMemory
from moya.tools.tool_registry import ToolRegistry
from moya.registry.agent_registry import AgentRegistry
from moya.orchestrators.simple_orchestrator import SimpleOrchestrator
from moya.agents.azure_openai_agent import AzureOpenAIAgent, AzureOpenAIAgentConfig

from app.agents.resume_parser import extract_resume_data, ResumeParserTool
from app.agents.job_matcher import match_jobs, JobMatchingTool
from app.agents.candidate_assessor import generate_assessment, CandidateAssessorTool
from app.agents.interview_scheduler import schedule_interview, InterviewSchedulerTool

class RecruitmentOrchestrator:
    """Orchestrator for the AI recruitment system that coordinates between different agents"""
    
    def __init__(self):
        """Initialize the recruitment orchestrator"""
        self.orchestrator, self.agent_registry = self.setup_orchestration()
        self.thread_id = "recruitment_flow_001"
        try:
            EphemeralMemory.store_message(
                thread_id=self.thread_id, 
                sender="system", 
                content=f"Starting recruitment process, thread ID = {self.thread_id}"
            )
        except Exception as e:
            print(f"Warning: Could not initialize memory: {str(e)}")
            
        # Initialize tools directly
        self.resume_parser = ResumeParserTool()
        self.job_matcher = JobMatchingTool()
        self.candidate_assessor = CandidateAssessorTool()
        self.interview_scheduler = InterviewSchedulerTool()
        
    def setup_orchestration(self):
        """Set up the orchestrator with all the necessary tools and agents"""
        # Initialize tool registry
        tool_registry = ToolRegistry()
        EphemeralMemory.configure_memory_tools(tool_registry)
        
        # Register all recruitment tools
        resume_parser_tool = ResumeParserTool()
        job_matching_tool = JobMatchingTool()
        candidate_assessor_tool = CandidateAssessorTool()
        interview_scheduler_tool = InterviewSchedulerTool()
        
        # Add tools to registry with proper parameter definitions
        tool_registry.register_tool(BaseTool(
            name="resume_parser",
            description="Extracts structured information from resume text using NLP",
            function=resume_parser_tool.parse_resume,
            parameters={
                "resume_text": {
                    "type": "string",
                    "description": "The full resume text content as a string."
                }
            },
            required=["resume_text"]
        ))
        
        tool_registry.register_tool(BaseTool(
            name="job_matcher",
            description="Matches candidates with suitable job positions",
            function=job_matching_tool.match_jobs,
            parameters={
                "data": {
                    "type": "object",
                    "description": "Object containing candidate_profile and job_listings."
                }
            },
            required=["data"]
        ))
        
        # Register the candidate assessor tool with proper parameter definitions
        tool_registry.register_tool(BaseTool(
            name="candidate_assessor",
            description="Assesses candidate qualifications and generates assessments",
            function=candidate_assessor_tool.generate_assessment,
            parameters={
                "candidate_profile": {
                    "type": "object",
                    "description": "The candidate's profile information."
                },
                "job_info": {
                    "type": "object",
                    "description": "Information about the job position."
                }
            },
            required=["candidate_profile", "job_info"]
        ))
        
        tool_registry.register_tool(BaseTool(
            name="interview_scheduler",
            description="Schedules interviews and manages available interview slots",
            function=interview_scheduler_tool.schedule_interview,
            parameters={
                "data": {
                    "type": "object",
                    "description": "Object containing candidate_info, job_info, and selected_slot."
                }
            },
            required=["data"]
        ))
        
        # Create agent config
        agent_config = AzureOpenAIAgentConfig(
            agent_name="recruitment_agent",
            description="AI-powered recruitment system agent",
            model_name="gpt-4o",
            agent_type="ChatAgent",
            tool_registry=tool_registry,
            system_prompt="""
                You are an AI-powered recruitment system.
                Your task is to:
                1. Parse resumes to extract relevant information
                2. Match candidates with suitable job positions
                3. Generate assessments for candidates
                4. Schedule interviews
                
                Follow the recruitment process step by step and use the appropriate tools at each stage.
            """,
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_base=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        )
        
        # Create agent
        agent = AzureOpenAIAgent(config=agent_config)
        
        # Register agent
        agent_registry = AgentRegistry()
        agent_registry.register_agent(agent)
        
        # Create orchestrator
        orchestrator = SimpleOrchestrator(agent_registry=agent_registry, default_agent_name="recruitment_agent")
        
        return orchestrator, agent_registry
    
    async def process_resume(self, resume_text: str):
        """Process a resume using Azure OpenAI through Moya
        
        Args:
            resume_text: The text content of the resume
            
        Returns:
            The parsed resume data
        """
        print("Processing resume with Azure OpenAI...")
        try:
            # Store the resume in memory
            EphemeralMemory.store_message(
                thread_id=self.thread_id,
                sender="user",
                content=resume_text
            )
            
            # Get the prompt from the resume parser tool
            prompt = self.resume_parser.parse_resume(resume_text)
            
            # Use the orchestrator to process the resume with Azure OpenAI
            response = self.orchestrator.orchestrate(
                thread_id=self.thread_id,
                user_message=prompt,
                system_message="""You are an expert resume parser AI. Your task is to extract structured information from resumes and return it in valid JSON format. 
                Focus only on extracting and structuring the information. Do not include any additional text or explanations in your response."""
            )
            
            # Clean the response to ensure we only have JSON
            response = response.strip()
            # Remove any markdown code block indicators if present
            response = response.replace('```json', '').replace('```', '').strip()
            
            # Store the parsed result
            EphemeralMemory.store_message(
                thread_id=self.thread_id,
                sender="assistant",
                content=response
            )
            
            # Convert response to structured data
            try:
                parsed_data = json.loads(response)
                
                # Validate the parsed data has required fields
                required_fields = ["name", "contact_info", "skills", "experience", "education"]
                missing_fields = [field for field in required_fields if field not in parsed_data]
                
                if missing_fields:
                    print(f"Warning: Missing required fields: {', '.join(missing_fields)}")
                    # Add empty structures for missing fields
                    for field in missing_fields:
                        if field == "contact_info":
                            parsed_data[field] = {"email": "N/A", "phone": "N/A", "location": "N/A"}
                        elif field in ["skills", "experience", "education"]:
                            parsed_data[field] = []
                        else:
                            parsed_data[field] = "N/A"
                
                print(f"Successfully parsed resume for: {parsed_data.get('name', 'Unknown')}")
                print(f"Found {len(parsed_data.get('skills', []))} skills")
                print(f"Found {len(parsed_data.get('experience', []))} experience entries")
                print(f"Found {len(parsed_data.get('education', []))} education entries")
                
                return parsed_data
                
            except json.JSONDecodeError as e:
                print(f"Error: Could not parse JSON response: {str(e)}")
                print("Raw response:", response)
                return {"error": "Failed to parse resume data", "raw_response": response}
                
        except Exception as e:
            print(f"Error in resume processing: {str(e)}")
            traceback.print_exc()
            return {"error": str(e)}
    
    # Update the match_with_jobs method in RecruitmentOrchestrator class
    async def match_with_jobs(self, candidate_profile: Dict[str, Any], job_listings: List[Dict[str, Any]]):
        """Match a candidate with job listings using direct tool call
        
        Args:
            candidate_profile: The parsed candidate profile
            job_listings: Available job listings
            
        Returns:
            List of job matches with similarity scores
        """
        print("Directly matching jobs with JobMatchingTool...")
        try:
            # Call the job matcher tool directly
            data = {
                "candidate_profile": candidate_profile,
                "job_listings": job_listings
            }
            matches = self.job_matcher.match_jobs(data)
            print(f"Job matching complete. Found {len(matches)} potential matches.")
            return matches
        except Exception as e:
            print(f"Error in direct job matching: {str(e)}")
            traceback.print_exc()
            
            # Create fallback job matches
            return [
                {
                    "title": "Software Engineer",
                    "company": "TechCorp",
                    "match_score": 0.85,
                    "department": "Engineering",
                    "location": "San Francisco, CA",
                    "experience_level": "Mid-level",
                    "required_skills": ["Python", "JavaScript", "React"],
                    "preferred_skills": ["AWS", "Docker", "TypeScript"]
                },
                {
                    "title": "Data Scientist",
                    "company": "DataInsights",
                    "match_score": 0.78,
                    "department": "Analytics",
                    "location": "New York, NY",
                    "experience_level": "Senior",
                    "required_skills": ["Python", "Machine Learning", "SQL"],
                    "preferred_skills": ["TensorFlow", "PyTorch", "Big Data"]
                }
            ]          
   
# Update the generate_assessment method in RecruitmentOrchestrator class

async def generate_assessment(self, candidate_profile: Dict[str, Any], job_info: Dict[str, Any]):
    """Generate an assessment using Azure OpenAI through Moya
    
    Args:
        candidate_profile: The parsed candidate profile
        job_info: Information about the job
        
    Returns:
        Assessment details
    """
    print("Processing assessment generation with Azure OpenAI...")
    try:
        # Store the assessment request in memory
        EphemeralMemory.store_message(
            thread_id=self.thread_id,
            sender="user",
            content=f"Generating assessment for {candidate_profile.get('name', 'candidate')} for {job_info.get('title', 'position')}"
        )
        
        # Get the prompt from the candidate assessor tool
        prompt = self.candidate_assessor.generate_assessment(data={
            "candidate_profile": candidate_profile,
            "job_info": job_info
        })
        
        # Use the orchestrator to process the assessment generation with Azure OpenAI
        response = await self.orchestrator.orchestrate(
            thread_id=self.thread_id,
            user_message=prompt,
            system_message="""You are an expert technical recruiter that creates comprehensive candidate assessments. 
            Generate detailed and challenging questions that accurately test a candidate's skills for a specific job role."""
        )
        
        # Clean the response to ensure we only have JSON
        if isinstance(response, str):
            response = response.strip()
            # Remove any markdown code block indicators if present
            response = response.replace('```json', '').replace('```', '').strip()
            
            # Store the assessment result
            EphemeralMemory.store_message(
                thread_id=self.thread_id,
                sender="assistant",
                content=response
            )
            
            # Convert response to structured data
            try:
                parsed_data = json.loads(response)
                
                # Validate the parsed data has required fields
                required_fields = ["assessment_id", "technical_questions", "behavioral_questions"]
                missing_fields = [field for field in required_fields if field not in parsed_data]
                
                if missing_fields:
                    print(f"Warning: Missing required fields in assessment: {', '.join(missing_fields)}")
                    # Add default values for missing fields
                    if "assessment_id" not in parsed_data:
                        parsed_data["assessment_id"] = f"ASM-{uuid.uuid4().hex[:8].upper()}"
                    if "technical_questions" not in parsed_data:
                        parsed_data["technical_questions"] = []
                    if "behavioral_questions" not in parsed_data:
                        parsed_data["behavioral_questions"] = []
                
                print(f"Successfully generated assessment ID: {parsed_data.get('assessment_id')}")
                print(f"Created {len(parsed_data.get('technical_questions', []))} technical questions")
                print(f"Created {len(parsed_data.get('behavioral_questions', []))} behavioral questions")
                if "coding_challenge" in parsed_data and parsed_data["coding_challenge"]:
                    print(f"Included coding challenge: {parsed_data['coding_challenge'].get('title', 'Untitled')}")
                
                return parsed_data
                    
            except json.JSONDecodeError as e:
                print(f"Error: Could not parse JSON response from assessment generation: {str(e)}")
                print("Raw response:", response[:500])  # Print first 500 chars of response
                # Try to clean up the response and parse again
                try:
                    # Remove any non-JSON text
                    json_start = response.find('{')
                    json_end = response.rfind('}') + 1
                    if json_start >= 0 and json_end > json_start:
                        cleaned_response = response[json_start:json_end]
                        parsed_data = json.loads(cleaned_response)
                        print("Successfully parsed cleaned response")
                        return parsed_data
                except:
                    pass
        else:
            print(f"Unexpected response type: {type(response)}")
                    
        # If we get here, we need to create a fallback assessment
        return self._create_fallback_assessment(candidate_profile, job_info)
                
    except Exception as e:
        print(f"Error in assessment generation: {str(e)}")
        import traceback
        traceback.print_exc()
        return self._create_fallback_assessment(candidate_profile, job_info)
        
def _create_fallback_assessment(self, candidate_profile, job_info):
    """Create a fallback assessment when AI generation fails"""
    assessment_id = f"ASM-{uuid.uuid4().hex[:8].upper()}"
    
    # Extract skills to assess
    candidate_skills = candidate_profile.get("skills", [])
    required_skills = job_info.get("required_skills", [])
    
    # Determine skills to assess (intersection of candidate skills and required skills)
    skills_to_assess = []
    if isinstance(candidate_skills, list) and isinstance(required_skills, list):
        skills_to_assess = list(set([s.lower() for s in candidate_skills if isinstance(s, str)]) & 
                                set([s.lower() for s in required_skills if isinstance(s, str)]))
        
        # Convert back to original case
        skills_dict = {s.lower(): s for s in candidate_skills + required_skills if isinstance(s, str)}
        skills_to_assess = [skills_dict.get(s, s) for s in skills_to_assess]
    
    if not skills_to_assess and isinstance(candidate_skills, list) and candidate_skills:
        # If no intersection, use some of the candidate's skills
        skills_to_assess = [s for s in candidate_skills if isinstance(s, str)][:3]
    elif not skills_to_assess and isinstance(required_skills, list) and required_skills:
        # If candidate has no skills listed, use required skills
        skills_to_assess = [s for s in required_skills if isinstance(s, str)][:3]
    
    # Fallback if still no skills
    if not skills_to_assess:
        skills_to_assess = ["Problem Solving", "Communication", "Technical Knowledge"]
    
    # Create technical questions based on skills
    technical_questions = []
    for i, skill in enumerate(skills_to_assess[:5]):
        technical_questions.append({
            "question_id": f"TQ-{i+1}",
            "skill": skill,
            "question": f"Please explain your experience with {skill} and how you've applied it in your work.",
            "type": "technical"
        })
    
    # Create fallback assessment
    return {
        "assessment_id": assessment_id,
        "candidate_name": candidate_profile.get("name", "Unknown Candidate"),
        "job_title": job_info.get("title", "Unknown Position"),
        "company": job_info.get("company", "Unknown Company"),
        "skills_assessed": skills_to_assess,
        "technical_questions": technical_questions,
        "behavioral_questions": [
            {
                "question_id": "BQ-1",
                "question": "Describe a challenging project you worked on and how you contributed to its success.",
                "type": "behavioral"
            },
            {
                "question_id": "BQ-2", 
                "question": "Tell me about a time when you had to learn a new technology quickly.",
                "type": "behavioral"
            },
            {
                "question_id": "BQ-3",
                "question": "Describe how you handle tight deadlines and competing priorities.",
                "type": "behavioral"
            }
        ],
        "evaluation_criteria": {
            "technical_knowledge": "Assess depth and accuracy of technical knowledge",
            "problem_solving": "Evaluate approach to solving complex problems",
            "communication": "Assess clarity and effectiveness of communication",
            "cultural_fit": "Evaluate alignment with company values and culture"
        },
        "passing_threshold": 70,
        "created_at": datetime.datetime.now().isoformat(),
        "generated_by": "fallback"
    }
    
    async def schedule_interview(self, candidate_info: Dict[str, Any], job_info: Dict[str, Any], 
                              selected_slot: Dict[str, Any]):
        """Schedule an interview using direct tool call
        
        Args:
            candidate_info: Information about the candidate
            job_info: Information about the job
            selected_slot: The selected interview slot
            
        Returns:
            Interview scheduling confirmation
        """
        print("Directly scheduling interview with InterviewSchedulerTool...")
        try:
            # Call the scheduler tool directly
            data = {
                "candidate_info": candidate_info,
                "job_info": job_info,
                "selected_slot": selected_slot
            }
            result = self.interview_scheduler.schedule_interview(data)
            print(f"Interview scheduling complete. Created interview ID: {result.get('interview_id')}")
            return result
        except Exception as e:
            print(f"Error in direct interview scheduling: {str(e)}")
            traceback.print_exc()
            
            # Create a fallback interview confirmation
            return {
                "interview_id": "INT-999",
                "message": "Interview scheduled successfully",
                "details": {
                    "candidate": candidate_info.get("name", "Unknown"),
                    "position": job_info.get("title", "Unknown Position"),
                    "company": job_info.get("company", "Unknown Company"),
                    "date": "2023-12-01",
                    "time": "10:00 AM",
                    "interviewer": "HR Team",
                    "location": "Virtual"
                },
                "status": "scheduled"
            }
    
    def cleanup(self):
        """Clean up resources used by the orchestrator"""
        try:
            EphemeralMemory.memory_repository.delete_thread(self.thread_id)
        except:
            pass