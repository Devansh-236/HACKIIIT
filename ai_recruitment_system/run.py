#!/usr/bin/env python
import asyncio
import os
import sys
import json

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.agents.resume_parser import ResumeParserAgent
from app.agents.job_matcher import JobMatchingAgent
from moya.agents.base_agent import AgentConfig

async def parse_resume(file_path):
    """Parse a resume file and extract structured information"""
    
    # Verify the file exists
    if not os.path.exists(file_path):
        print(f"Error: Resume file not found at {file_path}")
        return None
    
    # Read the file content
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            resume_text = f.read()
        
        print(f"Successfully read resume file: {file_path}")
        print(f"File size: {len(resume_text)} characters")
        print("First 100 characters of the file:")
        print("-" * 50)
        print(resume_text[:100] + "...")
        print("-" * 50)
        
        # Initialize the resume parser
        print("\nInitializing resume parser...")
        parser_config = AgentConfig(
            agent_name="resume_parser",
            agent_type="resume_parser",
            description="Extracts and analyzes information from resumes",
            system_prompt="You are a resume parsing assistant that extracts structured information from resumes."
        )
        parser_agent = ResumeParserAgent(parser_config)
        
        # Parse the resume
        print("Parsing resume...")
        parsed_resume = await parser_agent.handle_message(resume_text)
        
        # Check for errors
        if isinstance(parsed_resume, dict) and "error" in parsed_resume:
            print(f"\nError parsing resume: {parsed_resume['error']}")
            return None
        
        # Print the extracted information
        print("\n" + "=" * 30)
        print("EXTRACTED RESUME INFORMATION")
        print("=" * 30)
        
        print(f"\nName: {parsed_resume['name']}")
        
        print("\nContact Information:")
        for key, value in parsed_resume['contact_info'].items():
            if value:
                print(f"  {key.title()}: {value}")
        
        print("\nSkills:")
        for skill in parsed_resume['skills']:
            print(f"  - {skill}")
        
        print("\nEducation:")
        if parsed_resume['education']:
            for edu in parsed_resume['education']:
                print(f"  - {edu}")
        else:
            print("  No education information found")
        
        print("\nExperience:")
        if parsed_resume['experience']:
            for exp in parsed_resume['experience']:
                print(f"  - {exp}")
        else:
            print("  No experience information found")
            
        # Return the parsed resume data
        return parsed_resume
        
    except Exception as e:
        print(f"Error processing resume: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

async def load_job_listings(file_path):
    """Load job listings from a file"""
    
    # Verify the file exists
    if not os.path.exists(file_path):
        print(f"Error: Job listings file not found at {file_path}")
        return None
    
    # Read the file content
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"Successfully read job listings file: {file_path}")
        
        # Skip comments and find the start of JSON content
        json_content = content
        if content.startswith('#'):
            lines = content.split('\n')
            non_comment_lines = []
            for line in lines:
                if not line.strip().startswith('#'):
                    non_comment_lines.append(line)
            json_content = '\n'.join(non_comment_lines)
        
        # Parse the JSON content
        job_listings = json.loads(json_content)
        
        print(f"Loaded {len(job_listings)} job listings")
        
        return job_listings
        
    except json.JSONDecodeError as e:
        print(f"Error parsing job listings JSON: {str(e)}")
        print("Make sure the job listings file contains valid JSON data")
        return None
    except Exception as e:
        print(f"Error loading job listings: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

async def match_jobs(candidate_profile, job_listings):
    """Match a candidate profile with job listings"""
    
    if not candidate_profile or not job_listings:
        print("Error: Cannot perform job matching without valid candidate profile and job listings")
        return None
    
    try:
        # Initialize the job matcher
        print("\nInitializing job matcher...")
        matcher_config = AgentConfig(
            agent_name="job_matcher",
            agent_type="job_matcher",
            description="Matches candidates with suitable job positions",
            system_prompt="You are a job matching assistant that helps find the best job matches for candidates."
        )
        matcher_agent = JobMatchingAgent(matcher_config)
        
        # Match the candidate with jobs
        print("Finding job matches...")
        matches = await matcher_agent.handle_message({
            "candidate_profile": candidate_profile,
            "job_listings": job_listings
        })
        
        # Check for errors
        if isinstance(matches, dict) and "error" in matches:
            print(f"\nError matching jobs: {matches['error']}")
            return None
        
        return matches
        
    except Exception as e:
        print(f"Error matching jobs: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def print_job_matches(matches):
    """Print job matches in a readable format"""
    
    if not matches:
        print("\nNo job matches found")
        return
    
    print("\n" + "=" * 30)
    print("JOB MATCHING RESULTS")
    print("=" * 30)
    
    # Get the number of matches to display (up to 5)
    num_matches = min(len(matches), 5)
    print(f"\nTop {num_matches} Job Matches:")
    
    for i, job in enumerate(matches[:num_matches]):
        match_percentage = job['match_score'] * 100
        print(f"\n{i+1}. {job['title']} at {job['company']}")
        print(f"   Match Score: {match_percentage:.1f}%")
        print(f"   Required Skills: {', '.join(job['required_skills'])}")
        print(f"   Description: {job['description']}")
    
    # Show a brief summary of remaining matches if there are more than 5
    if len(matches) > 5:
        print(f"\nAnd {len(matches) - 5} more matches with lower scores...")

async def main():
    print("\n" + "=" * 50)
    print("AI RECRUITMENT SYSTEM - RESUME AND JOB MATCHER")
    print("=" * 50)
    
    # STEP 1: Parse the resume
    resume_path = input("\nEnter the path to the resume file: ").strip()
    abs_resume_path = os.path.abspath(resume_path)
    print(f"Using resume path: {abs_resume_path}")
    
    parsed_resume = await parse_resume(abs_resume_path)
    if not parsed_resume:
        print("Cannot proceed without a valid parsed resume.")
        return
    
    # STEP 2: Load job listings
    job_path = input("\nEnter the path to the job listings file: ").strip()
    abs_job_path = os.path.abspath(job_path)
    print(f"Using job listings path: {abs_job_path}")
    
    job_listings = await load_job_listings(abs_job_path)
    if not job_listings:
        print("Cannot proceed without valid job listings.")
        return
    
    # STEP 3: Match jobs
    job_matches = await match_jobs(parsed_resume, job_listings)
    if not job_matches:
        return
    
    # STEP 4: Print the results
    print_job_matches(job_matches)
    
    print("\nJob matching process complete.")

if __name__ == "__main__":
    asyncio.run(main())