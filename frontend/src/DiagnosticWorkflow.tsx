import React, { useState, useEffect, Suspense, lazy } from 'react';

// Lazy load the OHIF iframe viewer
const OhifIframeViewer = lazy(() => import('./components/OhifIframeViewer').catch(() => {
  // Return a fallback component if OHIF viewer fails to load
  return Promise.resolve({
    default: () => (
      <div style={{ 
        padding: '2rem', 
        textAlign: 'center', 
        background: 'rgba(26, 32, 44, 0.8)', 
        border: '1px solid #2d3748', 
        borderRadius: '8px',
        color: '#a0aec0'
      }}>
        <h3>Medical Image Viewer</h3>
        <p>Medical image viewer is currently unavailable.</p>
        <p>You can still complete the diagnostic workflow using the case information and questions.</p>
      </div>
    )
  });
}));

// Types for diagnostic workflow
interface DiagnosticQuestion {
  step: number;
  question: string;
  type: string;
  hint: string;
  expected_keywords: string[];
  context: string;
}

interface DiagnosticSession {
  session_id: string;
  case_id: string;
  current_step: number;
  total_steps: number;
  completed: boolean;
  answers: Record<string, string>;
  current_question: DiagnosticQuestion;
  progress: {
    completed_steps: number;
    current_step: number;
    total_steps: number;
  };
}

interface DiagnosticResponse {
  session_id: string;
  completed: boolean;
  answers: Record<string, string>;
  current_question?: DiagnosticQuestion;
  progress: {
    completed_steps: number;
    current_step: number;
    total_steps: number;
  };
  feedback?: {
    message: string;
    keywords_found: string[];
    next_focus: string;
  };
  final_assessment?: {
    message: string;
    grading_result: any;
  };
}

interface DiagnosticWorkflowProps {
  onBackToHome: () => void;
}

const CASE_METADATA = {
  id: 'TCGA-09-0364',
  title: 'Ovarian Cancer Case',
  description: 'A 55-year-old woman with abdominal pain and a pelvic mass.',
  modality: 'CT',
  body_region: 'Pelvis',
  difficulty_level: 'Intermediate',
};

