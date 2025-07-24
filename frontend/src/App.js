import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Quiz Creation Component
const QuizCreator = ({ onQuizCreated }) => {
  const [quizData, setQuizData] = useState({
    title: '',
    subject: '',
    description: '',
    time_limit: 30,
    questions: []
  });
  
  const [currentQuestion, setCurrentQuestion] = useState({
    question_text: '',
    question_type: 'multiple_choice',
    options: ['', '', '', ''],
    correct_answer: '',
    explanation: ''
  });

  const addQuestion = () => {
    if (currentQuestion.question_text && currentQuestion.correct_answer) {
      const filteredOptions = currentQuestion.options.filter(opt => opt.trim() !== '');
      if (filteredOptions.length < 2) {
        alert('Please provide at least 2 options for the question');
        return;
      }
      
      const newQuestion = {
        ...currentQuestion,
        options: filteredOptions
      };
      
      setQuizData(prev => ({
        ...prev,
        questions: [...prev.questions, newQuestion]
      }));
      
      // Reset current question
      setCurrentQuestion({
        question_text: '',
        question_type: 'multiple_choice',
        options: ['', '', '', ''],
        correct_answer: '',
        explanation: ''
      });
    }
  };

  const createQuiz = async () => {
    if (!quizData.title || !quizData.subject || quizData.questions.length === 0) {
      alert('Please fill in all required fields and add at least one question');
      return;
    }

    try {
      const response = await axios.post(`${API}/quizzes`, quizData);
      alert('Quiz created successfully!');
      onQuizCreated();
      setQuizData({
        title: '',
        subject: '',
        description: '',
        time_limit: 30,
        questions: []
      });
    } catch (error) {
      console.error('Error creating quiz:', error);
      alert('Error creating quiz. Please try again.');
    }
  };

  return (
    <div className="quiz-creator">
      <h2 className="text-2xl font-bold mb-6 text-blue-600">Create New Quiz</h2>
      
      {/* Quiz Info */}
      <div className="bg-white p-6 rounded-lg shadow-md mb-6">
        <h3 className="text-lg font-semibold mb-4">Quiz Information</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <input
            type="text"
            placeholder="Quiz Title *"
            className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={quizData.title}
            onChange={(e) => setQuizData(prev => ({ ...prev, title: e.target.value }))}
          />
          
          <input
            type="text"
            placeholder="Subject *"
            className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={quizData.subject}
            onChange={(e) => setQuizData(prev => ({ ...prev, subject: e.target.value }))}
          />
        </div>
        
        <textarea
          placeholder="Quiz Description"
          className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 mb-4"
          rows="3"
          value={quizData.description}
          onChange={(e) => setQuizData(prev => ({ ...prev, description: e.target.value }))}
        />
        
        <div className="flex items-center gap-2">
          <label className="font-medium">Time Limit (minutes):</label>
          <input
            type="number"
            className="w-20 p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={quizData.time_limit}
            onChange={(e) => setQuizData(prev => ({ ...prev, time_limit: parseInt(e.target.value) }))}
          />
        </div>
      </div>

      {/* Add Question */}
      <div className="bg-white p-6 rounded-lg shadow-md mb-6">
        <h3 className="text-lg font-semibold mb-4">Add Question</h3>
        
        <textarea
          placeholder="Question Text *"
          className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 mb-4"
          rows="3"
          value={currentQuestion.question_text}
          onChange={(e) => setCurrentQuestion(prev => ({ ...prev, question_text: e.target.value }))}
        />
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          {currentQuestion.options.map((option, index) => (
            <input
              key={index}
              type="text"
              placeholder={`Option ${index + 1} ${index < 2 ? '*' : ''}`}
              className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={option}
              onChange={(e) => {
                const newOptions = [...currentQuestion.options];
                newOptions[index] = e.target.value;
                setCurrentQuestion(prev => ({ ...prev, options: newOptions }));
              }}
            />
          ))}
        </div>
        
        <input
          type="text"
          placeholder="Correct Answer *"
          className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 mb-4"
          value={currentQuestion.correct_answer}
          onChange={(e) => setCurrentQuestion(prev => ({ ...prev, correct_answer: e.target.value }))}
        />
        
        <textarea
          placeholder="Explanation (optional)"
          className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 mb-4"
          rows="2"
          value={currentQuestion.explanation}
          onChange={(e) => setCurrentQuestion(prev => ({ ...prev, explanation: e.target.value }))}
        />
        
        <button
          onClick={addQuestion}
          className="bg-green-500 hover:bg-green-600 text-white px-6 py-2 rounded-lg font-medium transition-colors"
        >
          Add Question
        </button>
      </div>

      {/* Questions List */}
      {quizData.questions.length > 0 && (
        <div className="bg-white p-6 rounded-lg shadow-md mb-6">
          <h3 className="text-lg font-semibold mb-4">Questions Added ({quizData.questions.length})</h3>
          
          {quizData.questions.map((question, index) => (
            <div key={index} className="border-l-4 border-blue-500 pl-4 py-2 mb-4 bg-gray-50">
              <p className="font-medium">{index + 1}. {question.question_text}</p>
              <p className="text-sm text-gray-600 mt-1">
                Options: {question.options.join(', ')}
              </p>
              <p className="text-sm text-green-600 mt-1">
                Correct Answer: {question.correct_answer}
              </p>
            </div>
          ))}
        </div>
      )}

      <button
        onClick={createQuiz}
        className="bg-blue-500 hover:bg-blue-600 text-white px-8 py-3 rounded-lg font-medium text-lg transition-colors"
      >
        Create Quiz
      </button>
    </div>
  );
};

