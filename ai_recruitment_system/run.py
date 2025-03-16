#!/usr/bin/env python3
import asyncio
import os
import sys
import json
import traceback
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the new orchestrator
from app.orchestrator import RecruitmentOrchestrator

# Update the parse_resume function to better handle resume parsing results
async def parse_resume(file_path, orchestrator):
    """Parse a resume file and extract structured information using the orchestrator"""
    print(f"\n=== PARSING RESUME: {file_path} ===")
    
    # Check if file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Resume file not found: {file_path}")
    
    # Read the file content
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            file_size = os.path.getsize(file_path)
            
            print(f"Successfully read file ({file_size} bytes)")
            preview = content[:150] + "..." if len(content) > 150 else content
            print(f"Content preview: {preview}\n")
            
            # Parse the resume using the orchestrator
            parsed_data = await orchestrator.process_resume(content)
            
            # Check if we got valid data
            if not parsed_data or not isinstance(parsed_data, dict):
                print("\nError: Failed to parse resume properly")
                return None
                
            # If we have a raw_response, it might be worth checking
            if "raw_response" in parsed_data:
                print("\nNote: Got raw response from parser, attempting to extract structured data")
                # You could add additional parsing here if needed
            
            print("\n=== EXTRACTED INFORMATION ===")
            name = parsed_data.get('name', 'Not found')
            print(f"Name: {name}")
            
            # Handle contact information properly
            contact_info = parsed_data.get('contact_info', {})
            if not isinstance(contact_info, dict):
                contact_info = {}
                
            email = contact_info.get('email', 'Not found')
            phone = contact_info.get('phone', 'Not found')
            print(f"Email: {email}")
            print(f"Phone: {phone}")
            
            # Handle skills properly
            skills = parsed_data.get('skills', [])
            if not isinstance(skills, list):
                skills = []
            skills_str = ', '.join(skills) if skills else 'Not found'
            print(f"Skills: {skills_str}")
            
            # Handle education properly
            education = parsed_data.get('education', [])
            if not isinstance(education, list):
                education = [str(education)] if education else ['Not found']
            
            # Handle experience properly
            experience = parsed_data.get('experience', [])
            if not isinstance(experience, list):
                experience = [str(experience)] if experience else ['Not found']
            
            # Print education and experience count
            print(f"Education: {len(education)} entries")
            print(f"Experience: {len(experience)} entries")
            
            return parsed_data
            
    except Exception as e:
        print(f"Error parsing resume: {str(e)}")
        print("Stack trace:")
        traceback.print_exc()
        return None

def load_job_listings(file_path):
    """Load job listings from a JSON file"""
    print(f"\n=== LOADING JOB LISTINGS: {file_path} ===")
    
    # Check if file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Job listings file not found: {file_path}")
    
    # Read the file content
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            file_size = os.path.getsize(file_path)
            
            print(f"Successfully read file ({file_size} bytes)")
            
            # Skip comments and find the start of JSON content
            lines = content.split('\n')
            json_lines = []
            for line in lines:
                if not line.strip().startswith('#'):
                    json_lines.append(line)
            
            json_content = '\n'.join(json_lines)
            
            # Parse the JSON
            job_listings = json.loads(json_content)
            
            print(f"Loaded {len(job_listings)} job listings")
            return job_listings
            
    except json.JSONDecodeError as e:
        print(f"Error: The job listings file is not valid JSON: {str(e)}")
        print("Make sure the file contains properly formatted JSON data")
        raise
    except Exception as e:
        print(f"Error loading job listings: {str(e)}")
        traceback.print_exc()
        raise

async def match_candidate_with_jobs(candidate_profile, job_listings, orchestrator):
    """Match a candidate's profile with job listings using the orchestrator"""
    print("\n=== MATCHING JOBS ===")
    
    if not candidate_profile:
        raise ValueError("Candidate profile is empty or invalid")
    
    if not job_listings or not isinstance(job_listings, list):
        raise ValueError("Job listings are empty or invalid")
    
    try:
        # Call the orchestrator for job matching
        matches = await orchestrator.match_with_jobs(candidate_profile, job_listings)
        
        # Validate the matches
        if isinstance(matches, dict) and "error" in matches:
            print(f"Error from job matcher: {matches['error']}")
            return []
            
        if not isinstance(matches, list):
            print(f"Unexpected response type from job matcher: {type(matches)}")
            return []
        
        print(f"Found {len(matches)} potential job matches")
        return matches
        
    except Exception as e:
        print(f"Error matching jobs: {str(e)}")
        traceback.print_exc()
        return []