function DiagnosticWorkflow({ onBackToHome }: DiagnosticWorkflowProps) {
  const [session, setSession] = useState<DiagnosticSession | null>(null);
  const [currentAnswer, setCurrentAnswer] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [gradingResult, setGradingResult] = useState<any>(null);
  const [showHint, setShowHint] = useState(false);
  const [showDicomViewer, setShowDicomViewer] = useState(true);

  // API Base URL from environment variables
  const API_URL = `${import.meta.env.VITE_API_URL}/api/v1`;

  // Start diagnostic session
  const startDiagnosticSession = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_URL}/diagnostic-session?case_id=case001`);
      if (!res.ok) throw new Error('Failed to start diagnostic session');
      const data = await res.json();
      setSession(data);
    } catch (err: any) {
      setError(err.message || 'Failed to start session');
    } finally {
      setLoading(false);
    }
  };

  // Submit answer and get next question
  const submitAnswer = async () => {
    if (!session || !currentAnswer.trim()) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const res = await fetch(`${API_URL}/diagnostic-answer`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: session.session_id,
          case_id: 'case001',
          current_step: session.current_step,
          answer: currentAnswer,
          answers: session.answers
        }),
      });
      
      if (!res.ok) throw new Error('Failed to submit answer');
      const data: DiagnosticResponse = await res.json();
      
      if (data.completed) {
        // Session completed - now call grading endpoint
        try {
          const gradingRes = await fetch(`${API_URL}/grade`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              session_id: session.session_id,
              case_id: 'case001',
              answers: data.answers || session.answers
            }),
          });
          
          if (!gradingRes.ok) throw new Error('Failed to grade submission');
          const gradingData = await gradingRes.json();
          
          setSession(null);
          setGradingResult(gradingData);
        } catch (gradingErr: any) {
          console.error('Grading error:', gradingErr);
          setError(`Completed session but failed to get grading: ${gradingErr.message}`);
        }
      } else {
        setSession({
          ...session,
          current_step: data.progress.current_step,
          answers: data.answers,
          current_question: data.current_question!,
          progress: data.progress
        });
        setCurrentAnswer('');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to submit answer');
    } finally {
      setLoading(false);
    }
  };

  // Start session on component mount
  useEffect(() => {
    startDiagnosticSession();
  }, []);

  if (loading && !session) {
    return (
      <div className="App">
        <div className="loading-container">
          <h2>Starting Diagnostic Session...</h2>
          <div className="loading-spinner"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="App">
        <div className="error-container">
          <h2>Error</h2>
          <p>{error}</p>
          <button onClick={startDiagnosticSession} className="retry-btn">
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (gradingResult) {
    return (
      <div className="App">
        <header className="app-header">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', maxWidth: '1200px', margin: '0 auto', width: '100%' }}>
            <button 
              onClick={onBackToHome}
              style={{
                background: 'rgba(45, 55, 72, 0.6)',
                border: '1px solid #4a5568',
                color: '#e2e8f0',
                padding: '0.5rem 1rem',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '0.9rem',
                transition: 'all 0.3s ease'
              }}
            >
              ← Back to Home
            </button>
            <div style={{ textAlign: 'center', flex: 1 }}>
              <h1>CasewiseMD</h1>
              <p className="app-subtitle">AI-Powered Radiology Education Platform</p>
            </div>
            <div style={{ width: '100px' }}></div> {/* Spacer for centering */}
          </div>
        </header>

        <main className="app-main">
          {/* Case Metadata Section */}
          <section className="case-metadata">
            <h2>Case Information</h2>
            <div className="metadata-grid">
              <div className="metadata-item">
                <label>Case ID:</label>
                <span>{CASE_METADATA.id}</span>
              </div>
              <div className="metadata-item">
                <label>Title:</label>
                <span>{CASE_METADATA.title}</span>
              </div>
              <div className="metadata-item">
                <label>Description:</label>
                <span>{CASE_METADATA.description}</span>
              </div>
              <div className="metadata-item">
                <label>Modality:</label>
                <span className="badge">{CASE_METADATA.modality}</span>
              </div>
              <div className="metadata-item">
                <label>Body Region:</label>
                <span className="badge">{CASE_METADATA.body_region}</span>
              </div>
              <div className="metadata-item">
                <label>Difficulty:</label>
                <span className={`badge difficulty-${CASE_METADATA.difficulty_level.toLowerCase()}`}>
                  {CASE_METADATA.difficulty_level}
                </span>
              </div>
            </div>
          </section>

          {/* Final Results */}
          <section className="grading-results">
            <h2>Diagnostic Workflow Complete!</h2>
            
            {/* Score Summary */}
            <div className="score-summary">
              <div className="score-card">
                <div className="score-number">
                  {gradingResult.total_score}/{gradingResult.max_score}
                </div>
                <div className="score-percentage">
                  {gradingResult.percentage}%
                </div>
                <div className={`score-status ${gradingResult.passed ? 'passed' : 'failed'}`}>
                  {gradingResult.passed ? 'PASSED' : 'FAILED'}
                </div>
              </div>
              <div className="confidence-indicator">
                <label>Confidence:</label>
                <div className="confidence-bar">
                  <div 
                    className="confidence-fill" 
                    style={{ width: `${gradingResult.confidence * 100}%` }}
                  ></div>
                </div>
                <span>{(gradingResult.confidence * 100).toFixed(1)}%</span>
              </div>
            </div>

            {/* Overall Feedback */}
            <div className="feedback-section">
              <h3>Overall Feedback</h3>
              <p className="feedback-text">{gradingResult.overall_feedback}</p>
            </div>

            {/* Strengths and Areas for Improvement */}
            <div className="feedback-grid">
              <div className="strengths">
                <h4>Strengths</h4>
                <ul>
                  {gradingResult.strengths.map((strength: string, i: number) => (
                    <li key={i}>{strength}</li>
                  ))}
                </ul>
              </div>
              <div className="improvements">
                <h4>Areas for Improvement</h4>
                <ul>
                  {gradingResult.areas_for_improvement.map((area: string, i: number) => (
                    <li key={i}>{area}</li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Category Results */}
            <div className="category-results">
              <h3>Detailed Category Results</h3>
              <div className="categories-grid">
                {gradingResult.category_results.map((cat: any, i: number) => (
                  <div key={i} className="category-card">
                    <div className="category-header">
                      <h4>{cat.category_name || cat.name}</h4>
                      <div className="category-score">
                        {cat.score} / {cat.max_score}
                      </div>
                    </div>
                    <div className="category-progress">
                      <div 
                        className="progress-bar"
                        style={{ width: `${(cat.score / cat.max_score) * 100}%` }}
                      ></div>
                    </div>
                    {cat.criteria_results && (
                      <div className="criteria-list">
                        {cat.criteria_results.map((crit: any, j: number) => (
                          <div key={j} className="criterion-item">
                            <div className="criterion-header">
                              <span className="criterion-name">
                                {crit.criterion_name || crit.criterion_id}
                              </span>
                              <span className="criterion-score">
                                {crit.score} / {crit.max_score}
                              </span>
                            </div>
                            <p className="criterion-feedback">{crit.feedback}</p>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Restart Button */}
            <div className="restart-section">
              <button onClick={startDiagnosticSession} className="restart-btn">
                Start New Diagnostic Session
              </button>
            </div>
          </section>
        </main>
      </div>
    );
  }

  if (!session) {
    return (
      <div className="App">
        <div className="loading-container">
          <h2>Loading...</h2>
        </div>
      </div>
    );
  }

  return (
    <div className="App">
      <header className="app-header">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', maxWidth: '1200px', margin: '0 auto', width: '100%' }}>
          <button 
            onClick={onBackToHome}
            style={{
              background: 'rgba(45, 55, 72, 0.6)',
              border: '1px solid #4a5568',
              color: '#e2e8f0',
              padding: '0.5rem 1rem',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '0.9rem',
              transition: 'all 0.3s ease'
            }}
          >
            ← Back to Home
          </button>
          <div style={{ textAlign: 'center', flex: 1 }}>
            <h1>CasewiseMD</h1>
            <p className="app-subtitle">AI-Powered Radiology Education Platform</p>
          </div>
          <div style={{ width: '100px' }}></div> {/* Spacer for centering */}
        </div>
      </header>

      <main className="app-main">
        {/* Case Metadata Section */}
        <section className="case-metadata">
          <h2>Case Information</h2>
          <div className="metadata-grid">
            <div className="metadata-item">
              <label>Case ID:</label>
              <span>{CASE_METADATA.id}</span>
            </div>
            <div className="metadata-item">
              <label>Title:</label>
              <span>{CASE_METADATA.title}</span>
            </div>
            <div className="metadata-item">
              <label>Description:</label>
              <span>{CASE_METADATA.description}</span>
            </div>
            <div className="metadata-item">
              <label>Modality:</label>
              <span className="badge">{CASE_METADATA.modality}</span>
            </div>
            <div className="metadata-item">
              <label>Body Region:</label>
              <span className="badge">{CASE_METADATA.body_region}</span>
            </div>
            <div className="metadata-item">
              <label>Difficulty:</label>
              <span className={`badge difficulty-${CASE_METADATA.difficulty_level.toLowerCase()}`}>
                {CASE_METADATA.difficulty_level}
              </span>
            </div>
          </div>
        </section>

        {/* Medical Image Viewer - Full Width */}
        <div className="viewer-section" style={{ marginBottom: '2rem' }}>
          <div className="viewer-header">
            <h3>Medical Image Viewer</h3>
            <button 
              onClick={() => setShowDicomViewer(!showDicomViewer)}
              className="toggle-viewer-btn"
            >
              {showDicomViewer ? 'Hide Image Viewer' : 'Show Image Viewer'}
            </button>
          </div>
          {showDicomViewer && (
            <Suspense fallback={
              <div style={{ 
                padding: '2rem', 
                textAlign: 'center', 
                background: 'rgba(26, 32, 44, 0.8)', 
                border: '1px solid #2d3748', 
                borderRadius: '8px',
                color: '#a0aec0'
              }}>
                <div className="loading-spinner"></div>
                <p>Loading medical image viewer...</p>
              </div>
            }>
              <OhifIframeViewer caseId="case001" />
            </Suspense>
          )}
        </div>

        {/* Diagnostic Questions */}
        <div className="diagnostic-section">
          {/* Current Question */}
          <section className="question-section">
            <div className="question-context">
              <h3>Context</h3>
              <p>{session.current_question.context}</p>
            </div>
            
            <div className="question-content">
              <h3>Question {session.current_question.step}</h3>
              <p className="question-text">{session.current_question.question}</p>
              
              <div className="question-hint">
                <button
                  type="button"
                  className="hint-toggle-btn"
                  onClick={() => setShowHint((v) => !v)}
                  aria-expanded={showHint}
                  style={{
                    background: 'none',
                    border: 'none',
                    color: '#ecc94b',
                    fontWeight: 600,
                    cursor: 'pointer',
                    fontSize: '1rem',
                    padding: 0,
                    marginBottom: showHint ? '0.5rem' : 0
                  }}
                >
                  {showHint ? 'Hide Hint' : 'Show Hint'}
                </button>
                {showHint && (
                  <div className="hint-text" style={{ marginTop: '0.5rem', color: '#ecc94b' }}>
                    {session.current_question.hint}
                  </div>
                )}
              </div>
            </div>
          </section>

          {/* Answer Form */}
          <section className="answer-section">
            <form onSubmit={(e) => { e.preventDefault(); submitAnswer(); }}>
              <div className="form-group">
                <label htmlFor="answer">Your Answer:</label>
                <textarea
                  id="answer"
                  value={currentAnswer}
                  onChange={e => setCurrentAnswer(e.target.value)}
                  rows={6}
                  placeholder="Enter your detailed answer here..."
                  required
                  disabled={loading}
                />
              </div>
              <button type="submit" className="submit-btn" disabled={loading || !currentAnswer.trim()}>
                {loading ? 'Submitting...' : 'Submit Answer & Continue'}
              </button>
            </form>
          </section>

          {/* Previous Answers */}
          {Object.keys(session.answers).length > 0 && (
            <section className="previous-answers">
              <h3>Your Previous Answers</h3>
              <div className="answers-list">
                {Object.entries(session.answers).map(([step, answer], idx) => (
                  <div className="previous-answer" key={idx}>
                    <strong>Question {idx + 1}:</strong> {answer}
                  </div>
                ))}
              </div>
            </section>
          )}
        </div>

        {/* Simple Question Counter at Bottom */}
        <div style={{ 
          textAlign: 'center', 
          padding: '1rem', 
          color: '#a0aec0', 
          fontSize: '0.9rem',
          borderTop: '1px solid #2d3748',
          marginTop: '2rem'
        }}>
          Question {session.current_step} of {session.total_steps}
        </div>
      </main>
    </div>
  );
}

import React, { useState, useEffect, Suspense, lazy } from 'react';

// Lazy load the OHIF iframe viewer
const OhifIframeViewer = lazy(() => import('./components/OhifIframeViewer').catch(() => {
  // Return a fallback component if OHIF viewer fails to load
  return Promise.resolve({
    default: () => (
      <div style={{ 
        padding: '2rem', 
        textAlign: 'center', 
        background: 'rgba(26, 32, 44, 0.8)', 
        border: '1px solid #2d3748', 
        borderRadius: '8px',
        color: '#a0aec0'
      }}>
        <h3>Medical Image Viewer</h3>
        <p>Medical image viewer is currently unavailable.</p>
        <p>You can still complete the diagnostic workflow using the case information and questions.</p>
      </div>
    )
  });
}));

// Types for diagnostic workflow
interface DiagnosticQuestion {
  step: number;
  question: string;
  type: string;
  hint: string;
  expected_keywords: string[];
  context: string;
}

interface DiagnosticSession {
  session_id: string;
  case_id: string;
  current_step: number;
  total_steps: number;
  completed: boolean;
  answers: Record<string, string>;
  current_question: DiagnosticQuestion;
  progress: {
    completed_steps: number;
    current_step: number;
    total_steps: number;
  };
}

interface DiagnosticResponse {
  session_id: string;
  completed: boolean;
  answers: Record<string, string>;
  current_question?: DiagnosticQuestion;
  progress: {
    completed_steps: number;
    current_step: number;
    total_steps: number;
  };
  feedback?: {
    message: string;
    keywords_found: string[];
    next_focus: string;
  };
  final_assessment?: {
    message: string;
    grading_result: any;
  };
}

interface DiagnosticWorkflowProps {
  onBackToHome: () => void;
}

const CASE_METADATA = {
  id: 'TCGA-09-0364',
  title: 'Ovarian Cancer Case',
  description: 'A 55-year-old woman with abdominal pain and a pelvic mass.',
  modality: 'CT',
  body_region: 'Pelvis',
  difficulty_level: 'Intermediate',
};

function DiagnosticWorkflow({ onBackToHome }: DiagnosticWorkflowProps) {
  const [session, setSession] = useState<DiagnosticSession | null>(null);
  const [currentAnswer, setCurrentAnswer] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [gradingResult, setGradingResult] = useState<any>(null);
  const [showHint, setShowHint] = useState(false);
  const [showDicomViewer, setShowDicomViewer] = useState(true);

  // API Base URL from environment variables
  const API_URL = `${import.meta.env.VITE_API_URL}/api/v1`;

  // Start diagnostic session
  const startDiagnosticSession = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_URL}/diagnostic-session?case_id=case001`);
      if (!res.ok) throw new Error('Failed to start diagnostic session');
      const data = await res.json();
      setSession(data);
    } catch (err: any) {
      setError(err.message || 'Failed to start session');
    } finally {
      setLoading(false);
    }
  };

  // Submit answer and get next question
  const submitAnswer = async () => {
    if (!session || !currentAnswer.trim()) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const res = await fetch(`${API_URL}/diagnostic-answer`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: session.session_id,
          case_id: 'case001',
          current_step: session.current_step,
          answer: currentAnswer,
          answers: session.answers
        }),
      });
      
      if (!res.ok) throw new Error('Failed to submit answer');
      const data: DiagnosticResponse = await res.json();
      
      if (data.completed) {
        // Session completed - now call grading endpoint
        try {
          const gradingRes = await fetch(`${API_URL}/grade`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              session_id: session.session_id,
              case_id: 'case001',
              answers: data.answers || session.answers
            }),
          });
          
          if (!gradingRes.ok) throw new Error('Failed to grade submission');
          const gradingData = await gradingRes.json();
          
          setSession(null);
          setGradingResult(gradingData);
        } catch (gradingErr: any) {
          console.error('Grading error:', gradingErr);
          setError(`Completed session but failed to get grading: ${gradingErr.message}`);
        }
      } else {
        setSession({
          ...session,
          current_step: data.progress.current_step,
          answers: data.answers,
          current_question: data.current_question!,
          progress: data.progress
        });
        setCurrentAnswer('');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to submit answer');
    } finally {
      setLoading(false);
    }
  };

  // Start session on component mount
  useEffect(() => {
    startDiagnosticSession();
  }, []);

  if (loading && !session) {
    return (
      <div className="App">
        <div className="loading-container">
          <h2>Starting Diagnostic Session...</h2>
          <div className="loading-spinner"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="App">
        <div className="error-container">
          <h2>Error</h2>
          <p>{error}</p>
          <button onClick={startDiagnosticSession} className="retry-btn">
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (gradingResult) {
    return (
      <div className="App">
        <header className="app-header">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', maxWidth: '1200px', margin: '0 auto', width: '100%' }}>
            <button 
              onClick={onBackToHome}
              style={{
                background: 'rgba(45, 55, 72, 0.6)',
                border: '1px solid #4a5568',
                color: '#e2e8f0',
                padding: '0.5rem 1rem',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '0.9rem',
                transition: 'all 0.3s ease'
              }}
            >
              ← Back to Home
            </button>
            <div style={{ textAlign: 'center', flex: 1 }}>
              <h1>CasewiseMD</h1>
              <p className="app-subtitle">AI-Powered Radiology Education Platform</p>
            </div>
            <div style={{ width: '100px' }}></div> {/* Spacer for centering */}
          </div>
        </header>

        <main className="app-main">
          {/* Case Metadata Section */}
          <section className="case-metadata">
            <h2>Case Information</h2>
            <div className="metadata-grid">
              <div className="metadata-item">
                <label>Case ID:</label>
                <span>{CASE_METADATA.id}</span>
              </div>
              <div className="metadata-item">
                <label>Title:</label>
                <span>{CASE_METADATA.title}</span>
              </div>
              <div className="metadata-item">
                <label>Description:</label>
                <span>{CASE_METADATA.description}</span>
              </div>
              <div className="metadata-item">
                <label>Modality:</label>
                <span className="badge">{CASE_METADATA.modality}</span>
              </div>
              <div className="metadata-item">
                <label>Body Region:</label>
                <span className="badge">{CASE_METADATA.body_region}</span>
              </div>
              <div className="metadata-item">
                <label>Difficulty:</label>
                <span className={`badge difficulty-${CASE_METADATA.difficulty_level.toLowerCase()}`}>
                  {CASE_METADATA.difficulty_level}
                </span>
              </div>
            </div>
          </section>

          {/* Final Results */}
          <section className="grading-results">
            <h2>Diagnostic Workflow Complete!</h2>
            
            {/* Score Summary */}
            <div className="score-summary">
              <div className="score-card">
                <div className="score-number">
                  {gradingResult.total_score}/{gradingResult.max_score}
                </div>
                <div className="score-percentage">
                  {gradingResult.percentage}%
                </div>
                <div className={`score-status ${gradingResult.passed ? 'passed' : 'failed'}`}>
                  {gradingResult.passed ? 'PASSED' : 'FAILED'}
                </div>
              </div>
              <div className="confidence-indicator">
                <label>Confidence:</label>
                <div className="confidence-bar">
                  <div 
                    className="confidence-fill" 
                    style={{ width: `${gradingResult.confidence * 100}%` }}
                  ></div>
                </div>
                <span>{(gradingResult.confidence * 100).toFixed(1)}%</span>
              </div>
            </div>

            {/* Overall Feedback */}
            <div className="feedback-section">
              <h3>Overall Feedback</h3>
              <p className="feedback-text">{gradingResult.overall_feedback}</p>
            </div>

            {/* Strengths and Areas for Improvement */}
            <div className="feedback-grid">
              <div className="strengths">
                <h4>Strengths</h4>
                <ul>
                  {gradingResult.strengths.map((strength: string, i: number) => (
                    <li key={i}>{strength}</li>
                  ))}
                </ul>
              </div>
              <div className="improvements">
                <h4>Areas for Improvement</h4>
                <ul>
                  {gradingResult.areas_for_improvement.map((area: string, i: number) => (
                    <li key={i}>{area}</li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Category Results */}
            <div className="category-results">
              <h3>Detailed Category Results</h3>
              <div className="categories-grid">
                {gradingResult.category_results.map((cat: any, i: number) => (
                  <div key={i} className="category-card">
                    <div className="category-header">
                      <h4>{cat.category_name || cat.name}</h4>
                      <div className="category-score">
                        {cat.score} / {cat.max_score}
                      </div>
                    </div>
                    <div className="category-progress">
                      <div 
                        className="progress-bar"
                        style={{ width: `${(cat.score / cat.max_score) * 100}%` }}
                      ></div>
                    </div>
                    {cat.criteria_results && (
                      <div className="criteria-list">
                        {cat.criteria_results.map((crit: any, j: number) => (
                          <div key={j} className="criterion-item">
                            <div className="criterion-header">
                              <span className="criterion-name">
                                {crit.criterion_name || crit.criterion_id}
                              </span>
                              <span className="criterion-score">
                                {crit.score} / {crit.max_score}
                              </span>
                            </div>
                            <p className="criterion-feedback">{crit.feedback}</p>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Restart Button */}
            <div className="restart-section">
              <button onClick={startDiagnosticSession} className="restart-btn">
                Start New Diagnostic Session
              </button>
            </div>
          </section>
        </main>
      </div>
    );
  }

  if (!session) {
    return (
      <div className="App">
        <div className="loading-container">
          <h2>Loading...</h2>
        </div>
      </div>
    );
  }

  return (
    <div className="App">
      <header className="app-header">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', maxWidth: '1200px', margin: '0 auto', width: '100%' }}>
          <button 
            onClick={onBackToHome}
            style={{
              background: 'rgba(45, 55, 72, 0.6)',
              border: '1px solid #4a5568',
              color: '#e2e8f0',
              padding: '0.5rem 1rem',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '0.9rem',
              transition: 'all 0.3s ease'
            }}
          >
            ← Back to Home
          </button>
          <div style={{ textAlign: 'center', flex: 1 }}>
            <h1>CasewiseMD</h1>
            <p className="app-subtitle">AI-Powered Radiology Education Platform</p>
          </div>
          <div style={{ width: '100px' }}></div> {/* Spacer for centering */}
        </div>
      </header>

      <main className="app-main">
        {/* Case Metadata Section */}
        <section className="case-metadata">
          <h2>Case Information</h2>
          <div className="metadata-grid">
            <div className="metadata-item">
              <label>Case ID:</label>
              <span>{CASE_METADATA.id}</span>
            </div>
            <div className="metadata-item">
              <label>Title:</label>
              <span>{CASE_METADATA.title}</span>
            </div>
            <div className="metadata-item">
              <label>Description:</label>
              <span>{CASE_METADATA.description}</span>
            </div>
            <div className="metadata-item">
              <label>Modality:</label>
              <span className="badge">{CASE_METADATA.modality}</span>
            </div>
            <div className="metadata-item">
              <label>Body Region:</label>
              <span className="badge">{CASE_METADATA.body_region}</span>
            </div>
            <div className="metadata-item">
              <label>Difficulty:</label>
              <span className={`badge difficulty-${CASE_METADATA.difficulty_level.toLowerCase()}`}>
                {CASE_METADATA.difficulty_level}
              </span>
            </div>
          </div>
        </section>

        {/* Medical Image Viewer - Full Width */}
        <div className="viewer-section" style={{ marginBottom: '2rem' }}>
          <div className="viewer-header">
            <h3>Medical Image Viewer</h3>
            <button 
              onClick={() => setShowDicomViewer(!showDicomViewer)}
              className="toggle-viewer-btn"
            >
              {showDicomViewer ? 'Hide Image Viewer' : 'Show Image Viewer'}
            </button>
          </div>
          {showDicomViewer && (
            <Suspense fallback={
              <div style={{ 
                padding: '2rem', 
                textAlign: 'center', 
                background: 'rgba(26, 32, 44, 0.8)', 
                border: '1px solid #2d3748', 
                borderRadius: '8px',
                color: '#a0aec0'
              }}>
                <div className="loading-spinner"></div>
                <p>Loading medical image viewer...</p>
              </div>
            }>
              <OhifIframeViewer caseId="case001" />
            </Suspense>
          )}
        </div>

        {/* Diagnostic Questions */}
        <div className="diagnostic-section">
          {/* Current Question */}
          <section className="question-section">
            <div className="question-context">
              <h3>Context</h3>
              <p>{session.current_question.context}</p>
            </div>
            
            <div className="question-content">
              <h3>Question {session.current_question.step}</h3>
              <p className="question-text">{session.current_question.question}</p>
              
              <div className="question-hint">
                <button
                  type="button"
                  className="hint-toggle-btn"
                  onClick={() => setShowHint((v) => !v)}
                  aria-expanded={showHint}
                  style={{
                    background: 'none',
                    border: 'none',
                    color: '#ecc94b',
                    fontWeight: 600,
                    cursor: 'pointer',
                    fontSize: '1rem',
                    padding: 0,
                    marginBottom: showHint ? '0.5rem' : 0
                  }}
                >
                  {showHint ? 'Hide Hint' : 'Show Hint'}
                </button>
                {showHint && (
                  <div className="hint-text" style={{ marginTop: '0.5rem', color: '#ecc94b' }}>
                    {session.current_question.hint}
                  </div>
                )}
              </div>
            </div>
          </section>

          {/* Answer Form */}
          <section className="answer-section">
            <form onSubmit={(e) => { e.preventDefault(); submitAnswer(); }}>
              <div className="form-group">
                <label htmlFor="answer">Your Answer:</label>
                <textarea
                  id="answer"
                  value={currentAnswer}
                  onChange={e => setCurrentAnswer(e.target.value)}
                  rows={6}
                  placeholder="Enter your detailed answer here..."
                  required
                  disabled={loading}
                />
              </div>
              <button type="submit" className="submit-btn" disabled={loading || !currentAnswer.trim()}>
                {loading ? 'Submitting...' : 'Submit Answer & Continue'}
              </button>
            </form>
          </section>

          {/* Previous Answers */}
          {Object.keys(session.answers).length > 0 && (
            <section className="previous-answers">
              <h3>Your Previous Answers</h3>
              <div className="answers-list">
                {Object.entries(session.answers).map(([step, answer], idx) => (
                  <div className="previous-answer" key={idx}>
                    <strong>Question {idx + 1}:</strong> {answer}
                  </div>
                ))}
              </div>
            </section>
          )}
        </div>

        {/* Simple Question Counter at Bottom */}
        <div style={{ 
          textAlign: 'center', 
          padding: '1rem', 
          color: '#a0aec0', 
          fontSize: '0.9rem',
          borderTop: '1px solid #2d3748',
          marginTop: '2rem'
        }}>
          Question {session.current_step} of {session.total_steps}
        </div>
      </main>
    </div>
  );
}

export default DiagnosticWorkflow; 