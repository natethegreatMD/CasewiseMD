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
  available: boolean; // New field to track availability
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
    imageUrl: '/api/placeholder/ovarian',
    available: true
  },
  {
    id: 'chest-xray',
    title: 'Chest X-Ray',
    description: 'Basic to advanced chest radiography interpretation',
    difficulty: 'beginner',
    modality: 'X-Ray',
    caseCount: 0,
    imageUrl: '/api/placeholder/chest',
    available: false
  },
  {
    id: 'brain-mri',
    title: 'Brain MRI',
    description: 'Neurological imaging cases including tumors and vascular conditions',
    difficulty: 'advanced',
    modality: 'MRI',
    caseCount: 0,
    imageUrl: '/api/placeholder/brain',
    available: false
  },
  {
    id: 'abdomen-ct',
    title: 'Abdomen CT',
    description: 'Abdominal pathology and trauma cases',
    difficulty: 'intermediate',
    modality: 'CT',
    caseCount: 0,
    imageUrl: '/api/placeholder/abdomen',
    available: false
  },
  {
    id: 'obstetric-ultrasound',
    title: 'Obstetric Ultrasound',
    description: 'Prenatal imaging and fetal development assessment',
    difficulty: 'beginner',
    modality: 'Ultrasound',
    caseCount: 0,
    imageUrl: '/api/placeholder/obstetric',
    available: false
  },
  {
    id: 'cardiac-ct',
    title: 'Cardiac CT',
    description: 'Cardiovascular imaging and coronary artery assessment',
    difficulty: 'advanced',
    modality: 'CT',
    caseCount: 0,
    imageUrl: '/api/placeholder/cardiac',
    available: false
  }
];

// Navigation items
const NAVIGATION_ITEMS = [
  { id: 'home', label: 'Home', path: '/', available: true },
  { id: 'cases', label: 'Cases', path: '/cases', available: false },
  { id: 'progress', label: 'My Progress', path: '/progress', available: false },
  { id: 'leaderboard', label: 'Leaderboard', path: '/leaderboard', available: false },
  { id: 'resources', label: 'Resources', path: '/resources', available: false },
  { id: 'about', label: 'About', path: '/about', available: false }
];

