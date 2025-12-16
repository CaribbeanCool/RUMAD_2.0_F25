import re
import os

from pypdf import PdfReader
from os import listdir

from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    SentenceTransformersTokenTextSplitter,
)
from sentence_transformers import SentenceTransformer
from API.dao.syllabus import SyllabusDAO
from API.dao.classes import ClassDAO

model = SentenceTransformer("all-mpnet-base-v2")

# TODO cambiar al path correcto de tu computadora
PDF_DIR = r"C:\personal-projects\rumad_2.0\syllabus"


def extract_dept_code(filename):
    match = re.search(r"(CIIC|ICOM|INSO)[-_]?(\d{4})", filename.upper())
    if not match:
        return None, None
    return match.group(1), match.group(2)


def delete_empty_pages(texts):
    return [t for t in texts if t.strip() != ""]


def preprocess_syllabus(pdf_texts):
    """Preprocess syllabus text by extracting key sections with metadata labels."""
    raw_text = " ".join(pdf_texts)

    # Define patterns to match sections with clear semantic labels
    patterns = {
        "General Information": r"General Information:.*?(?=Course Description:)",
        "Course Description": r"Course Description:.*?(?=Pre/Co-requisites and other requirements:)",
        "Prerequisites and Corequisites": r"Pre/Co-requisites and other requirements:.*?(?=Course Objectives:)",
        "Course Objectives": r"Course Objectives.*?(?=Instructional Strategies:)",
        "Instructional Strategies": r"Instructional Strategies:.*?(?=Minimum or Required Resources Available:)",
        "Required Resources": r"Minimum or Required Resources Available:.*?(?=Course time frame and thematic outline)",
        "Course Outline and Topics": r"Course time frame and thematic outline.*?(?=Grading System)",
        "Grading System": r"Grading System.*?(?=Evaluation Strategies)",
        "Evaluation Strategies": r"Evaluation Strategies.*?(?=Bibliography)",
        "Textbooks and Bibliography": r"Bibliography.*?(?=Course Outcomes)",
        "Course Outcomes": r"Course Outcomes.*?(?=According to Law 51|Academic Integrity)",
    }

    cleaned_data = {}
    for section_label, pattern in patterns.items():
        match = re.search(pattern, raw_text, re.DOTALL)
        if match:
            cleaned_section = re.sub(r"\s+", " ", match.group(0)).strip()

            # Special processing for Evaluation Strategies to clarify the table structure
            if section_label == "Evaluation Strategies":
                # Try to make the percentages more explicit
                cleaned_section = re.sub(r"(\d+)\s*%", r"\1 percent", cleaned_section)
                cleaned_section = cleaned_section.replace("Percent", "Grade Percentage")
                cleaned_section = cleaned_section.replace("Quantity", "Number of Items")
                # Add explicit markers for better parsing
                cleaned_section = f"[{section_label}] {cleaned_section}. NOTE: Percentages shown represent grade weights, not quantities."
            else:
                # Add clear section label for LLM understanding
                cleaned_section = f"[{section_label}] {cleaned_section}"

            cleaned_data[section_label] = cleaned_section

    return cleaned_data


def process_pdf(filepath, courseid, dept=None, code=None):
    """Process a single syllabus file and store it in the database."""
    try:
        print(f"Processing file: {filepath}")
        reader = PdfReader(filepath)
        pdf_texts = [
            page.extract_text().strip() for page in reader.pages if page.extract_text()
        ]

        if not pdf_texts:
            print(f"No valid text found in {filepath}. Skipping.")
            return

        # Try to extract structured sections from syllabus
        processed_data = preprocess_syllabus(pdf_texts)
        combined_text = "\n\n".join(processed_data.values())

        # Use processed data if available, otherwise fall back to raw text
        character_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=80,
            length_function=len,
            is_separator_regex=False,
        )

        if len(combined_text) > 0:
            character_split_texts = character_splitter.split_text(combined_text)
            print(f"Successfully extracted {len(processed_data)} structured sections")
        else:
            character_split_texts = character_splitter.split_text(
                "\n\n".join(pdf_texts)
            )
            print("Using raw text (structured sections not found)")

        print(f"Total character chunks: {len(character_split_texts)}")

        # Token splitting
        token_splitter = SentenceTransformersTokenTextSplitter(
            chunk_overlap=0, tokens_per_chunk=256
        )

        token_split_texts = [
            chunk
            for text in character_split_texts
            for chunk in token_splitter.split_text(text)
        ]

        print(f"Total token chunks: {len(token_split_texts)}")

        # Insert chunks into database
        dao = SyllabusDAO()

        # Create course prefix to prepend to each chunk for better retrieval
        course_prefix = f"{dept} {code}: " if dept and code else ""

        for i, chunk in enumerate(token_split_texts):
            # Prepend course code to chunk for accurate retrieval
            enhanced_chunk = course_prefix + chunk
            emb = model.encode(enhanced_chunk).tolist()
            print(f"Inserting chunk {i + 1}/{len(token_split_texts)}")
            dao.insertChunk(courseid, enhanced_chunk, emb)

        print(f"✓ Finished processing file: {filepath}\n")

    except Exception as e:
        print(f"✗ Error processing {filepath}: {e}\n")


def process_all_pdfs():
    classdao = ClassDAO()
    for filename in listdir(PDF_DIR):
        if not filename.lower().endswith(".pdf"):
            continue

        dept, code = extract_dept_code(filename)
        if not dept:
            print(
                f"Could not extract department and code from filename: {filename}. Skipping."
            )
            continue
        courseid = classdao.getCourseIDByCode(dept, code)
        if not courseid:
            print(f"No course found for {dept} {code}. Skipping file: {filename}.")
            continue
        filepath = os.path.join(PDF_DIR, filename)
        process_pdf(filepath, courseid, dept, code)


if __name__ == "__main__":
    process_all_pdfs()
