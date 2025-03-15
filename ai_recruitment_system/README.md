# AI-Powered Recruitment System

An advanced recruitment system powered by the Moya framework, designed to streamline the hiring process through AI-driven resume parsing, job matching, interview scheduling, and candidate assessment.

## Features

- **Resume Parsing**: Extract structured information from resumes including name, contact information, skills, education, and experience.
- **Job Matching**: Match candidates with suitable job positions based on skills, experience, and other criteria.
- **Interview Scheduling**: Schedule interviews for matched jobs with available time slots.
- **Candidate Assessment**: Generate comprehensive candidate assessments including technical questions, behavioral questions, and coding challenges.

## System Components

1. **Resume Parser Agent**: Extracts and analyzes information from resumes using NLP techniques.
2. **Job Matcher Agent**: Matches candidates with suitable job positions using semantic analysis.
3. **Interview Scheduler Agent**: Manages interview scheduling and confirmation.
4. **Candidate Assessor Agent**: Generates technical and behavioral assessments based on job requirements.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Required Python packages (install via `pip install -r requirements.txt`)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/ai-recruitment-system.git
   cd ai-recruitment-system
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

### Usage

#### 1. Generate Job Listings

First, generate sample job listings for testing:

```bash
python create_job_listings.py [--output path/to/output.txt] [--company "Company Name"]
```

This will create a file with sample job listings in JSON format.

#### 2. Create a Test Resume (Optional)

You can create a test resume for testing:

```bash
python create_test_resume.py [--output path/to/output.txt]
```

#### 3. Run the Recruitment System

Run the main application:

```bash
python run.py
```

Follow the prompts to:
- Enter the path to your resume
- Enter the path to the job listings
- View job matches
- Select a job for interview scheduling or assessment

## Example Workflow

1. Parse a candidate's resume to extract structured information
2. Load available job listings from a company
3. Match the candidate with suitable positions
4. Select a job match to either:
   - Schedule an interview from available time slots
   - Generate a detailed candidate assessment with questions and coding challenges

## System Architecture

The system is built on the Moya framework, which provides the foundation for creating AI agents. Each component (resume parser, job matcher, interview scheduler, and candidate assessor) is implemented as a Moya agent with specialized tools.

```
├── app/
│   ├── agents/
│   │   ├── resume_parser.py       # Resume parsing agent
│   │   ├── job_matcher.py         # Job matching agent
│   │   ├── interview_scheduler.py # Interview scheduling agent
│   │   └── candidate_assessor.py  # Candidate assessment agent
│   └── utils/
│       └── text_processing.py     # Text processing utilities
├── create_job_listings.py         # Script to generate job listings
├── create_test_resume.py          # Script to generate test resumes
├── run.py                         # Main application
└── requirements.txt               # Dependencies
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 