async def generate_candidate_assessment(candidate_profile, job_info, orchestrator):
    """Generate an assessment for a candidate based on their profile and a job using the orchestrator"""
    print("\n=== GENERATING ASSESSMENT ===")
    
    if not candidate_profile:
        raise ValueError("Candidate profile is empty or invalid")
    
    if not job_info:
        raise ValueError("Job information is empty or invalid")
    
    try:
        # Call the orchestrator to generate assessment
        assessment = await orchestrator.generate_assessment(candidate_profile, job_info)
        
        if "error" in assessment:
            print(f"Error generating assessment: {assessment['error']}")
            return None
        
        print(f"Generated assessment ID: {assessment.get('assessment_id')}")
        print(f"Skills assessed: {', '.join(assessment.get('skills_assessed', []))}")
        print(f"Number of technical questions: {len(assessment.get('technical_questions', []))}")
        print(f"Number of behavioral questions: {len(assessment.get('behavioral_questions', []))}")
        if assessment.get('coding_challenge'):
            print(f"Coding challenge: {assessment.get('coding_challenge', {}).get('title', 'None')}")
        
        return assessment
        
    except Exception as e:
        print(f"Error generating assessment: {str(e)}")
        traceback.print_exc()
        raise

async def schedule_candidate_interview(candidate_profile, job, interview_slot, orchestrator):
    """Schedule an interview for a candidate using the orchestrator"""
    print("\n=== SCHEDULING INTERVIEW ===")
    
    try:
        # Prepare candidate info
        candidate_info = {
            "name": candidate_profile.get("name", "Candidate"),
            "contact_info": {
                "email": candidate_profile.get("contact_info", {}).get("email", "candidate@example.com"),
                "phone": candidate_profile.get("contact_info", {}).get("phone", "555-123-4567")
            }
        }
        
        # Call the orchestrator for interview scheduling
        result = await orchestrator.schedule_interview(candidate_info, job, interview_slot)
        
        if "error" in result:
            print(f"Error scheduling interview: {result['error']}")
            return None
        
        print(f"\n✅ Interview scheduled successfully!")
        print(f"Interview ID: {result.get('interview_id')}")
        print(f"Candidate: {result.get('details', {}).get('candidate')}")
        print(f"Position: {result.get('details', {}).get('position')} at {result.get('details', {}).get('company')}")
        print(f"Date: {result.get('details', {}).get('date')}")
        print(f"Time: {result.get('details', {}).get('time')}")
        print(f"Interviewer: {result.get('details', {}).get('interviewer')}")
        print(f"Location: {result.get('details', {}).get('location')}")
        
        return result
        
    except Exception as e:
        print(f"Error scheduling interview: {str(e)}")
        traceback.print_exc()
        return None

def print_job_matches(matches):
    """Display job matches in a readable format"""
    print("\n=== TOP JOB MATCHES ===")
    
    if not matches:
        print("No matching jobs found")
        return
    
    # Make sure we're working with properly formatted match data
    valid_matches = []
    for match in matches:
        if not isinstance(match, dict):
            print(f"Warning: Skipping invalid match data: {match}")
            continue
            
        # Ensure required fields exist
        if "title" not in match or "company" not in match:
            print(f"Warning: Skipping match with missing title/company: {match}")
            continue
            
        # Ensure match_score is a number
        if "match_score" not in match:
            match["match_score"] = 0.5  # Default score
        elif not isinstance(match["match_score"], (int, float)):
            try:
                match["match_score"] = float(match["match_score"])
            except (ValueError, TypeError):
                match["match_score"] = 0.5  # Default score if conversion fails
                
        valid_matches.append(match)
    
    # Sort matches by score (highest first)
    valid_matches.sort(key=lambda x: x["match_score"], reverse=True)
    
    if not valid_matches:
        print("No valid job matches found after filtering")
        return
        
    for i, match in enumerate(valid_matches):
        score_percent = int(match["match_score"] * 100)
        score_category = "Excellent" if score_percent >= 70 else "Good" if score_percent >= 50 else "Fair"
        
        print(f"\n{i+1}. {match['title']} at {match['company']} ({score_percent}% - {score_category} match)")
        print(f"   Department: {match.get('department', 'Not specified')}")
        print(f"   Location: {match.get('location', 'Not specified')}")
        print(f"   Experience Level: {match.get('experience_level', 'Not specified')}")
        
        # Make sure required_skills and preferred_skills are lists
        if "required_skills" not in match or not isinstance(match["required_skills"], list):
            match["required_skills"] = []
        if "preferred_skills" not in match or not isinstance(match["preferred_skills"], list):
            match["preferred_skills"] = []
            
        print(f"   Required Skills: {', '.join(match.get('required_skills', []))}")
        print(f"   Preferred Skills: {', '.join(match.get('preferred_skills', []))}")
        
        # Display if the job has interview slots
        if 'interview_slots' in match and match['interview_slots']:
            print(f"   Available Interview Slots: {len(match['interview_slots'])}")
          
