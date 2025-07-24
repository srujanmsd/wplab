from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any, Union
import uuid
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Security
SECRET_KEY = "your-secret-key-change-this-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Authentication Models
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: str = "user"  # user or admin

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    full_name: str
    role: str = "user"
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Token(BaseModel):
    access_token: str
    token_type: str
    user: User

# Enhanced Question Models
class Question(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question_text: str
    question_type: str  # "multiple_choice" or "text"
    options: Optional[List[str]] = None  # For multiple choice questions
    correct_answer: Optional[str] = None  # For multiple choice questions
    explanation: Optional[str] = None
    points: int = 1  # Points for this question

class QuestionCreate(BaseModel):
    question_text: str
    question_type: str = "multiple_choice"
    options: Optional[List[str]] = None
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None
    points: int = 1

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
    total_points: int = 0
    is_active: bool = True
    requires_evaluation: bool = False  # True if has text questions

class QuizCreate(BaseModel):
    title: str
    subject: str
    description: Optional[str] = None
    questions: List[QuestionCreate]
    time_limit: Optional[int] = None

class QuizResponse(BaseModel):
    question_id: str
    selected_answer: Optional[str] = None  # For MCQ
    text_answer: Optional[str] = None  # For text questions

class QuizAttemptSubmission(BaseModel):
    responses: List[QuizResponse]
    time_taken: Optional[int] = None  # in seconds

class TextAnswerEvaluation(BaseModel):
    question_id: str
    points_awarded: int
    feedback: Optional[str] = None

class QuizEvaluation(BaseModel):
    result_id: str
    evaluations: List[TextAnswerEvaluation]

class QuizResult(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    quiz_id: str
    quiz_title: str
    user_id: str
    user_email: str
    user_name: str
    responses: List[QuizResponse]
    auto_score: int = 0  # Score from MCQ questions
    manual_score: int = 0  # Score from evaluated text questions
    total_score: int = 0
    max_possible_score: int = 0
    percentage: float = 0.0
    time_taken: Optional[int] = None
    completed_at: datetime = Field(default_factory=datetime.utcnow)
    is_evaluated: bool = False
    is_published: bool = False
    detailed_results: List[Dict[str, Any]] = []
    evaluations: List[TextAnswerEvaluation] = []

# Authentication Helper Functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await db.users.find_one({"email": email}, {"_id": 0})
    if user is None:
        raise credentials_exception
    return User(**user)

async def get_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

@api_router.post("/register", response_model=User)
async def register_user(user_data: UserCreate):
    try:
        # Check if user already exists
        existing_user = await db.users.find_one({"email": user_data.email})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password and create user
        hashed_password = get_password_hash(user_data.password)
        user_dict = user_data.dict()
        user_dict.pop("password")
        user_dict["hashed_password"] = hashed_password
        user_dict["id"] = str(uuid.uuid4())
        user_dict["is_active"] = True
        user_dict["created_at"] = datetime.utcnow()
        
        # Insert to database
        await db.users.insert_one(user_dict)
        
        # Return user without password
        response_dict = user_dict.copy()
        response_dict.pop("hashed_password")
        return User(**response_dict)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")

@api_router.post("/login", response_model=Token)
async def login_user(user_credentials: UserLogin):
    try:
        # Find user by email
        user_data = await db.users.find_one({"email": user_credentials.email}, {"_id": 0})
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Check if user has hashed_password field
        if "hashed_password" not in user_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User data corrupted. Please contact administrator."
            )
        
        # Verify password
        if not verify_password(user_credentials.password, user_data["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user_data["email"]}, expires_delta=access_token_expires
        )
        
        user_data.pop("hashed_password")  # Remove password from response
        user = User(**user_data)
        
        return Token(access_token=access_token, token_type="bearer", user=user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during login: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login error: {str(e)}")

@api_router.get("/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

# Enhanced Quiz Management Endpoints
@api_router.post("/quizzes", response_model=Quiz)
async def create_quiz(quiz_data: QuizCreate, current_user: User = Depends(get_admin_user)):
    """Create a new quiz (Admin only)"""
    try:
        # Convert QuestionCreate to Question models
        questions = []
        total_points = 0
        requires_evaluation = False
        
        for q in quiz_data.questions:
            question = Question(**q.dict())
            questions.append(question)
            total_points += question.points
            if question.question_type == "text":
                requires_evaluation = True
        
        quiz_dict = quiz_data.dict()
        quiz_dict['questions'] = [q.dict() for q in questions]
        quiz_dict['total_questions'] = len(questions)
        quiz_dict['total_points'] = total_points
        quiz_dict['requires_evaluation'] = requires_evaluation
        quiz_dict['created_by'] = current_user.email
        
        quiz = Quiz(**quiz_dict)
        
        # Insert into database
        await db.quizzes.insert_one(quiz.dict())
        
        return quiz
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating quiz: {str(e)}")

@api_router.get("/quizzes", response_model=List[Dict[str, Any]])
async def get_all_quizzes(current_user: User = Depends(get_current_user)):
    """Get all available quizzes"""
    try:
        quizzes = await db.quizzes.find(
            {"is_active": True},
            {
                "_id": 0, "id": 1, "title": 1, "subject": 1, "description": 1,
                "total_questions": 1, "total_points": 1, "time_limit": 1, 
                "created_at": 1, "requires_evaluation": 1
            }
        ).to_list(1000)
        
        return quizzes
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching quizzes: {str(e)}")

@api_router.get("/quizzes/{quiz_id}")
async def get_quiz(quiz_id: str, current_user: User = Depends(get_current_user)):
    """Get a specific quiz for taking"""
    try:
        quiz = await db.quizzes.find_one({"id": quiz_id, "is_active": True}, {"_id": 0})
        
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")
        
        # Remove correct answers from MCQ questions for quiz taking
        safe_questions = []
        for question in quiz['questions']:
            safe_question = {
                "id": question['id'],
                "question_text": question['question_text'],
                "question_type": question['question_type'],
                "points": question['points']
            }
            
            if question['question_type'] == "multiple_choice":
                safe_question['options'] = question['options']
            
            safe_questions.append(safe_question)
        
        quiz['questions'] = safe_questions
        return quiz
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching quiz: {str(e)}")

@api_router.post("/quizzes/{quiz_id}/attempt", response_model=QuizResult)
async def submit_quiz_attempt(quiz_id: str, attempt: QuizAttemptSubmission, current_user: User = Depends(get_current_user)):
    """Submit quiz responses and get results"""
    try:
        # Get the quiz with correct answers
        quiz = await db.quizzes.find_one({"id": quiz_id, "is_active": True}, {"_id": 0})
        
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")
        
        # Create a lookup for questions
        questions_lookup = {}
        for question in quiz['questions']:
            questions_lookup[question['id']] = question
        
        # Calculate auto score (MCQ only) and prepare detailed results
        auto_score = 0
        detailed_results = []
        
        for response in attempt.responses:
            question_id = response.question_id
            question_data = questions_lookup.get(question_id, {})
            
            if question_data.get('question_type') == 'multiple_choice':
                selected_answer = response.selected_answer
                correct_answer = question_data.get('correct_answer')
                
                is_correct = selected_answer == correct_answer
                points_earned = question_data.get('points', 1) if is_correct else 0
                auto_score += points_earned
                
                detailed_results.append({
                    "question_id": question_id,
                    "question_text": question_data.get('question_text', ''),
                    "question_type": "multiple_choice",
                    "selected_answer": selected_answer,
                    "correct_answer": correct_answer,
                    "is_correct": is_correct,
                    "points_possible": question_data.get('points', 1),
                    "points_earned": points_earned,
                    "explanation": question_data.get('explanation', '')
                })
            
            elif question_data.get('question_type') == 'text':
                detailed_results.append({
                    "question_id": question_id,
                    "question_text": question_data.get('question_text', ''),
                    "question_type": "text",
                    "text_answer": response.text_answer,
                    "points_possible": question_data.get('points', 1),
                    "points_earned": 0,  # Will be updated after evaluation
                    "is_evaluated": False
                })
        
        # Create result object
        is_evaluated = not quiz.get('requires_evaluation', False)  # Auto-evaluated if no text questions
        total_score = auto_score  # Will be updated after manual evaluation
        max_possible_score = quiz.get('total_points', 0)
        percentage = (total_score / max_possible_score * 100) if max_possible_score > 0 else 0
        
        result = QuizResult(
            quiz_id=quiz_id,
            quiz_title=quiz['title'],
            user_id=current_user.id,
            user_email=current_user.email,
            user_name=current_user.full_name,
            responses=attempt.responses,
            auto_score=auto_score,
            manual_score=0,
            total_score=total_score,
            max_possible_score=max_possible_score,
            percentage=round(percentage, 2),
            time_taken=attempt.time_taken,
            is_evaluated=is_evaluated,
            is_published=is_evaluated,  # Auto-publish if no manual evaluation needed
            detailed_results=detailed_results
        )
        
        # Save result to database
        await db.quiz_results.insert_one(result.dict())
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing quiz attempt: {str(e)}")

# Admin Evaluation Endpoints
@api_router.get("/admin/results/pending")
async def get_pending_evaluations(current_user: User = Depends(get_admin_user)):
    """Get quiz results that need manual evaluation"""
    try:
        results = await db.quiz_results.find(
            {"is_evaluated": False},
            {"_id": 0}
        ).sort("completed_at", 1).to_list(1000)
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching pending evaluations: {str(e)}")

@api_router.post("/admin/evaluate/{result_id}")
async def evaluate_quiz_result(result_id: str, evaluation: QuizEvaluation, current_user: User = Depends(get_admin_user)):
    """Evaluate text questions and update result"""
    try:
        # Get the result
        result = await db.quiz_results.find_one({"id": result_id}, {"_id": 0})
        if not result:
            raise HTTPException(status_code=404, detail="Result not found")
        
        # Calculate manual score
        manual_score = sum(eval.points_awarded for eval in evaluation.evaluations)
        total_score = result['auto_score'] + manual_score
        max_possible_score = result['max_possible_score']
        percentage = (total_score / max_possible_score * 100) if max_possible_score > 0 else 0
        
        # Update detailed results with evaluation
        detailed_results = result['detailed_results']
        evaluation_lookup = {eval.question_id: eval for eval in evaluation.evaluations}
        
        for detail in detailed_results:
            if detail['question_type'] == 'text' and detail['question_id'] in evaluation_lookup:
                eval_data = evaluation_lookup[detail['question_id']]
                detail['points_earned'] = eval_data.points_awarded
                detail['feedback'] = eval_data.feedback
                detail['is_evaluated'] = True
        
        # Update result in database
        await db.quiz_results.update_one(
            {"id": result_id},
            {
                "$set": {
                    "manual_score": manual_score,
                    "total_score": total_score,
                    "percentage": round(percentage, 2),
                    "is_evaluated": True,
                    "detailed_results": detailed_results,
                    "evaluations": [eval.dict() for eval in evaluation.evaluations]
                }
            }
        )
        
        return {"message": "Evaluation completed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error evaluating result: {str(e)}")

@api_router.post("/admin/publish/{result_id}")
async def publish_result(result_id: str, current_user: User = Depends(get_admin_user)):
    """Publish a quiz result"""
    try:
        result = await db.quiz_results.update_one(
            {"id": result_id},
            {"$set": {"is_published": True}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Result not found")
        
        return {"message": "Result published successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error publishing result: {str(e)}")

@api_router.post("/admin/publish-all/{quiz_id}")
async def publish_all_results(quiz_id: str, current_user: User = Depends(get_admin_user)):
    """Publish all evaluated results for a quiz"""
    try:
        result = await db.quiz_results.update_many(
            {"quiz_id": quiz_id, "is_evaluated": True},
            {"$set": {"is_published": True}}
        )
        
        return {"message": f"Published {result.modified_count} results"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error publishing results: {str(e)}")

# Results Endpoints
@api_router.get("/results/{result_id}", response_model=QuizResult)
async def get_quiz_result(result_id: str, current_user: User = Depends(get_current_user)):
    """Get quiz result by ID"""
    try:
        result = await db.quiz_results.find_one({"id": result_id}, {"_id": 0})
        
        if not result:
            raise HTTPException(status_code=404, detail="Result not found")
        
        # Users can only see their own results unless they're admin
        if current_user.role != "admin" and result['user_id'] != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return QuizResult(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching result: {str(e)}")

@api_router.get("/results/my/all")
async def get_my_results(current_user: User = Depends(get_current_user)):
    """Get all results for current user"""
    try:
        results = await db.quiz_results.find(
            {"user_id": current_user.id, "is_published": True},
            {"_id": 0}
        ).sort("completed_at", -1).to_list(1000)
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching results: {str(e)}")

@api_router.get("/results/published/{quiz_id}")
async def get_published_results(quiz_id: str, current_user: User = Depends(get_current_user)):
    """Get all published results for a quiz"""
    try:
        results = await db.quiz_results.find(
            {"quiz_id": quiz_id, "is_published": True},
            {
                "_id": 0, "id": 1, "user_name": 1, "user_email": 1,
                "total_score": 1, "max_possible_score": 1, "percentage": 1,
                "completed_at": 1
            }
        ).sort("percentage", -1).to_list(1000)
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching published results: {str(e)}")

@api_router.get("/admin/results")
async def get_all_results(current_user: User = Depends(get_admin_user)):
    """Get all quiz results for admin"""
    try:
        results = await db.quiz_results.find({}, {"_id": 0}).sort("completed_at", -1).to_list(1000)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching results: {str(e)}")

# Health check endpoint
@api_router.get("/")
async def root():
    return {"message": "Mini Quiz Platform API with Authentication", "status": "running"}

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