#!/usr/bin/env python
"""
This script creates a sample job listings file for testing the job matcher.
The job listings will be saved in a format that can be parsed by the job matcher.
"""

import os
import sys
import json
import datetime

def create_job_listings(output_path):
    """Create a sample job listings file for testing the job matcher"""
    
    # Create timestamp to ensure unique content
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Sample job listings
    job_listings = [
        {
            "title": "Senior Machine Learning Engineer",
            "company": "AI Innovations Inc",
            "required_skills": ["python", "machine learning", "tensorflow", "deep learning", "ai"],
            "description": "We're looking for an experienced ML engineer to lead the development of cutting-edge AI solutions for our enterprise clients. Experience with TensorFlow and PyTorch required."
        },
        {
            "title": "Full Stack JavaScript Developer",
            "company": "Web Solutions Ltd",
            "required_skills": ["javascript", "react", "node.js", "mongodb", "express"],
            "description": "Join our team to build modern web applications. You'll work on both frontend with React and backend with Node.js and Express."
        },
        {
            "title": "DevOps Engineer",
            "company": "Cloud Systems",
            "required_skills": ["aws", "docker", "kubernetes", "ci/cd", "python"],
            "description": "Help us automate and optimize our cloud infrastructure. Experience with AWS, Docker, and Kubernetes is essential."
        },
        {
            "title": "Data Scientist",
            "company": "Data Analytics Pro",
            "required_skills": ["python", "machine learning", "statistics", "sql", "data visualization"],
            "description": "Analyze complex datasets and build predictive models to drive business decisions."
        },
        {
            "title": "Frontend Developer",
            "company": "UX Masters",
            "required_skills": ["javascript", "html", "css", "react", "typescript"],
            "description": "Create beautiful and responsive user interfaces for our web applications."
        },
        {
            "title": "Backend Engineer",
            "company": "Server Systems Inc",
            "required_skills": ["java", "spring", "sql", "rest api", "microservices"],
            "description": "Design and implement scalable backend services and APIs for our enterprise products."
        },
        {
            "title": "Mobile App Developer",
            "company": "App Creators",
            "required_skills": ["react native", "javascript", "mobile development", "ios", "android"],
            "description": "Develop cross-platform mobile applications using React Native."
        },
        {
            "title": "Database Administrator",
            "company": "Data Storage Solutions",
            "required_skills": ["sql", "postgresql", "mongodb", "database optimization", "backup and recovery"],
            "description": "Manage and optimize our database systems to ensure high performance and reliability."
        }
    ]
    
    # Add timestamp to ensure uniqueness
    header = f"# Job Listings Generated on: {timestamp}\n# Format: JSON\n\n"
    
    # Write the job listings to the specified file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(header)
        json.dump(job_listings, f, indent=2)
    
    print(f"Job listings created at: {output_path}")
    print(f"Timestamp included: {timestamp}")
    return output_path, job_listings

if __name__ == "__main__":
    # Default output path is job_listings.txt in the current directory
    default_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "job_listings.txt")
    
    # Allow specifying custom path via command line
    output_path = sys.argv[1] if len(sys.argv) > 1 else default_path
    
    # Create the job listings
    created_path, _ = create_job_listings(output_path)
    
    print("\nTo test the job matcher with these listings, run:")
    print(f"python run.py")
    print("Enter the path to your resume when prompted, then")
    print(f"Enter the path to job listings: {created_path}") 