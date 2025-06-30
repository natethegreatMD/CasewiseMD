import React, { useState, useEffect } from 'react';
import './App.css';
// Import DiagnosticWorkflow with proper error handling
import DiagnosticWorkflow from './DiagnosticWorkflow';

// Types for case categories
interface CaseCategory {
  id: string;
  title: string;
  description: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  modality: string;
  caseCount: number;
  imageUrl?: string;
}

// Sample case categories
const CASE_CATEGORIES: CaseCategory[] = [
  {
    id: 'ovarian-cancer',
    title: 'Ovarian Cancer',
    description: 'Complex cases involving ovarian malignancies and differential diagnoses',
    difficulty: 'intermediate',
    modality: 'CT',
    caseCount: 1,
    imageUrl: '/api/placeholder/ovarian'
  },
  {
    id: 'chest-xray',
    title: 'Chest X-Ray',
    description: 'Basic to advanced chest radiography interpretation',
    difficulty: 'beginner',
    modality: 'X-Ray',
    caseCount: 5,
    imageUrl: '/api/placeholder/chest'
  },
  {
    id: 'brain-mri',
    title: 'Brain MRI',
    description: 'Neurological imaging cases including tumors and vascular conditions',
    difficulty: 'advanced',
    modality: 'MRI',
    caseCount: 3,
    imageUrl: '/api/placeholder/brain'
  },
  {
    id: 'abdomen-ct',
    title: 'Abdomen CT',
    description: 'Abdominal pathology and trauma cases',
    difficulty: 'intermediate',
    modality: 'CT',
    caseCount: 4,
    imageUrl: '/api/placeholder/abdomen'
  },
  {
    id: 'obstetric-ultrasound',
    title: 'Obstetric Ultrasound',
    description: 'Prenatal imaging and fetal development assessment',
    difficulty: 'beginner',
    modality: 'Ultrasound',
    caseCount: 2,
    imageUrl: '/api/placeholder/obstetric'
  },
  {
    id: 'cardiac-ct',
    title: 'Cardiac CT',
    description: 'Cardiovascular imaging and coronary artery assessment',
    difficulty: 'advanced',
    modality: 'CT',
    caseCount: 2,
    imageUrl: '/api/placeholder/cardiac'
  }
];

// Navigation items
const NAVIGATION_ITEMS = [
  { id: 'home', label: 'Home', path: '/' },
  { id: 'cases', label: 'Cases', path: '/cases' },
  { id: 'progress', label: 'My Progress', path: '/progress' },
  { id: 'leaderboard', label: 'Leaderboard', path: '/leaderboard' },
  { id: 'resources', label: 'Resources', path: '/resources' },
  { id: 'about', label: 'About', path: '/about' }
];

