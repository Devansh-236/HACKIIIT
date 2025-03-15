from typing import Dict, List, Any, Optional
import datetime
import random
from moya.agents.base_agent import Agent, AgentConfig
from moya.tools.base_tool import BaseTool

class CandidateAssessorTool(BaseTool):
    """Tool for assessing candidates and generating interview questions"""
    
    name = "candidate_assessor"
    description = "Assesses candidate qualifications and generates assessments"
    function = "generate_assessment"
    
    def __init__(self):
        """Initialize the candidate assessor tool"""
        super().__init__(name=self.name, function=self.function)
        
    def generate_assessment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate an assessment for a candidate based on their profile and the job
        
        Args:
            data: Dictionary containing:
                - candidate_profile: Information about the candidate
                - job_info: Information about the job
                
        Returns:
            Assessment details including questions and evaluation criteria
        """
        candidate_profile = data.get("candidate_profile", {})
        job_info = data.get("job_info", {})
        
        # Validate required fields
        if not candidate_profile:
            return {"error": "Candidate profile is required"}
        
        if not job_info:
            return {"error": "Job information is required"}
        
        # Extract skills to assess
        candidate_skills = set(candidate_profile.get("skills", []))
        required_skills = set(job_info.get("required_skills", []))
        preferred_skills = set(job_info.get("preferred_skills", []))
        
        # Determine skills to test (skills the candidate claims to have that are required/preferred)
        skills_to_test = list((candidate_skills & (required_skills | preferred_skills)))
        
        # Generate technical questions based on overlapping skills
        technical_questions = self._generate_technical_questions(skills_to_test)
        
        # Generate behavioral questions based on job description
        behavioral_questions = self._generate_behavioral_questions(job_info.get("title", ""))
        
        # Generate coding challenge if appropriate for the role
        coding_challenge = None
        if any(skill in candidate_skills for skill in ["python", "java", "javascript", "c++", "ruby"]):
            coding_challenge = self._generate_coding_challenge(candidate_skills)
        
        # Create assessment ID
        assessment_id = f"ASM-{random.randint(1000, 9999)}"
        
        # Prepare assessment package
        assessment = {
            "assessment_id": assessment_id,
            "candidate_name": candidate_profile.get("name"),
            "job_title": job_info.get("title"),
            "company": job_info.get("company"),
            "skills_assessed": skills_to_test,
            "technical_questions": technical_questions,
            "behavioral_questions": behavioral_questions,
            "coding_challenge": coding_challenge,
            "evaluation_criteria": {
                "technical_knowledge": "Assess depth and accuracy of technical knowledge",
                "problem_solving": "Evaluate approach to solving complex problems",
                "communication": "Clarity and effectiveness of communication",
                "cultural_fit": "Alignment with company values and culture",
                "experience": "Relevance and depth of prior experience"
            },
            "scoring_guide": {
                "1": "Does not meet expectations",
                "2": "Partially meets expectations",
                "3": "Meets expectations",
                "4": "Exceeds expectations",
                "5": "Significantly exceeds expectations"
            },
            "passing_threshold": 70,
            "created_at": datetime.datetime.now().isoformat()
        }
        
        return assessment
    
    def evaluate_submission(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a candidate's assessment submission
        
        Args:
            data: Dictionary containing:
                - assessment_id: ID of the assessment
                - submission: Candidate's answers and solutions
                - evaluator_notes: Notes from the evaluator
                
        Returns:
            Evaluation results with scores and feedback
        """
        assessment_id = data.get("assessment_id")
        submission = data.get("submission", {})
        evaluator_notes = data.get("evaluator_notes", {})
        
        # Validate required fields
        if not assessment_id:
            return {"error": "Assessment ID is required"}
        
        if not submission:
            return {"error": "Submission data is required"}
        
        # In a real system, this would retrieve the original assessment and perform
        # a detailed evaluation. For this demo, we'll generate a mock evaluation.
        
        # Generate scores for different areas (mocked for demo)
        scores = {
            "technical_knowledge": random.randint(65, 95),
            "problem_solving": random.randint(65, 95),
            "communication": random.randint(65, 95),
            "cultural_fit": random.randint(65, 95),
            "experience": random.randint(65, 95)
        }
        
        # Calculate overall score (weighted average)
        weights = {
            "technical_knowledge": 0.3,
            "problem_solving": 0.3,
            "communication": 0.15,
            "cultural_fit": 0.15,
            "experience": 0.1
        }
        
        overall_score = sum(scores[area] * weights[area] for area in scores)
        
        # Generate feedback based on scores
        feedback = {}
        for area, score in scores.items():
            if score >= 90:
                feedback[area] = "Exceptional performance in this area."
            elif score >= 80:
                feedback[area] = "Strong performance in this area."
            elif score >= 70:
                feedback[area] = "Satisfactory performance in this area."
            else:
                feedback[area] = "Needs improvement in this area."
        
        # Determine if candidate passed
        passed = overall_score >= 70
        
        # Create evaluation result
        evaluation = {
            "assessment_id": assessment_id,
            "scores": scores,
            "overall_score": round(overall_score, 1),
            "feedback": feedback,
            "evaluator_notes": evaluator_notes,
            "status": "passed" if passed else "failed",
            "recommendation": self._generate_recommendation(overall_score),
            "next_steps": self._generate_next_steps(passed),
            "evaluated_at": datetime.datetime.now().isoformat()
        }
        
        return evaluation
    
    def _generate_technical_questions(self, skills: List[str]) -> List[Dict[str, Any]]:
        """Generate technical questions based on the candidate's skills"""
        questions = []
        
        # Question bank by skill (simplified for demo)
        question_bank = {
            "python": [
                "Explain the difference between lists and tuples in Python.",
                "How would you handle exceptions in Python?",
                "Describe Python's memory management approach."
            ],
            "javascript": [
                "Explain closures in JavaScript.",
                "What's the difference between '==' and '===' in JavaScript?",
                "How does event delegation work in JavaScript?"
            ],
            "machine learning": [
                "Explain the difference between supervised and unsupervised learning.",
                "How would you handle imbalanced data in a classification problem?",
                "Describe the tradeoff between bias and variance."
            ],
            "react": [
                "Explain the virtual DOM in React.",
                "What are React hooks and how are they useful?",
                "Describe the component lifecycle in React."
            ],
            "aws": [
                "What AWS services would you use for a serverless architecture?",
                "Explain the difference between EC2 and Lambda.",
                "How would you design a scalable architecture in AWS?"
            ],
            "sql": [
                "Explain the difference between INNER and LEFT JOIN.",
                "How would you optimize a slow SQL query?",
                "Describe normalization and when you might want to denormalize."
            ]
        }
        
        # Select questions based on skills
        for skill in skills:
            if skill in question_bank:
                # Add questions for this skill (up to 2)
                skill_questions = random.sample(question_bank[skill], min(2, len(question_bank[skill])))
                for question in skill_questions:
                    questions.append({
                        "question_id": f"TQ-{len(questions)+1}",
                        "skill": skill,
                        "question": question,
                        "type": "technical"
                    })
        
        # If we don't have enough questions, add generic ones
        generic_questions = [
            "Describe your approach to debugging a complex problem.",
            "How do you stay updated with the latest technologies?",
            "Describe a technically challenging project you worked on."
        ]
        
        while len(questions) < 5 and generic_questions:
            question = generic_questions.pop(0)
            questions.append({
                "question_id": f"TQ-{len(questions)+1}",
                "skill": "general",
                "question": question,
                "type": "technical"
            })
        
        return questions[:8]  # Limit to 8 questions
    
    def _generate_behavioral_questions(self, job_title: str) -> List[Dict[str, Any]]:
        """Generate behavioral questions based on the job title"""
        # Base set of behavioral questions
        questions = [
            "Describe a situation where you had to meet a tight deadline.",
            "Tell me about a time when you had to work with a difficult team member.",
            "Describe a project that failed and what you learned from it.",
            "Tell me about a time when you took initiative on a project.",
            "Describe how you handled a situation with competing priorities."
        ]
        
        # Add role-specific questions
        if "lead" in job_title.lower() or "senior" in job_title.lower() or "manager" in job_title.lower():
            leadership_questions = [
                "Describe your leadership style and how you motivate your team.",
                "Tell me about a time when you had to make a difficult decision as a leader.",
                "How do you delegate tasks within your team?"
            ]
            questions.extend(leadership_questions[:2])
        
        # Format the questions
        formatted_questions = []
        for i, question in enumerate(questions[:5]):  # Limit to 5 questions
            formatted_questions.append({
                "question_id": f"BQ-{i+1}",
                "question": question,
                "type": "behavioral"
            })
        
        return formatted_questions
    
    def _generate_coding_challenge(self, skills: List[str]) -> Dict[str, Any]:
        """Generate a coding challenge appropriate for the candidate's skills"""
        # Determine programming language based on skills
        language = "python"  # Default
        for skill in skills:
            if skill in ["javascript", "typescript", "react", "node.js"]:
                language = "javascript"
                break
            elif skill in ["java", "spring"]:
                language = "java"
                break
        
        # Challenge bank by language
        challenges = {
            "python": {
                "title": "Data Analysis Pipeline",
                "description": "Create a data processing pipeline that reads input from a CSV file, performs basic analysis (mean, median, mode), and outputs results to a JSON file.",
                "requirements": [
                    "Read data from the provided CSV file",
                    "Calculate statistics on the numeric columns",
                    "Handle missing values appropriately",
                    "Output results in JSON format"
                ],
                "time_limit": "1 hour",
                "language": "python"
            },
            "javascript": {
                "title": "Interactive Dashboard Component",
                "description": "Create a React component for a dashboard that displays data from an API and allows users to filter and sort the results.",
                "requirements": [
                    "Fetch data from the provided API endpoint",
                    "Display the data in a table or card layout",
                    "Implement filtering and sorting functionality",
                    "Handle loading and error states"
                ],
                "time_limit": "1 hour",
                "language": "javascript"
            },
            "java": {
                "title": "RESTful API Service",
                "description": "Implement a simple RESTful API service for a task management system using Spring Boot.",
                "requirements": [
                    "Create endpoints for CRUD operations on tasks",
                    "Implement proper error handling",
                    "Add basic authentication",
                    "Include unit tests for your API"
                ],
                "time_limit": "1 hour",
                "language": "java"
            }
        }
        
        return challenges.get(language, challenges["python"])
    
    def _generate_recommendation(self, score: float) -> str:
        """Generate a recommendation based on the candidate's score"""
        if score >= 90:
            return "Strongly recommend proceeding to final interview."
        elif score >= 80:
            return "Recommend proceeding to next interview stage."
        elif score >= 70:
            return "Conditionally recommend - proceed if other candidates are not stronger."
        else:
            return "Do not recommend proceeding with this candidate at this time."
    
    def _generate_next_steps(self, passed: bool) -> List[str]:
        """Generate next steps based on whether the candidate passed"""
        if passed:
            return [
                "Schedule technical interview with the hiring team",
                "Send coding exercise results to the team for review",
                "Prepare interview questions based on assessment results"
            ]
        else:
            return [
                "Send rejection email with constructive feedback",
                "Keep resume on file for future opportunities",
                "Suggest additional learning resources if appropriate"
            ]


