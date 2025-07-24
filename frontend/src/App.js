import React, { useState, useEffect, createContext, useContext } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Auth Context
const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      fetchUserProfile();
    } else {
      setLoading(false);
    }
  }, [token]);

  const fetchUserProfile = async () => {
    try {
      const response = await axios.get(`${API}/me`);
      setUser(response.data);
    } catch (error) {
      console.error('Error fetching user profile:', error);
      logout();
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    try {
      const response = await axios.post(`${API}/login`, { email, password });
      const { access_token, user: userData } = response.data;
      
      localStorage.setItem('token', access_token);
      setToken(access_token);
      setUser(userData);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Login failed' 
      };
    }
  };

  const register = async (email, password, fullName, role = 'user') => {
    try {
      await axios.post(`${API}/register`, {
        email,
        password,
        full_name: fullName,
        role
      });
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Registration failed' 
      };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    delete axios.defaults.headers.common['Authorization'];
  };

  const value = {
    user,
    token,
    login,
    register,
    logout,
    loading,
    isAuthenticated: !!token && !!user,
    isAdmin: user?.role === 'admin'
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Landing Page Component
const LandingPage = ({ setShowLanding, setAuthView }) => {
  const handleGetStarted = () => {
    setShowLanding(false);
    setAuthView('register');
  };

  const handleLogin = () => {
    setShowLanding(false);
    setAuthView('login');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
      {/* Navigation */}
      <nav className="bg-white/80 backdrop-blur-md shadow-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                  Mini Quiz Platform
                </h1>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={handleLogin}
                className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
              >
                Login
              </button>
              <button
                onClick={handleGetStarted}
                className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-6 py-2 rounded-lg text-sm font-medium hover:from-blue-700 hover:to-indigo-700 transition-all transform hover:scale-105"
              >
                Get Started
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative py-20 lg:py-32">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div className="text-center lg:text-left">
              <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-gray-900 leading-tight">
                Create & Take
                <span className="block bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                  Smart Quizzes
                </span>
              </h1>
              <p className="mt-6 text-xl text-gray-600 leading-relaxed">
                A comprehensive platform for creating interactive quizzes with multiple choice and text questions, 
                complete with admin evaluation and detailed feedback systems.
              </p>
              <div className="mt-8 flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
                <button
                  onClick={handleGetStarted}
                  className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-8 py-4 rounded-lg text-lg font-medium hover:from-blue-700 hover:to-indigo-700 transition-all transform hover:scale-105 shadow-lg"
                >
                  Start Creating Quizzes
                </button>
                <button
                  onClick={handleLogin}
                  className="border-2 border-gray-300 text-gray-700 px-8 py-4 rounded-lg text-lg font-medium hover:border-blue-600 hover:text-blue-600 transition-all"
                >
                  Sign In
                </button>
              </div>
            </div>
            <div className="relative">
              <div className="relative z-10">
                <img
                  src="https://images.unsplash.com/photo-1551533256-ab4695bca419?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1Nzl8MHwxfHNlYXJjaHwzfHxvbmxpbmUlMjBxdWl6fGVufDB8fHxibHVlfDE3NTMzNDc4NzV8MA&ixlib=rb-4.1.0&q=85"
                  alt="Online Learning"
                  className="rounded-2xl shadow-2xl"
                />
              </div>
              <div className="absolute -top-4 -right-4 w-24 h-24 bg-gradient-to-r from-blue-400 to-indigo-400 rounded-full opacity-20 animate-pulse"></div>
              <div className="absolute -bottom-4 -left-4 w-32 h-32 bg-gradient-to-r from-indigo-400 to-purple-400 rounded-full opacity-20 animate-pulse animation-delay-1000"></div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Powerful Features for Modern Learning
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Everything you need to create, manage, and evaluate quizzes with advanced features
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="bg-gradient-to-br from-blue-50 to-indigo-50 p-8 rounded-2xl hover:shadow-lg transition-shadow">
              <div className="w-12 h-12 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center mb-6">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Mixed Question Types</h3>
              <p className="text-gray-600">
                Create quizzes with both multiple choice and text-based questions for comprehensive assessment.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="bg-gradient-to-br from-green-50 to-emerald-50 p-8 rounded-2xl hover:shadow-lg transition-shadow">
              <div className="w-12 h-12 bg-gradient-to-r from-green-600 to-emerald-600 rounded-lg flex items-center justify-center mb-6">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"></path>
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Smart Evaluation</h3>
              <p className="text-gray-600">
                Automatic scoring for multiple choice with manual evaluation and feedback for text answers.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="bg-gradient-to-br from-purple-50 to-pink-50 p-8 rounded-2xl hover:shadow-lg transition-shadow">
              <div className="w-12 h-12 bg-gradient-to-r from-purple-600 to-pink-600 rounded-lg flex items-center justify-center mb-6">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"></path>
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Role-Based Access</h3>
              <p className="text-gray-600">
                Secure authentication with admin and student roles for complete quiz management control.
              </p>
            </div>

            {/* Feature 4 */}
            <div className="bg-gradient-to-br from-orange-50 to-red-50 p-8 rounded-2xl hover:shadow-lg transition-shadow">
              <div className="w-12 h-12 bg-gradient-to-r from-orange-600 to-red-600 rounded-lg flex items-center justify-center mb-6">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Detailed Analytics</h3>
              <p className="text-gray-600">
                Comprehensive results with scores, feedback, and detailed performance insights.
              </p>
            </div>

            {/* Feature 5 */}
            <div className="bg-gradient-to-br from-teal-50 to-cyan-50 p-8 rounded-2xl hover:shadow-lg transition-shadow">
              <div className="w-12 h-12 bg-gradient-to-r from-teal-600 to-cyan-600 rounded-lg flex items-center justify-center mb-6">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Real-time Updates</h3>
              <p className="text-gray-600">
                Instant quiz submissions and real-time evaluation status updates for seamless workflow.
              </p>
            </div>

            {/* Feature 6 */}
            <div className="bg-gradient-to-br from-indigo-50 to-blue-50 p-8 rounded-2xl hover:shadow-lg transition-shadow">
              <div className="w-12 h-12 bg-gradient-to-r from-indigo-600 to-blue-600 rounded-lg flex items-center justify-center mb-6">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Fast & Reliable</h3>
              <p className="text-gray-600">
                Modern architecture ensuring quick load times and reliable performance for all users.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-20 bg-gradient-to-br from-gray-50 to-blue-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              How It Works
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Simple steps to get started with creating and managing quizzes
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Step 1 */}
            <div className="text-center">
              <div className="relative">
                <img
                  src="https://images.unsplash.com/photo-1544731612-de7f96afe55f?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1Nzl8MHwxfHNlYXJjaHw0fHxvbmxpbmUlMjBxdWl6fGVufDB8fHxibHVlfDE3NTMzNDc4NzV8MA&ixlib=rb-4.1.0&q=85"
                  alt="Create Quiz"
                  className="w-full h-64 object-cover rounded-2xl shadow-lg"
                />
                <div className="absolute -top-4 -left-4 w-12 h-12 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-full flex items-center justify-center text-white font-bold text-lg">
                  1
                </div>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mt-6 mb-3">Create Your Quiz</h3>
              <p className="text-gray-600">
                Design engaging quizzes with multiple choice and text questions, set point values, and add explanations.
              </p>
            </div>

            {/* Step 2 */}
            <div className="text-center">
              <div className="relative">
                <img
                  src="https://images.unsplash.com/photo-1541178735493-479c1a27ed24?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1Nzl8MHwxfHNlYXJjaHwyfHxkaWdpdGFsJTIwbGVhcm5pbmd8ZW58MHx8fGJsdWV8MTc1MzM0Nzg4Mnww&ixlib=rb-4.1.0&q=85"
                  alt="Take Quiz"
                  className="w-full h-64 object-cover rounded-2xl shadow-lg"
                />
                <div className="absolute -top-4 -left-4 w-12 h-12 bg-gradient-to-r from-green-600 to-emerald-600 rounded-full flex items-center justify-center text-white font-bold text-lg">
                  2
                </div>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mt-6 mb-3">Students Take Quizzes</h3>
              <p className="text-gray-600">
                Students can access and complete quizzes with an intuitive interface supporting all question types.
              </p>
            </div>

            {/* Step 3 */}
            <div className="text-center">
              <div className="relative">
                <img
                  src="https://images.unsplash.com/photo-1651796704084-a115817945b2?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1Nzl8MHwxfHNlYXJjaHwzfHxkaWdpdGFsJTIwbGVhcm5pbmd8ZW58MHx8fGJsdWV8MTc1MzM0Nzg4Mnww&ixlib=rb-4.1.0&q=85"
                  alt="Evaluate Results"
                  className="w-full h-64 object-cover rounded-2xl shadow-lg"
                />
                <div className="absolute -top-4 -left-4 w-12 h-12 bg-gradient-to-r from-purple-600 to-pink-600 rounded-full flex items-center justify-center text-white font-bold text-lg">
                  3
                </div>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mt-6 mb-3">Review & Grade</h3>
              <p className="text-gray-600">
                Admins can review text answers, provide feedback, assign grades, and publish comprehensive results.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-blue-600 to-indigo-700">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
            Ready to Transform Your Quizzes?
          </h2>
          <p className="text-xl text-blue-100 mb-8 leading-relaxed">
            Join educators and students who are already using our platform to create better learning experiences.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button
              onClick={handleGetStarted}
              className="bg-white text-blue-600 px-8 py-4 rounded-lg text-lg font-medium hover:bg-gray-50 transition-all transform hover:scale-105 shadow-lg"
            >
              Get Started Free
            </button>
            <button
              onClick={handleLogin}
              className="border-2 border-white text-white px-8 py-4 rounded-lg text-lg font-medium hover:bg-white hover:text-blue-600 transition-all"
            >
              Sign In Now
            </button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h3 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent mb-4">
              Mini Quiz Platform
            </h3>
            <p className="text-gray-400 mb-6">
              Empowering education through intelligent quiz management
            </p>
            <div className="flex justify-center space-x-6">
              <span className="text-gray-400">© 2024 Mini Quiz Platform. All rights reserved.</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

// Login Component
const Login = ({ onSwitchToRegister, onBackToLanding }) => {
  const [formData, setFormData] = useState({ email: '', password: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const result = await login(formData.email, formData.password);
    
    if (!result.success) {
      setError(result.error);
    }
    
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center px-4">
      <div className="max-w-md w-full bg-white p-8 rounded-2xl shadow-xl">
        {/* Back Button */}
        <button
          onClick={onBackToLanding}
          className="flex items-center text-gray-600 hover:text-blue-600 mb-6 group"
        >
          <svg className="w-5 h-5 mr-2 group-hover:-translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 19l-7-7 7-7"></path>
          </svg>
          Back to Home
        </button>

        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent mb-2">
            Welcome Back
          </h2>
          <p className="text-gray-600">Sign in to your Quiz Platform account</p>
        </div>
        
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6 flex items-center">
            <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd"></path>
            </svg>
            {error}
          </div>
        )}
        
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Email Address</label>
            <input
              type="email"
              placeholder="Enter your email"
              className="w-full p-4 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
              value={formData.email}
              onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Password</label>
            <input
              type="password"
              placeholder="Enter your password"
              className="w-full p-4 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
              value={formData.password}
              onChange={(e) => setFormData(prev => ({ ...prev, password: e.target.value }))}
              required
            />
          </div>
          
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white py-4 px-4 rounded-lg font-medium transition-all transform hover:scale-[1.02] disabled:opacity-50 disabled:transform-none shadow-lg"
          >
            {loading ? (
              <div className="flex items-center justify-center">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                Signing In...
              </div>
            ) : (
              'Sign In'
            )}
          </button>
        </form>
        
        <div className="text-center mt-6 pt-6 border-t border-gray-200">
          <p className="text-gray-600">
            Don't have an account?{' '}
            <button
              onClick={onSwitchToRegister}
              className="text-blue-600 hover:text-blue-700 font-medium hover:underline"
            >
              Create Account
            </button>
          </p>
        </div>
      </div>
    </div>
  );
};

// Register Component
const Register = ({ onSwitchToLogin }) => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    fullName: '',
    role: 'user'
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const { register } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const result = await register(formData.email, formData.password, formData.fullName, formData.role);
    
    if (result.success) {
      setSuccess(true);
      setTimeout(() => {
        onSwitchToLogin();
      }, 2000);
    } else {
      setError(result.error);
    }
    
    setLoading(false);
  };

  if (success) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="max-w-md w-full bg-white p-8 rounded-lg shadow-md text-center">
          <div className="text-green-600 text-5xl mb-4">✓</div>
          <h2 className="text-2xl font-bold text-green-600 mb-4">Registration Successful!</h2>
          <p className="text-gray-600">Redirecting to login...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <div className="max-w-md w-full bg-white p-8 rounded-lg shadow-md">
        <h2 className="text-2xl font-bold text-center mb-6 text-blue-600">Register for Quiz Platform</h2>
        
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}
        
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <input
              type="text"
              placeholder="Full Name"
              className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={formData.fullName}
              onChange={(e) => setFormData(prev => ({ ...prev, fullName: e.target.value }))}
              required
            />
          </div>
          
          <div className="mb-4">
            <input
              type="email"
              placeholder="Email"
              className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={formData.email}
              onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
              required
            />
          </div>
          
          <div className="mb-4">
            <input
              type="password"
              placeholder="Password"
              className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={formData.password}
              onChange={(e) => setFormData(prev => ({ ...prev, password: e.target.value }))}
              required
            />
          </div>
          
          <div className="mb-6">
            <select
              className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={formData.role}
              onChange={(e) => setFormData(prev => ({ ...prev, role: e.target.value }))}
            >
              <option value="user">Student</option>
              <option value="admin">Admin/Teacher</option>
            </select>
          </div>
          
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-500 hover:bg-blue-600 text-white py-3 px-4 rounded-lg font-medium transition-colors disabled:opacity-50"
          >
            {loading ? 'Creating Account...' : 'Create Account'}
          </button>
        </form>
        
        <div className="text-center mt-4">
          <p className="text-gray-600">
            Already have an account?{' '}
            <button
              onClick={onSwitchToLogin}
              className="text-blue-500 hover:text-blue-600 font-medium"
            >
              Sign In
            </button>
          </p>
        </div>
      </div>
    </div>
  );
};

