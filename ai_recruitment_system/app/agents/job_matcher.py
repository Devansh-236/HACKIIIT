from typing import Dict, List, Any, Optional
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
                
        Returns:
            A list of job matches with similarity scores
        """
        try:
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
            return {"error": f"Failed to match jobs: {str(e)}"}
    
    async def handle_message_stream(self, message: str, **kwargs):
        """Stream is not supported for job matching"""
        yield "Streaming is not supported for job matching. Please use handle_message instead."


# Helper function for standalone use
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