function App() {
  const [currentPage, setCurrentPage] = useState('home');
  const [currentRoute, setCurrentRoute] = useState('home');
  const [showComingSoonModal, setShowComingSoonModal] = useState(false);
  const [comingSoonFeature, setComingSoonFeature] = useState('');

  // Handle route changes
  useEffect(() => {
    const path = window.location.pathname;
    if (path === '/diagnostic') {
      setCurrentRoute('diagnostic');
    } else {
      setCurrentRoute('home');
    }
  }, []);

  // Handle browser back/forward button
  useEffect(() => {
    const handlePopState = (event: PopStateEvent) => {
      const path = window.location.pathname;
      if (path === '/diagnostic') {
        setCurrentRoute('diagnostic');
      } else {
        setCurrentRoute('home');
        setCurrentPage('home');
      }
    };

    window.addEventListener('popstate', handlePopState);
    
    // Cleanup
    return () => {
      window.removeEventListener('popstate', handlePopState);
    };
  }, []);

  const handleCaseClick = (categoryId: string) => {
    const category = CASE_CATEGORIES.find(cat => cat.id === categoryId);
    
    if (category?.available) {
      // Navigate to the diagnostic workflow
      window.history.pushState({}, '', '/diagnostic');
      setCurrentRoute('diagnostic');
    } else {
      // Show coming soon modal instead of alert
      setComingSoonFeature(category?.title || 'This feature');
      setShowComingSoonModal(true);
    }
  };

  const handleNavigationClick = (pageId: string) => {
    const navItem = NAVIGATION_ITEMS.find(item => item.id === pageId);
    
    if (navItem?.available) {
      window.history.pushState({}, '', '/');
      setCurrentRoute('home');
      setCurrentPage('home');
    } else {
      // Show coming soon modal instead of alert
      setComingSoonFeature(navItem?.label || 'This feature');
      setShowComingSoonModal(true);
    }
  };

  const handleBackToHome = () => {
    window.history.pushState({}, '', '/');
    setCurrentRoute('home');
    setCurrentPage('home');
  };

  const closeComingSoonModal = () => {
    setShowComingSoonModal(false);
    setComingSoonFeature('');
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
        <div className="header-content">
          <h1>CasewiseMD</h1>
          <p className="app-subtitle">AI-Powered Radiology Education Platform</p>
        </div>
        
        {/* Navigation */}
        <nav className="main-navigation">
          {NAVIGATION_ITEMS.map((item) => (
            <button
              key={item.id}
              className={`nav-item ${currentPage === item.id ? 'active' : ''} ${!item.available ? 'disabled' : ''}`}
              onClick={() => handleNavigationClick(item.id)}
            >
              {item.label}
              {!item.available && <span className="coming-soon-badge">Soon</span>}
            </button>
          ))}
        </nav>
      </header>

      <main className="app-main">
        {/* Hero Section */}
        <section className="hero-section">
          <div className="hero-content">
            <h2>Master Radiology with Interactive Cases</h2>
            <p>Practice with real cases, get instant AI feedback, and track your progress. Start with our featured case and watch as thousands more cases become available.</p>
            <div className="hero-stats">
              <div className="stat-item">
                <span className="stat-number">1</span>
                <span className="stat-label">Available Now</span>
              </div>
              <div className="stat-item">
                <span className="stat-number">1000+</span>
                <span className="stat-label">Cases Coming Soon</span>
              </div>
              <div className="stat-item">
                <span className="stat-number">6</span>
                <span className="stat-label">Modalities Planned</span>
              </div>
            </div>
          </div>
        </section>

        {/* Quick Actions */}
        <section className="quick-actions">
          <h2>Get Started</h2>
          <div className="actions-grid">
            <button className="action-btn primary featured" onClick={() => handleCaseClick('ovarian-cancer')}>
              <span className="action-icon">🚀</span>
              <span className="action-title">Start Available Case</span>
              <span className="action-subtitle">Ovarian Cancer - Interactive Diagnostic Workflow</span>
            </button>
            <button className="action-btn disabled" onClick={() => handleNavigationClick('progress')}>
              <span className="action-icon">📈</span>
              <span>Progress Tracking</span>
              <span className="coming-soon-text">Coming Soon</span>
            </button>
            <button className="action-btn disabled" onClick={() => handleNavigationClick('leaderboard')}>
              <span className="action-icon">🏅</span>
              <span>Leaderboard</span>
              <span className="coming-soon-text">Coming Soon</span>
            </button>
            <button className="action-btn disabled" onClick={() => handleNavigationClick('resources')}>
              <span className="action-icon">📖</span>
              <span>Learning Resources</span>
              <span className="coming-soon-text">Coming Soon</span>
            </button>
          </div>
        </section>

        {/* Case Categories */}
        <section className="case-categories">
          <h2>Case Categories</h2>
          <p className="section-description">
            Start with our featured ovarian cancer case. More categories with hundreds of cases each are in development.
          </p>
          
          <div className="categories-grid">
            {CASE_CATEGORIES.map((category) => (
              <div
                key={category.id}
                className={`category-card ${!category.available ? 'disabled' : ''}`}
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
                  <span className="case-count">
                    {category.available 
                      ? `${category.caseCount} case${category.caseCount === 1 ? '' : 's'} available`
                      : 'Cases in development'
                    }
                  </span>
                  <button className={`start-case-btn ${!category.available ? 'disabled' : ''}`}>
                    {category.available ? 'Start Case' : 'Coming Soon'}
                  </button>
                </div>
                {!category.available && (
                  <div className="coming-soon-overlay">
                    <div className="coming-soon-content">
                      <span className="coming-soon-icon">🚧</span>
                      <span className="coming-soon-label">In Development</span>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </section>

        {/* Development Status */}
        <section className="development-status">
          <h2>Platform Development</h2>
          <div className="status-grid">
            <div className="status-card completed">
              <div className="status-icon">✅</div>
              <h3>Available Now</h3>
              <ul>
                <li>Interactive diagnostic workflow</li>
                <li>AI-powered feedback system</li>
                <li>Professional DICOM viewer</li>
                <li>Ovarian cancer case study</li>
              </ul>
            </div>
            <div className="status-card in-progress">
              <div className="status-icon">🔄</div>
              <h3>Coming Soon</h3>
              <ul>
                <li>1000+ additional cases</li>
                <li>Progress tracking & analytics</li>
                <li>Student leaderboards</li>
                <li>Comprehensive learning resources</li>
                <li>Multiple imaging modalities</li>
              </ul>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="features-section">
          <h2>Platform Features</h2>
          <div className="features-grid">
            <div className="feature-card available">
              <div className="feature-icon">🔍</div>
              <h3>Interactive Diagnosis</h3>
              <p>Step-by-step diagnostic workflow with AI-guided feedback</p>
              <span className="feature-status available">Available Now</span>
            </div>
            <div className="feature-card available">
              <div className="feature-icon">🖼️</div>
              <h3>DICOM Viewer</h3>
              <p>Professional-grade image viewing with advanced tools</p>
              <span className="feature-status available">Available Now</span>
            </div>
            <div className="feature-card available">
              <div className="feature-icon">🤖</div>
              <h3>AI Assistance</h3>
              <p>Get intelligent hints and explanations throughout your practice</p>
              <span className="feature-status available">Available Now</span>
            </div>
            <div className="feature-card coming-soon">
              <div className="feature-icon">📊</div>
              <h3>Progress Tracking</h3>
              <p>Monitor your improvement with detailed analytics and performance metrics</p>
              <span className="feature-status coming-soon">Coming Soon</span>
            </div>
            <div className="feature-card coming-soon">
              <div className="feature-icon">🏆</div>
              <h3>Leaderboards</h3>
              <p>Compete with peers and climb the rankings</p>
              <span className="feature-status coming-soon">Coming Soon</span>
            </div>
            <div className="feature-card coming-soon">
              <div className="feature-icon">📚</div>
              <h3>Learning Resources</h3>
              <p>Access comprehensive educational materials and references</p>
              <span className="feature-status coming-soon">Coming Soon</span>
            </div>
          </div>
        </section>
      </main>

      {/* Coming Soon Modal */}
      {showComingSoonModal && (
        <div className="modal-overlay" onClick={closeComingSoonModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>🚧 {comingSoonFeature} - Coming Soon!</h3>
              <button className="modal-close" onClick={closeComingSoonModal}>×</button>
            </div>
            <div className="modal-body">
              <p>We're working hard to bring you thousands of additional cases and features.</p>
              <p>Start with our available ovarian cancer case while we develop more content!</p>
            </div>
            <div className="modal-footer">
              <button className="modal-btn primary" onClick={() => {
                closeComingSoonModal();
                handleCaseClick('ovarian-cancer');
              }}>
                Try Available Case
              </button>
              <button className="modal-btn secondary" onClick={closeComingSoonModal}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      <footer className="app-footer">
        <div className="footer-content">
          <div className="footer-section">
            <h4>CasewiseMD</h4>
            <p>Advancing radiology education through AI-powered interactive learning. Currently in active development.</p>
          </div>
          <div className="footer-section">
            <h4>Development Status</h4>
            <p>✅ Core platform available</p>
            <p>🔄 1000+ cases in development</p>
            <p>🔄 Advanced features coming soon</p>
          </div>
          <div className="footer-section">
            <h4>Get Updates</h4>
            <p>Follow our progress as we add more cases and features</p>
            <p>Start practicing with our available case today!</p>
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
