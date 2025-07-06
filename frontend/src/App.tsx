import React, { useState, useEffect } from 'react';
import './App.css';
// Import components
import DiagnosticWorkflow from './DiagnosticWorkflow';
import CaseSelection from './components/CaseSelection';

// Types for case categories
interface CaseCategory {
  id: string;
  title: string;
  description: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  modality: string;
  count: number;
  imageUrl?: string;
}

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
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [selectedCaseId, setSelectedCaseId] = useState<string | null>(null);
  const [caseCategories, setCaseCategories] = useState<CaseCategory[]>([]);
  const [categoriesLoading, setCategoriesLoading] = useState(false);

  const API_URL = `${import.meta.env.VITE_API_URL || 'https://api.casewisemd.org'}/api/v1`;

  // Handle route changes
  useEffect(() => {
    const path = window.location.pathname;
    const params = new URLSearchParams(window.location.search);
    
    if (path === '/diagnostic') {
      const caseId = params.get('case_id');
      if (caseId) {
        setSelectedCaseId(caseId);
        setCurrentRoute('diagnostic');
      } else {
        // No case ID, redirect to home
        setCurrentRoute('home');
        window.history.pushState({}, '', '/');
      }
    } else if (path === '/case-selection') {
      const category = params.get('category');
      if (category) {
        setSelectedCategory(category);
        setCurrentRoute('case-selection');
      } else {
        // No category, redirect to home
        setCurrentRoute('home');
        window.history.pushState({}, '', '/');
      }
    } else {
      setCurrentRoute('home');
    }
  }, []);

  // Load case categories from API
  useEffect(() => {
    loadCaseCategories();
  }, []);

  const loadCaseCategories = async () => {
    setCategoriesLoading(true);
    
    try {
      const response = await fetch(`${API_URL}/categories`);
      
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          // Transform API data to match our interface
          const categories = data.categories.map((cat: any) => ({
            id: cat.id,
            title: cat.title,
            description: cat.description,
            difficulty: cat.difficulty as 'beginner' | 'intermediate' | 'advanced',
            modality: cat.modality,
            count: cat.count,
            imageUrl: `/api/placeholder/${cat.id}`
          }));
          setCaseCategories(categories);
        }
      } else {
        // Fallback to static categories if API fails
        console.warn('Failed to load categories from API, using fallback');
        setCaseCategories(getDefaultCategories());
      }
    } catch (error) {
      console.error('Error loading categories:', error);
      // Fallback to static categories
      setCaseCategories(getDefaultCategories());
    } finally {
      setCategoriesLoading(false);
    }
  };

  const getDefaultCategories = (): CaseCategory[] => [
    {
      id: 'ovarian-cancer',
      title: 'Ovarian Cancer',
      description: 'Complex cases involving ovarian malignancies and differential diagnoses',
      difficulty: 'intermediate',
      modality: 'CT',
      count: 1,
      imageUrl: '/api/placeholder/ovarian'
    },
    {
      id: 'chest-xray',
      title: 'Chest X-Ray',
      description: 'Basic to advanced chest radiography interpretation',
      difficulty: 'beginner',
      modality: 'X-Ray',
      count: 0,
      imageUrl: '/api/placeholder/chest'
    },
    {
      id: 'brain-mri',
      title: 'Brain MRI',
      description: 'Neurological imaging cases including tumors and vascular conditions',
      difficulty: 'advanced',
      modality: 'MRI',
      count: 0,
      imageUrl: '/api/placeholder/brain'
    },
    {
      id: 'abdomen-ct',
      title: 'Abdomen CT',
      description: 'Abdominal pathology and trauma cases',
      difficulty: 'intermediate',
      modality: 'CT',
      count: 0,
      imageUrl: '/api/placeholder/abdomen'
    },
    {
      id: 'obstetric-ultrasound',
      title: 'Obstetric Ultrasound',
      description: 'Prenatal imaging and fetal development assessment',
      difficulty: 'beginner',
      modality: 'Ultrasound',
      count: 0,
      imageUrl: '/api/placeholder/obstetric'
    },
    {
      id: 'cardiac-ct',
      title: 'Cardiac CT',
      description: 'Cardiovascular imaging and coronary artery assessment',
      difficulty: 'advanced',
      modality: 'CT',
      count: 0,
      imageUrl: '/api/placeholder/cardiac'
    }
  ];

  const handleCaseClick = (categoryId: string) => {
    // Navigate to case selection for the category
    setSelectedCategory(categoryId);
    window.history.pushState({}, '', `/case-selection?category=${categoryId}`);
    setCurrentRoute('case-selection');
  };

  const handleCaseSelect = (caseId: string) => {
    // Navigate to diagnostic workflow with selected case
    setSelectedCaseId(caseId);
    window.history.pushState({}, '', `/diagnostic?case_id=${caseId}`);
    setCurrentRoute('diagnostic');
  };

  const handleNavigationClick = (pageId: string) => {
    if (pageId === 'home') {
      handleBackToHome();
    } else {
      // Show coming soon for other pages
      alert('Coming Soon! This feature is under development.');
    }
  };

  const handleBackToHome = () => {
    window.history.pushState({}, '', '/');
    setCurrentRoute('home');
    setCurrentPage('home');
    setSelectedCategory(null);
    setSelectedCaseId(null);
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

  // Render case selection if on that route
  if (currentRoute === 'case-selection' && selectedCategory) {
    return (
      <CaseSelection
        category={selectedCategory}
        onCaseSelect={handleCaseSelect}
        onBackToHome={handleBackToHome}
      />
    );
  }

  // Render diagnostic workflow if on that route
  if (currentRoute === 'diagnostic' && selectedCaseId) {
    return (
      <DiagnosticWorkflow
        caseId={selectedCaseId}
        onBackToHome={handleBackToHome}
      />
    );
  }

  // Render home page
  return (
    <div className="App">
      {/* Header */}
      <header className="app-header">
        <div className="header-content">
          <h1>CasewiseMD</h1>
          <p className="app-subtitle">AI-Powered Radiology Education Platform</p>
        </div>
        
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

      {/* Main Content */}
      <main className="app-main">
        {/* Hero Section */}
        <section className="hero">
          <div className="hero-content">
            <h2>Master Radiology with AI-Powered Learning</h2>
            <p>Practice with real cases, get instant feedback, and track your progress</p>
            
            <div className="hero-stats">
              <div className="stat">
                <span className="stat-number">{caseCategories.reduce((sum, cat) => sum + cat.count, 0)}</span>
                <span className="stat-label">Practice Cases</span>
              </div>
              <div className="stat">
                <span className="stat-number">AI</span>
                <span className="stat-label">Powered Feedback</span>
              </div>
              <div className="stat">
                <span className="stat-number">∞</span>
                <span className="stat-label">Learning Potential</span>
              </div>
            </div>
          </div>
        </section>

        {/* Quick Actions */}
        <section className="quick-actions">
          <h2>Get Started</h2>
          <div className="actions-grid">
            <button 
              className="action-btn primary featured" 
              onClick={() => handleCaseClick('ovarian-cancer')}
              disabled={categoriesLoading}
            >
              <span className="action-icon">🚀</span>
              <span className="action-title">Start Practice Case</span>
              <span className="action-subtitle">
                {categoriesLoading 
                  ? 'Loading cases...' 
                  : `Ovarian Cancer - ${caseCategories.find(c => c.id === 'ovarian-cancer')?.count || 0} cases available`
                }
              </span>
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
          
          {categoriesLoading ? (
            <div className="loading-container">
              <div className="loading-spinner"></div>
              <p>Loading case categories...</p>
            </div>
          ) : (
            <div className="categories-grid">
              {caseCategories.map((category) => (
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
                    <span className="case-count">
                      {category.count} {category.count === 1 ? 'case' : 'cases'} available
                    </span>
                    <button className="start-case-btn">
                      {category.count > 0 ? 'Browse Cases' : 'Coming Soon'}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* Features Section */}
        <section className="features">
          <h2>Why Choose CasewiseMD?</h2>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">🧠</div>
              <h3>AI-Powered Assessment</h3>
              <p>Get intelligent feedback on your diagnostic reasoning and learn from your mistakes</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🏥</div>
              <h3>Real Clinical Cases</h3>
              <p>Practice with authentic medical cases from leading institutions and expert radiologists</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">📊</div>
              <h3>Progress Tracking</h3>
              <p>Monitor your learning journey with detailed analytics and performance insights</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">👥</div>
              <h3>Collaborative Learning</h3>
              <p>Learn with peers, compare approaches, and benefit from community knowledge</p>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="app-footer">
        <div className="footer-content">
          <div className="footer-section">
            <h4>CasewiseMD</h4>
            <p>Revolutionizing medical education through AI-powered case-based learning</p>
          </div>
          <div className="footer-section">
            <h4>Platform</h4>
            <ul>
              <li><a href="#cases">Case Library</a></li>
              <li><a href="#progress">Progress Tracking</a></li>
              <li><a href="#leaderboard">Leaderboard</a></li>
            </ul>
          </div>
          <div className="footer-section">
            <h4>Support</h4>
            <ul>
              <li><a href="#help">Help Center</a></li>
              <li><a href="#contact">Contact Us</a></li>
              <li><a href="#feedback">Feedback</a></li>
            </ul>
          </div>
          <div className="footer-section">
            <h4>Legal</h4>
            <ul>
              <li><a href="#privacy">Privacy Policy</a></li>
              <li><a href="#terms">Terms of Service</a></li>
              <li><a href="#cookies">Cookie Policy</a></li>
            </ul>
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
