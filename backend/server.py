from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Define Models
class Question(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question_text: str
    question_type: str = "multiple_choice"  # multiple_choice, true_false
    options: List[str]  # For multiple choice questions
    correct_answer: str
    explanation: Optional[str] = None

class QuestionCreate(BaseModel):
    question_text: str
    question_type: str = "multiple_choice"
    options: List[str]
    correct_answer: str
    explanation: Optional[str] = None

class Quiz(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    subject: str
    description: Optional[str] = None
    questions: List[Question]
    created_by: str = "admin"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    time_limit: Optional[int] = None  # in minutes
    total_questions: int = 0
    is_active: bool = True

class QuizCreate(BaseModel):
    title: str
    subject: str
    description: Optional[str] = None
    questions: List[QuestionCreate]
    time_limit: Optional[int] = None

class QuizResponse(BaseModel):
    question_id: str
    selected_answer: str

class QuizAttemptSubmission(BaseModel):
    responses: List[QuizResponse]
    time_taken: Optional[int] = None  # in seconds

class QuizResult(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    quiz_id: str
    quiz_title: str
    student_name: Optional[str] = None
    responses: List[QuizResponse]
    score: int
    total_questions: int
    percentage: float
    correct_answers: int
    incorrect_answers: int
    time_taken: Optional[int] = None
    completed_at: datetime = Field(default_factory=datetime.utcnow)
    detailed_results: List[Dict[str, Any]] = []

# Quiz Management Endpoints
@api_router.post("/quizzes", response_model=Quiz)
async def create_quiz(quiz_data: QuizCreate):
    """Create a new quiz"""
    try:
        # Convert QuestionCreate to Question models
        questions = []
        for q in quiz_data.questions:
            question = Question(**q.dict())
            questions.append(question)
        
        quiz_dict = quiz_data.dict()
        quiz_dict['questions'] = [q.dict() for q in questions]
        quiz_dict['total_questions'] = len(questions)
        
        quiz = Quiz(**quiz_dict)
        
        # Insert into database
        await db.quizzes.insert_one(quiz.dict())
        
        return quiz
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating quiz: {str(e)}")

@api_router.get("/quizzes", response_model=List[Dict[str, Any]])
async def get_all_quizzes():
    """Get all available quizzes (without questions for listing)"""
    try:
        quizzes = await db.quizzes.find(
            {"is_active": True},
            {
                "_id": 0, "id": 1, "title": 1, "subject": 1, "description": 1,
                "total_questions": 1, "time_limit": 1, "created_at": 1
            }
        ).to_list(1000)
        
        return quizzes
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching quizzes: {str(e)}")

@api_router.get("/quizzes/{quiz_id}")
async def get_quiz(quiz_id: str):
    """Get a specific quiz for taking (without correct answers)"""
    try:
        quiz = await db.quizzes.find_one({"id": quiz_id, "is_active": True}, {"_id": 0})
        
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")
        
        # Remove correct answers from questions for quiz taking
        safe_questions = []
        for question in quiz['questions']:
            safe_question = {
                "id": question['id'],
                "question_text": question['question_text'],
                "question_type": question['question_type'],
                "options": question['options']
            }
            safe_questions.append(safe_question)
        
        quiz['questions'] = safe_questions
        return quiz
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching quiz: {str(e)}")

@api_router.post("/quizzes/{quiz_id}/attempt", response_model=QuizResult)
async def submit_quiz_attempt(quiz_id: str, attempt: QuizAttemptSubmission, student_name: Optional[str] = None):
    """Submit quiz responses and get results"""
    try:
        # Get the quiz with correct answers
        quiz = await db.quizzes.find_one({"id": quiz_id, "is_active": True})
        
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")
        
        # Create a lookup for correct answers
        correct_answers = {}
        questions_lookup = {}
        for question in quiz['questions']:
            correct_answers[question['id']] = question['correct_answer']
            questions_lookup[question['id']] = question
        
        # Calculate score
        correct_count = 0
        total_questions = len(quiz['questions'])
        detailed_results = []
        
        for response in attempt.responses:
            question_id = response.question_id
            selected_answer = response.selected_answer
            correct_answer = correct_answers.get(question_id)
            
            is_correct = selected_answer == correct_answer
            if is_correct:
                correct_count += 1
            
            # Add detailed result
            question_data = questions_lookup.get(question_id, {})
            detailed_results.append({
                "question_id": question_id,
                "question_text": question_data.get('question_text', ''),
                "selected_answer": selected_answer,
                "correct_answer": correct_answer,
                "is_correct": is_correct,
                "explanation": question_data.get('explanation', '')
            })
        
        # Calculate percentage
        percentage = (correct_count / total_questions) * 100 if total_questions > 0 else 0
        
        # Create result object
        result = QuizResult(
            quiz_id=quiz_id,
            quiz_title=quiz['title'],
            student_name=student_name,
            responses=attempt.responses,
            score=correct_count,
            total_questions=total_questions,
            percentage=round(percentage, 2),
            correct_answers=correct_count,
            incorrect_answers=total_questions - correct_count,
            time_taken=attempt.time_taken,
            detailed_results=detailed_results
        )
        
        # Save result to database
        await db.quiz_results.insert_one(result.dict())
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing quiz attempt: {str(e)}")

@api_router.get("/results/{result_id}", response_model=QuizResult)
async def get_quiz_result(result_id: str):
    """Get quiz result by ID"""
    try:
        result = await db.quiz_results.find_one({"id": result_id})
        
        if not result:
            raise HTTPException(status_code=404, detail="Result not found")
        
        return QuizResult(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching result: {str(e)}")

@api_router.get("/admin/results")
async def get_all_results():
    """Get all quiz results for admin"""
    try:
        results = await db.quiz_results.find().sort("completed_at", -1).to_list(1000)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching results: {str(e)}")

# Health check endpoint
@api_router.get("/")
async def root():
    return {"message": "Mini Quiz Platform API", "status": "running"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()