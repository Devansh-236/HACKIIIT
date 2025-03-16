from typing import Dict, List, Any, Optional
import json
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from moya.agents.base_agent import Agent, AgentConfig
from moya.tools.base_tool import BaseTool

class JobMatchingTool(BaseTool):
    """Tool for matching jobs with candidates using TF-IDF and cosine similarity"""
    
    name = "job_matcher"
    description = "Matches candidates with jobs based on skills and requirements"
    function = "match_jobs"
    
    def __init__(self):
        """Initialize the job matching tool"""
        super().__init__(name=self.name, function=self.function)
        self.vectorizer = TfidfVectorizer(lowercase=True, stop_words='english', 
                                         token_pattern=r'(?u)\b[a-zA-Z][a-zA-Z.+\-]+\b')
        # Default job database path
        self.job_database_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            'data', 'job_listings.json'
        )
    
    def match_jobs(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Match a candidate profile with job listings
        
        Args:
            data: A dictionary containing:
                - candidate_profile: The parsed candidate profile
                - job_listings: List of available job positions
                
        Returns:
            A list of job matches with similarity scores
        """
        candidate_profile = data.get("candidate_profile", {})
        job_listings = data.get("job_listings", [])
        
        if not candidate_profile or not job_listings:
            return {"error": "Missing candidate profile or job listings"}
            
        return self._match_jobs(candidate_profile, job_listings)
    
    def get_all_jobs(self, database_path: str = None) -> List[Dict[str, Any]]:
        """Retrieve all available jobs from the database
        
        Args:
            database_path: Optional path to the job listings JSON file.
                          If not provided, uses the default path.
                
        Returns:
            A list of all available job positions
        """
        try:
            # Use provided path or fall back to default
            file_path = database_path or self.job_database_path
            
            # Check if file exists
            if not os.path.exists(file_path):
                return {"error": f"Job database not found at: {file_path}"}
            
            # Read and parse the job listings
            with open(file_path, 'r', encoding='utf-8') as file:
                job_data = json.load(file)
                
                # Handle different possible structures
                if isinstance(job_data, list):
                    return job_data
                elif isinstance(job_data, dict) and "jobs" in job_data:
                    return job_data["jobs"]
                else:
                    return {"error": "Invalid job database format"}
                
        except json.JSONDecodeError:
            return {"error": "Job database contains invalid JSON"}
        except Exception as e:
            return {"error": f"Failed to retrieve jobs: {str(e)}"}
    
    def get_job_by_id(self, job_id: str, database_path: str = None) -> Dict[str, Any]:
        """Retrieve a specific job by ID
        
        Args:
            job_id: The unique identifier of the job
            database_path: Optional path to the job listings JSON file
                
        Returns:
            The job information if found, otherwise an error
        """
        jobs = self.get_all_jobs(database_path)
        
        # Check if we got an error
        if isinstance(jobs, dict) and "error" in jobs:
            return jobs
        
        # Find job by ID
        for job in jobs:
            if job.get("id") == job_id or job.get("job_id") == job_id:
                return job
                
        return {"error": f"Job with ID {job_id} not found"}
    
    def _match_jobs(self, candidate_profile: Dict[str, Any], job_listings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Internal method to perform job matching"""
        # Create a text representation of the candidate profile
        skills = candidate_profile.get("skills", [])
        
        # Add experience keywords from the candidate's experience
        experience_text = " ".join(str(candidate_profile.get("experience", [])))
        experience_keywords = self._extract_keywords_from_text(experience_text)
        
        # Combine skills and experience keywords
        candidate_keywords = skills + experience_keywords
        candidate_text = " ".join(candidate_keywords)
        
        if not candidate_text.strip():
            # Fallback if no skills or experience are found
            return []
        
        # Create text representations of job listings
        job_texts = []
        for job in job_listings:
            job_text = " ".join(job.get("required_skills", []))
            job_text += " " + job.get("description", "")
            job_texts.append(job_text)
        
        # Add candidate text to create the complete corpus
        all_texts = [candidate_text] + job_texts
        
        # Calculate TF-IDF vectors
        tfidf_matrix = self.vectorizer.fit_transform(all_texts)
        
        # Calculate similarity between candidate and each job
        similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])
        
        # Create ranked matches
        matches = []
        for idx, score in enumerate(similarities[0]):
            job_match = {
                **job_listings[idx],
                "match_score": float(score)
            }
            matches.append(job_match)
        
        # Sort by match score in descending order
        matches.sort(key=lambda x: x["match_score"], reverse=True)
        
        return matches
    
    def _extract_keywords_from_text(self, text: str) -> List[str]:
        """Extract important keywords from a text"""
        # Basic extraction - in a real system, this would use more sophisticated NLP
        words = text.lower().split()
        # Filter out short words and common words
        keywords = [word for word in words if len(word) > 3 and word not in ['and', 'the', 'for', 'with']]
        return keywords
    
    def filter_candidates(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Filter candidates for a job
        
        Args:
            data: A dictionary containing:
                - job_requirements: Requirements for the job
                - candidates: List of candidates to filter
                
        Returns:
            A filtered list of candidates with match scores
        """
        job_requirements = data.get("job_requirements", {})
        candidates = data.get("candidates", [])
        
        if not job_requirements or not candidates:
            return {"error": "Missing job requirements or candidates"}
            
        # Create a text representation of the job requirements
        req_skills = job_requirements.get("required_skills", [])
        req_text = " ".join(req_skills) + " " + job_requirements.get("description", "")
        
        # Create text representations of candidates
        candidate_texts = []
        for candidate in candidates:
            skills = candidate.get("skills", [])
            experience = " ".join(candidate.get("experience", []))
            candidate_texts.append(" ".join(skills) + " " + experience)
        
        # Add job text to create the complete corpus
        all_texts = [req_text] + candidate_texts
        
        # Calculate TF-IDF vectors
        tfidf_matrix = self.vectorizer.fit_transform(all_texts)
        
        # Calculate similarity between job and each candidate
        similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])
        
        # Create ranked matches
        matches = []
        for idx, score in enumerate(similarities[0]):
            candidate_match = {
                **candidates[idx],
                "match_score": float(score)
            }
            matches.append(candidate_match)
        
        # Sort by match score in descending order
        matches.sort(key=lambda x: x["match_score"], reverse=True)
        
        return matches


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
    
    async def handle_message(self, message: Dict[str, Any], **kwargs) -> List[Dict[str, Any]]:
        """Handle job matching request
        
        Args:
            message: A dictionary containing:
                - candidate_profile: The parsed candidate profile 
                - job_listings: List of available job positions
                - action: Optional action to perform ('match_jobs', 'get_all_jobs', 'get_job_by_id')
                - job_id: Required for 'get_job_by_id' action
                
        Returns:
            A list of job matches with similarity scores or job information based on the action
        """
        try:
            # Check if this is a special action request
            action = message.get("action", "match_jobs")
            
            if action == "get_all_jobs":
                # Return all available jobs
                database_path = message.get("database_path")
                return self.matcher_tool.get_all_jobs(database_path)
                
            elif action == "get_job_by_id":
                # Get a specific job by ID
                job_id = message.get("job_id")
                if not job_id:
                    return {"error": "job_id is required for get_job_by_id action"}
                
                database_path = message.get("database_path")
                return self.matcher_tool.get_job_by_id(job_id, database_path)
                
            else:
                # Default: perform job matching
                # Validate the input message
                if not isinstance(message, dict):
                    return {"error": "Message must be a dictionary"}
                    
                if "candidate_profile" not in message:
                    return {"error": "Message must contain candidate_profile"}
                    
                if "job_listings" not in message:
                    return {"error": "Message must contain job_listings"}
                
                # Perform the matching
                return self.matcher_tool.match_jobs(message)
            
        except Exception as e:
            return {"error": f"Failed to process request: {str(e)}"}
    
    async def handle_message_stream(self, message: str, **kwargs):
        """Stream is not supported for job matching"""
        yield "Streaming is not supported for job matching. Please use handle_message instead."


# Helper functions for standalone use
async def match_jobs(candidate_profile: Dict[str, Any], job_listings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Match a candidate with job listings
    
    Args:
        candidate_profile: The parsed candidate profile
        job_listings: List of available job positions
        
    Returns:
        A list of job matches with similarity scores
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

async def get_all_jobs(database_path: str = None) -> List[Dict[str, Any]]:
    """Get all available jobs from the database
    
    Args:
        database_path: Optional path to the job database
        
    Returns:
        A list of all available job positions
    """
    tool = JobMatchingTool()
    return tool.get_all_jobs(database_path)

async def get_job_by_id(job_id: str, database_path: str = None) -> Dict[str, Any]:
    """Get a specific job by ID
    
    Args:
        job_id: The unique identifier of the job
        database_path: Optional path to the job database
        
    Returns:
        The job information if found
    """
    tool = JobMatchingTool()
    return tool.get_job_by_id(job_id, database_path)