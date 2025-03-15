from typing import Dict, Any, Optional, List
from datetime import datetime
from .agents.resume_parser import ResumeParserAgent
from .agents.job_matcher import JobMatchingAgent
from .agents.interview_scheduler import InterviewSchedulerAgent
from .agents.candidate_assessor import CandidateAssessorAgent
from moya.agents.base_agent import AgentConfig
import asyncio
import os

class RecruitmentError(Exception):
    """Base exception for recruitment system errors"""
    pass

class RecruitmentSystem:
    def __init__(self):
        self.resume_parser = ResumeParserAgent()
        self.job_matcher = JobMatchingAgent()
        self.interview_scheduler = InterviewSchedulerAgent()
        self.candidate_assessor = CandidateAssessorAgent()
    
    async def process_application(self, resume_text: str, job_listings: list) -> Dict[str, Any]:
        """
        Process a complete job application.
        
        Args:
            resume_text (str): The text content of the resume
            job_listings (list): Available job positions
            
        Returns:
            Dict[str, Any]: Processing results including matches and next steps
            
        Raises:
            RecruitmentError: If there's an error processing the application
        """
        try:
            if not resume_text or not job_listings:
                raise RecruitmentError("Resume text and job listings cannot be empty")
            
            # Step 1: Parse resume
            candidate_profile = await self.resume_parser.extract_resume_data(resume_text)
            if not candidate_profile.get("skills"):
                return {
                    "candidate_profile": candidate_profile,
                    "status": "no_skills_found",
                    "message": "No relevant skills found in the resume"
                }
            
            # Step 2: Match with jobs
            job_matches = await self.job_matcher.match_jobs(candidate_profile, job_listings)
            
            # Step 3: Generate assessment if there are good matches
            assessment = None
            if job_matches and job_matches[0]["match_score"] > 0.6:  # Threshold for good match
                assessment = await self.candidate_assessor.generate_assessment(candidate_profile)
            
            return {
                "candidate_profile": candidate_profile,
                "job_matches": job_matches,
                "assessment": assessment,
                "status": "pending_assessment" if assessment else "no_suitable_matches"
            }
            
        except Exception as e:
            raise RecruitmentError(f"Error processing application: {str(e)}")
    
    async def evaluate_candidate(self, candidate_id: str, assessment_id: str, 
                               submission: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate a candidate's assessment submission.
        
        Args:
            candidate_id (str): ID of the candidate
            assessment_id (str): ID of the assessment
            submission (Dict[str, Any]): Candidate's assessment submission
            
        Returns:
            Dict[str, Any]: Evaluation results and next steps
            
        Raises:
            RecruitmentError: If there's an error evaluating the candidate
        """
        try:
            if not candidate_id or not assessment_id or not submission:
                raise RecruitmentError("Missing required parameters for evaluation")
            
            # Evaluate the submission
            evaluation = await self.candidate_assessor.evaluate_submission(assessment_id, submission)
            
            # Determine next steps based on score
            next_steps = []
            if evaluation["overall_score"] >= 70:  # Passing score threshold
                # Find available interview slots
                available_slots = await self.interview_scheduler.find_available_slots(
                    interviewer_id=self._get_suitable_interviewer(evaluation),
                    date=datetime.now()
                )
                
                if available_slots:
                    next_steps.append({
                        "type": "schedule_interview",
                        "available_slots": available_slots
                    })
            
            return {
                "evaluation": evaluation,
                "next_steps": next_steps,
                "status": "passed" if evaluation["overall_score"] >= 70 else "failed"
            }
            
        except Exception as e:
            raise RecruitmentError(f"Error evaluating candidate: {str(e)}")
    
    async def schedule_candidate_interview(self, candidate_id: str, interviewer_id: str, 
                                        slot: datetime) -> Dict[str, Any]:
        """
        Schedule an interview for a candidate.
        
        Args:
            candidate_id (str): ID of the candidate
            interviewer_id (str): ID of the interviewer
            slot (datetime): Selected interview slot
            
        Returns:
            Dict[str, Any]: Interview details
            
        Raises:
            RecruitmentError: If there's an error scheduling the interview
        """
        try:
            if not candidate_id or not interviewer_id or not slot:
                raise RecruitmentError("Missing required parameters for interview scheduling")
            
            # Validate the slot is in the future
            if slot < datetime.now():
                raise RecruitmentError("Cannot schedule interview in the past")
            
            return await self.interview_scheduler.schedule_interview(
                candidate_id=candidate_id,
                interviewer_id=interviewer_id,
                slot=slot
            )
            
        except Exception as e:
            raise RecruitmentError(f"Error scheduling interview: {str(e)}")
    
    def _get_suitable_interviewer(self, evaluation: Dict[str, Any]) -> str:
        """Helper method to determine suitable interviewer based on evaluation"""
        # In a real system, this would use logic to match interviewer expertise with candidate skills
        return "default_interviewer"

def create_app() -> RecruitmentSystem:
    """Create and return the recruitment system instance"""
    return RecruitmentSystem()

async def process_candidate(resume_text: str, job_listings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Process a candidate's resume and find matching jobs"""
    
    # Initialize agents
    parser_config = AgentConfig(
        agent_name="resume_parser",
        agent_type="resume_parser",
        description="Extracts and analyzes information from resumes"
    )
    parser_agent = ResumeParserAgent(parser_config)
    
    matcher_config = AgentConfig(
        agent_name="job_matcher",
        agent_type="job_matcher",
        description="Matches candidates with suitable job positions"
    )
    matcher_agent = JobMatchingAgent(matcher_config)
    
    # Parse resume
    parsed_resume = await parser_agent.handle_message(resume_text)
    if "error" in parsed_resume:
        return parsed_resume
    
    # Find matching jobs
    matches = await matcher_agent.handle_message({
        "candidate_profile": parsed_resume,
        "job_listings": job_listings
    })
    
    return {
        "candidate_profile": parsed_resume,
        "job_matches": matches
    }

async def main():
    # Sample job listings
    sample_jobs = [
        {
            "title": "Senior AI Engineer",
            "company": "AI Solutions Inc",
            "required_skills": ["python", "machine learning", "ai", "deep learning"],
            "description": "Looking for an experienced AI engineer to lead ML projects"
        },
        {
            "title": "Full Stack Developer",
            "company": "Web Tech Co",
            "required_skills": ["javascript", "typescript", "react", "node.js"],
            "description": "Seeking a full-stack developer with React and Node.js experience"
        },
        {
            "title": "DevOps Engineer",
            "company": "Cloud Systems",
            "required_skills": ["docker", "kubernetes", "aws", "ci/cd"],
            "description": "Need a DevOps engineer to manage cloud infrastructure"
        }
    ]
    
    # Get resume file path
    resume_path = input("Enter the path of the resume file: ").strip()
    
    if not os.path.exists(resume_path):
        print(f"Error: File not found at {resume_path}")
        return
        
    try:
        # Read resume file
        with open(resume_path, 'r', encoding='utf-8') as f:
            resume_text = f.read()
            
        # Process the candidate
        result = await process_candidate(resume_text, sample_jobs)
        
        if "error" in result:
            print(f"\nError: {result['error']}")
            return
            
        # Print parsed resume information
        print("\nParsed Resume Information:")
        print("=========================")
        print(f"Name: {result['candidate_profile']['name']}")
        
        print("\nContact Information:")
        for key, value in result['candidate_profile']['contact_info'].items():
            if value:
                print(f"{key.title()}: {value}")
        
        print("\nSkills:")
        for skill in result['candidate_profile']['skills']:
            print(f"- {skill}")
        
        print("\nEducation:")
        if result['candidate_profile']['education']:
            for edu in result['candidate_profile']['education']:
                print(f"- {edu}")
        else:
            print("No education information found")
        
        print("\nExperience:")
        if result['candidate_profile']['experience']:
            for exp in result['candidate_profile']['experience']:
                print(f"- {exp}")
        else:
            print("No experience information found")
        
        # Print job matches
        print("\nMatching Jobs:")
        print("==============")
        if isinstance(result['job_matches'], list):
            for job in result['job_matches']:
                if isinstance(job, dict) and "error" not in job:
                    print(f"\nTitle: {job['title']}")
                    print(f"Company: {job['company']}")
                    print(f"Match Score: {job['match_score']:.2f}")
                    print(f"Required Skills: {', '.join(job['required_skills'])}")
                    print(f"Description: {job['description']}")
        else:
            print("No matching jobs found or error in matching process")
            
    except Exception as e:
        print(f"Error processing resume: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 