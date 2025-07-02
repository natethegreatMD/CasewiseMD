<<<<<<< HEAD
import React, { useState } from 'react';

interface OhifIframeViewerProps {
  caseId?: string;
  className?: string;
}

const OhifIframeViewer: React.FC<OhifIframeViewerProps> = ({ caseId = 'case001', className = '' }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Get URLs from environment variables with fallbacks
  const API_URL = import.meta.env.VITE_API_URL || 'https://api.casewisemd.org';
  const VIEWER_URL = import.meta.env.VITE_VIEWER_URL || 'https://viewer.casewisemd.org';

  // Build a list of DICOM file URLs for OHIF
  // Based on the case metadata, we know we have axial, delayed, and scout series
  const buildDicomUrls = () => {
    const baseUrl = `${API_URL}/dicom/${caseId}`;
    
    // These are the series UIDs from the metadata
    const series = {
      axial: '1.3.6.1.4.1.14519.5.2.1.7695.4007.115512319570807352125051359179',
      delayed: '1.3.6.1.4.1.14519.5.2.1.7695.4007.290560597213035590678005726868',
      scout: '1.3.6.1.4.1.14519.5.2.1.7695.4007.335478662210512911160907262491'
    };

    // Build URLs for the axial series (main CT images)
    const axialUrls = [];
    for (let i = 1; i <= 18; i++) {
      axialUrls.push(`${baseUrl}/${series.axial}/${i.toString().padStart(2, '0')}-01.dcm`);
    }

    // Build URLs for the delayed series
    const delayedUrls = [];
    for (let i = 1; i <= 15; i++) {
      delayedUrls.push(`${baseUrl}/${series.delayed}/${i.toString().padStart(2, '0')}-01.dcm`);
    }

    // Build URLs for the scout series
    const scoutUrls = [];
    for (let i = 1; i <= 1; i++) {
      scoutUrls.push(`${baseUrl}/${series.scout}/${i.toString().padStart(2, '0')}-01.dcm`);
    }

    // Combine all URLs
    return [...axialUrls, ...delayedUrls, ...scoutUrls];
  };

  const dicomUrls = buildDicomUrls();
  
  // Create the OHIF URL with DICOM file URLs as query parameters
  // Add parameters to force direct loading without study selection
  const urlParams = new URLSearchParams({
    url: dicomUrls.join(','),
    // Force the viewer to load directly without showing study list
    studyInstanceUIDs: '1.3.6.1.4.1.14519.5.2.1.7695.4007.115512319570807352125051359179',
    // Disable the study list
    showStudyList: 'false'
  });
  
  const ohifUrl = `${VIEWER_URL}/?${urlParams.toString()}`;

  const handleIframeLoad = () => {
    setLoading(false);
  };

  const handleIframeError = () => {
    setError('Failed to load OHIF viewer');
    setLoading(false);
  };

  if (error) {
    return (
      <div className={`ohif-iframe-viewer error ${className}`}>
        <div className="error-message">
          <h3>Error Loading OHIF Viewer</h3>
          <p>{error}</p>
          <p>Please ensure the OHIF server is running on port 8081 and DICOM files are accessible.</p>
          <button onClick={() => window.location.reload()}>Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div className={`ohif-iframe-viewer ${className}`}>
      {loading && (
        <div className="loading-overlay">
          <div className="loading-spinner"></div>
          <p>Loading OHIF DICOM viewer...</p>
          <p>Loading {dicomUrls.length} DICOM files...</p>
        </div>
      )}
      
      <iframe
        src={ohifUrl}
        title="OHIF DICOM Viewer"
        className="ohif-iframe"
        style={{
          width: '100%',
          height: '600px',
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

=======
import React, { useState } from 'react';

interface OhifIframeViewerProps {
  caseId?: string;
  className?: string;
}

const OhifIframeViewer: React.FC<OhifIframeViewerProps> = ({ caseId = 'case001', className = '' }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Get URLs from environment variables with fallbacks
  const API_URL = import.meta.env.VITE_API_URL || 'https://api.casewisemd.org';
  const VIEWER_URL = import.meta.env.VITE_VIEWER_URL || 'https://viewer.casewisemd.org';

  // Build a list of DICOM file URLs for OHIF
  // Based on the case metadata, we know we have axial, delayed, and scout series
  const buildDicomUrls = () => {
    const baseUrl = `${API_URL}/dicom/${caseId}`;
    
    // These are the series UIDs from the metadata
    const series = {
      axial: '1.3.6.1.4.1.14519.5.2.1.7695.4007.115512319570807352125051359179',
      delayed: '1.3.6.1.4.1.14519.5.2.1.7695.4007.290560597213035590678005726868',
      scout: '1.3.6.1.4.1.14519.5.2.1.7695.4007.335478662210512911160907262491'
    };

    // Build URLs for the axial series (main CT images)
    const axialUrls = [];
    for (let i = 1; i <= 18; i++) {
      axialUrls.push(`${baseUrl}/${series.axial}/${i.toString().padStart(2, '0')}-01.dcm`);
    }

    // Build URLs for the delayed series
    const delayedUrls = [];
    for (let i = 1; i <= 15; i++) {
      delayedUrls.push(`${baseUrl}/${series.delayed}/${i.toString().padStart(2, '0')}-01.dcm`);
    }

    // Build URLs for the scout series
    const scoutUrls = [];
    for (let i = 1; i <= 1; i++) {
      scoutUrls.push(`${baseUrl}/${series.scout}/${i.toString().padStart(2, '0')}-01.dcm`);
    }

    // Combine all URLs
    return [...axialUrls, ...delayedUrls, ...scoutUrls];
  };

  const dicomUrls = buildDicomUrls();
  
  // Create the OHIF URL with DICOM file URLs as query parameters
  // Add parameters to force direct loading without study selection
  const urlParams = new URLSearchParams({
    url: dicomUrls.join(','),
    // Force the viewer to load directly without showing study list
    studyInstanceUIDs: '1.3.6.1.4.1.14519.5.2.1.7695.4007.115512319570807352125051359179',
    // Disable the study list
    showStudyList: 'false'
  });
  
  const ohifUrl = `${VIEWER_URL}/?${urlParams.toString()}`;

  const handleIframeLoad = () => {
    setLoading(false);
  };

  const handleIframeError = () => {
    setError('Failed to load OHIF viewer');
    setLoading(false);
  };

  if (error) {
    return (
      <div className={`ohif-iframe-viewer error ${className}`}>
        <div className="error-message">
          <h3>Error Loading OHIF Viewer</h3>
          <p>{error}</p>
          <p>Please ensure the OHIF server is running on port 8081 and DICOM files are accessible.</p>
          <button onClick={() => window.location.reload()}>Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div className={`ohif-iframe-viewer ${className}`}>
      {loading && (
        <div className="loading-overlay">
          <div className="loading-spinner"></div>
          <p>Loading OHIF DICOM viewer...</p>
          <p>Loading {dicomUrls.length} DICOM files...</p>
        </div>
      )}
      
      <iframe
        src={ohifUrl}
        title="OHIF DICOM Viewer"
        className="ohif-iframe"
        style={{
          width: '100%',
          height: '600px',
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

>>>>>>> da6d34f279c03146f63538b30f43f508521da53d
export default OhifIframeViewer; 