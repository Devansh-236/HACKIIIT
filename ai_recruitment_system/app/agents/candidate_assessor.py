from typing import Dict, List, Any
import json
import random

class CandidateAssessorAgent:
    def __init__(self):
        # In a real system, these would be loaded from a database
        self.coding_challenges = {
            "python": [
                {
                    "id": "py_001",
                    "title": "Array Sum",
                    "difficulty": "easy",
                    "description": "Write a function that returns the sum of an array of integers",
                    "test_cases": [
                        {"input": [1, 2, 3, 4, 5], "expected": 15},
                        {"input": [-1, -2, 0, 1], "expected": -2}
                    ]
                }
                # Add more challenges here
            ],
            "javascript": [
                {
                    "id": "js_001",
                    "title": "String Reverse",
                    "difficulty": "easy",
                    "description": "Write a function that reverses a string",
                    "test_cases": [
                        {"input": "hello", "expected": "olleh"},
                        {"input": "world", "expected": "dlrow"}
                    ]
                }
                # Add more challenges here
            ]
        }
    
    async def generate_assessment(self, candidate_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a technical assessment based on candidate's profile.
        
        Args:
            candidate_profile (Dict[str, Any]): Candidate's profile including skills
            
        Returns:
            Dict[str, Any]: Assessment details including questions and tests
        """
        assessment = {
            "id": f"ASS_{int(random.random() * 1000000)}",
            "candidate_id": candidate_profile.get("id"),
            "sections": []
        }
        
        # Add coding challenges based on candidate's skills
        for skill in candidate_profile.get("skills", []):
            if skill.lower() in self.coding_challenges:
                challenges = self.coding_challenges[skill.lower()]
                if challenges:
                    assessment["sections"].append({
                        "type": "coding",
                        "skill": skill,
                        "challenges": random.sample(challenges, min(2, len(challenges)))
                    })
        
        # Add technical questions (mock implementation)
        assessment["sections"].append({
            "type": "multiple_choice",
            "questions": self._generate_technical_questions(candidate_profile)
        })
        
        return assessment
    
    async def evaluate_submission(self, assessment_id: str, submission: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate a candidate's assessment submission.
        
        Args:
            assessment_id (str): ID of the assessment
            submission (Dict[str, Any]): Candidate's submitted answers and code
            
        Returns:
            Dict[str, Any]: Evaluation results with scores and feedback
        """
        evaluation = {
            "assessment_id": assessment_id,
            "submission_id": f"SUB_{int(random.random() * 1000000)}",
            "sections": []
        }
        
        # Evaluate coding challenges
        for section in submission.get("sections", []):
            if section["type"] == "coding":
                evaluation["sections"].append(
                    self._evaluate_coding_submission(section)
                )
            elif section["type"] == "multiple_choice":
                evaluation["sections"].append(
                    self._evaluate_multiple_choice(section)
                )
        
        # Calculate overall score
        total_score = sum(section.get("score", 0) for section in evaluation["sections"])
        total_possible = len(evaluation["sections"]) * 100
        evaluation["overall_score"] = (total_score / total_possible) * 100 if total_possible > 0 else 0
        
        return evaluation
    
    def _generate_technical_questions(self, candidate_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate technical multiple choice questions based on candidate's profile"""
        # Mock implementation - in reality, would pull from a question bank
        return [
            {
                "id": "q1",
                "question": "What is the time complexity of quicksort in the average case?",
                "options": ["O(n)", "O(n log n)", "O(n^2)", "O(log n)"],
                "correct_answer": 1  # Index of correct option
            },
            {
                "id": "q2",
                "question": "Which HTTP method is idempotent?",
                "options": ["POST", "GET", "PATCH", "DELETE"],
                "correct_answer": 1  # Index of correct option
            }
        ]
    
    def _evaluate_coding_submission(self, submission: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a coding challenge submission"""
        # Mock implementation - in reality, would run tests in a sandbox
        return {
            "type": "coding",
            "challenge_id": submission.get("challenge_id"),
            "score": random.randint(60, 100),  # Mock score
            "feedback": "Good solution, but could be optimized for space complexity",
            "test_results": [
                {"test_case": 1, "passed": True, "output": "Expected output matched"},
                {"test_case": 2, "passed": True, "output": "Expected output matched"}
            ]
        }
    
    def _evaluate_multiple_choice(self, submission: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate multiple choice questions"""
        # Mock implementation
        return {
            "type": "multiple_choice",
            "score": random.randint(70, 100),  # Mock score
            "correct_answers": 4,
            "total_questions": 5
        } 