// Quiz List Component
const QuizList = ({ onSelectQuiz }) => {
  const [quizzes, setQuizzes] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchQuizzes();
  }, []);

  const fetchQuizzes = async () => {
    try {
      const response = await axios.get(`${API}/quizzes`);
      setQuizzes(response.data);
    } catch (error) {
      console.error('Error fetching quizzes:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="text-center py-8">Loading quizzes...</div>;
  }

  return (
    <div className="quiz-list">
      <h2 className="text-2xl font-bold mb-6 text-blue-600">Available Quizzes</h2>
      
      {quizzes.length === 0 ? (
        <div className="text-center py-8 text-gray-600">
          No quizzes available. Create one to get started!
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {quizzes.map((quiz) => (
            <div key={quiz.id} className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow">
              <h3 className="text-xl font-semibold mb-2 text-gray-800">{quiz.title}</h3>
              <p className="text-gray-600 mb-2">Subject: {quiz.subject}</p>
              <p className="text-gray-600 mb-2">Questions: {quiz.total_questions}</p>
              {quiz.time_limit && (
                <p className="text-gray-600 mb-4">Time Limit: {quiz.time_limit} minutes</p>
              )}
              {quiz.description && (
                <p className="text-gray-700 mb-4 text-sm">{quiz.description}</p>
              )}
              
              <button
                onClick={() => onSelectQuiz(quiz.id)}
                className="w-full bg-blue-500 hover:bg-blue-600 text-white py-2 px-4 rounded-lg font-medium transition-colors"
              >
                Take Quiz
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// Quiz Taking Component
const QuizTaker = ({ quizId, onQuizComplete }) => {
  const [quiz, setQuiz] = useState(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [responses, setResponses] = useState({});
  const [timeLeft, setTimeLeft] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchQuiz();
  }, [quizId]);

  useEffect(() => {
    if (quiz && quiz.time_limit) {
      setTimeLeft(quiz.time_limit * 60); // Convert minutes to seconds
    }
  }, [quiz]);

  useEffect(() => {
    if (timeLeft !== null && timeLeft > 0) {
      const timer = setTimeout(() => setTimeLeft(timeLeft - 1), 1000);
      return () => clearTimeout(timer);
    } else if (timeLeft === 0) {
      submitQuiz();
    }
  }, [timeLeft]);

  const fetchQuiz = async () => {
    try {
      const response = await axios.get(`${API}/quizzes/${quizId}`);
      setQuiz(response.data);
    } catch (error) {
      console.error('Error fetching quiz:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAnswer = (questionId, answer) => {
    setResponses(prev => ({
      ...prev,
      [questionId]: answer
    }));
  };

  const submitQuiz = async () => {
    const responseList = Object.entries(responses).map(([questionId, selectedAnswer]) => ({
      question_id: questionId,
      selected_answer: selectedAnswer
    }));

    const timeTaken = quiz.time_limit ? (quiz.time_limit * 60 - (timeLeft || 0)) : null;

    try {
      const response = await axios.post(`${API}/quizzes/${quizId}/attempt`, {
        responses: responseList,
        time_taken: timeTaken
      });
      
      onQuizComplete(response.data);
    } catch (error) {
      console.error('Error submitting quiz:', error);
      alert('Error submitting quiz. Please try again.');
    }
  };

  const formatTime = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  if (loading) {
    return <div className="text-center py-8">Loading quiz...</div>;
  }

  if (!quiz) {
    return <div className="text-center py-8 text-red-600">Quiz not found.</div>;
  }

  const currentQuestion = quiz.questions[currentQuestionIndex];
  const progress = ((currentQuestionIndex + 1) / quiz.questions.length) * 100;

  return (
    <div className="quiz-taker max-w-4xl mx-auto">
      {/* Header */}
      <div className="bg-white p-6 rounded-lg shadow-md mb-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold text-blue-600">{quiz.title}</h2>
          {timeLeft !== null && (
            <div className={`text-lg font-bold ${timeLeft < 300 ? 'text-red-600' : 'text-green-600'}`}>
              Time Left: {formatTime(timeLeft)}
            </div>
          )}
        </div>
        
        <div className="flex justify-between items-center">
          <span className="text-gray-600">
            Question {currentQuestionIndex + 1} of {quiz.questions.length}
          </span>
          <span className="text-gray-600">Subject: {quiz.subject}</span>
        </div>
        
        {/* Progress Bar */}
        <div className="w-full bg-gray-200 rounded-full h-2 mt-4">
          <div 
            className="bg-blue-500 h-2 rounded-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          ></div>
        </div>
      </div>

      {/* Question */}
      <div className="bg-white p-6 rounded-lg shadow-md mb-6">
        <h3 className="text-xl font-semibold mb-6">{currentQuestion.question_text}</h3>
        
        <div className="space-y-3">
          {currentQuestion.options.map((option, index) => (
            <label key={index} className="flex items-center p-4 border rounded-lg hover:bg-gray-50 cursor-pointer">
              <input
                type="radio"
                name={`question-${currentQuestion.id}`}
                value={option}
                checked={responses[currentQuestion.id] === option}
                onChange={(e) => handleAnswer(currentQuestion.id, e.target.value)}
                className="mr-3 text-blue-500"
              />
              <span className="text-lg">{option}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Navigation */}
      <div className="flex justify-between items-center">
        <div>
          {currentQuestionIndex > 0 && (
            <button
              onClick={() => setCurrentQuestionIndex(prev => prev - 1)}
              className="bg-gray-500 hover:bg-gray-600 text-white px-6 py-2 rounded-lg font-medium transition-colors"
            >
              Previous
            </button>
          )}
        </div>
        
        <div>
          {currentQuestionIndex < quiz.questions.length - 1 ? (
            <button
              onClick={() => setCurrentQuestionIndex(prev => prev + 1)}
              className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded-lg font-medium transition-colors"
            >
              Next
            </button>
          ) : (
            <button
              onClick={submitQuiz}
              className="bg-green-500 hover:bg-green-600 text-white px-6 py-2 rounded-lg font-medium transition-colors"
            >
              Submit Quiz
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

// Results Component
const QuizResults = ({ result, onReturnHome }) => {
  const getGrade = (percentage) => {
    if (percentage >= 90) return { grade: 'A+', color: 'text-green-600' };
    if (percentage >= 80) return { grade: 'A', color: 'text-green-600' };
    if (percentage >= 70) return { grade: 'B', color: 'text-blue-600' };
    if (percentage >= 60) return { grade: 'C', color: 'text-yellow-600' };
    return { grade: 'F', color: 'text-red-600' };
  };

  const gradeInfo = getGrade(result.percentage);

  return (
    <div className="quiz-results max-w-4xl mx-auto">
      {/* Score Overview */}
      <div className="bg-white p-8 rounded-lg shadow-md mb-6 text-center">
        <h2 className="text-3xl font-bold mb-4 text-blue-600">Quiz Completed!</h2>
        <h3 className="text-xl font-semibold mb-6 text-gray-700">{result.quiz_title}</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
          <div className="bg-blue-50 p-4 rounded-lg">
            <div className="text-2xl font-bold text-blue-600">{result.score}/{result.total_questions}</div>
            <div className="text-gray-600">Score</div>
          </div>
          
          <div className="bg-green-50 p-4 rounded-lg">
            <div className={`text-2xl font-bold ${gradeInfo.color}`}>{result.percentage}%</div>
            <div className="text-gray-600">Percentage</div>
          </div>
          
          <div className="bg-purple-50 p-4 rounded-lg">
            <div className={`text-2xl font-bold ${gradeInfo.color}`}>{gradeInfo.grade}</div>
            <div className="text-gray-600">Grade</div>
          </div>
          
          {result.time_taken && (
            <div className="bg-yellow-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-yellow-600">
                {Math.floor(result.time_taken / 60)}:{(result.time_taken % 60).toString().padStart(2, '0')}
              </div>
              <div className="text-gray-600">Time Taken</div>
            </div>
          )}
        </div>
      </div>

      {/* Detailed Results */}
      <div className="bg-white p-6 rounded-lg shadow-md mb-6">
        <h3 className="text-xl font-semibold mb-6">Detailed Results</h3>
        
        {result.detailed_results.map((item, index) => (
          <div key={index} className={`border-l-4 ${item.is_correct ? 'border-green-500 bg-green-50' : 'border-red-500 bg-red-50'} p-4 mb-4 rounded-r-lg`}>
            <div className="flex items-start justify-between mb-2">
              <p className="font-medium text-gray-800">
                {index + 1}. {item.question_text}
              </p>
              <span className={`px-2 py-1 rounded text-sm font-medium ${item.is_correct ? 'bg-green-200 text-green-800' : 'bg-red-200 text-red-800'}`}>
                {item.is_correct ? 'Correct' : 'Incorrect'}
              </span>
            </div>
            
            <div className="space-y-1 text-sm">
              <p><span className="font-medium">Your Answer:</span> {item.selected_answer}</p>
              {!item.is_correct && (
                <p><span className="font-medium">Correct Answer:</span> {item.correct_answer}</p>
              )}
              {item.explanation && (
                <p className="text-blue-600"><span className="font-medium">Explanation:</span> {item.explanation}</p>
              )}
            </div>
          </div>
        ))}
      </div>

      <div className="text-center">
        <button
          onClick={onReturnHome}
          className="bg-blue-500 hover:bg-blue-600 text-white px-8 py-3 rounded-lg font-medium text-lg transition-colors"
        >
          Take Another Quiz
        </button>
      </div>
    </div>
  );
};

// Main App Component
function App() {
  const [currentView, setCurrentView] = useState('home');
  const [selectedQuizId, setSelectedQuizId] = useState(null);
  const [quizResult, setQuizResult] = useState(null);

  const handleSelectQuiz = (quizId) => {
    setSelectedQuizId(quizId);
    setCurrentView('taking');
  };

  const handleQuizComplete = (result) => {
    setQuizResult(result);
    setCurrentView('results');
  };

  const handleReturnHome = () => {
    setCurrentView('home');
    setSelectedQuizId(null);
    setQuizResult(null);
  };

  return (
    <div className="App min-h-screen bg-gray-100">
      {/* Navigation */}
      <nav className="bg-white shadow-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-blue-600">Mini Quiz Platform</h1>
            </div>
            
            <div className="flex space-x-4">
              <button
                onClick={() => setCurrentView('home')}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${currentView === 'home' ? 'bg-blue-500 text-white' : 'text-gray-600 hover:text-blue-600'}`}
              >
                Home
              </button>
              <button
                onClick={() => setCurrentView('create')}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${currentView === 'create' ? 'bg-blue-500 text-white' : 'text-gray-600 hover:text-blue-600'}`}
              >
                Create Quiz
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        {currentView === 'home' && (
          <QuizList onSelectQuiz={handleSelectQuiz} />
        )}
        
        {currentView === 'create' && (
          <QuizCreator onQuizCreated={() => setCurrentView('home')} />
        )}
        
        {currentView === 'taking' && selectedQuizId && (
          <QuizTaker
            quizId={selectedQuizId}
            onQuizComplete={handleQuizComplete}
          />
        )}
        
        {currentView === 'results' && quizResult && (
          <QuizResults
            result={quizResult}
            onReturnHome={handleReturnHome}
          />
        )}
      </main>
    </div>
  );
}

export default App;