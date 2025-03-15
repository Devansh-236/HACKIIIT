import asyncio
import os
from app.agents.resume_parser import extract_resume_data

async def main():
    """Main async function to run the recruitment system"""
    file_path = input("Enter the path of the resume file: ").strip()

    if not os.path.exists(file_path):
        print(f"Error: The file '{file_path}' does not exist.")
        exit(1)

    with open(file_path, "r", encoding="utf-8") as file:
        resume_text = file.read()

    # Since extract_resume_data is async, we need to await it
    extracted_data = await extract_resume_data(resume_text)
    
    print("\nExtracted Resume Data:")
    print(extracted_data)

if __name__ == "__main__":
    # Run the async main function using asyncio
    asyncio.run(main())
