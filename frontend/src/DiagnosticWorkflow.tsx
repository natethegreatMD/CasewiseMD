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

// Add interface for follow-up questions
interface FollowUpQuestion {
  category: string;
  question: string;
  purpose: string;
  score: number;
}

// Add interface for case metadata from API
interface CaseMetadata {
  id: string;
  title: string;
  description?: string;
  modality: string;
  body_region: string;
  difficulty_level?: string;
  study_instance_uid?: string;
  series_count?: number;
  series_descriptions?: string[];
  study_date?: string;
  patient_age?: string;
  contrast?: string;
}

// Add interface for case viewer URL response
interface CaseViewerResponse {
  success: boolean;
  viewer_url: string;
  case_id: string;
  study_instance_uid?: string;
  error?: string;
}

function DiagnosticWorkflow({ onBackToHome }: DiagnosticWorkflowProps) {
  const [session, setSession] = useState<DiagnosticSession | null>(null);
  const [currentAnswer, setCurrentAnswer] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [gradingResult, setGradingResult] = useState<any>(null);
  const [showHint, setShowHint] = useState(false);
  const [showDicomViewer, setShowDicomViewer] = useState(true);
  
  // New state for follow-up questions
  const [followUpQuestions, setFollowUpQuestions] = useState<FollowUpQuestion[]>([]);
  const [currentFollowUpIndex, setCurrentFollowUpIndex] = useState(0);
  const [followUpAnswers, setFollowUpAnswers] = useState<Record<number, string>>({});
  const [showingFollowUps, setShowingFollowUps] = useState(false);
  const [currentFollowUpAnswer, setCurrentFollowUpAnswer] = useState('');

  // New state for case metadata and viewer URL
  const [caseMetadata, setCaseMetadata] = useState<CaseMetadata | null>(null);
  const [viewerUrl, setViewerUrl] = useState<string | null>(null);
  const [caseLoading, setCaseLoading] = useState(false);

  // API Base URL from environment variables
  const API_URL = `${import.meta.env.VITE_API_URL || 'https://api.casewisemd.org'}/api/v1`;

  // Load case metadata and viewer URL when component mounts
  useEffect(() => {
    loadCaseData();
  }, []);

  // Load case metadata and viewer URL from MCP API
  const loadCaseData = async () => {
    setCaseLoading(true);
    setError(null);
    
    try {
      // Get case metadata
      const metadataRes = await fetch(`${API_URL}/cases/case001/metadata`);
      if (!metadataRes.ok) throw new Error('Failed to load case metadata');
      const metadataData = await metadataRes.json();
      
      if (metadataData.success) {
        // Transform API metadata to component format
        const metadata: CaseMetadata = {
          id: metadataData.case_id,
          title: metadataData.metadata.title,
          description: 'A complex medical case for diagnostic evaluation.',
          modality: metadataData.metadata.modality,
          body_region: metadataData.metadata.body_region,
          difficulty_level: 'Advanced',
          study_instance_uid: metadataData.metadata.study_instance_uid,
          series_count: metadataData.metadata.series_count,
          series_descriptions: metadataData.metadata.series_descriptions,
          study_date: metadataData.metadata.study_date,
          patient_age: metadataData.metadata.patient_age,
          contrast: metadataData.metadata.contrast
        };
        setCaseMetadata(metadata);
      }

      // Get case viewer URL
      const viewerRes = await fetch(`${API_URL}/viewer-url`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          case_id: 'case001'
        }),
      });
      
      if (!viewerRes.ok) throw new Error('Failed to load viewer URL');
      const viewerData: CaseViewerResponse = await viewerRes.json();
      
      if (viewerData.success) {
        setViewerUrl(viewerData.viewer_url);
      } else {
        console.warn('Failed to get viewer URL:', viewerData.error);
        // Set fallback URL
        setViewerUrl('https://viewer.casewisemd.org/viewer');
      }
      
    } catch (err: any) {
      console.error('Error loading case data:', err);
      setError(`Failed to load case data: ${err.message}`);
      
      // Set fallback data
      setCaseMetadata({
        id: 'case001',
        title: 'Ovarian Cancer Case - TCGA-09-0364',
        description: 'A complex medical case for diagnostic evaluation.',
        modality: 'CT',
        body_region: 'Pelvis',
        difficulty_level: 'Advanced'
      });
      setViewerUrl('https://viewer.casewisemd.org/viewer');
    } finally {
      setCaseLoading(false);
    }
  };

  // Start session on component mount
  useEffect(() => {
    // Only start session after case data is loaded
    if (caseMetadata && !caseLoading) {
      startDiagnosticSession();
    }
  }, [caseMetadata, caseLoading]);

  // Show loading state while case data is loading
  if (caseLoading) {
    return (
      <div className="App">
        <div className="loading-container">
          <h2>Loading Case Data...</h2>
          <div className="loading-spinner"></div>
        </div>
      </div>
    );
  }

  // Start diagnostic session
  const startDiagnosticSession = async () => {
    setLoading(true);
    setError(null);
    setGradingResult(null);
    setFollowUpQuestions([]);
    setShowingFollowUps(false);
    setCurrentFollowUpIndex(0);
    setFollowUpAnswers({});
    setCurrentFollowUpAnswer('');
    
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
          
          // Check if there are follow-up questions
          if (gradingData.follow_up_questions && gradingData.follow_up_questions.length > 0) {
            setFollowUpQuestions(gradingData.follow_up_questions);
            setShowingFollowUps(true);
            setCurrentFollowUpIndex(0);
            setGradingResult(gradingData); // Store for later
          } else {
            // No follow-up questions, show results immediately
            setGradingResult(gradingData);
          }
          
          setSession(null);
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

  // Skip current question
  const skipQuestion = async () => {
    if (!session) return;
    
    setLoading(true);
    setError(null);
    
    try {
      // Submit empty answer for skipped question
      const res = await fetch(`${API_URL}/diagnostic-answer`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: session.session_id,
          case_id: 'case001',
          current_step: session.current_step,
          answer: '[SKIPPED]', // Mark as skipped
          answers: session.answers
        }),
      });
      
      if (!res.ok) throw new Error('Failed to skip question');
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
          
          // Check if there are follow-up questions
          if (gradingData.follow_up_questions && gradingData.follow_up_questions.length > 0) {
            setFollowUpQuestions(gradingData.follow_up_questions);
            setShowingFollowUps(true);
            setCurrentFollowUpIndex(0);
            setGradingResult(gradingData); // Store for later
          } else {
            // No follow-up questions, show results immediately
            setGradingResult(gradingData);
          }
          
          setSession(null);
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
      setError(err.message || 'Failed to skip question');
    } finally {
      setLoading(false);
    }
  };

  // Submit follow-up answer
  const submitFollowUpAnswer = () => {
    if (!currentFollowUpAnswer.trim()) return;
    
    setFollowUpAnswers(prev => ({
      ...prev,
      [currentFollowUpIndex]: currentFollowUpAnswer
    }));
    
    setCurrentFollowUpAnswer('');
    
    if (currentFollowUpIndex < followUpQuestions.length - 1) {
      setCurrentFollowUpIndex(prev => prev + 1);
    } else {
      // Completed all follow-up questions, evaluate them
      evaluateFollowUpAnswers();
    }
  };

  // Evaluate follow-up answers with AI
  const evaluateFollowUpAnswers = async () => {
    if (!gradingResult || Object.keys(followUpAnswers).length === 0) {
      setShowingFollowUps(false);
      return;
    }

    setLoading(true);
    
    try {
      // Include the current answer if it exists
      const allFollowUpAnswers = {
        ...followUpAnswers,
        [currentFollowUpIndex]: currentFollowUpAnswer.trim() || ''
      };

      const evaluationData = {
        case_id: 'case001',
        session_id: gradingResult.session_id || 'unknown',
        followup_answers: allFollowUpAnswers,
        original_followup_questions: followUpQuestions,
        original_grading: gradingResult
      };

      const response = await fetch(`${API_URL}/evaluate-followup`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(evaluationData),
      });

      if (!response.ok) throw new Error('Failed to evaluate follow-up answers');
      
      const evaluationResults = await response.json();
      
      // Update grading result with follow-up evaluation
      setGradingResult(prev => ({
        ...prev,
        followup_evaluation: evaluationResults,
        has_followup_feedback: true
      }));

      setShowingFollowUps(false);
      
    } catch (error) {
      console.error('Error evaluating follow-up answers:', error);
      // Still show results even if evaluation fails
      setShowingFollowUps(false);
    } finally {
      setLoading(false);
    }
  };

  // Skip follow-up questions
  const skipFollowUps = () => {
    setShowingFollowUps(false);
  };

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

  // Show follow-up questions if they exist
  if (showingFollowUps && followUpQuestions.length > 0) {
    const currentFollowUp = followUpQuestions[currentFollowUpIndex];
    
    return (
      <div className="App">
        <header className="app-header">
          <div className="header-content" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <button 
              onClick={onBackToHome}
              className="back-to-home-btn"
            >
              ← Back to Home
            </button>
            <div style={{ textAlign: 'center', flex: 1 }}>
              <h1>CasewiseMD</h1>
              <p className="app-subtitle">Follow-up Questions for Learning</p>
            </div>
            <div style={{ width: '100px' }}></div>
          </div>
        </header>

        <main className="app-main">
          <section className="follow-up-questions">
            <h2>Follow-up Questions</h2>
            <p className="follow-up-intro">
              Based on your responses, we've identified some areas where additional discussion could enhance your learning.
              These questions are designed to help you think more deeply about the case.
            </p>
            
            {/* Progress Information */}
            <div className="progress-info">
              <span className="progress-text">
                Question {currentFollowUpIndex + 1} of {followUpQuestions.length}
              </span>
              <div className="progress-bar">
                <div 
                  className="progress-fill" 
                  style={{ width: `${((currentFollowUpIndex + 1) / followUpQuestions.length) * 100}%` }}
                />
              </div>
              <span className="progress-text">
                {Math.round(((currentFollowUpIndex + 1) / followUpQuestions.length) * 100)}% Complete
              </span>
            </div>

            <div className="follow-up-question">
              <div className="follow-up-header">
                <span className="follow-up-category">{currentFollowUp.category}</span>
                <span className="follow-up-score">Score: {currentFollowUp.score}%</span>
              </div>
              
              <div className="follow-up-content">
                <p className="follow-up-question-text">{currentFollowUp.question}</p>
                <p className="follow-up-purpose">{currentFollowUp.purpose}</p>
              </div>
            </div>

            {/* Answer Input */}
            <div className="answer-input">
              <label htmlFor="followup-answer">Your Reflection:</label>
              <textarea
                id="followup-answer"
                value={currentFollowUpAnswer}
                onChange={e => setCurrentFollowUpAnswer(e.target.value)}
                placeholder="Take a moment to reflect on this question. Your response will help reinforce your learning..."
              />
            </div>

            {/* Action Buttons */}
            <div className="action-buttons">
              <button 
                onClick={submitFollowUpAnswer}
                className="action-btn primary"
                disabled={!currentFollowUpAnswer.trim()}
              >
                {currentFollowUpIndex < followUpQuestions.length - 1 ? 'Next Question' : 'Complete Follow-up'}
              </button>
              <button 
                onClick={skipFollowUps}
                className="action-btn secondary"
              >
                Skip Follow-up Questions
              </button>
            </div>

            {/* Previous follow-up answers */}
            {Object.keys(followUpAnswers).length > 0 && (
              <div className="previous-followups" style={{ marginTop: '2rem' }}>
                <h3>Your Previous Reflections</h3>
                <div className="followup-answers-list">
                  {Object.entries(followUpAnswers).map(([index, answer]) => (
                    <div key={index} className="previous-followup" style={{ 
                      padding: '1rem', 
                      background: 'rgba(45, 55, 72, 0.6)', 
                      border: '1px solid #4a5568',
                      borderRadius: '8px',
                      marginBottom: '1rem'
                    }}>
                      <strong style={{ color: '#f7fafc' }}>{followUpQuestions[parseInt(index)].category}:</strong> 
                      <p style={{ color: '#e2e8f0', marginTop: '0.5rem' }}>{answer}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </section>
        </main>
      </div>
    );
  }

  if (gradingResult) {
    return (
      <div className="App">
        <header className="app-header">
          <div className="header-content" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <button 
              onClick={onBackToHome}
              className="back-to-home-btn"
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
            <h2>📋 Clinical Case Overview</h2>
            <p className="case-subtitle">Advanced Diagnostic Challenge in Radiology Education</p>
            
            {/* Primary Case Information */}
            <div className="case-summary" style={{
              background: 'linear-gradient(135deg, rgba(66, 153, 225, 0.1), rgba(159, 122, 234, 0.1))',
              border: '1px solid rgba(66, 153, 225, 0.3)',
              borderRadius: '16px',
              padding: '2rem',
              marginBottom: '2rem',
              textAlign: 'center'
            }}>
              <h3 style={{
                color: '#f7fafc',
                fontSize: '1.5rem',
                fontWeight: '700',
                marginBottom: '1rem',
                background: 'linear-gradient(135deg, #4299e1, #9f7aea)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text'
              }}>
                🏥 Complex Pelvic Imaging Case - Suspected Ovarian Pathology
              </h3>
              <p style={{
                color: '#e2e8f0',
                fontSize: '1.1rem',
                lineHeight: '1.6',
                maxWidth: '800px',
                margin: '0 auto'
              }}>
                This case presents a challenging diagnostic scenario involving a female patient with pelvic symptoms. 
                The imaging study reveals complex findings that require careful analysis and systematic evaluation 
                to arrive at an accurate diagnosis.
              </p>
            </div>
            
            <div className="metadata-grid">
              <div className="metadata-item">
                <div className="metadata-item-header">
                  <span className="metadata-icon">🏥</span>
                  <label>Medical Record Number</label>
                </div>
                <div className="metadata-value">
                  Case #{caseMetadata?.id?.toUpperCase() || 'CASE001'}
                  <br />
                  <small style={{ color: '#a0aec0', fontSize: '0.9rem' }}>
                    Educational Case - TCGA Database
                  </small>
                </div>
              </div>
              
              <div className="metadata-item">
                <div className="metadata-item-header">
                  <span className="metadata-icon">📋</span>
                  <label>Chief Complaint & History</label>
                </div>
                <div className="metadata-value">
                  <strong>Chief Complaint:</strong> Pelvic pain and abdominal distension
                  <br />
                  <strong>History:</strong> 6-month history of progressive pelvic discomfort, 
                  early satiety, and increasing abdominal girth
                  <br />
                  <strong>Clinical Concern:</strong> Suspected ovarian mass
                </div>
              </div>
              
              <div className="metadata-item">
                <div className="metadata-item-header">
                  <span className="metadata-icon">🔬</span>
                  <label>Imaging Protocol</label>
                </div>
                <div className="metadata-value">
                  <strong>Study Type:</strong> CT Abdomen & Pelvis with IV Contrast
                  <br />
                  <strong>Technique:</strong> Multiphasic contrast-enhanced CT
                  <br />
                  <strong>Slice Thickness:</strong> 2.5mm axial reconstructions
                  <br />
                  <strong>Contrast:</strong> Iodinated contrast material IV
                </div>
                <span className={`badge modality-${caseMetadata?.modality?.toLowerCase() || 'ct'}`}>
                  {caseMetadata?.modality || 'CT'} Imaging
                </span>
              </div>
              
              <div className="metadata-item">
                <div className="metadata-item-header">
                  <span className="metadata-icon">🎯</span>
                  <label>Anatomical Coverage</label>
                </div>
                <div className="metadata-value">
                  <strong>Primary Focus:</strong> Pelvis and lower abdomen
                  <br />
                  <strong>Organs of Interest:</strong> Ovaries, uterus, bladder, bowel
                  <br />
                  <strong>Additional Coverage:</strong> Peritoneal cavity, lymph nodes
                </div>
                <span className="badge body-region">
                  {caseMetadata?.body_region || 'Pelvis'}
                </span>
              </div>
              
              <div className="metadata-item">
                <div className="metadata-item-header">
                  <span className="metadata-icon">👩‍⚕️</span>
                  <label>Patient Information</label>
                </div>
                <div className="metadata-value">
                  <strong>Demographics:</strong> Adult female patient
                  <br />
                  <strong>Age Range:</strong> {caseMetadata?.patient_age || 'Middle-aged adult'}
                  <br />
                  <strong>Clinical Status:</strong> Stable, outpatient study
                  <br />
                  <small style={{ color: '#a0aec0', fontSize: '0.9rem', fontStyle: 'italic' }}>
                    All patient identifiers anonymized for educational use
                  </small>
                </div>
              </div>
              
              <div className="metadata-item">
                <div className="metadata-item-header">
                  <span className="metadata-icon">⚡</span>
                  <label>Case Complexity</label>
                </div>
                <div className="metadata-value">
                  <strong>Difficulty Level:</strong> Advanced
                  <br />
                  <strong>Learning Objectives:</strong> 
                  <ul style={{ margin: '0.5rem 0 0 0', paddingLeft: '1rem' }}>
                    <li>Complex mass characterization</li>
                    <li>Differential diagnosis formation</li>
                    <li>Staging assessment</li>
                  </ul>
                </div>
                <span className={`badge difficulty-${caseMetadata?.difficulty_level?.toLowerCase() || 'advanced'}`}>
                  {caseMetadata?.difficulty_level || 'Advanced'} Level
                </span>
              </div>
              
              <div className="metadata-item">
                <div className="metadata-item-header">
                  <span className="metadata-icon">🔍</span>
                  <label>Key Clinical Questions</label>
                </div>
                <div className="metadata-value">
                  <strong>Primary Questions:</strong>
                  <ul style={{ margin: '0.5rem 0 0 0', paddingLeft: '1rem' }}>
                    <li>What is the nature of the pelvic mass?</li>
                    <li>Are there signs of malignancy?</li>
                    <li>What is the extent of disease?</li>
                    <li>Are there associated complications?</li>
                  </ul>
                </div>
              </div>
              
              <div className="metadata-item">
                <div className="metadata-item-header">
                  <span className="metadata-icon">📊</span>
                  <label>Study Details</label>
                </div>
                <div className="metadata-value">
                  <strong>Study Date:</strong> {caseMetadata?.study_date || 'Educational case'}
                  <br />
                  <strong>Series Count:</strong> {caseMetadata?.series_count || 'Multiple series'}
                  <br />
                  <strong>Study UID:</strong> 
                  <small style={{ color: '#a0aec0', fontSize: '0.8rem', wordBreak: 'break-all' }}>
                    {caseMetadata?.study_instance_uid || 'Educational case identifier'}
                  </small>
                </div>
              </div>
            </div>
          </section>

          {/* Final Results */}
          <section className="results-section">
            <h2>Diagnostic Workflow Complete!</h2>
            
            {/* Show follow-up completion message if they were answered */}
            {Object.keys(followUpAnswers).length > 0 && (
              <div className="followup-completion">
                <h3>✅ Follow-up Questions Completed</h3>
                <p>You completed {Object.keys(followUpAnswers).length} follow-up questions to enhance your learning.</p>
              </div>
            )}
            
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
            <div className="strengths-improvements">
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
              <div className="category-list">
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

            {/* Follow-up Evaluation Results */}
            {gradingResult.has_followup_feedback && gradingResult.followup_evaluation && (
              <div className="followup-evaluation-results">
                <h3>Follow-up Learning Assessment</h3>
                
                {/* Updated Assessment Summary */}
                {gradingResult.followup_evaluation.updated_assessment && (
                  <div className="updated-assessment-summary">
                    <div className="assessment-comparison">
                      <div className="score-before">
                        <h4>Original Score</h4>
                        <div className="score-display">
                          {gradingResult.followup_evaluation.updated_assessment.original_score}%
                        </div>
                      </div>
                      <div className="score-after">
                        <h4>After Follow-up</h4>
                        <div className="score-display">
                          {gradingResult.followup_evaluation.updated_assessment.updated_score}%
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Individual Follow-up Evaluations */}
                {gradingResult.followup_evaluation.followup_evaluations && gradingResult.followup_evaluation.followup_evaluations.length > 0 && (
                  <div className="individual-followup-evaluations">
                    <h4>Detailed Reflection Feedback</h4>
                    <div className="evaluations-list">
                      {gradingResult.followup_evaluation.followup_evaluations.map((evaluation: any, i: number) => (
                        <div key={i} className="followup-evaluation-card">
                          <div className="evaluation-header">
                            <span className="evaluation-category">{evaluation.category}</span>
                            <span className="evaluation-score">{evaluation.improvement_score}/100</span>
                          </div>
                          
                          <div className="evaluation-content">
                            {evaluation.knowledge_demonstration && (
                              <div className="evaluation-section">
                                <strong>Knowledge Demonstrated:</strong>
                                <p>{evaluation.knowledge_demonstration}</p>
                              </div>
                            )}
                            
                            {evaluation.clinical_reasoning && (
                              <div className="evaluation-section">
                                <strong>Clinical Reasoning:</strong>
                                <p>{evaluation.clinical_reasoning}</p>
                              </div>
                            )}
                            
                            {evaluation.learning_progress && (
                              <div className="evaluation-section">
                                <strong>Learning Progress:</strong>
                                <p>{evaluation.learning_progress}</p>
                              </div>
                            )}
                            
                            {evaluation.areas_for_continued_focus && (
                              <div className="evaluation-section">
                                <strong>Focus Areas:</strong>
                                <p>{evaluation.areas_for_continued_focus}</p>
                              </div>
                            )}
                            
                            {evaluation.feedback_summary && (
                              <div className="evaluation-summary">
                                <strong>Summary:</strong>
                                <p>{evaluation.feedback_summary}</p>
                              </div>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Learning Improvement Metrics */}
                {gradingResult.followup_evaluation.learning_improvement && (
                  <div className="learning-improvement">
                    <h4>Learning Metrics</h4>
                    <div className="metrics-grid">
                      <div className="metric-item">
                        <label>Engagement Level:</label>
                        <span className={`metric-value ${gradingResult.followup_evaluation.updated_assessment?.engagement_level || 'moderate'}`}>
                          {gradingResult.followup_evaluation.updated_assessment?.engagement_level || 'Moderate'}
                        </span>
                      </div>
                      <div className="metric-item">
                        <label>Completion Rate:</label>
                        <span className="metric-value">
                          {gradingResult.followup_evaluation.learning_improvement.followup_completion_rate}%
                        </span>
                      </div>
                      <div className="metric-item">
                        <label>Average Reflection Score:</label>
                        <span className="metric-value">
                          {gradingResult.followup_evaluation.learning_improvement.average_reflection_score}/100
                        </span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Follow-up Questions for Learning - now shows original questions that were asked */}
            {followUpQuestions.length > 0 && (
              <div className="follow-up-questions">
                <h3>Follow-up Questions You Addressed</h3>
                <p className="follow-up-intro">
                  Here are the follow-up questions you worked on to deepen your understanding:
                </p>
                <div className="follow-up-list">
                  {followUpQuestions.map((fq: any, i: number) => (
                    <div key={i} className="follow-up-question">
                      <div className="follow-up-header">
                        <span className="follow-up-category">{fq.category}</span>
                        <span className="follow-up-score">Score: {fq.score}%</span>
                      </div>
                      <div className="follow-up-content">
                        <p className="follow-up-question-text">{fq.question}</p>
                        <p className="follow-up-purpose">{fq.purpose}</p>
                        {followUpAnswers[i] && (
                          <div className="follow-up-answer">
                            <strong>Your reflection:</strong> {followUpAnswers[i]}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Restart Button */}
            <div className="restart-section">
              <button onClick={startDiagnosticSession} className="action-btn primary">
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
        <header className="app-header">
          <div className="header-content" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <button 
              onClick={onBackToHome}
              className="back-to-home-btn"
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
            <h2>📋 Clinical Case Overview</h2>
            <p className="case-subtitle">Advanced Diagnostic Challenge in Radiology Education</p>
            
            {/* Primary Case Information */}
            <div className="case-summary" style={{
              background: 'linear-gradient(135deg, rgba(66, 153, 225, 0.1), rgba(159, 122, 234, 0.1))',
              border: '1px solid rgba(66, 153, 225, 0.3)',
              borderRadius: '16px',
              padding: '2rem',
              marginBottom: '2rem',
              textAlign: 'center'
            }}>
              <h3 style={{
                color: '#f7fafc',
                fontSize: '1.5rem',
                fontWeight: '700',
                marginBottom: '1rem',
                background: 'linear-gradient(135deg, #4299e1, #9f7aea)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text'
              }}>
                🏥 Complex Pelvic Imaging Case - Suspected Ovarian Pathology
              </h3>
              <p style={{
                color: '#e2e8f0',
                fontSize: '1.1rem',
                lineHeight: '1.6',
                maxWidth: '800px',
                margin: '0 auto'
              }}>
                This case presents a challenging diagnostic scenario involving a female patient with pelvic symptoms. 
                The imaging study reveals complex findings that require careful analysis and systematic evaluation 
                to arrive at an accurate diagnosis.
              </p>
            </div>
            
            <div className="metadata-grid">
              <div className="metadata-item">
                <div className="metadata-item-header">
                  <span className="metadata-icon">🏥</span>
                  <label>Medical Record Number</label>
                </div>
                <div className="metadata-value">
                  Case #{caseMetadata?.id?.toUpperCase() || 'CASE001'}
                  <br />
                  <small style={{ color: '#a0aec0', fontSize: '0.9rem' }}>
                    Educational Case - TCGA Database
                  </small>
                </div>
              </div>
              
              <div className="metadata-item">
                <div className="metadata-item-header">
                  <span className="metadata-icon">📋</span>
                  <label>Chief Complaint & History</label>
                </div>
                <div className="metadata-value">
                  <strong>Chief Complaint:</strong> Pelvic pain and abdominal distension
                  <br />
                  <strong>History:</strong> 6-month history of progressive pelvic discomfort, 
                  early satiety, and increasing abdominal girth
                  <br />
                  <strong>Clinical Concern:</strong> Suspected ovarian mass
                </div>
              </div>
              
              <div className="metadata-item">
                <div className="metadata-item-header">
                  <span className="metadata-icon">🔬</span>
                  <label>Imaging Protocol</label>
                </div>
                <div className="metadata-value">
                  <strong>Study Type:</strong> CT Abdomen & Pelvis with IV Contrast
                  <br />
                  <strong>Technique:</strong> Multiphasic contrast-enhanced CT
                  <br />
                  <strong>Slice Thickness:</strong> 2.5mm axial reconstructions
                  <br />
                  <strong>Contrast:</strong> Iodinated contrast material IV
                </div>
                <span className={`badge modality-${caseMetadata?.modality?.toLowerCase() || 'ct'}`}>
                  {caseMetadata?.modality || 'CT'} Imaging
                </span>
              </div>
              
              <div className="metadata-item">
                <div className="metadata-item-header">
                  <span className="metadata-icon">🎯</span>
                  <label>Anatomical Coverage</label>
                </div>
                <div className="metadata-value">
                  <strong>Primary Focus:</strong> Pelvis and lower abdomen
                  <br />
                  <strong>Organs of Interest:</strong> Ovaries, uterus, bladder, bowel
                  <br />
                  <strong>Additional Coverage:</strong> Peritoneal cavity, lymph nodes
                </div>
                <span className="badge body-region">
                  {caseMetadata?.body_region || 'Pelvis'}
                </span>
              </div>
              
              <div className="metadata-item">
                <div className="metadata-item-header">
                  <span className="metadata-icon">👩‍⚕️</span>
                  <label>Patient Information</label>
                </div>
                <div className="metadata-value">
                  <strong>Demographics:</strong> Adult female patient
                  <br />
                  <strong>Age Range:</strong> {caseMetadata?.patient_age || 'Middle-aged adult'}
                  <br />
                  <strong>Clinical Status:</strong> Stable, outpatient study
                  <br />
                  <small style={{ color: '#a0aec0', fontSize: '0.9rem', fontStyle: 'italic' }}>
                    All patient identifiers anonymized for educational use
                  </small>
                </div>
              </div>
              
              <div className="metadata-item">
                <div className="metadata-item-header">
                  <span className="metadata-icon">⚡</span>
                  <label>Case Complexity</label>
                </div>
                <div className="metadata-value">
                  <strong>Difficulty Level:</strong> Advanced
                  <br />
                  <strong>Learning Objectives:</strong> 
                  <ul style={{ margin: '0.5rem 0 0 0', paddingLeft: '1rem' }}>
                    <li>Complex mass characterization</li>
                    <li>Differential diagnosis formation</li>
                    <li>Staging assessment</li>
                  </ul>
                </div>
                <span className={`badge difficulty-${caseMetadata?.difficulty_level?.toLowerCase() || 'advanced'}`}>
                  {caseMetadata?.difficulty_level || 'Advanced'} Level
                </span>
              </div>
              
              <div className="metadata-item">
                <div className="metadata-item-header">
                  <span className="metadata-icon">🔍</span>
                  <label>Key Clinical Questions</label>
                </div>
                <div className="metadata-value">
                  <strong>Primary Questions:</strong>
                  <ul style={{ margin: '0.5rem 0 0 0', paddingLeft: '1rem' }}>
                    <li>What is the nature of the pelvic mass?</li>
                    <li>Are there signs of malignancy?</li>
                    <li>What is the extent of disease?</li>
                    <li>Are there associated complications?</li>
                  </ul>
                </div>
              </div>
              
              <div className="metadata-item">
                <div className="metadata-item-header">
                  <span className="metadata-icon">📊</span>
                  <label>Study Details</label>
                </div>
                <div className="metadata-value">
                  <strong>Study Date:</strong> {caseMetadata?.study_date || 'Educational case'}
                  <br />
                  <strong>Series Count:</strong> {caseMetadata?.series_count || 'Multiple series'}
                  <br />
                  <strong>Study UID:</strong> 
                  <small style={{ color: '#a0aec0', fontSize: '0.8rem', wordBreak: 'break-all' }}>
                    {caseMetadata?.study_instance_uid || 'Educational case identifier'}
                  </small>
                </div>
              </div>
            </div>
          </section>

          {/* Medical Image Viewer - Full Width */}
          <section className="medical-image-viewer">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <h3>Medical Image Viewer</h3>
              <button 
                onClick={() => setShowDicomViewer(!showDicomViewer)}
                className="action-btn secondary"
              >
                {showDicomViewer ? 'Hide Image Viewer' : 'Show Image Viewer'}
              </button>
            </div>
            {showDicomViewer && (
              <div className="viewer-container">
                <Suspense fallback={
                  <div className="loading-container">
                    <div className="loading-spinner"></div>
                    <p>Loading medical image viewer...</p>
                  </div>
                }>
                  <OhifIframeViewer 
                    caseId="case001" 
                    viewerUrl={viewerUrl || undefined}
                  />
                </Suspense>
              </div>
            )}
          </section>

          {/* Start Session Button */}
          <div className="start-session-section">
            <button 
              onClick={startDiagnosticSession} 
              className="start-session-btn"
              disabled={loading}
            >
              {loading ? 'Loading...' : 'Start Diagnostic Session'}
            </button>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="App">
      <header className="app-header">
        <div className="header-content" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <button 
            onClick={onBackToHome}
            className="back-to-home-btn"
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
          <h2>📋 Clinical Case Overview</h2>
          <p className="case-subtitle">Advanced Diagnostic Challenge in Radiology Education</p>
          
          {/* Primary Case Information */}
          <div className="case-summary" style={{
            background: 'linear-gradient(135deg, rgba(66, 153, 225, 0.1), rgba(159, 122, 234, 0.1))',
            border: '1px solid rgba(66, 153, 225, 0.3)',
            borderRadius: '16px',
            padding: '2rem',
            marginBottom: '2rem',
            textAlign: 'center'
          }}>
            <h3 style={{
              color: '#f7fafc',
              fontSize: '1.5rem',
              fontWeight: '700',
              marginBottom: '1rem',
              background: 'linear-gradient(135deg, #4299e1, #9f7aea)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text'
            }}>
              🏥 Complex Pelvic Imaging Case - Suspected Ovarian Pathology
            </h3>
            <p style={{
              color: '#e2e8f0',
              fontSize: '1.1rem',
              lineHeight: '1.6',
              maxWidth: '800px',
              margin: '0 auto'
            }}>
              This case presents a challenging diagnostic scenario involving a female patient with pelvic symptoms. 
              The imaging study reveals complex findings that require careful analysis and systematic evaluation 
              to arrive at an accurate diagnosis.
            </p>
          </div>
          
          <div className="metadata-grid">
            <div className="metadata-item">
              <div className="metadata-item-header">
                <span className="metadata-icon">🏥</span>
                <label>Medical Record Number</label>
              </div>
              <div className="metadata-value">
                Case #{caseMetadata?.id?.toUpperCase() || 'CASE001'}
                <br />
                <small style={{ color: '#a0aec0', fontSize: '0.9rem' }}>
                  Educational Case - TCGA Database
                </small>
              </div>
            </div>
            
            <div className="metadata-item">
              <div className="metadata-item-header">
                <span className="metadata-icon">📋</span>
                <label>Chief Complaint & History</label>
              </div>
              <div className="metadata-value">
                <strong>Chief Complaint:</strong> Pelvic pain and abdominal distension
                <br />
                <strong>History:</strong> 6-month history of progressive pelvic discomfort, 
                early satiety, and increasing abdominal girth
                <br />
                <strong>Clinical Concern:</strong> Suspected ovarian mass
              </div>
            </div>
            
            <div className="metadata-item">
              <div className="metadata-item-header">
                <span className="metadata-icon">🔬</span>
                <label>Imaging Protocol</label>
              </div>
              <div className="metadata-value">
                <strong>Study Type:</strong> CT Abdomen & Pelvis with IV Contrast
                <br />
                <strong>Technique:</strong> Multiphasic contrast-enhanced CT
                <br />
                <strong>Slice Thickness:</strong> 2.5mm axial reconstructions
                <br />
                <strong>Contrast:</strong> Iodinated contrast material IV
              </div>
              <span className={`badge modality-${caseMetadata?.modality?.toLowerCase() || 'ct'}`}>
                {caseMetadata?.modality || 'CT'} Imaging
              </span>
            </div>
            
            <div className="metadata-item">
              <div className="metadata-item-header">
                <span className="metadata-icon">🎯</span>
                <label>Anatomical Coverage</label>
              </div>
              <div className="metadata-value">
                <strong>Primary Focus:</strong> Pelvis and lower abdomen
                <br />
                <strong>Organs of Interest:</strong> Ovaries, uterus, bladder, bowel
                <br />
                <strong>Additional Coverage:</strong> Peritoneal cavity, lymph nodes
              </div>
              <span className="badge body-region">
                {caseMetadata?.body_region || 'Pelvis'}
              </span>
            </div>
            
            <div className="metadata-item">
              <div className="metadata-item-header">
                <span className="metadata-icon">👩‍⚕️</span>
                <label>Patient Information</label>
              </div>
              <div className="metadata-value">
                <strong>Demographics:</strong> Adult female patient
                <br />
                <strong>Age Range:</strong> {caseMetadata?.patient_age || 'Middle-aged adult'}
                <br />
                <strong>Clinical Status:</strong> Stable, outpatient study
                <br />
                <small style={{ color: '#a0aec0', fontSize: '0.9rem', fontStyle: 'italic' }}>
                  All patient identifiers anonymized for educational use
                </small>
              </div>
            </div>
            
            <div className="metadata-item">
              <div className="metadata-item-header">
                <span className="metadata-icon">⚡</span>
                <label>Case Complexity</label>
              </div>
              <div className="metadata-value">
                <strong>Difficulty Level:</strong> Advanced
                <br />
                <strong>Learning Objectives:</strong> 
                <ul style={{ margin: '0.5rem 0 0 0', paddingLeft: '1rem' }}>
                  <li>Complex mass characterization</li>
                  <li>Differential diagnosis formation</li>
                  <li>Staging assessment</li>
                </ul>
              </div>
              <span className={`badge difficulty-${caseMetadata?.difficulty_level?.toLowerCase() || 'advanced'}`}>
                {caseMetadata?.difficulty_level || 'Advanced'} Level
              </span>
            </div>
            
            <div className="metadata-item">
              <div className="metadata-item-header">
                <span className="metadata-icon">🔍</span>
                <label>Key Clinical Questions</label>
              </div>
              <div className="metadata-value">
                <strong>Primary Questions:</strong>
                <ul style={{ margin: '0.5rem 0 0 0', paddingLeft: '1rem' }}>
                  <li>What is the nature of the pelvic mass?</li>
                  <li>Are there signs of malignancy?</li>
                  <li>What is the extent of disease?</li>
                  <li>Are there associated complications?</li>
                </ul>
              </div>
            </div>
            
            <div className="metadata-item">
              <div className="metadata-item-header">
                <span className="metadata-icon">📊</span>
                <label>Study Details</label>
              </div>
              <div className="metadata-value">
                <strong>Study Date:</strong> {caseMetadata?.study_date || 'Educational case'}
                <br />
                <strong>Series Count:</strong> {caseMetadata?.series_count || 'Multiple series'}
                <br />
                <strong>Study UID:</strong> 
                <small style={{ color: '#a0aec0', fontSize: '0.8rem', wordBreak: 'break-all' }}>
                  {caseMetadata?.study_instance_uid || 'Educational case identifier'}
                </small>
              </div>
            </div>
          </div>
        </section>

        {/* Medical Image Viewer - Full Width */}
        <section className="medical-image-viewer">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h3>Medical Image Viewer</h3>
            <button 
              onClick={() => setShowDicomViewer(!showDicomViewer)}
              className="action-btn secondary"
            >
              {showDicomViewer ? 'Hide Image Viewer' : 'Show Image Viewer'}
            </button>
          </div>
          {showDicomViewer && (
            <div className="viewer-container">
              <Suspense fallback={
                <div className="loading-container">
                  <div className="loading-spinner"></div>
                  <p>Loading medical image viewer...</p>
                </div>
              }>
                <OhifIframeViewer 
                  caseId="case001" 
                  viewerUrl={viewerUrl || undefined}
                />
              </Suspense>
            </div>
          )}
        </section>

        {/* Diagnostic Questions */}
        <section className="diagnostic-session">
          <h2>Diagnostic Workflow</h2>
          
          {/* Progress Information */}
          <div className="progress-info">
            <span className="progress-text">
              Question {session.current_step} of {session.total_steps}
            </span>
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: `${(session.current_step / session.total_steps) * 100}%` }}
              />
            </div>
            <span className="progress-text">
              {Math.round((session.current_step / session.total_steps) * 100)}% Complete
            </span>
          </div>

          {/* Current Question */}
          <div className="question-section">
            <div className="context-section">
              <h3>Context</h3>
              <p>{session.current_question.context}</p>
            </div>
            
            <div className="question-content">
              <h3>Question {session.current_question.step}</h3>
              <p>{session.current_question.question}</p>
              
              <button
                type="button"
                className="show-hint"
                onClick={() => setShowHint((v) => !v)}
                aria-expanded={showHint}
              >
                {showHint ? 'Hide Hint' : 'Show Hint'}
              </button>
              {showHint && (
                <div className="hint">
                  {session.current_question.hint}
                </div>
              )}
            </div>
          </div>

          {/* Answer Form */}
          <div className="answer-input">
            <label htmlFor="answer">Your Answer:</label>
            <textarea
              id="answer"
              value={currentAnswer}
              onChange={e => setCurrentAnswer(e.target.value)}
              placeholder="Enter your detailed answer here..."
              disabled={loading}
            />
          </div>

          {/* Action Buttons */}
          <div className="action-buttons">
            <button 
              onClick={submitAnswer}
              className="action-btn primary" 
              disabled={loading || !currentAnswer.trim()}
            >
              {loading ? 'Submitting...' : 'Submit Answer & Continue'}
            </button>
            <button 
              onClick={() => {
                if (window.confirm('Are you sure you want to skip this question? Skipped questions will receive a score of 0.')) {
                  skipQuestion();
                }
              }}
              className="action-btn secondary"
              disabled={loading}
            >
              Skip Question
            </button>
          </div>

          {/* Previous Answers */}
          {Object.keys(session.answers).length > 0 && (
            <div className="previous-answers" style={{ marginTop: '2rem' }}>
              <h3>Your Previous Answers</h3>
              <div className="answers-list">
                {Object.entries(session.answers).map(([step, answer], idx) => (
                  <div className="previous-answer" key={idx} style={{ 
                    padding: '1rem', 
                    background: 'rgba(45, 55, 72, 0.6)', 
                    border: '1px solid #4a5568',
                    borderRadius: '8px',
                    marginBottom: '1rem'
                  }}>
                    <strong style={{ color: '#f7fafc' }}>Question {idx + 1}:</strong> 
                    {answer === "[SKIPPED]" ? (
                      <div style={{ color: '#fbb6ce', fontStyle: 'italic' }}>
                        <em>Question was skipped</em>
                      </div>
                    ) : (
                      <p style={{ color: '#e2e8f0', marginTop: '0.5rem' }}>{answer}</p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </section>

        {/* Error Messages */}
        {error && (
          <div className="error-message">
            {error}
          </div>
        )}
      </main>
    </div>
  );
}

export default DiagnosticWorkflow;