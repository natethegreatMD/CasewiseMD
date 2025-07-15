import React, { useState } from 'react';

interface OhifIframeViewerProps {
  caseId?: string;
  className?: string;
  viewerUrl?: string;
}

const OhifIframeViewer: React.FC<OhifIframeViewerProps> = ({ 
  caseId = 'case001', 
  className = '', 
  viewerUrl 
}) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Use the provided viewerUrl or fall back to environment variables
  const VIEWER_URL = viewerUrl || import.meta.env.VITE_VIEWER_URL || 'https://viewer.casewisemd.org';

  const handleIframeLoad = () => {
    setLoading(false);
  };

  const handleIframeError = () => {
    setError('Failed to load OHIF viewer');
    setLoading(false);
  };

  // If no viewer URL is provided, show a message
  if (!viewerUrl && !import.meta.env.VITE_VIEWER_URL) {
    return (
      <div className={`ohif-iframe-viewer error ${className}`}>
        <div className="error-message">
          <h3>OHIF Viewer Configuration</h3>
          <p>Viewer URL not configured. Please check your environment variables or API response.</p>
          <p>Expected: Dynamic URL from MCP API</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`ohif-iframe-viewer error ${className}`}>
        <div className="error-message">
          <h3>Error Loading OHIF Viewer</h3>
          <p>{error}</p>
          <p>Viewer URL: {VIEWER_URL}</p>
          <button onClick={() => window.location.reload()}>Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div className={`ohif-iframe-viewer ${className}`} style={{ width: '100%', height: '100%' }}>
      {loading && (
        <div className="loading-overlay">
          <div className="loading-spinner"></div>
          <p>Loading OHIF DICOM viewer...</p>
          <p>Case: {caseId}</p>
          {viewerUrl && (
            <p style={{ fontSize: '0.8rem', color: '#a0aec0' }}>
              Using dynamic viewer URL from MCP API
            </p>
          )}
        </div>
      )}
      
      <iframe
        src={VIEWER_URL}
        title="OHIF DICOM Viewer"
        className="ohif-iframe"
        style={{
          width: '100%',
          height: '100%',
          border: 'none',
          borderRadius: '8px',
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
        }}
        onLoad={handleIframeLoad}
        onError={handleIframeError}
        allow="fullscreen"
      />
    </div>
  );
};

export default OhifIframeViewer; 