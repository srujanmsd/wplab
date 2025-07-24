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

    def test_create_quiz(self) -> bool:
        """Test POST /api/quizzes - Create new quiz"""
        try:
            # Create a comprehensive quiz with realistic data
            quiz_data = {
                "title": "Introduction to Python Programming",
                "subject": "Computer Science",
                "description": "Basic concepts and syntax of Python programming language",
                "time_limit": 30,
                "questions": [
                    {
                        "question_text": "What is the correct way to create a list in Python?",
                        "question_type": "multiple_choice",
                        "options": ["list = []", "list = {}", "list = ()", "list = <>"],
                        "correct_answer": "list = []",
                        "explanation": "Square brackets [] are used to create lists in Python"
                    },
                    {
                        "question_text": "Which keyword is used to define a function in Python?",
                        "question_type": "multiple_choice", 
                        "options": ["function", "def", "func", "define"],
                        "correct_answer": "def",
                        "explanation": "The 'def' keyword is used to define functions in Python"
                    },
                    {
                        "question_text": "What does the len() function return?",
                        "question_type": "multiple_choice",
                        "options": ["The length of an object", "The type of an object", "The value of an object", "The memory address"],
                        "correct_answer": "The length of an object",
                        "explanation": "len() returns the number of items in an object like string, list, tuple, etc."
                    }
                ]
            }
            
            response = self.session.post(
                f"{self.base_url}/quizzes",
                json=quiz_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["id", "title", "subject", "questions", "total_questions"]
                
                if all(field in data for field in required_fields):
                    self.created_quiz_id = data["id"]
                    if data["total_questions"] == len(quiz_data["questions"]):
                        self.log_test("Create Quiz", "PASS", f"Quiz created with ID: {self.created_quiz_id}")
                        return True
                    else:
                        self.log_test("Create Quiz", "FAIL", "Total questions count mismatch")
                        return False
                else:
                    self.log_test("Create Quiz", "FAIL", "Response missing required fields")
                    return False
            else:
                self.log_test("Create Quiz", "FAIL", f"Status code: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Create Quiz", "FAIL", f"Exception: {str(e)}")
            return False

    def test_list_quizzes(self) -> bool:
        """Test GET /api/quizzes - List all quizzes"""
        try:
            response = self.session.get(f"{self.base_url}/quizzes")
            
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
                                if "questions" not in quiz:
                                    self.log_test("List Quizzes", "PASS", f"Found {len(data)} quizzes, questions properly hidden")
                                    return True
                                else:
                                    self.log_test("List Quizzes", "FAIL", "Questions should not be included in quiz listing")
                                    return False
                        
                        if not quiz_found:
                            self.log_test("List Quizzes", "FAIL", "Created quiz not found in listing")
                            return False
                    else:
                        self.log_test("List Quizzes", "PASS", "Empty quiz list returned")
                        return True
                else:
                    self.log_test("List Quizzes", "FAIL", "Response is not a list")
                    return False
            else:
                self.log_test("List Quizzes", "FAIL", f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("List Quizzes", "FAIL", f"Exception: {str(e)}")
            return False

    def test_get_quiz_for_taking(self) -> bool:
        """Test GET /api/quizzes/{quiz_id} - Get quiz for taking"""
        try:
            if not self.created_quiz_id:
                self.log_test("Get Quiz for Taking", "FAIL", "No quiz ID available for testing")
                return False
                
            response = self.session.get(f"{self.base_url}/quizzes/{self.created_quiz_id}")
            
            if response.status_code == 200:
                data = response.json()
                
                required_fields = ["id", "title", "subject", "questions"]
                if all(field in data for field in required_fields):
                    # Verify that correct answers are hidden
                    questions = data["questions"]
                    answers_hidden = True
                    
                    for question in questions:
                        if "correct_answer" in question or "explanation" in question:
                            answers_hidden = False
                            break
                        
                        # Verify required fields are present
                        required_q_fields = ["id", "question_text", "question_type", "options"]
                        if not all(field in question for field in required_q_fields):
                            self.log_test("Get Quiz for Taking", "FAIL", "Question missing required fields")
                            return False
                    
                    if answers_hidden:
                        self.log_test("Get Quiz for Taking", "PASS", "Quiz retrieved with answers properly hidden")
                        return True
                    else:
                        self.log_test("Get Quiz for Taking", "FAIL", "Correct answers not properly hidden")
                        return False
                else:
                    self.log_test("Get Quiz for Taking", "FAIL", "Response missing required fields")
                    return False
            else:
                self.log_test("Get Quiz for Taking", "FAIL", f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Get Quiz for Taking", "FAIL", f"Exception: {str(e)}")
            return False

    def test_invalid_quiz_retrieval(self) -> bool:
        """Test GET /api/quizzes/{invalid_id} - Invalid quiz ID"""
        try:
            invalid_id = "non-existent-quiz-id"
            response = self.session.get(f"{self.base_url}/quizzes/{invalid_id}")
            
            if response.status_code == 404:
                self.log_test("Invalid Quiz Retrieval", "PASS", "Properly returns 404 for invalid quiz ID")
                return True
            else:
                self.log_test("Invalid Quiz Retrieval", "FAIL", f"Expected 404, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Invalid Quiz Retrieval", "FAIL", f"Exception: {str(e)}")
            return False

    def test_submit_quiz_attempt(self) -> bool:
        """Test POST /api/quizzes/{quiz_id}/attempt - Submit quiz responses"""
        try:
            if not self.created_quiz_id:
                self.log_test("Submit Quiz Attempt", "FAIL", "No quiz ID available for testing")
                return False
            
            # First get the quiz to know question IDs
            quiz_response = self.session.get(f"{self.base_url}/quizzes/{self.created_quiz_id}")
            if quiz_response.status_code != 200:
                self.log_test("Submit Quiz Attempt", "FAIL", "Could not retrieve quiz for attempt")
                return False
                
            quiz_data = quiz_response.json()
            questions = quiz_data["questions"]
            
            # Create responses (mix of correct and incorrect answers)
            responses = []
            for i, question in enumerate(questions):
                if i == 0:  # First question - correct answer
                    responses.append({
                        "question_id": question["id"],
                        "selected_answer": "list = []"  # Correct answer
                    })
                elif i == 1:  # Second question - correct answer
                    responses.append({
                        "question_id": question["id"],
                        "selected_answer": "def"  # Correct answer
                    })
                else:  # Third question - incorrect answer
                    responses.append({
                        "question_id": question["id"],
                        "selected_answer": "The type of an object"  # Incorrect answer
                    })
            
            attempt_data = {
                "responses": responses,
                "time_taken": 1200  # 20 minutes in seconds
            }
            
            response = self.session.post(
                f"{self.base_url}/quizzes/{self.created_quiz_id}/attempt",
                json=attempt_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                
                required_fields = ["id", "quiz_id", "score", "total_questions", "percentage", 
                                 "correct_answers", "incorrect_answers", "detailed_results"]
                
                if all(field in result for field in required_fields):
                    # Verify scoring calculation
                    expected_score = 2  # 2 correct out of 3
                    expected_percentage = round((2/3) * 100, 2)
                    
                    if (result["score"] == expected_score and 
                        result["correct_answers"] == expected_score and
                        result["incorrect_answers"] == 1 and
                        result["percentage"] == expected_percentage):
                        
                        # Verify detailed results
                        detailed_results = result["detailed_results"]
                        if len(detailed_results) == 3:
                            self.created_result_id = result["id"]
                            self.log_test("Submit Quiz Attempt", "PASS", 
                                        f"Score: {result['score']}/{result['total_questions']} ({result['percentage']}%)")
                            return True
                        else:
                            self.log_test("Submit Quiz Attempt", "FAIL", "Detailed results count mismatch")
                            return False
                    else:
                        self.log_test("Submit Quiz Attempt", "FAIL", 
                                    f"Scoring calculation error. Got: {result['score']}/{result['total_questions']}")
                        return False
                else:
                    self.log_test("Submit Quiz Attempt", "FAIL", "Response missing required fields")
                    return False
            else:
                self.log_test("Submit Quiz Attempt", "FAIL", f"Status code: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Submit Quiz Attempt", "FAIL", f"Exception: {str(e)}")
            return False

    def test_get_quiz_result(self) -> bool:
        """Test GET /api/results/{result_id} - Get specific quiz result"""
        try:
            if not self.created_result_id:
                self.log_test("Get Quiz Result", "FAIL", "No result ID available for testing")
                return False
                
            response = self.session.get(f"{self.base_url}/results/{self.created_result_id}")
            
            if response.status_code == 200:
                result = response.json()
                
                required_fields = ["id", "quiz_id", "quiz_title", "score", "percentage", "detailed_results"]
                if all(field in result for field in required_fields):
                    # Verify detailed results include explanations
                    detailed_results = result["detailed_results"]
                    explanations_present = all("explanation" in dr for dr in detailed_results)
                    correct_answers_present = all("correct_answer" in dr for dr in detailed_results)
                    
                    if explanations_present and correct_answers_present:
                        self.log_test("Get Quiz Result", "PASS", "Result retrieved with complete details")
                        return True
                    else:
                        self.log_test("Get Quiz Result", "FAIL", "Detailed results missing explanations or correct answers")
                        return False
                else:
                    self.log_test("Get Quiz Result", "FAIL", "Response missing required fields")
                    return False
            else:
                self.log_test("Get Quiz Result", "FAIL", f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Get Quiz Result", "FAIL", f"Exception: {str(e)}")
            return False

    def test_get_all_results_admin(self) -> bool:
        """Test GET /api/admin/results - Get all quiz results for admin"""
        try:
            response = self.session.get(f"{self.base_url}/admin/results")
            
            if response.status_code == 200:
                results = response.json()
                
                if isinstance(results, list):
                    if len(results) > 0:
                        # Check if our result is in the list
                        result_found = any(result.get("id") == self.created_result_id for result in results)
                        
                        if result_found:
                            self.log_test("Get All Results (Admin)", "PASS", f"Found {len(results)} results")
                            return True
                        else:
                            self.log_test("Get All Results (Admin)", "FAIL", "Created result not found in admin results")
                            return False
                    else:
                        self.log_test("Get All Results (Admin)", "PASS", "Empty results list returned")
                        return True
                else:
                    self.log_test("Get All Results (Admin)", "FAIL", "Response is not a list")
                    return False
            else:
                self.log_test("Get All Results (Admin)", "FAIL", f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Get All Results (Admin)", "FAIL", f"Exception: {str(e)}")
            return False

    def test_empty_quiz_attempt(self) -> bool:
        """Test submitting empty quiz attempt"""
        try:
            if not self.created_quiz_id:
                self.log_test("Empty Quiz Attempt", "FAIL", "No quiz ID available for testing")
                return False
            
            attempt_data = {
                "responses": [],
                "time_taken": 60
            }
            
            response = self.session.post(
                f"{self.base_url}/quizzes/{self.created_quiz_id}/attempt",
                json=attempt_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Should handle empty responses gracefully
                if result["score"] == 0 and result["percentage"] == 0.0:
                    self.log_test("Empty Quiz Attempt", "PASS", "Empty attempt handled correctly")
                    return True
                else:
                    self.log_test("Empty Quiz Attempt", "FAIL", "Empty attempt scoring incorrect")
                    return False
            else:
                self.log_test("Empty Quiz Attempt", "FAIL", f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Empty Quiz Attempt", "FAIL", f"Exception: {str(e)}")
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