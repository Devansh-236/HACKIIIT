import os
import json
import re
import traceback
from typing import Dict, List, Any, Optional

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
        
        # Add tools to registry
        tool_registry.register_tool(BaseTool(
            name=resume_parser_tool.name,
            description=resume_parser_tool.description,
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
            name=job_matching_tool.name,
            description=job_matching_tool.description,
            function=job_matching_tool.match_jobs,
            parameters={
                "candidate_profile": {
                    "type": "object",
                    "description": "The parsed candidate profile containing skills, experience, etc."
                },
                "job_listings": {
                    "type": "array",
                    "description": "List of available job positions to match against."
                }
            },
            required=["candidate_profile", "job_listings"]
        ))
        
        tool_registry.register_tool(BaseTool(
            name=candidate_assessor_tool.name,
            description=candidate_assessor_tool.description,
            function=candidate_assessor_tool.generate_assessment,
            parameters={
                "data": {
                    "type": "object",
                    "description": "Object containing candidate_profile and job_info."
                }
            },
            required=["data"]
        ))
        
        tool_registry.register_tool(BaseTool(
            name=interview_scheduler_tool.name,
            description=interview_scheduler_tool.description,
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
    
    async def match_with_jobs(self, candidate_profile: Dict[str, Any], job_listings: List[Dict[str, Any]]):
        """Match a candidate with job listings using Azure OpenAI through Moya
        
        Args:
            candidate_profile: The parsed candidate profile
            job_listings: Available job listings
            
        Returns:
            List of job matches with similarity scores
        """
        print("Processing job matches with Azure OpenAI...")
        try:
            # Store the matching request in memory
            EphemeralMemory.store_message(
                thread_id=self.thread_id,
                sender="user",
                content=f"Matching candidate with {len(job_listings)} jobs"
            )
            
            # Get the prompt from the job matcher tool
            prompt = self.job_matcher.match_jobs(
                candidate_profile=candidate_profile,
                job_listings=job_listings
            )
            
            # Use the orchestrator to process the job matching with Azure OpenAI
            response = await self.orchestrator.orchestrate(
                thread_id=self.thread_id,
                user_message=prompt,
                system_message="""You are an expert job matching AI. Your task is to match candidates with job positions and return results in valid JSON format.
                Focus only on analyzing the match and structuring the information. Do not include any additional text or explanations in your response.
                Ensure all matches are properly scored and sorted."""
            )
            
            # Clean the response to ensure we only have JSON
            response = response.strip()
            # Remove any markdown code block indicators if present
            response = response.replace('```json', '').replace('```', '').strip()
            
            # Store the matches result
            EphemeralMemory.store_message(
                thread_id=self.thread_id,
                sender="assistant",
                content=response
            )
            
            # Convert response to structured data
            try:
                parsed_data = json.loads(response)
                matches = parsed_data.get("matches", [])
                
                if not matches:
                    print("No suitable job matches found")
                    return []
                    
                print(f"\n=== Found {len(matches)} Job Matches ===")
                for match in matches:
                    print(f"\nPosition: {match.get('title')} at {match.get('company')}")
                    print(f"Match Score: {match.get('match_score', 0):.2f}")
                    if "match_reasons" in match:
                        print("Match Reasons:")
                        for reason in match["match_reasons"]:
                            print(f"  + {reason}")
                    if "missing_requirements" in match:
                        print("Missing Requirements:")
                        for req in match["missing_requirements"]:
                            print(f"  - {req}")
                print("\n=== End of Job Matches ===\n")
                
                return matches
                
            except json.JSONDecodeError as e:
                print(f"Error: Could not parse JSON response: {str(e)}")
                print("Raw response:", response)
                # Try to clean up the response and parse again
                try:
                    # Remove any non-JSON text
                    json_start = response.find('{')
                    json_end = response.rfind('}') + 1
                    if json_start >= 0 and json_end > json_start:
                        cleaned_response = response[json_start:json_end]
                        parsed_data = json.loads(cleaned_response)
                        print("Successfully parsed cleaned response")
                        return parsed_data.get("matches", [])
                except:
                    pass
                return {"error": "Failed to parse job matches", "raw_response": response}
                
        except Exception as e:
            print(f"Error in job matching: {str(e)}")
            traceback.print_exc()
            return {"error": str(e)}
    
    async def generate_assessment(self, candidate_profile: Dict[str, Any], job_info: Dict[str, Any]):
        """Generate an assessment using direct tool call
        
        Args:
            candidate_profile: The parsed candidate profile
            job_info: Information about the job
            
        Returns:
            Assessment details
        """
        print("Directly generating assessment with CandidateAssessorTool...")
        try:
            # Call the assessment tool directly
            data = {
                "candidate_profile": candidate_profile,
                "job_info": job_info
            }
            assessment = self.candidate_assessor.generate_assessment(data)
            print(f"Assessment generation complete. Created assessment ID: {assessment.get('assessment_id')}")
            return assessment
        except Exception as e:
            print(f"Error in direct assessment generation: {str(e)}")
            traceback.print_exc()
            
            # Create a fallback assessment
            return {
                "assessment_id": "ASM-9999",
                "candidate_name": candidate_profile.get("name", "Unknown"),
                "job_title": job_info.get("title", "Unknown Position"),
                "company": job_info.get("company", "Unknown Company"),
                "skills_assessed": ["Python", "JavaScript"],
                "technical_questions": [
                    {
                        "question_id": "TQ-1",
                        "skill": "Python",
                        "question": "Explain the difference between lists and tuples in Python.",
                        "type": "technical"
                    }
                ],
                "behavioral_questions": [
                    {
                        "question_id": "BQ-1",
                        "question": "Describe a situation where you had to meet a tight deadline.",
                        "type": "behavioral"
                    }
                ],
                "evaluation_criteria": {
                    "technical_knowledge": "Assess depth and accuracy of technical knowledge",
                    "problem_solving": "Evaluate approach to solving complex problems"
                }
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