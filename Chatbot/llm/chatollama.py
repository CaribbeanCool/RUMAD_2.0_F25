import sys
import re

# import os
import time
from pathlib import Path
from sentence_transformers import SentenceTransformer
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Add project root to path FIRST
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from API.dao.syllabus import SyllabusDAO
from API.dao.classes import ClassDAO


MODEL = "all-mpnet-base-v2"


class ChatOllamaBot:
    def __init__(self, username):
        self.username = username
        self.model = SentenceTransformer(MODEL)

    def extract_course(self, question):
        match = re.search(r"(CIIC|ICOM|INSO)\s?(\d{4})", question.upper())
        if match:
            return match.group(1), match.group(2)
        return None, None

    def chat(self, question):
        start_time = time.time()

        # Extract course code from question
        dept, code = self.extract_course(question)

        # Enhance query for better embedding similarity
        enhanced_query = question
        if dept and code:
            enhanced_query = f"{dept} {code}: {question}"

        # Check if asking about textbooks/bibliography
        if any(
            keyword in question.lower()
            for keyword in ["textbook", "book", "bibliography", "reading", "material"]
        ):
            enhanced_query += " textbooks bibliography required reading materials"

        # Check if asking about grading/evaluation
        if any(
            keyword in question.lower()
            for keyword in [
                "grade",
                "grading",
                "evaluation",
                "exam",
                "percent",
                "score",
                "assessment",
            ]
        ):
            enhanced_query += " evaluation strategies grading percent breakdown"

        emb = self.model.encode(enhanced_query)

        dao = SyllabusDAO()
        classdao = ClassDAO()

        if dept and code:
            courseid = classdao.getCourseIDByCode(dept, code)
            if courseid:
                fragments = dao.getFragmentsByCourseAndEmbedding(courseid, emb)
            else:
                fragments = dao.getFragments(emb)
        else:
            fragments = dao.getFragments(emb)

        context = []
        for i, f in enumerate(fragments):
            context.append((f"Section {i + 1}: {f[2]}"))

        documents = "\\n".join(context)

        prompt = ChatPromptTemplate.from_template(
            template="""
            You are an assistant trained to answer questions based on syllabus documents.
            You must always greet the user by their username {username}. 
            Your role is to help users understand their syllabus, answer course-related questions, and provide information directly from the provided documents.

        Instructions:
        - Use the provided syllabus documents to answer questions as accurately as possible, only referencing the relevant course information.
        - If the user asks about a specific course (e.g., CIIC 4151), focus on the syllabus information related to that course.
        - Pay special attention to section labels like [Textbooks and Bibliography], [Grading System], [Prerequisites and Corequisites], etc.
        - When asked about textbooks, books, bibliography, or reading materials, look for the [Textbooks and Bibliography] section.
        - When asked about grading, grades, percentages, or evaluation, look for the [Evaluation Strategies] section.
        - CRITICAL: Look for numbers followed by "percent" (e.g., "35 percent", "25 percent", "40 percent") - these are the actual grade percentages.
        - IGNORE any standalone numbers that represent quantities or counts - only report percentages with the word "percent" or "%" symbol.
        - Present grading information clearly, showing only the items with actual percentages assigned.
        - When asked about prerequisites or corequisites, look for the [Prerequisites and Corequisites] section.
        - If the question is about requisites, grading, or other course-specific information, ensure the answer matches the exact course in the question.
        - If the syllabus does not contain the required information or the question cannot be answered, respond with: "Sorry, I don't know."
        - Keep your answers concise, confident, and ideally under five sentences. Use bullet points for clarity when listing multiple points.
        - Maintain a professional, helpful tone at all times.

        Context:
        {database_response}

        Current Question:
        {question}
        
        Answer:
        """
        )

        # print(prompt)
        # print(
        prompt.format(
            question=question, database_response=documents, username=self.username
        )
        # )

        llm = ChatOllama(
            model="llama3.2:latest",
            temperature=0,
        )
        rag_chain = prompt | llm | StrOutputParser()

        answer = rag_chain.invoke(
            {
                "username": self.username,
                "question": question,
                "database_response": documents,
            }
        )

        elapsed_time = time.time() - start_time
        print(f"Response time with model {llm.model}: {elapsed_time:.2f} seconds")

        # print(answer)
        return answer
