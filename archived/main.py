import argparse

from resume_extractor import process_resume


def main():
    """
    Main entry point for the CV generation pipeline.
    """

    parser = argparse.ArgumentParser(description="LLM-based CV Builder")

    parser.add_argument(
        "--resume",
        required=True,
        help="Path to the resume PDF file"
    )

    parser.add_argument(
        "--job",
        required=True,
        help="Path to the job description text file"
    )

    parser.add_argument(
        "--output",
        default="generated_cv.docx",
        help="Output CV file name"
    )

    args = parser.parse_args()

    resume_path = args.resume
    job_path = args.job
    output_file = args.output

    print("Step 1: Extracting resume information...")
    resume_data = process_resume(resume_path)
    print("Extracted Resume Data:")
    print(resume_data)

    print("Step 2: Parsing job description...")
    job_data = parse_job_description(job_path)

    print("Step 3: Generating tailored CV...")
    generate_cv(resume_data, job_data, output_file)

    print(f"CV generated successfully: {output_file}")

if __name__ == '__main__':
    main()