def print_assessment(assessment):
    """Display assessment details in a readable format"""
    if not assessment:
        print("\nNo assessment generated")
        return
    
    print("\n=== ASSESSMENT DETAILS ===")
    print(f"Assessment ID: {assessment.get('assessment_id')}")
    print(f"For: {assessment.get('candidate_name')} - {assessment.get('job_title')} at {assessment.get('company')}")
    
    # Technical questions
    print("\nTechnical Questions:")
    for q in assessment.get('technical_questions', []):
        print(f"- [{q.get('skill', 'general')}] {q.get('question')}")
    
    # Behavioral questions
    print("\nBehavioral Questions:")
    for q in assessment.get('behavioral_questions', []):
        print(f"- {q.get('question')}")
    
    # Coding challenge
    if assessment.get('coding_challenge'):
        challenge = assessment.get('coding_challenge')
        print("\nCoding Challenge:")
        print(f"Title: {challenge.get('title')}")
        print(f"Description: {challenge.get('description')}")
        print(f"Language: {challenge.get('language')}")
        print(f"Time Limit: {challenge.get('time_limit')}")
        print("\nRequirements:")
        for req in challenge.get('requirements', []):
            print(f"- {req}")
    
    # Evaluation criteria
    print("\nEvaluation Criteria:")
    for area, description in assessment.get('evaluation_criteria', {}).items():
        print(f"- {area.title()}: {description}")

async def automated_recruitment_process(candidate_profile, job_listings, orchestrator):
    """Automated recruitment process using the orchestrator"""
    if not candidate_profile or not job_listings:
        print("Cannot proceed without valid candidate profile and job listings")
        return
    
    # Match candidate with jobs
    try:
        matches = await match_candidate_with_jobs(candidate_profile, job_listings, orchestrator)
        if not matches or len(matches) == 0:
            print("No suitable job matches found")
            return
        
        # Print job matches
        print_job_matches(matches)
        
        # Validate matches before proceeding
        valid_matches = [m for m in matches if isinstance(m, dict) and "title" in m and "company" in m]
        if not valid_matches:
            print("No valid job matches to proceed with")
            return
            
        # Automatically select the best match (highest score)
        # Sort by match_score to ensure we get the best match
        valid_matches.sort(
            key=lambda x: float(x["match_score"]) if isinstance(x.get("match_score"), (int, float)) 
                           else 0.0,
            reverse=True
        )
        best_match = valid_matches[0]
        
        print(f"\n=== AUTOMATICALLY SELECTING BEST MATCH ===")
        print(f"Selected: {best_match['title']} at {best_match['company']}")
        
        match_score = best_match.get("match_score", 0)
        if isinstance(match_score, (int, float)):
            print(f"Match Score: {int(match_score * 100)}%")
        else:
            print(f"Match Score: Not available")
        
        # Generate assessment for the candidate
        print("\n=== GENERATING CANDIDATE ASSESSMENT ===")
        assessment = await generate_candidate_assessment(candidate_profile, best_match, orchestrator)
        print_assessment(assessment)
        
        # Check if the job has interview slots available
        if 'interview_slots' in best_match and best_match['interview_slots'] and len(best_match['interview_slots']) > 0:
            # Automatically select the first available interview slot
            selected_slot = best_match['interview_slots'][0]
            print(f"\n=== AUTOMATICALLY SCHEDULING INTERVIEW ===")
            print(f"Selected Interview Slot: {selected_slot.get('date')} at {selected_slot.get('time')}")
            print(f"Interviewer: {selected_slot.get('interviewer')}")
            
            # Schedule the interview
            await schedule_candidate_interview(candidate_profile, best_match, selected_slot, orchestrator)
        else:
            print("\nNo interview slots available for the selected job")
        
        print("\n===== AUTOMATED RECRUITMENT PROCESS COMPLETED =====")
    except Exception as e:
        print(f"Error in recruitment process: {str(e)}")
        traceback.print_exc()
            
async def main():
    """Main function to orchestrate the AI recruitment system"""
    print("\n===== AI RECRUITMENT SYSTEM =====")
    print("Powered by Moya Framework")
    print(f"Session started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nRunning in fully automated mode - no further user interaction required")
    
    # Initialize the recruitment orchestrator
    orchestrator = RecruitmentOrchestrator()
    
    try:
        # Get resume file path - this is the only user input needed
        resume_path = input("\nEnter the path to your resume file: ")
        resume_path = os.path.abspath(resume_path)
        
        # Parse the resume
        candidate_profile = await parse_resume(resume_path, orchestrator)
        
        if not candidate_profile:
            print("Error: Failed to parse resume")
            return
        
        # Use default job listings path or a predefined path
        job_listings_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "job_listings.txt")
        if not os.path.exists(job_listings_path):
            print(f"Default job listings file not found at: {job_listings_path}")
            job_listings_path = input("\nEnter the path to job listings file: ")
            job_listings_path = os.path.abspath(job_listings_path)
        else:
            print(f"Using default job listings file: {job_listings_path}")
        
        # Load job listings
        job_listings = load_job_listings(job_listings_path)
        
        if not job_listings:
            print("Error: Failed to load job listings")
            return
        
        # Run the automated recruitment process
        await automated_recruitment_process(candidate_profile, job_listings, orchestrator)
        
        print("\n===== SESSION COMPLETED =====")
        print(f"Thank you for using the AI Recruitment System!")
        
    except FileNotFoundError as e:
        print(f"Error: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        print("Stack trace:")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())