#!/usr/bin/env python3
"""
Backend API Testing for Mini Quiz Platform with Authentication
Tests authentication, quiz management, evaluation system, and result publishing
"""

import requests
import json
import time
from typing import Dict, List, Any
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from frontend environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE_URL = f"{BACKEND_URL}/api"

class QuizPlatformTester:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.session = requests.Session()
        self.admin_token = None
        self.user_token = None
        self.admin_user = None
        self.regular_user = None
        self.created_quiz_id = None
        self.created_result_id = None
        
    def log_test(self, test_name: str, status: str, details: str = ""):
        """Log test results"""
        status_symbol = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_symbol} {test_name}: {status}")
        if details:
            print(f"   Details: {details}")
        print()

    def test_health_check(self) -> bool:
        """Test GET /api/ - Health check endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/")
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "status" in data:
                    self.log_test("Health Check", "PASS", f"API is running: {data['message']}")
                    return True
                else:
                    self.log_test("Health Check", "FAIL", "Response missing required fields")
                    return False
            else:
                self.log_test("Health Check", "FAIL", f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Health Check", "FAIL", f"Exception: {str(e)}")
            return False

    def test_user_registration(self) -> bool:
        """Test POST /api/register - User registration"""
        try:
            # Register admin user
            admin_data = {
                "email": "admin@quizplatform.com",
                "password": "AdminPass123!",
                "full_name": "Quiz Administrator",
                "role": "admin"
            }
            
            response = self.session.post(
                f"{self.base_url}/register",
                json=admin_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                admin_user = response.json()
                required_fields = ["id", "email", "full_name", "role", "is_active"]
                
                if all(field in admin_user for field in required_fields):
                    if admin_user["role"] == "admin" and admin_user["email"] == admin_data["email"]:
                        self.admin_user = admin_user
                        
                        # Register regular user
                        user_data = {
                            "email": "student@quizplatform.com",
                            "password": "StudentPass123!",
                            "full_name": "John Student",
                            "role": "user"
                        }
                        
                        user_response = self.session.post(
                            f"{self.base_url}/register",
                            json=user_data,
                            headers={"Content-Type": "application/json"}
                        )
                        
                        if user_response.status_code == 200:
                            regular_user = user_response.json()
                            if regular_user["role"] == "user":
                                self.regular_user = regular_user
                                self.log_test("User Registration", "PASS", "Both admin and user registered successfully")
                                return True
                            else:
                                self.log_test("User Registration", "FAIL", "User role incorrect")
                                return False
                        else:
                            self.log_test("User Registration", "FAIL", f"User registration failed: {user_response.status_code}")
                            return False
                    else:
                        self.log_test("User Registration", "FAIL", "Admin user data incorrect")
                        return False
                else:
                    self.log_test("User Registration", "FAIL", "Response missing required fields")
                    return False
            else:
                self.log_test("User Registration", "FAIL", f"Status code: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("User Registration", "FAIL", f"Exception: {str(e)}")
            return False

    def test_user_login(self) -> bool:
        """Test POST /api/login - User login and JWT token generation"""
        try:
            # Login admin user
            admin_login = {
                "email": "admin@quizplatform.com",
                "password": "AdminPass123!"
            }
            
            response = self.session.post(
                f"{self.base_url}/login",
                json=admin_login,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                token_data = response.json()
                required_fields = ["access_token", "token_type", "user"]
                
                if all(field in token_data for field in required_fields):
                    if token_data["token_type"] == "bearer" and token_data["user"]["role"] == "admin":
                        self.admin_token = token_data["access_token"]
                        
                        # Login regular user
                        user_login = {
                            "email": "student@quizplatform.com",
                            "password": "StudentPass123!"
                        }
                        
                        user_response = self.session.post(
                            f"{self.base_url}/login",
                            json=user_login,
                            headers={"Content-Type": "application/json"}
                        )
                        
                        if user_response.status_code == 200:
                            user_token_data = user_response.json()
                            if user_token_data["user"]["role"] == "user":
                                self.user_token = user_token_data["access_token"]
                                self.log_test("User Login", "PASS", "Both admin and user login successful with JWT tokens")
                                return True
                            else:
                                self.log_test("User Login", "FAIL", "User login role incorrect")
                                return False
                        else:
                            self.log_test("User Login", "FAIL", f"User login failed: {user_response.status_code}")
                            return False
                    else:
                        self.log_test("User Login", "FAIL", "Admin login data incorrect")
                        return False
                else:
                    self.log_test("User Login", "FAIL", "Response missing required fields")
                    return False
            else:
                self.log_test("User Login", "FAIL", f"Status code: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("User Login", "FAIL", f"Exception: {str(e)}")
            return False

    def test_protected_profile_endpoint(self) -> bool:
        """Test GET /api/me - Protected profile endpoint"""
        try:
            if not self.user_token:
                self.log_test("Protected Profile Endpoint", "FAIL", "No user token available")
                return False
            
            # Test with valid token
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = self.session.get(f"{self.base_url}/me", headers=headers)
            
            if response.status_code == 200:
                user_data = response.json()
                required_fields = ["id", "email", "full_name", "role"]
                
                if all(field in user_data for field in required_fields):
                    if user_data["email"] == "student@quizplatform.com":
                        # Test without token (should fail)
                        no_auth_response = self.session.get(f"{self.base_url}/me")
                        
                        if no_auth_response.status_code == 401:
                            self.log_test("Protected Profile Endpoint", "PASS", "Profile endpoint properly protected")
                            return True
                        else:
                            self.log_test("Protected Profile Endpoint", "FAIL", "Endpoint not properly protected")
                            return False
                    else:
                        self.log_test("Protected Profile Endpoint", "FAIL", "Wrong user data returned")
                        return False
                else:
                    self.log_test("Protected Profile Endpoint", "FAIL", "Response missing required fields")
                    return False
            else:
                self.log_test("Protected Profile Endpoint", "FAIL", f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Protected Profile Endpoint", "FAIL", f"Exception: {str(e)}")
            return False

    def test_role_based_access(self) -> bool:
        """Test role-based access control"""
        try:
            if not self.user_token or not self.admin_token:
                self.log_test("Role-based Access Control", "FAIL", "Missing tokens for testing")
                return False
            
            # Test user trying to access admin endpoint (should fail)
            user_headers = {"Authorization": f"Bearer {self.user_token}"}
            response = self.session.get(f"{self.base_url}/admin/results", headers=user_headers)
            
            if response.status_code == 403:
                # Test admin accessing admin endpoint (should succeed)
                admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
                admin_response = self.session.get(f"{self.base_url}/admin/results", headers=admin_headers)
                
                if admin_response.status_code == 200:
                    self.log_test("Role-based Access Control", "PASS", "Role-based access properly enforced")
                    return True
                else:
                    self.log_test("Role-based Access Control", "FAIL", "Admin access failed")
                    return False
            else:
                self.log_test("Role-based Access Control", "FAIL", "User access not properly restricted")
                return False
                
        except Exception as e:
            self.log_test("Role-based Access Control", "FAIL", f"Exception: {str(e)}")
            return False

    def test_create_quiz_with_mixed_questions(self) -> bool:
        """Test POST /api/quizzes - Create quiz with both MCQ and text questions"""
        try:
            if not self.admin_token:
                self.log_test("Create Quiz with Mixed Questions", "FAIL", "No admin token available")
                return False
            
            # Create a comprehensive quiz with mixed question types
            quiz_data = {
                "title": "Advanced Python Programming Assessment",
                "subject": "Computer Science",
                "description": "Comprehensive assessment covering Python concepts with both multiple choice and text-based questions",
                "time_limit": 45,
                "questions": [
                    {
                        "question_text": "What is the correct way to create a list in Python?",
                        "question_type": "multiple_choice",
                        "options": ["list = []", "list = {}", "list = ()", "list = <>"],
                        "correct_answer": "list = []",
                        "explanation": "Square brackets [] are used to create lists in Python",
                        "points": 2
                    },
                    {
                        "question_text": "Which keyword is used to define a function in Python?",
                        "question_type": "multiple_choice", 
                        "options": ["function", "def", "func", "define"],
                        "correct_answer": "def",
                        "explanation": "The 'def' keyword is used to define functions in Python",
                        "points": 2
                    },
                    {
                        "question_text": "Explain the difference between a list and a tuple in Python. Provide examples and discuss when you would use each.",
                        "question_type": "text",
                        "points": 5
                    },
                    {
                        "question_text": "Write a Python function that takes a list of numbers and returns the sum of all even numbers. Explain your approach.",
                        "question_type": "text",
                        "points": 6
                    }
                ]
            }
            
            headers = {"Authorization": f"Bearer {self.admin_token}", "Content-Type": "application/json"}
            response = self.session.post(f"{self.base_url}/quizzes", json=quiz_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["id", "title", "subject", "questions", "total_questions", "total_points", "requires_evaluation"]
                
                if all(field in data for field in required_fields):
                    self.created_quiz_id = data["id"]
                    if (data["total_questions"] == 4 and 
                        data["total_points"] == 15 and 
                        data["requires_evaluation"] == True):
                        self.log_test("Create Quiz with Mixed Questions", "PASS", 
                                    f"Quiz created with mixed questions, total points: {data['total_points']}")
                        return True
                    else:
                        self.log_test("Create Quiz with Mixed Questions", "FAIL", 
                                    f"Quiz metadata incorrect: questions={data['total_questions']}, points={data['total_points']}, eval={data['requires_evaluation']}")
                        return False
                else:
                    self.log_test("Create Quiz with Mixed Questions", "FAIL", "Response missing required fields")
                    return False
            else:
                self.log_test("Create Quiz with Mixed Questions", "FAIL", f"Status code: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Create Quiz with Mixed Questions", "FAIL", f"Exception: {str(e)}")
            return False

    def test_list_quizzes_authenticated(self) -> bool:
        """Test GET /api/quizzes - List all quizzes (authenticated)"""
        try:
            if not self.user_token:
                self.log_test("List Quizzes (Authenticated)", "FAIL", "No user token available")
                return False
            
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = self.session.get(f"{self.base_url}/quizzes", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list):
                    if len(data) > 0:
                        # Check if our created quiz is in the list
                        quiz_found = False
                        for quiz in data:
                            if quiz.get("id") == self.created_quiz_id:
                                quiz_found = True
                                # Verify that questions are not included in listing
                                if ("questions" not in quiz and 
                                    "requires_evaluation" in quiz and
                                    quiz["requires_evaluation"] == True):
                                    self.log_test("List Quizzes (Authenticated)", "PASS", 
                                                f"Found {len(data)} quizzes, metadata properly included")
                                    return True
                                else:
                                    self.log_test("List Quizzes (Authenticated)", "FAIL", 
                                                "Quiz listing format incorrect")
                                    return False
                        
                        if not quiz_found:
                            self.log_test("List Quizzes (Authenticated)", "FAIL", "Created quiz not found in listing")
                            return False
                    else:
                        self.log_test("List Quizzes (Authenticated)", "PASS", "Empty quiz list returned")
                        return True
                else:
                    self.log_test("List Quizzes (Authenticated)", "FAIL", "Response is not a list")
                    return False
            else:
                self.log_test("List Quizzes (Authenticated)", "FAIL", f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("List Quizzes (Authenticated)", "FAIL", f"Exception: {str(e)}")
            return False

    def test_get_quiz_for_taking_mixed(self) -> bool:
        """Test GET /api/quizzes/{quiz_id} - Get quiz with mixed question types"""
        try:
            if not self.created_quiz_id or not self.user_token:
                self.log_test("Get Quiz for Taking (Mixed)", "FAIL", "Missing quiz ID or token")
                return False
                
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = self.session.get(f"{self.base_url}/quizzes/{self.created_quiz_id}", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                required_fields = ["id", "title", "subject", "questions"]
                if all(field in data for field in required_fields):
                    questions = data["questions"]
                    
                    # Verify mixed question types and proper data structure
                    mcq_count = 0
                    text_count = 0
                    answers_hidden = True
                    
                    for question in questions:
                        if question["question_type"] == "multiple_choice":
                            mcq_count += 1
                            # MCQ should have options but no correct_answer
                            if "options" not in question or "correct_answer" in question:
                                answers_hidden = False
                                break
                        elif question["question_type"] == "text":
                            text_count += 1
                            # Text questions should not have options or correct_answer
                            if "options" in question or "correct_answer" in question:
                                self.log_test("Get Quiz for Taking (Mixed)", "FAIL", "Text question has invalid fields")
                                return False
                        
                        # All questions should have required fields
                        required_q_fields = ["id", "question_text", "question_type", "points"]
                        if not all(field in question for field in required_q_fields):
                            self.log_test("Get Quiz for Taking (Mixed)", "FAIL", "Question missing required fields")
                            return False
                    
                    if mcq_count == 2 and text_count == 2 and answers_hidden:
                        self.log_test("Get Quiz for Taking (Mixed)", "PASS", 
                                    f"Mixed quiz retrieved correctly: {mcq_count} MCQ, {text_count} text questions")
                        return True
                    else:
                        self.log_test("Get Quiz for Taking (Mixed)", "FAIL", 
                                    f"Question types or security incorrect: MCQ={mcq_count}, Text={text_count}, Hidden={answers_hidden}")
                        return False
                else:
                    self.log_test("Get Quiz for Taking (Mixed)", "FAIL", "Response missing required fields")
                    return False
            else:
                self.log_test("Get Quiz for Taking (Mixed)", "FAIL", f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Get Quiz for Taking (Mixed)", "FAIL", f"Exception: {str(e)}")
            return False
    def test_submit_mixed_quiz_attempt(self) -> bool:
        """Test POST /api/quizzes/{quiz_id}/attempt - Submit mixed quiz responses"""
        try:
            if not self.created_quiz_id or not self.user_token:
                self.log_test("Submit Mixed Quiz Attempt", "FAIL", "Missing quiz ID or token")
                return False
            
            # First get the quiz to know question IDs
            headers = {"Authorization": f"Bearer {self.user_token}"}
            quiz_response = self.session.get(f"{self.base_url}/quizzes/{self.created_quiz_id}", headers=headers)
            if quiz_response.status_code != 200:
                self.log_test("Submit Mixed Quiz Attempt", "FAIL", "Could not retrieve quiz for attempt")
                return False
                
            quiz_data = quiz_response.json()
            questions = quiz_data["questions"]
            
            # Create responses for mixed question types
            responses = []
            for question in questions:
                if question["question_type"] == "multiple_choice":
                    if "list" in question["question_text"].lower():
                        responses.append({
                            "question_id": question["id"],
                            "selected_answer": "list = []"  # Correct answer
                        })
                    elif "function" in question["question_text"].lower():
                        responses.append({
                            "question_id": question["id"],
                            "selected_answer": "def"  # Correct answer
                        })
                elif question["question_type"] == "text":
                    if "list and tuple" in question["question_text"].lower():
                        responses.append({
                            "question_id": question["id"],
                            "text_answer": "Lists are mutable and use square brackets [], while tuples are immutable and use parentheses (). Example: my_list = [1, 2, 3] can be modified, but my_tuple = (1, 2, 3) cannot be changed after creation. Use lists when you need to modify data, tuples for fixed data."
                        })
                    elif "function" in question["question_text"].lower() and "sum" in question["question_text"].lower():
                        responses.append({
                            "question_id": question["id"],
                            "text_answer": "def sum_even_numbers(numbers):\n    return sum(num for num in numbers if num % 2 == 0)\n\nThis function uses a generator expression to filter even numbers and sum them efficiently."
                        })
            
            attempt_data = {
                "responses": responses,
                "time_taken": 2700  # 45 minutes in seconds
            }
            
            response = self.session.post(
                f"{self.base_url}/quizzes/{self.created_quiz_id}/attempt",
                json=attempt_data,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                
                required_fields = ["id", "quiz_id", "auto_score", "manual_score", "total_score", 
                                 "max_possible_score", "percentage", "is_evaluated", "is_published", "detailed_results"]
                
                if all(field in result for field in required_fields):
                    # Verify scoring for mixed questions
                    expected_auto_score = 4  # 2 MCQ questions worth 2 points each
                    expected_manual_score = 0  # Text questions not yet evaluated
                    expected_total_score = 4
                    expected_max_score = 15  # Total points from all questions
                    
                    if (result["auto_score"] == expected_auto_score and 
                        result["manual_score"] == expected_manual_score and
                        result["total_score"] == expected_total_score and
                        result["max_possible_score"] == expected_max_score and
                        result["is_evaluated"] == False and  # Requires manual evaluation
                        result["is_published"] == False):  # Not published until evaluated
                        
                        # Verify detailed results structure
                        detailed_results = result["detailed_results"]
                        if len(detailed_results) == 4:
                            mcq_results = [dr for dr in detailed_results if dr["question_type"] == "multiple_choice"]
                            text_results = [dr for dr in detailed_results if dr["question_type"] == "text"]
                            
                            if len(mcq_results) == 2 and len(text_results) == 2:
                                # Check MCQ results have correct answers and scoring
                                mcq_correct = all(dr["is_correct"] == True and dr["points_earned"] == 2 for dr in mcq_results)
                                # Check text results are pending evaluation
                                text_pending = all(dr["points_earned"] == 0 and dr["is_evaluated"] == False for dr in text_results)
                                
                                if mcq_correct and text_pending:
                                    self.created_result_id = result["id"]
                                    self.log_test("Submit Mixed Quiz Attempt", "PASS", 
                                                f"Mixed quiz submitted: Auto={result['auto_score']}, Manual={result['manual_score']}, Total={result['total_score']}/{result['max_possible_score']}")
                                    return True
                                else:
                                    self.log_test("Submit Mixed Quiz Attempt", "FAIL", "Detailed results scoring incorrect")
                                    return False
                            else:
                                self.log_test("Submit Mixed Quiz Attempt", "FAIL", "Detailed results count incorrect")
                                return False
                        else:
                            self.log_test("Submit Mixed Quiz Attempt", "FAIL", "Wrong number of detailed results")
                            return False
                    else:
                        self.log_test("Submit Mixed Quiz Attempt", "FAIL", 
                                    f"Scoring incorrect: Auto={result['auto_score']}, Manual={result['manual_score']}, Evaluated={result['is_evaluated']}")
                        return False
                else:
                    self.log_test("Submit Mixed Quiz Attempt", "FAIL", "Response missing required fields")
                    return False
            else:
                self.log_test("Submit Mixed Quiz Attempt", "FAIL", f"Status code: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Submit Mixed Quiz Attempt", "FAIL", f"Exception: {str(e)}")
            return False

    def test_admin_pending_evaluations(self) -> bool:
        """Test GET /api/admin/results/pending - Get pending evaluations"""
        try:
            if not self.admin_token:
                self.log_test("Admin Pending Evaluations", "FAIL", "No admin token available")
                return False
            
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.get(f"{self.base_url}/admin/results/pending", headers=headers)
            
            if response.status_code == 200:
                results = response.json()
                
                if isinstance(results, list):
                    # Should find our submitted result that needs evaluation
                    pending_result = None
                    for result in results:
                        if result.get("id") == self.created_result_id:
                            pending_result = result
                            break
                    
                    if pending_result:
                        if (pending_result["is_evaluated"] == False and 
                            pending_result["auto_score"] == 4 and
                            pending_result["manual_score"] == 0):
                            self.log_test("Admin Pending Evaluations", "PASS", 
                                        f"Found {len(results)} pending evaluations including our test result")
                            return True
                        else:
                            self.log_test("Admin Pending Evaluations", "FAIL", "Pending result has incorrect status")
                            return False
                    else:
                        self.log_test("Admin Pending Evaluations", "FAIL", "Our test result not found in pending evaluations")
                        return False
                else:
                    self.log_test("Admin Pending Evaluations", "FAIL", "Response is not a list")
                    return False
            else:
                self.log_test("Admin Pending Evaluations", "FAIL", f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Admin Pending Evaluations", "FAIL", f"Exception: {str(e)}")
            return False

    def test_admin_evaluate_text_questions(self) -> bool:
        """Test POST /api/admin/evaluate/{result_id} - Evaluate text questions"""
        try:
            if not self.admin_token or not self.created_result_id:
                self.log_test("Admin Evaluate Text Questions", "FAIL", "Missing admin token or result ID")
                return False
            
            # First get the result to know question IDs
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            result_response = self.session.get(f"{self.base_url}/results/{self.created_result_id}", headers=headers)
            
            if result_response.status_code != 200:
                self.log_test("Admin Evaluate Text Questions", "FAIL", "Could not retrieve result for evaluation")
                return False
            
            result_data = result_response.json()
            text_questions = [dr for dr in result_data["detailed_results"] if dr["question_type"] == "text"]
            
            # Create evaluations for text questions
            evaluations = []
            for text_q in text_questions:
                if "list and tuple" in text_q["question_text"].lower():
                    evaluations.append({
                        "question_id": text_q["question_id"],
                        "points_awarded": 4,  # Out of 5 possible
                        "feedback": "Good explanation of the differences. Could have included more examples of when to use each."
                    })
                elif "function" in text_q["question_text"].lower():
                    evaluations.append({
                        "question_id": text_q["question_id"],
                        "points_awarded": 6,  # Full points
                        "feedback": "Excellent solution! Clean code with good explanation of the approach."
                    })
            
            evaluation_data = {
                "result_id": self.created_result_id,
                "evaluations": evaluations
            }
            
            response = self.session.post(
                f"{self.base_url}/admin/evaluate/{self.created_result_id}",
                json=evaluation_data,
                headers=headers
            )
            
            if response.status_code == 200:
                response_data = response.json()
                
                if "message" in response_data and "successfully" in response_data["message"].lower():
                    # Verify the evaluation was applied by getting the updated result
                    updated_result_response = self.session.get(f"{self.base_url}/results/{self.created_result_id}", headers=headers)
                    
                    if updated_result_response.status_code == 200:
                        updated_result = updated_result_response.json()
                        
                        expected_manual_score = 10  # 4 + 6 points from evaluations
                        expected_total_score = 14   # 4 (auto) + 10 (manual)
                        expected_percentage = round((14/15) * 100, 2)  # 93.33%
                        
                        if (updated_result["manual_score"] == expected_manual_score and
                            updated_result["total_score"] == expected_total_score and
                            updated_result["percentage"] == expected_percentage and
                            updated_result["is_evaluated"] == True):
                            
                            # Check that detailed results were updated with feedback
                            text_results = [dr for dr in updated_result["detailed_results"] if dr["question_type"] == "text"]
                            feedback_present = all("feedback" in tr and tr["is_evaluated"] == True for tr in text_results)
                            
                            if feedback_present:
                                self.log_test("Admin Evaluate Text Questions", "PASS", 
                                            f"Text questions evaluated: Manual={expected_manual_score}, Total={expected_total_score}/{updated_result['max_possible_score']} ({expected_percentage}%)")
                                return True
                            else:
                                self.log_test("Admin Evaluate Text Questions", "FAIL", "Feedback not properly applied to detailed results")
                                return False
                        else:
                            self.log_test("Admin Evaluate Text Questions", "FAIL", 
                                        f"Evaluation scoring incorrect: Manual={updated_result['manual_score']}, Total={updated_result['total_score']}")
                            return False
                    else:
                        self.log_test("Admin Evaluate Text Questions", "FAIL", "Could not retrieve updated result")
                        return False
                else:
                    self.log_test("Admin Evaluate Text Questions", "FAIL", "Unexpected response message")
                    return False
            else:
                self.log_test("Admin Evaluate Text Questions", "FAIL", f"Status code: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Evaluate Text Questions", "FAIL", f"Exception: {str(e)}")
            return False

    def test_admin_publish_result(self) -> bool:
        """Test POST /api/admin/publish/{result_id} - Publish quiz result"""
        try:
            if not self.admin_token or not self.created_result_id:
                self.log_test("Admin Publish Result", "FAIL", "Missing admin token or result ID")
                return False
            
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.post(f"{self.base_url}/admin/publish/{self.created_result_id}", headers=headers)
            
            if response.status_code == 200:
                response_data = response.json()
                
                if "message" in response_data and "published" in response_data["message"].lower():
                    # Verify the result is now published
                    result_response = self.session.get(f"{self.base_url}/results/{self.created_result_id}", headers=headers)
                    
                    if result_response.status_code == 200:
                        result_data = result_response.json()
                        
                        if result_data["is_published"] == True:
                            self.log_test("Admin Publish Result", "PASS", "Result published successfully")
                            return True
                        else:
                            self.log_test("Admin Publish Result", "FAIL", "Result not marked as published")
                            return False
                    else:
                        self.log_test("Admin Publish Result", "FAIL", "Could not verify published status")
                        return False
                else:
                    self.log_test("Admin Publish Result", "FAIL", "Unexpected response message")
                    return False
            else:
                self.log_test("Admin Publish Result", "FAIL", f"Status code: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Publish Result", "FAIL", f"Exception: {str(e)}")
            return False

    def test_user_get_published_results(self) -> bool:
        """Test GET /api/results/my/all - Get user's published results"""
        try:
            if not self.user_token:
                self.log_test("User Get Published Results", "FAIL", "No user token available")
                return False
            
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = self.session.get(f"{self.base_url}/results/my/all", headers=headers)
            
            if response.status_code == 200:
                results = response.json()
                
                if isinstance(results, list):
                    # Should find our published result
                    published_result = None
                    for result in results:
                        if result.get("id") == self.created_result_id:
                            published_result = result
                            break
                    
                    if published_result:
                        if (published_result["is_published"] == True and 
                            published_result["is_evaluated"] == True and
                            published_result["total_score"] == 14):
                            self.log_test("User Get Published Results", "PASS", 
                                        f"User can access their published result: {published_result['total_score']}/{published_result['max_possible_score']}")
                            return True
                        else:
                            self.log_test("User Get Published Results", "FAIL", "Published result has incorrect data")
                            return False
                    else:
                        self.log_test("User Get Published Results", "FAIL", "Published result not found in user's results")
                        return False
                else:
                    self.log_test("User Get Published Results", "FAIL", "Response is not a list")
                    return False
            else:
                self.log_test("User Get Published Results", "FAIL", f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("User Get Published Results", "FAIL", f"Exception: {str(e)}")
            return False

    def test_get_quiz_result_with_feedback(self) -> bool:
        """Test GET /api/results/{result_id} - Get detailed result with feedback"""
        try:
            if not self.user_token or not self.created_result_id:
                self.log_test("Get Quiz Result with Feedback", "FAIL", "Missing user token or result ID")
                return False
            
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = self.session.get(f"{self.base_url}/results/{self.created_result_id}", headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                
                required_fields = ["id", "quiz_id", "quiz_title", "auto_score", "manual_score", 
                                 "total_score", "percentage", "detailed_results", "evaluations"]
                
                if all(field in result for field in required_fields):
                    # Verify comprehensive result data
                    if (result["auto_score"] == 4 and 
                        result["manual_score"] == 10 and
                        result["total_score"] == 14 and
                        result["is_evaluated"] == True and
                        result["is_published"] == True):
                        
                        # Check detailed results include feedback for text questions
                        detailed_results = result["detailed_results"]
                        mcq_results = [dr for dr in detailed_results if dr["question_type"] == "multiple_choice"]
                        text_results = [dr for dr in detailed_results if dr["question_type"] == "text"]
                        
                        # MCQ should have explanations, text should have feedback
                        mcq_complete = all("explanation" in dr and "correct_answer" in dr for dr in mcq_results)
                        text_complete = all("feedback" in dr and dr["is_evaluated"] == True for dr in text_results)
                        
                        if mcq_complete and text_complete and len(result["evaluations"]) == 2:
                            self.log_test("Get Quiz Result with Feedback", "PASS", 
                                        "Complete result with feedback retrieved successfully")
                            return True
                        else:
                            self.log_test("Get Quiz Result with Feedback", "FAIL", "Feedback or explanations missing")
                            return False
                    else:
                        self.log_test("Get Quiz Result with Feedback", "FAIL", "Result data incorrect")
                        return False
                else:
                    self.log_test("Get Quiz Result with Feedback", "FAIL", "Response missing required fields")
                    return False
            else:
                self.log_test("Get Quiz Result with Feedback", "FAIL", f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Get Quiz Result with Feedback", "FAIL", f"Exception: {str(e)}")
            return False

    def run_all_tests(self) -> Dict[str, bool]:
        """Run all backend API tests"""
        print("=" * 60)
        print("MINI QUIZ PLATFORM - BACKEND API TESTING")
        print("=" * 60)
        print(f"Testing API at: {self.base_url}")
        print()
        
        test_results = {}
        
        # Core API Tests
        test_results["health_check"] = self.test_health_check()
        test_results["create_quiz"] = self.test_create_quiz()
        test_results["list_quizzes"] = self.test_list_quizzes()
        test_results["get_quiz_for_taking"] = self.test_get_quiz_for_taking()
        test_results["submit_quiz_attempt"] = self.test_submit_quiz_attempt()
        test_results["get_quiz_result"] = self.test_get_quiz_result()
        test_results["get_all_results_admin"] = self.test_get_all_results_admin()
        
        # Edge Case Tests
        test_results["invalid_quiz_retrieval"] = self.test_invalid_quiz_retrieval()
        test_results["empty_quiz_attempt"] = self.test_empty_quiz_attempt()
        
        # Summary
        print("=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in test_results.values() if result)
        total = len(test_results)
        
        for test_name, result in test_results.items():
            status = "PASS" if result else "FAIL"
            symbol = "✅" if result else "❌"
            print(f"{symbol} {test_name.replace('_', ' ').title()}: {status}")
        
        print()
        print(f"Overall Result: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All backend API tests PASSED!")
        else:
            print(f"⚠️  {total - passed} test(s) FAILED")
        
        return test_results

if __name__ == "__main__":
    tester = QuizPlatformTester()
    results = tester.run_all_tests()