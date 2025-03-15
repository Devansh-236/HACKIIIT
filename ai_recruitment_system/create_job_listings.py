#!/usr/bin/env python
"""
This script creates sample job listings from a single company for testing the job matcher.
The job listings will be saved in a format that can be parsed by the job matcher.
"""

import os
import sys
import json
import datetime
import random

def create_job_listings(output_path, company_name="TechNova Innovations"):
    """Create a sample job listings file with positions from a single company"""
    
    # Create timestamp to ensure unique content
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Sample job listings all from the same company
    job_listings = [
        {
            "job_id": "JOB-ML-001",
            "title": "Senior Machine Learning Engineer",
            "company": company_name,
            "department": "Artificial Intelligence",
            "location": "San Francisco, CA (Remote Option)",
            "required_skills": ["python", "machine learning", "tensorflow", "deep learning", "ai"],
            "preferred_skills": ["pytorch", "kubernetes", "mlops", "computer vision"],
            "experience_level": "5+ years",
            "description": "Lead the development of cutting-edge AI solutions for our enterprise clients. You'll design and implement machine learning models and collaborate with cross-functional teams.",
            "interview_slots": generate_interview_slots(5)
        },
        {
            "job_id": "JOB-FS-002",
            "title": "Full Stack JavaScript Developer",
            "company": company_name,
            "department": "Web Development",
            "location": "Austin, TX (Hybrid)",
            "required_skills": ["javascript", "react", "node.js", "mongodb", "express"],
            "preferred_skills": ["typescript", "redis", "aws", "graphql"],
            "experience_level": "3+ years",
            "description": "Join our web development team to build modern applications. You'll work on both frontend with React and backend with Node.js and Express.",
            "interview_slots": generate_interview_slots(4)
        },
        {
            "job_id": "JOB-DEV-003",
            "title": "DevOps Engineer",
            "company": company_name,
            "department": "Infrastructure",
            "location": "Seattle, WA (On-site)",
            "required_skills": ["aws", "docker", "kubernetes", "ci/cd", "python"],
            "preferred_skills": ["terraform", "ansible", "prometheus", "grafana"],
            "experience_level": "4+ years",
            "description": "Automate and optimize our cloud infrastructure. You'll implement CI/CD pipelines and maintain our container orchestration platform.",
            "interview_slots": generate_interview_slots(3)
        },
        {
            "job_id": "JOB-DS-004",
            "title": "Data Scientist",
            "company": company_name,
            "department": "Data Analytics",
            "location": "Boston, MA (Remote Option)",
            "required_skills": ["python", "machine learning", "statistics", "sql", "data visualization"],
            "preferred_skills": ["r", "tableau", "spark", "hadoop", "big data"],
            "experience_level": "3+ years",
            "description": "Analyze complex datasets and build predictive models to drive business decisions. You'll work with stakeholders to identify opportunities for data-driven solutions.",
            "interview_slots": generate_interview_slots(4)
        },
        {
            "job_id": "JOB-FE-005",
            "title": "Frontend Developer",
            "company": company_name,
            "department": "User Experience",
            "location": "New York, NY (Hybrid)",
            "required_skills": ["javascript", "html", "css", "react", "typescript"],
            "preferred_skills": ["redux", "sass", "webpack", "jest", "accessibility"],
            "experience_level": "2+ years",
            "description": "Create beautiful and responsive user interfaces for our web applications. You'll collaborate with designers to implement pixel-perfect UIs.",
            "interview_slots": generate_interview_slots(3)
        },
        {
            "job_id": "JOB-BE-006",
            "title": "Backend Engineer",
            "company": company_name,
            "department": "Core Services",
            "location": "Chicago, IL (On-site)",
            "required_skills": ["java", "spring", "sql", "rest api", "microservices"],
            "preferred_skills": ["kafka", "elasticsearch", "docker", "aws", "nosql"],
            "experience_level": "4+ years",
            "description": "Design and implement scalable backend services and APIs for our enterprise products. You'll build robust and maintainable systems.",
            "interview_slots": generate_interview_slots(3)
        },
        {
            "job_id": "JOB-MOB-007",
            "title": "Mobile App Developer",
            "company": company_name,
            "department": "Mobile Solutions",
            "location": "Los Angeles, CA (Remote Option)",
            "required_skills": ["react native", "javascript", "mobile development", "ios", "android"],
            "preferred_skills": ["redux", "native modules", "app store deployment", "firebase"],
            "experience_level": "3+ years",
            "description": "Develop cross-platform mobile applications using React Native. You'll build features that work flawlessly on both iOS and Android.",
            "interview_slots": generate_interview_slots(3)
        },
        {
            "job_id": "JOB-DBA-008",
            "title": "Database Administrator",
            "company": company_name,
            "department": "Data Infrastructure",
            "location": "Denver, CO (Hybrid)",
            "required_skills": ["sql", "postgresql", "mongodb", "database optimization", "backup and recovery"],
            "preferred_skills": ["mysql", "oracle", "data modeling", "high availability", "cloud databases"],
            "experience_level": "5+ years",
            "description": "Manage and optimize our database systems to ensure high performance and reliability. You'll be responsible for database security, backup, and recovery procedures.",
            "interview_slots": generate_interview_slots(2)
        }
    ]
    
    # Add timestamp to ensure uniqueness
    header = f"# Job Listings for {company_name}\n# Generated on: {timestamp}\n# Format: JSON\n\n"
    
    # Write the job listings to the specified file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(header)
        json.dump(job_listings, f, indent=2)
    
    print(f"Job listings for {company_name} created at: {output_path}")
    print(f"Total positions: {len(job_listings)}")
    print(f"Timestamp included: {timestamp}")
    return output_path, job_listings

def generate_interview_slots(num_slots=3):
    """Generate random interview slots for the coming week"""
    slots = []
    today = datetime.datetime.now()
    
    # Generate slots for the next 7 days
    for i in range(1, 8):
        # Skip weekends
        day = today + datetime.timedelta(days=i)
        if day.weekday() >= 5:  # Saturday or Sunday
            continue
            
        # Generate random times (9 AM to 4 PM)
        for _ in range(min(num_slots, 3)):  # Max 3 slots per day
            hour = random.randint(9, 16)
            slot = {
                "date": day.strftime("%Y-%m-%d"),
                "time": f"{hour:02d}:00",
                "interviewer": random.choice([
                    "Sarah Johnson, Senior Recruiter",
                    "Michael Chen, Technical Lead",
                    "Emily Rodriguez, VP of Engineering",
                    "David Kim, Department Manager",
                    "Lisa Patel, CTO"
                ]),
                "location": random.choice([
                    "Virtual (Zoom)",
                    "HQ Conference Room A",
                    "HQ Conference Room B",
                    "Branch Office Conference Room",
                    "Video Call (Microsoft Teams)"
                ])
            }
            slots.append(slot)
    
    return slots

if __name__ == "__main__":
    # Default output path is job_listings.txt in the current directory
    default_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "job_listings.txt")
    
    # Allow specifying custom path and company name via command line
    output_path = sys.argv[1] if len(sys.argv) > 1 else default_path
    company_name = sys.argv[2] if len(sys.argv) > 2 else "TechNova Innovations"
    
    # Create the job listings
    created_path, _ = create_job_listings(output_path, company_name)
    
    print("\nTo test the job matcher with these listings, run:")
    print(f"python run.py")
    print("Enter the path to your resume when prompted, then")
    print(f"Enter the path to job listings: {created_path}") 