import asyncio
from datetime import datetime, timedelta
from app.main import create_app

async def main():
    """Example usage of the AI Recruitment System"""
    
    # Create the recruitment system
    recruitment_system = create_app()
    
    # Example resume text
    resume_text = """
    John Doe
    Email: john.doe@example.com
    Phone: (555) 123-4567

    SKILLS
    - Python programming
    - Machine Learning
    - React.js
    - SQL
    - Docker

    EXPERIENCE
    Senior Software Engineer at Tech Corp (2018-Present)
    - Led development of machine learning pipeline
    - Managed team of 5 developers

    Software Developer at StartUp Inc (2015-2018)
    - Full-stack development using React and Node.js
    - Implemented CI/CD pipeline

    EDUCATION
    Master of Science in Computer Science
    Stanford University (2013-2015)

    Bachelor of Engineering in Software Engineering
    MIT (2009-2013)
    """
    
    # Example job listings
    job_listings = [
        {
            "id": "job1",
            "title": "Senior ML Engineer",
            "required_skills": ["python", "machine learning", "docker"],
            "description": "Looking for an experienced ML engineer to lead our AI initiatives."
        },
        {
            "id": "job2",
            "title": "Full Stack Developer",
            "required_skills": ["react", "node.js", "sql"],
            "description": "Full stack role focusing on our web applications."
        },
        {
            "id": "job3",
            "title": "DevOps Engineer",
            "required_skills": ["docker", "kubernetes", "ci/cd"],
            "description": "Help us build and maintain our cloud infrastructure."
        }
    ]
    
    try:
        print("1. Processing Application...")
        result = await recruitment_system.process_application(resume_text, job_listings)
        
        print("\nCandidate Profile:")
        print(f"Name: {result['candidate_profile']['name']}")
        print(f"Skills: {', '.join(result['candidate_profile']['skills'])}")
        print(f"Status: {result['status']}")
        
        print("\nJob Matches:")
        for job in result["job_matches"]:
            print(f"- {job['title']}: {job['match_score']:.2%} match")
        
        if result["assessment"]:
            print("\n2. Evaluating Assessment...")
            # Mock assessment submission
            submission = {
                "sections": [
                    {
                        "type": "coding",
                        "challenge_id": "py_001",
                        "solution": "def array_sum(arr): return sum(arr)"
                    },
                    {
                        "type": "multiple_choice",
                        "answers": [1, 1]  # Correct answers for both questions
                    }
                ]
            }
            
            evaluation = await recruitment_system.evaluate_candidate(
                candidate_id="candidate1",
                assessment_id=result["assessment"]["id"],
                submission=submission
            )
            
            print(f"Assessment Score: {evaluation['evaluation']['overall_score']}%")
            print(f"Status: {evaluation['status']}")
            
            if evaluation["next_steps"]:
                print("\n3. Scheduling Interview...")
                # Get first available slot
                available_slots = evaluation["next_steps"][0]["available_slots"]
                if available_slots:
                    # Schedule interview for first available slot
                    interview = await recruitment_system.schedule_candidate_interview(
                        candidate_id="candidate1",
                        interviewer_id="interviewer1",
                        slot=available_slots[0]
                    )
                    
                    print("Interview Scheduled!")
                    print(f"Date: {interview['start_time']}")
                    print(f"Meeting Link: {interview['meeting_link']}")
    
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 