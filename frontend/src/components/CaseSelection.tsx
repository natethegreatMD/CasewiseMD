import React, { useState, useEffect } from 'react';
import './CaseSelection.css';

interface Case {
  case_id: string;
  title: string;
  description: string;
  difficulty: string;
  difficulty_score: number;
  patient_id: string;
  modality: string;
  anatomy: string;
  learning_objectives: string[];
  annotation_count: number;
  reviewer_count: number;
  case_complexity: string;
  created_date: string;
  preview_info: {
    specialty: string;
    source: string;
    keywords: string[];
  };
}

interface CaseSelectionProps {
  category: string;
  onCaseSelect: (caseId: string) => void;
  onBackToHome: () => void;
}

const CaseSelection: React.FC<CaseSelectionProps> = ({ category, onCaseSelect, onBackToHome }) => {
  const [cases, setCases] = useState<Case[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCase, setSelectedCase] = useState<string | null>(null);

  // Category display names
  const categoryDisplayNames: { [key: string]: string } = {
    'ovarian-cancer': 'Ovarian Cancer',
    'chest-xray': 'Chest X-Ray',
    'brain-mri': 'Brain MRI',
    'abdomen-ct': 'Abdomen CT',
    'obstetric-ultrasound': 'Obstetric Ultrasound',
    'cardiac-ct': 'Cardiac CT'
  };

  const API_URL = `${import.meta.env.VITE_API_URL || 'https://api.casewisemd.org'}/api/v1`;

  useEffect(() => {
    loadCases();
  }, [category]);

  const loadCases = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_URL}/cases/by-category?category=${category}`);
      
      if (!response.ok) {
        throw new Error(`Failed to load cases: ${response.status}`);
      }
      
      const data = await response.json();
      
      if (data.success) {
        setCases(data.cases || []);
      } else {
        setError(data.message || 'Failed to load cases');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load cases');
    } finally {
      setLoading(false);
    }
  };

  const handleCaseSelect = (caseId: string) => {
    setSelectedCase(caseId);
    // Add a small delay to show selection feedback
    setTimeout(() => {
      onCaseSelect(caseId);
    }, 200);
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty.toLowerCase()) {
      case 'beginner': return '#4CAF50';
      case 'intermediate': return '#FF9800';
      case 'advanced': return '#F44336';
      default: return '#757575';
    }
  };

  const getComplexityColor = (complexity: string) => {
    switch (complexity.toLowerCase()) {
      case 'low': return '#4CAF50';
      case 'moderate': return '#FF9800';
      case 'high': return '#F44336';
      default: return '#757575';
    }
  };

  const formatDate = (dateString: string) => {
    if (!dateString) return 'Unknown';
    try {
      return new Date(dateString).toLocaleDateString();
    } catch {
      return 'Unknown';
    }
  };

  if (loading) {
    return (
      <div className="case-selection-container">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <h2>Loading {categoryDisplayNames[category] || category} cases...</h2>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="case-selection-container">
        <div className="error-container">
          <h2>Error Loading Cases</h2>
          <p>{error}</p>
          <div className="error-actions">
            <button onClick={loadCases} className="retry-btn">
              Try Again
            </button>
            <button onClick={onBackToHome} className="back-btn">
              Back to Home
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="case-selection-container">
      <header className="case-selection-header">
        <button onClick={onBackToHome} className="back-button">
          ← Back to Home
        </button>
        <div className="header-content">
          <h1>{categoryDisplayNames[category] || category}</h1>
          <p>Select a case to begin your diagnostic practice</p>
        </div>
      </header>

      <main className="case-selection-main">
        {cases.length === 0 ? (
          <div className="no-cases-container">
            <div className="no-cases-message">
              <h2>No Cases Available</h2>
              <p>There are currently no cases available in the {categoryDisplayNames[category] || category} category.</p>
              <p>Cases are being added regularly. Please check back soon!</p>
              <button onClick={onBackToHome} className="back-btn">
                Back to Home
              </button>
            </div>
          </div>
        ) : (
          <>
            <div className="cases-summary">
              <h2>{cases.length} {cases.length === 1 ? 'Case' : 'Cases'} Available</h2>
              <p>Choose a case based on your experience level and learning goals</p>
            </div>

            <div className="cases-grid">
              {cases.map((case_item) => (
                <div
                  key={case_item.case_id}
                  className={`case-card ${selectedCase === case_item.case_id ? 'selected' : ''}`}
                  onClick={() => handleCaseSelect(case_item.case_id)}
                >
                  <div className="case-header">
                    <h3>{case_item.title}</h3>
                    <div className="case-badges">
                      <span 
                        className="badge difficulty-badge"
                        style={{ backgroundColor: getDifficultyColor(case_item.difficulty) }}
                      >
                        {case_item.difficulty}
                      </span>
                      <span 
                        className="badge complexity-badge"
                        style={{ backgroundColor: getComplexityColor(case_item.case_complexity) }}
                      >
                        {case_item.case_complexity} complexity
                      </span>
                    </div>
                  </div>

                  <div className="case-body">
                    <p className="case-description">{case_item.description}</p>
                    
                    <div className="case-details">
                      <div className="detail-item">
                        <span className="label">Patient ID:</span>
                        <span className="value">{case_item.patient_id}</span>
                      </div>
                      <div className="detail-item">
                        <span className="label">Modality:</span>
                        <span className="value">{case_item.modality}</span>
                      </div>
                      <div className="detail-item">
                        <span className="label">Anatomy:</span>
                        <span className="value">{case_item.anatomy}</span>
                      </div>
                      <div className="detail-item">
                        <span className="label">Expert Reviews:</span>
                        <span className="value">{case_item.reviewer_count} reviewers</span>
                      </div>
                    </div>

                    {case_item.learning_objectives && case_item.learning_objectives.length > 0 && (
                      <div className="learning-objectives">
                        <h4>Learning Objectives:</h4>
                        <ul>
                          {case_item.learning_objectives.slice(0, 3).map((objective, index) => (
                            <li key={index}>{objective}</li>
                          ))}
                          {case_item.learning_objectives.length > 3 && (
                            <li className="more-objectives">
                              ...and {case_item.learning_objectives.length - 3} more
                            </li>
                          )}
                        </ul>
                      </div>
                    )}
                  </div>

                  <div className="case-footer">
                    <div className="case-meta">
                      <span className="case-source">Source: {case_item.preview_info.source}</span>
                      <span className="case-date">Added: {formatDate(case_item.created_date)}</span>
                    </div>
                    <button className="start-case-btn">
                      {selectedCase === case_item.case_id ? 'Loading...' : 'Start Case'}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </>
        )}
      </main>
    </div>
  );
};

export default CaseSelection; 