class CandidateAssessorAgent(Agent):
    """Agent for assessing candidates and generating interview materials"""
    
    def __init__(self, config: AgentConfig = None):
        """Initialize the candidate assessor agent"""
        if config is None:
            config = AgentConfig(
                agent_name="candidate_assessor",
                agent_type="candidate_assessor",
                description="Assesses candidate qualifications and generates interview materials",
                system_prompt="You are a candidate assessment assistant that helps evaluate job applicants and prepare interview materials."
            )
        super().__init__(config)
        self.assessor_tool = CandidateAssessorTool()
    
    async def handle_message(self, message: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Handle candidate assessment requests
        
        Args:
            message: Dictionary containing assessment request details
                
        Returns:
            Assessment or evaluation results
        """
        try:
            # Validate the input message
            if not isinstance(message, dict):
                return {"error": "Message must be a dictionary"}
            
            action = message.get("action", "generate")
            
            if action == "generate":
                # Generate an assessment
                if "candidate_profile" not in message:
                    return {"error": "Message must contain candidate_profile"}
                    
                if "job_info" not in message:
                    return {"error": "Message must contain job_info"}
                
                return self.assessor_tool.generate_assessment(message)
                
            elif action == "evaluate":
                # Evaluate a submission
                if "assessment_id" not in message:
                    return {"error": "Message must contain assessment_id"}
                    
                if "submission" not in message:
                    return {"error": "Message must contain submission"}
                
                return self.assessor_tool.evaluate_submission(message)
                
            else:
                return {"error": f"Unknown action: {action}"}
                
        except Exception as e:
            return {"error": f"Failed to process assessment request: {str(e)}"}
    
    async def handle_message_stream(self, message: str, **kwargs):
        """Stream is not supported for candidate assessment"""
        yield "Streaming is not supported for candidate assessment. Please use handle_message instead."


# Helper function for standalone use
async def generate_assessment(candidate_profile: Dict[str, Any], job_info: Dict[str, Any]) -> Dict[str, Any]:
    """Generate an assessment for a candidate
    
    Args:
        candidate_profile: Information about the candidate
        job_info: Information about the job
        
    Returns:
        Assessment details including questions and evaluation criteria
    """
    config = AgentConfig(
        agent_name="candidate_assessor",
        agent_type="candidate_assessor",
        description="Assesses candidate qualifications and generates interview materials",
        system_prompt="You are a candidate assessment assistant that helps evaluate job applicants and prepare interview materials."
    )
    agent = CandidateAssessorAgent(config)
    
    return await agent.handle_message({
        "action": "generate",
        "candidate_profile": candidate_profile,
        "job_info": job_info
    })


async def evaluate_submission(assessment_id: str, submission: Dict[str, Any], 
                           evaluator_notes: Dict[str, Any] = None) -> Dict[str, Any]:
    """Evaluate a candidate's assessment submission
    
    Args:
        assessment_id: ID of the assessment
        submission: Candidate's answers and solutions
        evaluator_notes: Notes from the evaluator (optional)
        
    Returns:
        Evaluation results with scores and feedback
    """
    config = AgentConfig(
        agent_name="candidate_assessor",
        agent_type="candidate_assessor",
        description="Assesses candidate qualifications and generates interview materials",
        system_prompt="You are a candidate assessment assistant that helps evaluate job applicants and prepare interview materials."
    )
    agent = CandidateAssessorAgent(config)
    
    return await agent.handle_message({
        "action": "evaluate",
        "assessment_id": assessment_id,
        "submission": submission,
        "evaluator_notes": evaluator_notes or {}
    }) 