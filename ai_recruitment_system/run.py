#!/usr/bin/env python3
import asyncio
import os
import sys
import json
import traceback
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the agent functions from the respective modules
from app.agents.resume_parser import extract_resume_data
from app.agents.job_matcher import match_jobs
from app.agents.candidate_assessor import generate_assessment, evaluate_submission
from app.agents.interview_scheduler import schedule_interview

async def parse_resume(file_path):
    """Parse a resume file and extract structured information"""
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
            
            # Parse the resume
            parsed_data = await extract_resume_data(content)
            
            print("\n=== EXTRACTED INFORMATION ===")
            print(f"Name: {parsed_data.get('name', 'Not found')}")
            
            # Handle contact information properly
            contact = parsed_data.get('contact', '')
            if isinstance(contact, dict):
                for key, value in contact.items():
                    print(f"{key.capitalize()}: {value}")
            else:
                print(f"Contact: {contact}")
            
            print(f"Skills: {', '.join(parsed_data.get('skills', ['Not found']))}")
            print(f"Education: {', '.join(parsed_data.get('education', ['Not found']))}")
            print(f"Experience: {', '.join(parsed_data.get('experience', ['Not found']))}")
            
            return parsed_data
            
    except Exception as e:
        print(f"Error parsing resume: {str(e)}")
        print("Stack trace:")
        traceback.print_exc()
        raise

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

async def match_candidate_with_jobs(candidate_profile, job_listings):
    """Match a candidate's profile with job listings"""
    print("\n=== MATCHING JOBS ===")
    
    if not candidate_profile:
        raise ValueError("Candidate profile is empty or invalid")
    
    if not job_listings or not isinstance(job_listings, list):
        raise ValueError("Job listings are empty or invalid")
    
    try:
        # Call the job matcher
        matches = await match_jobs(candidate_profile, job_listings)
        
        print(f"Found {len(matches)} potential job matches")
        return matches
        
    except Exception as e:
        print(f"Error matching jobs: {str(e)}")
        traceback.print_exc()
        raise

async def generate_candidate_assessment(candidate_profile, job_info):
    """Generate an assessment for a candidate based on their profile and a job"""
    print("\n=== GENERATING ASSESSMENT ===")
    
    if not candidate_profile:
        raise ValueError("Candidate profile is empty or invalid")
    
    if not job_info:
        raise ValueError("Job information is empty or invalid")
    
    try:
        # Call the candidate assessor
        assessment = await generate_assessment(candidate_profile, job_info)
        
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

async def schedule_candidate_interview(candidate_profile, job, interview_slot):
    """Schedule an interview for a candidate"""
    print("\n=== SCHEDULING INTERVIEW ===")
    
    try:
        # Prepare candidate info
        candidate_info = {
            "name": candidate_profile.get("name", "Candidate"),
            "contact_info": {
                "email": candidate_profile.get("contact", {}).get("email", "candidate@example.com"),
                "phone": candidate_profile.get("contact", {}).get("phone", "555-123-4567")
            }
        }
        
        # Call the interview scheduler
        result = await schedule_interview(candidate_info, job, interview_slot)
        
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
    
    for i, match in enumerate(matches):
        score_percent = int(match["match_score"] * 100)
        score_category = "Excellent" if score_percent >= 70 else "Good" if score_percent >= 50 else "Fair"
        
        print(f"\n{i+1}. {match['title']} at {match['company']} ({score_percent}% - {score_category} match)")
        print(f"   Department: {match.get('department', 'Not specified')}")
        print(f"   Location: {match.get('location', 'Not specified')}")
        print(f"   Experience Level: {match.get('experience_level', 'Not specified')}")
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

async def automated_recruitment_process(candidate_profile, job_listings):
    """Automated recruitment process without user interaction"""
    if not candidate_profile or not job_listings:
        print("Cannot proceed without valid candidate profile and job listings")
        return
    
    # Match candidate with jobs
    matches = await match_candidate_with_jobs(candidate_profile, job_listings)
    if not matches or len(matches) == 0:
        print("No suitable job matches found")
        return
    
    # Print job matches
    print_job_matches(matches)
    
    # Automatically select the best match (highest score)
    best_match = matches[0]  # The matches are already sorted by score
    print(f"\n=== AUTOMATICALLY SELECTING BEST MATCH ===")
    print(f"Selected: {best_match['title']} at {best_match['company']}")
    print(f"Match Score: {int(best_match['match_score'] * 100)}%")
    
    # Generate assessment for the candidate
    print("\n=== GENERATING CANDIDATE ASSESSMENT ===")
    assessment = await generate_candidate_assessment(candidate_profile, best_match)
    print_assessment(assessment)
    
    # Check if the job has interview slots available
    if 'interview_slots' in best_match and best_match['interview_slots']:
        # Automatically select the first available interview slot
        selected_slot = best_match['interview_slots'][0]
        print(f"\n=== AUTOMATICALLY SCHEDULING INTERVIEW ===")
        print(f"Selected Interview Slot: {selected_slot.get('date')} at {selected_slot.get('time')}")
        print(f"Interviewer: {selected_slot.get('interviewer')}")
        
        # Schedule the interview
        await schedule_candidate_interview(candidate_profile, best_match, selected_slot)
    else:
        print("\nNo interview slots available for the selected job")
    
    print("\n===== AUTOMATED RECRUITMENT PROCESS COMPLETED =====")
            
async def main():
    """Main function to orchestrate the AI recruitment system"""
    print("\n===== AI RECRUITMENT SYSTEM =====")
    print("Powered by Moya Framework")
    print(f"Session started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nRunning in fully automated mode - no further user interaction required")
    
    try:
        # Get resume file path - this is the only user input needed
        resume_path = input("\nEnter the path to your resume file: ")
        resume_path = os.path.abspath(resume_path)
        
        # Parse the resume
        candidate_profile = await parse_resume(resume_path)
        
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
        await automated_recruitment_process(candidate_profile, job_listings)
        
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