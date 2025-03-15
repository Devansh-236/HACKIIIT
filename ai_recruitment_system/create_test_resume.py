#!/usr/bin/env python
"""
This script creates a test resume file at the specified path.
It's useful for testing the resume parser with fresh data.
"""

import os
import sys
import datetime

def create_test_resume(output_path):
    """Create a test resume file with timestamp to ensure it's unique"""
    
    # Create timestamp to ensure unique content
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Resume content template
    resume_content = f"""Alex Johnson
Email: alex.johnson@example.com
Phone: (555) 987-6543

SUMMARY
Experienced software developer with focus on machine learning and cloud technologies.
Created on: {timestamp}

SKILLS
- Python, JavaScript, Java
- Machine Learning, Neural Networks
- Docker, Kubernetes, AWS
- React, Node.js, Express
- MongoDB, PostgreSQL

EXPERIENCE
Machine Learning Engineer | TechCorp Inc. (2021-Present)
- Developed predictive models for customer behavior analysis
- Optimized recommendation algorithms improving conversion by 25%
- Led team of 3 developers on AI integration projects

Web Developer | Digital Solutions (2018-2021)
- Built responsive web applications using React and Node.js
- Implemented CI/CD pipelines for automated testing and deployment
- Created RESTful APIs for mobile and web applications

EDUCATION
Master of Science in Computer Science
Tech University (2016-2018)
- Specialization in Artificial Intelligence
- GPA: 3.8/4.0

Bachelor of Engineering in Software Engineering
State University (2012-2016)
- Dean's List all semesters
- Senior Project: Smart Home Automation System
"""

    # Write the content to the specified file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(resume_content)
    
    print(f"Test resume created at: {output_path}")
    print(f"Timestamp included: {timestamp}")
    return output_path

if __name__ == "__main__":
    # Default output path is test_resume.txt in the current directory
    default_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_resume.txt")
    
    # Allow specifying custom path via command line
    output_path = sys.argv[1] if len(sys.argv) > 1 else default_path
    
    # Create the test resume
    created_path = create_test_resume(output_path)
    
    print("\nTo parse this test resume, run:")
    print(f"python run.py")
    print("Then enter the path when prompted:")
    print(f"{created_path}") 