from fastapi import FastAPI, Query
from typing import Annotated
from QuizLLM import generateOutput, generateOuputFromPdf
from fastapi.responses import JSONResponse, Response
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI()
origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/quiz/")
async def get_quiz_from_topic(topic = Annotated[str, Query(max_length=50)]):
   llm_output = generateOutput(topic)
   return Response(content=json.dumps(llm_output, default=str), media_type='application/json')

@app.get("/quizFromPdf/")
async def get_quiz_from_pdf():
   llm_output = generateOuputFromPdf("./football_tutorial.pdf")
   return Response(content=json.dumps(llm_output, default=str), media_type='application/json')