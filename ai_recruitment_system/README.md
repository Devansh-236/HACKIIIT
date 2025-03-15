# AI-Powered Recruitment System with Moya

This is an AI-powered recruitment system that uses the Moya framework to intelligently parse resumes and match candidates with suitable job positions.

## Features

- **Resume Parsing**: Extracts structured information from resume text, including:
  - Name and contact information
  - Skills and technologies
  - Education history
  - Professional experience

- **Job Matching**: Matches candidates with suitable job positions using:
  - TF-IDF vectorization
  - Cosine similarity scoring
  - Skills and experience matching

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd ai-recruitment-system
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

4. Download the spaCy language model:
```bash
python -m spacy download en_core_web_sm
```

## Usage

### Running the System

1. From the project root directory, run:
```bash
python run.py
```

2. When prompted, enter the path to a resume file:
```
Enter the path of the resume file: sample_resume.txt
```

3. The system will:
   - Parse the resume and extract structured data
   - Match the candidate with sample job listings
   - Display the parsed resume information and matching job opportunities

### Sample Files

- `sample_resume.txt`: A sample resume to demonstrate the system's capabilities

## Project Structure

- `app/`: Main application directory
  - `agents/`: Contains Moya-based agents
    - `resume_parser.py`: Agent for parsing resumes
    - `job_matcher.py`: Agent for matching candidates with jobs
  - `main.py`: Core application logic
- `run.py`: Entry point for running the application
- `requirements.txt`: Package dependencies

## Integrating with Moya

This system extends Moya's agent and tool classes:

- `ResumeParserAgent` - Inherits from Moya's `Agent` class
- `ResumeParserTool` - Inherits from Moya's `BaseTool` class
- `JobMatchingAgent` - Inherits from Moya's `Agent` class
- `JobMatchingTool` - Inherits from Moya's `BaseTool` class

Each agent handles the high-level operations, while each tool implements the specific functionality.

## Extending the System

To extend this system:

1. Add new tools by subclassing `BaseTool`
2. Add new agents by subclassing `Agent`
3. Register tools with agents as needed
4. Update the main script to use your new components

## Requirements

- Python 3.8+
- spaCy and the en_core_web_sm model
- scikit-learn
- Moya framework
- Other dependencies listed in requirements.txt

## Configuration

The system can be configured through environment variables:

- `MOYA_API_KEY`: Your Moya API key
- `CALENDAR_API_KEY`: API key for calendar integration
- `ASSESSMENT_PASS_THRESHOLD`: Minimum score to pass assessment (default: 70)

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Moya Framework](https://github.com/moya/moya)
- Uses [spaCy](https://spacy.io/) for NLP tasks
- Employs [scikit-learn](https://scikit-learn.org/) for ML-based matching 