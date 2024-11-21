from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_ollama import OllamaEmbeddings
import re
import json

def parseOuput(output: str):
    
    question_pattern = r'Question:\s([\da-zA-Z0-9À-ž" ",\(\)\'\-\.]*)\??\n?'
    answers_pattern = r'Answers:\s?\n?\\?n?[A-Z]\)\s([\da-zA-Z0-9À-ž" ",\(\)\'\-\.]*)\s?\n?\\?n?[A-Z]\)\s([\da-zA-Z0-9À-ž" ",\(\)\'\-\.]*)\s?\n?\\?n?[A-Z]\)\s([\da-zA-Z0-9À-ž" ",\(\)\'\-\.]*)\s?\n?\\?n?[A-Z]\)\s([\da-zA-Z0-9À-ž" ",\(\)\'\-\.]*)\s?\n?\\?n?'
    correct_answer_pattern = r'Correct Answer:\s[A-Z]?\)?\s?([A-Z\d][\da-zA-Z0-9À-ž" ",\(\)\'\-\.]*)'

    questions = re.findall(question_pattern, output)
    answers = re.findall(answers_pattern, output)
    correct_answers= re.findall(correct_answer_pattern, output)
    
    return createJson(questions, answers, correct_answers)


def createJson(questions: list, answers:list, correct_answers:list):
    json_list= []
    for i,question in enumerate(questions):
        
        item = {
             
            'question': question,
            'answers': answers[i],
            'correct_answer': correct_answers[i],
            
        }
        json_list.append(item)
    
    return json.dumps(json_list)


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def generateOuputFromPdf(file_path: str):
    loader = PyPDFLoader(file_path)
    docs = loader.load()    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)
    vectorstore = InMemoryVectorStore.from_documents(
        documents=splits, embedding=OllamaEmbeddings(model="llama3.2")
    )

    llm = OllamaLLM(model="llama3.2")

    retriever = vectorstore.as_retriever()


    system_prompt_quesitons = """You are an assistant for creating quiz questions.
                            Use the following pieces of retrieved context to create five questions. 
                            Use the following pieces of retrieved context to answer the questions, and create three wrong answers as well. 
                           The questions you create must be answerable with one sentence only. 
                           The output must use the following template for all five questions:
                        Question: the question asked
                        Answers: One correct answer and three wrong answers. The three wrong answers must be different than the correct answer. The format for the answers must be:
                        Answers: 
                        A) Answer
                        B) Answer
                        C) Answer
                        D) Answer
                        Correct Answer: The correct answer.

                        Ignore everything after context  {context} {ignore}"""


    questions_prompt = ChatPromptTemplate.from_template(system_prompt_quesitons)

    rag_chain =(
        {"context": retriever | format_docs, 'ignore': RunnablePassthrough()}
        | questions_prompt
        | llm
        | StrOutputParser()
    )

    output=""
    for chunk in rag_chain.invoke("ignore"):
        output = output+chunk
    return parseOuput(output)

def generateOutput(topic: str):
    questions_template = """Create 5 different questions about {topic}, that can be answered with one word only. """

    questions_prompt = ChatPromptTemplate.from_template(questions_template)

    answer_template = """Answer these {questions} using only one word.
    Use the following template:
    Question: The question
    Answers: One correct answer and three wrong answers. The three wrong answers must be different than the correct answer. The format for the answers must be:
    Answers: 
    A) Answer
    B) Answer
    C) Answer
    D) Answer
    Correct Answer: The correct answer.
    """
    answer_prompt = ChatPromptTemplate.from_template(answer_template)

    llm = OllamaLLM(model="llama3.2")

    question_chain = questions_prompt | llm

    answer_chain = {'questions': question_chain} | answer_prompt | llm
    output = answer_chain.invoke({"topic": topic})
    print(output)
    return parseOuput(output)


    