function App() {
  const [currentPage, setCurrentPage] = useState('home');
  const [currentRoute, setCurrentRoute] = useState('home');

  // Handle route changes
  useEffect(() => {
    const path = window.location.pathname;
    if (path === '/diagnostic') {
      setCurrentRoute('diagnostic');
    } else {
      setCurrentRoute('home');
    }
  }, []);

  const handleCaseClick = (categoryId: string) => {
    if (categoryId === 'ovarian-cancer') {
      // Navigate to the diagnostic workflow
      window.history.pushState({}, '', '/diagnostic');
      setCurrentRoute('diagnostic');
    } else {
      // Show coming soon for other cases
      alert('Coming Soon! This case category is under development.');
    }
  };

  const handleNavigationClick = (pageId: string) => {
    if (pageId === 'home') {
      window.history.pushState({}, '', '/');
      setCurrentRoute('home');
      setCurrentPage('home');
    } else {
      // Show coming soon for other pages
      alert('Coming Soon! This feature is under development.');
    }
  };

  const handleBackToHome = () => {
    window.history.pushState({}, '', '/');
    setCurrentRoute('home');
    setCurrentPage('home');
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner': return 'difficulty-beginner';
      case 'intermediate': return 'difficulty-intermediate';
      case 'advanced': return 'difficulty-advanced';
      default: return '';
    }
  };

  const getModalityColor = (modality: string) => {
    switch (modality.toLowerCase()) {
      case 'ct': return '#3182ce';
      case 'mri': return '#38a169';
      case 'x-ray': return '#d69e2e';
      case 'ultrasound': return '#805ad5';
      default: return '#718096';
    }
  };

  // Render diagnostic workflow if on that route
  if (currentRoute === 'diagnostic') {
    return <DiagnosticWorkflow onBackToHome={handleBackToHome} />;
  }

  // Render home page
  return (
    <div className="App">
      <header className="app-header">
        <h1>CasewiseMD</h1>
        <p className="app-subtitle">AI-Powered Radiology Education Platform</p>
        
        {/* Navigation */}
        <nav className="main-navigation">
          {NAVIGATION_ITEMS.map((item) => (
            <button
              key={item.id}
              className={`nav-item ${currentPage === item.id ? 'active' : ''}`}
              onClick={() => handleNavigationClick(item.id)}
            >
              {item.label}
            </button>
          ))}
        </nav>
      </header>

      <main className="app-main">
        {/* Hero Section */}
        <section className="hero-section">
          <div className="hero-content">
            <h2>Master Radiology Through Interactive Cases</h2>
            <p>Practice with real-world scenarios, get instant feedback, and track your progress as you develop your diagnostic skills.</p>
            <div className="hero-stats">
              <div className="stat-item">
                <span className="stat-number">50+</span>
                <span className="stat-label">Cases</span>
              </div>
              <div className="stat-item">
                <span className="stat-number">5</span>
                <span className="stat-label">Modalities</span>
              </div>
              <div className="stat-item">
                <span className="stat-number">3</span>
                <span className="stat-label">Difficulty Levels</span>
              </div>
            </div>
          </div>
        </section>

        {/* Quick Actions - Moved to top */}
        <section className="quick-actions">
          <h2>Get Started</h2>
          <div className="actions-grid">
            <button className="action-btn primary featured" onClick={() => handleCaseClick('ovarian-cancer')}>
              <span className="action-icon">🚀</span>
              <span className="action-title">Start Practice Case</span>
              <span className="action-subtitle">Ovarian Cancer - Interactive Diagnostic Workflow</span>
            </button>
            <button className="action-btn" onClick={() => handleNavigationClick('progress')}>
              <span className="action-icon">📈</span>
              <span>View Progress</span>
            </button>
            <button className="action-btn" onClick={() => handleNavigationClick('leaderboard')}>
              <span className="action-icon">🏅</span>
              <span>Leaderboard</span>
            </button>
            <button className="action-btn" onClick={() => handleNavigationClick('resources')}>
              <span className="action-icon">📖</span>
              <span>Learning Resources</span>
            </button>
          </div>
        </section>

        {/* Case Categories */}
        <section className="case-categories">
          <h2>Case Categories</h2>
          <p className="section-description">Choose a category to start practicing with interactive diagnostic cases</p>
          
          <div className="categories-grid">
            {CASE_CATEGORIES.map((category) => (
              <div
                key={category.id}
                className="category-card"
                onClick={() => handleCaseClick(category.id)}
              >
                <div className="category-header">
                  <h3>{category.title}</h3>
                  <div className="category-badges">
                    <span className={`badge ${getDifficultyColor(category.difficulty)}`}>
                      {category.difficulty}
                    </span>
                    <span 
                      className="badge modality-badge"
                      style={{ backgroundColor: getModalityColor(category.modality) }}
                    >
                      {category.modality}
                    </span>
                  </div>
                </div>
                <p className="category-description">{category.description}</p>
                <div className="category-footer">
                  <span className="case-count">{category.caseCount} cases available</span>
                  <button className="start-case-btn">
                    {category.id === 'ovarian-cancer' ? 'Start Case' : 'Coming Soon'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Features Section */}
        <section className="features-section">
          <h2>Platform Features</h2>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">🔍</div>
              <h3>Interactive Diagnosis</h3>
              <p>Step-by-step diagnostic workflow with AI-guided feedback</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">📊</div>
              <h3>Progress Tracking</h3>
              <p>Monitor your improvement with detailed analytics and performance metrics</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🏆</div>
              <h3>Leaderboards</h3>
              <p>Compete with peers and climb the rankings</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">📚</div>
              <h3>Learning Resources</h3>
              <p>Access comprehensive educational materials and references</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🖼️</div>
              <h3>DICOM Viewer</h3>
              <p>Professional-grade image viewing with advanced tools</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🤖</div>
              <h3>AI Assistance</h3>
              <p>Get intelligent hints and explanations throughout your practice</p>
            </div>
          </div>
        </section>
      </main>

      <footer className="app-footer">
        <div className="footer-content">
          <div className="footer-section">
            <h4>CasewiseMD</h4>
            <p>Advancing radiology education through AI-powered interactive learning.</p>
          </div>
          <div className="footer-section">
            <h4>Contact</h4>
            <p>Email: support@casewisemd.org</p>
            <p>Follow us for updates</p>
          </div>
          <div className="footer-section">
            <h4>Legal</h4>
            <p>Privacy Policy</p>
            <p>Terms of Service</p>
          </div>
        </div>
        <div className="footer-bottom">
          <p>&copy; 2024 CasewiseMD. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
