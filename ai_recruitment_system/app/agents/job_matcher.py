from typing import Dict, List, Any
from moya.agents.base_agent import Agent, AgentConfig
from moya.tools.base_tool import BaseTool
import json

class JobMatchingTool(BaseTool):
    """Tool for matching candidates with jobs using Azure OpenAI through Moya."""
    
    def __init__(self):
        self.name = "job_matcher"
        self.description = "Matches candidate profiles with job listings using AI"
        super().__init__(
            name=self.name,
            description=self.description,
            function=self.match_jobs,
            parameters={
                "candidate_profile": {
                    "type": "object",
                    "description": "The parsed candidate profile"
                },
                "job_listings": {
                    "type": "array",
                    "description": "List of available job positions"
                }
            },
            required=["candidate_profile", "job_listings"]
        )
        
    def match_jobs(self, candidate_profile: Dict[str, Any], job_listings: List[Dict[str, Any]]) -> str:
        """
        Create a prompt for matching jobs using Azure OpenAI through Moya.
        
        Args:
            candidate_profile: The parsed candidate profile
            job_listings: List of available job positions
            
        Returns:
            Prompt for the AI model
        """
        # Print extracted data
        print("\n=== Extracted Candidate Data ===")
        print("Education:")
        if "education" in candidate_profile:
            for edu in candidate_profile["education"]:
                print(f"- {edu.get('degree', 'N/A')} from {edu.get('institution', 'N/A')} ({edu.get('year', 'N/A')})")
        else:
            print("No education data found")

        print("\nExperience:")
        if "experience" in candidate_profile:
            for exp in candidate_profile["experience"]:
                print(f"- {exp.get('title', 'N/A')} at {exp.get('company', 'N/A')}")
                print(f"  Duration: {exp.get('duration', 'N/A')}")
                if "responsibilities" in exp:
                    print("  Key responsibilities:")
                    for resp in exp["responsibilities"]:
                        print(f"    * {resp}")
        else:
            print("No experience data found")

        print("\nSkills:")
        if "skills" in candidate_profile:
            for skill in candidate_profile["skills"]:
                print(f"- {skill}")
        else:
            print("No skills data found")
        print("\n=== End of Extracted Data ===\n")
        
        # Prepare the prompt for the AI model
        prompt = f"""You are an expert job matcher. Your task is to match a candidate with suitable job positions.

INSTRUCTIONS:
1. Analyze the candidate profile carefully
2. Compare candidate's skills and experience with job requirements
3. Calculate match scores based on:
   - Required skills match (highest weight)
   - Preferred skills match
   - Experience level alignment
   - Education requirements
   - Domain/industry alignment
4. Return matches in valid JSON format
5. Score range: 0.0 (no match) to 1.0 (perfect match)

CANDIDATE PROFILE:
{json.dumps(candidate_profile, indent=2)}

JOB LISTINGS:
{json.dumps(job_listings, indent=2)}

REQUIRED OUTPUT FORMAT:
{{
    "matches": [
        {{
            "job_id": "ID of the job",
            "title": "job title",
            "company": "company name",
            "match_score": 0.XX,
            "match_reasons": [
                "Reason 1 for match",
                "Reason 2 for match"
            ],
            "missing_requirements": [
                "Missing requirement 1",
                "Missing requirement 2"
            ]
        }}
    ]
}}

IMPORTANT:
- Sort matches by match_score in descending order
- Include only jobs with match_score > 0.3
- Provide specific reasons for each match
- List any missing critical requirements
- Return valid JSON only
- Maximum 5 best matches
- Focus on skills alignment and experience relevance
- Consider both technical and soft skills
- Account for years of experience in the field

Please analyze and return the job matches:"""
        
        return prompt


class JobMatchingAgent(Agent):
    """Agent for matching jobs with candidates"""
    
    def __init__(self, config: AgentConfig = None):
        """Initialize the job matching agent"""
        if config is None:
            config = AgentConfig(
                agent_name="job_matcher",
                agent_type="job_matcher",
                description="Matches candidates with suitable job positions",
                system_prompt="You are a job matching assistant that helps find the best job matches for candidates."
            )
        super().__init__(config)
        self.matcher_tool = JobMatchingTool()
    
    async def handle_message(self, message: Dict[str, Any], **kwargs) -> str:
        """Handle job matching request
        
        Args:
            message: Dictionary containing candidate_profile and job_listings
                
        Returns:
            Prompt for the AI model to process
        """
        try:
            # Extract required arguments from message dictionary
            candidate_profile = message.get("candidate_profile")
            job_listings = message.get("job_listings")
            
            if not candidate_profile or not job_listings:
                raise ValueError("Missing required fields: candidate_profile and job_listings must be provided")
                
            return self.matcher_tool.match_jobs(
                candidate_profile=candidate_profile,
                job_listings=job_listings
            )
        except Exception as e:
            return {"error": f"Failed to create job matching prompt: {str(e)}"}
    
    async def handle_message_stream(self, message: str, **kwargs):
        """Stream is not supported for job matching"""
        yield "Streaming is not supported for job matching. Please use handle_message instead."


# Helper function for standalone use
async def match_jobs(candidate_profile: Dict[str, Any], job_listings: List[Dict[str, Any]]) -> str:
    """Create a job matching prompt
    
    Args:
        candidate_profile: The parsed candidate profile
        job_listings: List of available job positions
        
    Returns:
        Prompt for the AI model to process
    """
    config = AgentConfig(
        agent_name="job_matcher",
        agent_type="job_matcher",
        description="Matches candidates with suitable job positions",
        system_prompt="You are a job matching assistant that helps find the best job matches for candidates."
    )
    agent = JobMatchingAgent(config)
    
    return await agent.handle_message({
        "candidate_profile": candidate_profile,
        "job_listings": job_listings
    })