// Enhanced Quiz Creator Component
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
    explanation: '',
    points: 1
  });

  const addQuestion = () => {
    if (!currentQuestion.question_text) {
      alert('Please enter question text');
      return;
    }
    
    if (currentQuestion.question_type === 'multiple_choice') {
      const filteredOptions = currentQuestion.options.filter(opt => opt.trim() !== '');
      if (filteredOptions.length < 2) {
        alert('Please provide at least 2 options for multiple choice questions');
        return;
      }
      if (!currentQuestion.correct_answer) {
        alert('Please provide the correct answer');
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
    } else if (currentQuestion.question_type === 'text') {
      const newQuestion = {
        question_text: currentQuestion.question_text,
        question_type: 'text',
        points: currentQuestion.points,
        explanation: currentQuestion.explanation
      };
      
      setQuizData(prev => ({
        ...prev,
        questions: [...prev.questions, newQuestion]
      }));
    }
    
    // Reset current question
    setCurrentQuestion({
      question_text: '',
      question_type: 'multiple_choice',
      options: ['', '', '', ''],
      correct_answer: '',
      explanation: '',
      points: 1
    });
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
        
        <div className="mb-4">
          <select
            className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={currentQuestion.question_type}
            onChange={(e) => setCurrentQuestion(prev => ({ 
              ...prev, 
              question_type: e.target.value,
              options: e.target.value === 'multiple_choice' ? ['', '', '', ''] : [],
              correct_answer: ''
            }))}
          >
            <option value="multiple_choice">Multiple Choice</option>
            <option value="text">Text Answer</option>
          </select>
        </div>
        
        <textarea
          placeholder="Question Text *"
          className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 mb-4"
          rows="3"
          value={currentQuestion.question_text}
          onChange={(e) => setCurrentQuestion(prev => ({ ...prev, question_text: e.target.value }))}
        />
        
        {currentQuestion.question_type === 'multiple_choice' && (
          <>
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
          </>
        )}
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <input
            type="number"
            placeholder="Points"
            min="1"
            className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={currentQuestion.points}
            onChange={(e) => setCurrentQuestion(prev => ({ ...prev, points: parseInt(e.target.value) || 1 }))}
          />
          
          <textarea
            placeholder="Explanation (optional)"
            className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            rows="2"
            value={currentQuestion.explanation}
            onChange={(e) => setCurrentQuestion(prev => ({ ...prev, explanation: e.target.value }))}
          />
        </div>
        
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
              <div className="flex justify-between items-start mb-2">
                <p className="font-medium">{index + 1}. {question.question_text}</p>
                <span className="text-sm bg-blue-100 text-blue-800 px-2 py-1 rounded">
                  {question.question_type === 'multiple_choice' ? 'MCQ' : 'Text'} ({question.points} pts)
                </span>
              </div>
              
              {question.question_type === 'multiple_choice' && (
                <>
                  <p className="text-sm text-gray-600 mt-1">
                    Options: {question.options.join(', ')}
                  </p>
                  <p className="text-sm text-green-600 mt-1">
                    Correct Answer: {question.correct_answer}
                  </p>
                </>
              )}
              
              {question.explanation && (
                <p className="text-sm text-blue-600 mt-1">
                  Explanation: {question.explanation}
                </p>
              )}
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

// Enhanced Quiz Taking Component
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
      setTimeLeft(quiz.time_limit * 60);
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

  const handleAnswer = (questionId, answer, answerType = 'selected') => {
    setResponses(prev => ({
      ...prev,
      [questionId]: {
        ...prev[questionId],
        [answerType === 'selected' ? 'selected_answer' : 'text_answer']: answer
      }
    }));
  };

  const submitQuiz = async () => {
    const responseList = Object.entries(responses).map(([questionId, answerData]) => ({
      question_id: questionId,
      selected_answer: answerData.selected_answer || null,
      text_answer: answerData.text_answer || null
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
        <div className="flex justify-between items-start mb-4">
          <h3 className="text-xl font-semibold">{currentQuestion.question_text}</h3>
          <span className="text-sm bg-blue-100 text-blue-800 px-2 py-1 rounded">
            {currentQuestion.points} {currentQuestion.points === 1 ? 'point' : 'points'}
          </span>
        </div>
        
        {currentQuestion.question_type === 'multiple_choice' ? (
          <div className="space-y-3">
            {currentQuestion.options.map((option, index) => (
              <label key={index} className="flex items-center p-4 border rounded-lg hover:bg-gray-50 cursor-pointer">
                <input
                  type="radio"
                  name={`question-${currentQuestion.id}`}
                  value={option}
                  checked={responses[currentQuestion.id]?.selected_answer === option}
                  onChange={(e) => handleAnswer(currentQuestion.id, e.target.value, 'selected')}
                  className="mr-3 text-blue-500"
                />
                <span className="text-lg">{option}</span>
              </label>
            ))}
          </div>
        ) : (
          <div>
            <textarea
              placeholder="Type your answer here..."
              className="w-full p-4 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows="6"
              value={responses[currentQuestion.id]?.text_answer || ''}
              onChange={(e) => handleAnswer(currentQuestion.id, e.target.value, 'text')}
            />
            <p className="text-sm text-gray-600 mt-2">
              This question will be manually evaluated by your instructor.
            </p>
          </div>
        )}
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

// Enhanced Results Component
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
        
        {!result.is_evaluated && result.detailed_results.some(r => r.question_type === 'text') && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
            <p className="text-yellow-800 font-medium">
              ⏳ Some questions require manual evaluation. Your final score will be available once graded.
            </p>
          </div>
        )}
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
          <div className="bg-blue-50 p-4 rounded-lg">
            <div className="text-2xl font-bold text-blue-600">{result.total_score}/{result.max_possible_score}</div>
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
          <div key={index} className={`border-l-4 ${
            item.question_type === 'text' 
              ? item.is_evaluated 
                ? (item.points_earned > 0 ? 'border-green-500 bg-green-50' : 'border-red-500 bg-red-50')
                : 'border-yellow-500 bg-yellow-50'
              : item.is_correct 
                ? 'border-green-500 bg-green-50' 
                : 'border-red-500 bg-red-50'
          } p-4 mb-4 rounded-r-lg`}>
            <div className="flex items-start justify-between mb-2">
              <p className="font-medium text-gray-800">
                {index + 1}. {item.question_text}
              </p>
              <div className="flex items-center gap-2">
                <span className="text-sm bg-blue-100 text-blue-800 px-2 py-1 rounded">
                  {item.points_earned}/{item.points_possible} pts
                </span>
                {item.question_type === 'multiple_choice' && (
                  <span className={`px-2 py-1 rounded text-sm font-medium ${
                    item.is_correct ? 'bg-green-200 text-green-800' : 'bg-red-200 text-red-800'
                  }`}>
                    {item.is_correct ? 'Correct' : 'Incorrect'}
                  </span>
                )}
                {item.question_type === 'text' && (
                  <span className={`px-2 py-1 rounded text-sm font-medium ${
                    !item.is_evaluated ? 'bg-yellow-200 text-yellow-800' :
                    item.points_earned > 0 ? 'bg-green-200 text-green-800' : 'bg-red-200 text-red-800'
                  }`}>
                    {!item.is_evaluated ? 'Pending' : 'Graded'}
                  </span>
                )}
              </div>
            </div>
            
            <div className="space-y-1 text-sm">
              {item.question_type === 'multiple_choice' && (
                <>
                  <p><span className="font-medium">Your Answer:</span> {item.selected_answer}</p>
                  {!item.is_correct && (
                    <p><span className="font-medium">Correct Answer:</span> {item.correct_answer}</p>
                  )}
                </>
              )}
              
              {item.question_type === 'text' && (
                <div>
                  <p><span className="font-medium">Your Answer:</span></p>
                  <div className="bg-gray-100 p-3 rounded mt-1 whitespace-pre-wrap">
                    {item.text_answer}
                  </div>
                  {item.feedback && (
                    <p className="text-blue-600 mt-2">
                      <span className="font-medium">Feedback:</span> {item.feedback}
                    </p>
                  )}
                </div>
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
          Back to Dashboard
        </button>
      </div>
    </div>
  );
};

// Admin Evaluation Component
const AdminEvaluation = () => {
  const [pendingResults, setPendingResults] = useState([]);
  const [selectedResult, setSelectedResult] = useState(null);
  const [evaluations, setEvaluations] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPendingEvaluations();
  }, []);

  const fetchPendingEvaluations = async () => {
    try {
      const response = await axios.get(`${API}/admin/results/pending`);
      setPendingResults(response.data);
    } catch (error) {
      console.error('Error fetching pending evaluations:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleEvaluationChange = (questionId, field, value) => {
    setEvaluations(prev => ({
      ...prev,
      [questionId]: {
        ...prev[questionId],
        question_id: questionId,
        [field]: value
      }
    }));
  };

  const submitEvaluation = async () => {
    if (!selectedResult) return;

    const evaluationList = Object.values(evaluations).map(evaluation => ({
      question_id: evaluation.question_id,
      points_awarded: parseInt(evaluation.points_awarded) || 0,
      feedback: evaluation.feedback || ''
    }));

    try {
      await axios.post(`${API}/admin/evaluate/${selectedResult.id}`, {
        result_id: selectedResult.id,
        evaluations: evaluationList
      });
      
      alert('Evaluation completed successfully!');
      setSelectedResult(null);
      setEvaluations({});
      fetchPendingEvaluations();
    } catch (error) {
      console.error('Error submitting evaluation:', error);
      alert('Error submitting evaluation. Please try again.');
    }
  };

  const publishResult = async (resultId) => {
    try {
      await axios.post(`${API}/admin/publish/${resultId}`);
      alert('Result published successfully!');
      fetchPendingEvaluations();
    } catch (error) {
      console.error('Error publishing result:', error);
      alert('Error publishing result. Please try again.');
    }
  };

  if (loading) {
    return <div className="text-center py-8">Loading pending evaluations...</div>;
  }

  if (selectedResult) {
    const textQuestions = selectedResult.detailed_results.filter(r => r.question_type === 'text');
    
    return (
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-blue-600">Evaluate Quiz Attempt</h2>
          <button
            onClick={() => {
              setSelectedResult(null);
              setEvaluations({});
            }}
            className="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded-lg"
          >
            Back to List
          </button>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-md mb-6">
          <h3 className="text-lg font-semibold mb-4">Quiz: {selectedResult.quiz_title}</h3>
          <p className="text-gray-600 mb-2">Student: {selectedResult.user_name} ({selectedResult.user_email})</p>
          <p className="text-gray-600 mb-4">Auto Score: {selectedResult.auto_score} points</p>
        </div>

        {textQuestions.map((question, index) => (
          <div key={question.question_id} className="bg-white p-6 rounded-lg shadow-md mb-6">
            <h4 className="font-semibold mb-4">
              Question {index + 1}: {question.question_text}
            </h4>
            <p className="text-sm text-gray-600 mb-2">Points Possible: {question.points_possible}</p>
            
            <div className="bg-gray-50 p-4 rounded-lg mb-4">
              <p className="font-medium mb-2">Student's Answer:</p>
              <div className="whitespace-pre-wrap">{question.text_answer}</div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Points Awarded (0-{question.points_possible})
                </label>
                <input
                  type="number"
                  min="0"
                  max={question.points_possible}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  value={evaluations[question.question_id]?.points_awarded || ''}
                  onChange={(e) => handleEvaluationChange(question.question_id, 'points_awarded', e.target.value)}
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Feedback (optional)
                </label>
                <textarea
                  className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  rows="3"
                  value={evaluations[question.question_id]?.feedback || ''}
                  onChange={(e) => handleEvaluationChange(question.question_id, 'feedback', e.target.value)}
                  placeholder="Provide feedback to the student..."
                />
              </div>
            </div>
          </div>
        ))}
        
        <div className="text-center">
          <button
            onClick={submitEvaluation}
            className="bg-green-500 hover:bg-green-600 text-white px-8 py-3 rounded-lg font-medium text-lg"
          >
            Submit Evaluation
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="admin-evaluation">
      <h2 className="text-2xl font-bold mb-6 text-blue-600">Pending Evaluations</h2>
      
      {pendingResults.length === 0 ? (
        <div className="text-center py-8 text-gray-600">
          No pending evaluations found.
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6">
          {pendingResults.map((result) => (
            <div key={result.id} className="bg-white p-6 rounded-lg shadow-md">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-semibold">{result.quiz_title}</h3>
                  <p className="text-gray-600">Student: {result.user_name} ({result.user_email})</p>
                  <p className="text-gray-600">Submitted: {new Date(result.completed_at).toLocaleString()}</p>
                  <p className="text-gray-600">Auto Score: {result.auto_score}/{result.max_possible_score} points</p>
                </div>
                
                <div className="flex gap-2">
                  <button
                    onClick={() => setSelectedResult(result)}
                    className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg text-sm"
                  >
                    Evaluate
                  </button>
                  
                  {result.is_evaluated && (
                    <button
                      onClick={() => publishResult(result.id)}
                      className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg text-sm"
                    >
                      Publish
                    </button>
                  )}
                </div>
              </div>
              
              <div className="text-sm text-yellow-600">
                {result.detailed_results.filter(r => r.question_type === 'text').length} text question(s) need evaluation
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// Enhanced Quiz List Component
const QuizList = ({ onSelectQuiz }) => {
  const [quizzes, setQuizzes] = useState([]);
  const [loading, setLoading] = useState(true);
  const { isAdmin } = useAuth();

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
          No quizzes available. {isAdmin && "Create one to get started!"}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {quizzes.map((quiz) => (
            <div key={quiz.id} className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow">
              <h3 className="text-xl font-semibold mb-2 text-gray-800">{quiz.title}</h3>
              <p className="text-gray-600 mb-2">Subject: {quiz.subject}</p>
              <p className="text-gray-600 mb-2">Questions: {quiz.total_questions}</p>
              <p className="text-gray-600 mb-2">Total Points: {quiz.total_points}</p>
              {quiz.time_limit && (
                <p className="text-gray-600 mb-2">Time Limit: {quiz.time_limit} minutes</p>
              )}
              {quiz.requires_evaluation && (
                <p className="text-yellow-600 mb-2 text-sm">⚠️ Contains text questions</p>
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

// My Results Component
const MyResults = () => {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMyResults();
  }, []);

  const fetchMyResults = async () => {
    try {
      const response = await axios.get(`${API}/results/my/all`);
      setResults(response.data);
    } catch (error) {
      console.error('Error fetching results:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="text-center py-8">Loading your results...</div>;
  }

  return (
    <div className="my-results">
      <h2 className="text-2xl font-bold mb-6 text-blue-600">My Quiz Results</h2>
      
      {results.length === 0 ? (
        <div className="text-center py-8 text-gray-600">
          No quiz results found. Take a quiz to see your results here!
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6">
          {results.map((result) => (
            <div key={result.id} className="bg-white p-6 rounded-lg shadow-md">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-semibold">{result.quiz_title}</h3>
                  <p className="text-gray-600">Completed: {new Date(result.completed_at).toLocaleString()}</p>
                </div>
                
                <div className="text-right">
                  <div className="text-2xl font-bold text-blue-600">
                    {result.total_score}/{result.max_possible_score}
                  </div>
                  <div className="text-lg text-gray-600">{result.percentage}%</div>
                </div>
              </div>
              
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  {result.is_evaluated ? (
                    <span className="text-green-600 text-sm">✓ Fully Graded</span>
                  ) : (
                    <span className="text-yellow-600 text-sm">⏳ Pending Evaluation</span>
                  )}
                  
                  {result.time_taken && (
                    <span className="text-gray-600 text-sm">
                      Time: {Math.floor(result.time_taken / 60)}:{(result.time_taken % 60).toString().padStart(2, '0')}
                    </span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// Main App Component
function App() {
  const [authView, setAuthView] = useState('login');
  const [showLanding, setShowLanding] = useState(true);
  
  return (
    <AuthProvider>
      <AppContent 
        authView={authView} 
        setAuthView={setAuthView}
        showLanding={showLanding}
        setShowLanding={setShowLanding}
      />
    </AuthProvider>
  );
}

const AppContent = ({ authView, setAuthView, showLanding, setShowLanding }) => {
  const { isAuthenticated, isAdmin, loading, user, logout } = useAuth();
  const [currentView, setCurrentView] = useState('home');
  const [selectedQuizId, setSelectedQuizId] = useState(null);
  const [quizResult, setQuizResult] = useState(null);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 text-lg">Loading...</p>
        </div>
      </div>
    );
  }

  // Show landing page if not authenticated and showLanding is true
  if (!isAuthenticated && showLanding) {
    return <LandingPage setShowLanding={setShowLanding} setAuthView={setAuthView} />;
  }

  if (!isAuthenticated) {
    return authView === 'login' ? (
      <Login 
        onSwitchToRegister={() => setAuthView('register')} 
        onBackToLanding={() => setShowLanding(true)}
      />
    ) : (
      <Register 
        onSwitchToLogin={() => setAuthView('login')} 
        onBackToLanding={() => setShowLanding(true)}
      />
    );
  }

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
            
            <div className="flex items-center space-x-4">
              <span className="text-gray-600">Welcome, {user?.full_name}</span>
              <span className={`px-2 py-1 rounded text-xs font-medium ${
                isAdmin ? 'bg-purple-100 text-purple-800' : 'bg-green-100 text-green-800'
              }`}>
                {isAdmin ? 'Admin' : 'Student'}
              </span>
              
              <div className="flex space-x-2">
                <button
                  onClick={() => setCurrentView('home')}
                  className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                    currentView === 'home' ? 'bg-blue-500 text-white' : 'text-gray-600 hover:text-blue-600'
                  }`}
                >
                  Dashboard
                </button>
                
                {!isAdmin && (
                  <button
                    onClick={() => setCurrentView('my-results')}
                    className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                      currentView === 'my-results' ? 'bg-blue-500 text-white' : 'text-gray-600 hover:text-blue-600'
                    }`}
                  >
                    My Results
                  </button>
                )}
                
                {isAdmin && (
                  <>
                    <button
                      onClick={() => setCurrentView('create')}
                      className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                        currentView === 'create' ? 'bg-blue-500 text-white' : 'text-gray-600 hover:text-blue-600'
                      }`}
                    >
                      Create Quiz
                    </button>
                    
                    <button
                      onClick={() => setCurrentView('evaluate')}
                      className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                        currentView === 'evaluate' ? 'bg-blue-500 text-white' : 'text-gray-600 hover:text-blue-600'
                      }`}
                    >
                      Evaluate
                    </button>
                  </>
                )}
                
                <button
                  onClick={logout}
                  className="text-red-600 hover:text-red-700 font-medium px-4 py-2"
                >
                  Logout
                </button>
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        {currentView === 'home' && (
          <QuizList onSelectQuiz={handleSelectQuiz} />
        )}
        
        {currentView === 'my-results' && !isAdmin && (
          <MyResults />
        )}
        
        {currentView === 'create' && isAdmin && (
          <QuizCreator onQuizCreated={() => setCurrentView('home')} />
        )}
        
        {currentView === 'evaluate' && isAdmin && (
          <AdminEvaluation />
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
};

export default App;