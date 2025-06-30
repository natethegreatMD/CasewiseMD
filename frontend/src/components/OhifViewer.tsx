<<<<<<< HEAD
import React, { useEffect, useRef, useState } from 'react';

interface OhifViewerProps {
  caseId?: string;
  className?: string;
}

const OhifViewer: React.FC<OhifViewerProps> = ({ caseId = 'case001', className = '' }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const initializeOhif = async () => {
      try {
        setLoading(true);
        setError(null);

        // Check if OHIF is available
        if (typeof window !== 'undefined' && window.OHIF) {
          console.log('OHIF is available globally');
        } else {
          // Try to import OHIF dynamically
          console.log('Attempting to import OHIF...');
          try {
            const { default: OHIFViewer } = await import('@ohif/viewer');
            console.log('OHIF imported successfully');
            
            if (containerRef.current) {
              // Initialize OHIF viewer
              const viewer = new OHIFViewer({
                container: containerRef.current,
                url: `/demo_cases/${caseId}/slices`,
                studyInstanceUID: '1.3.6.1.4.1.14519.5.2.1.7695.4007.115512319570807352125051359179'
              });
              
              console.log('OHIF viewer initialized');
              setLoading(false);
            }
          } catch (importError) {
            console.error('Failed to import OHIF:', importError);
            setError('Failed to load OHIF viewer. Please check the installation.');
            setLoading(false);
          }
        }
      } catch (err) {
        console.error('Error initializing OHIF viewer:', err);
        setError('Failed to initialize OHIF viewer');
        setLoading(false);
      }
    };

    initializeOhif();
  }, [caseId]);

  if (loading) {
    return (
      <div className={`ohif-viewer loading ${className}`}>
        <div className="loading-spinner"></div>
        <p>Loading OHIF DICOM viewer...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`ohif-viewer error ${className}`}>
        <div className="error-message">
          <h3>Error Loading OHIF Viewer</h3>
          <p>{error}</p>
          <button onClick={() => window.location.reload()}>Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div className={`ohif-viewer ${className}`}>
      <div 
        ref={containerRef}
        className="ohif-container"
        style={{ width: '100%', height: '600px' }}
      />
    </div>
  );
};

=======
import React, { useEffect, useRef, useState } from 'react';

interface OhifViewerProps {
  caseId?: string;
  className?: string;
}

const OhifViewer: React.FC<OhifViewerProps> = ({ caseId = 'case001', className = '' }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const initializeOhif = async () => {
      try {
        setLoading(true);
        setError(null);

        // Check if OHIF is available
        if (typeof window !== 'undefined' && window.OHIF) {
          console.log('OHIF is available globally');
        } else {
          // Try to import OHIF dynamically
          console.log('Attempting to import OHIF...');
          try {
            const { default: OHIFViewer } = await import('@ohif/viewer');
            console.log('OHIF imported successfully');
            
            if (containerRef.current) {
              // Initialize OHIF viewer
              const viewer = new OHIFViewer({
                container: containerRef.current,
                url: `/demo_cases/${caseId}/slices`,
                studyInstanceUID: '1.3.6.1.4.1.14519.5.2.1.7695.4007.115512319570807352125051359179'
              });
              
              console.log('OHIF viewer initialized');
              setLoading(false);
            }
          } catch (importError) {
            console.error('Failed to import OHIF:', importError);
            setError('Failed to load OHIF viewer. Please check the installation.');
            setLoading(false);
          }
        }
      } catch (err) {
        console.error('Error initializing OHIF viewer:', err);
        setError('Failed to initialize OHIF viewer');
        setLoading(false);
      }
    };

    initializeOhif();
  }, [caseId]);

  if (loading) {
    return (
      <div className={`ohif-viewer loading ${className}`}>
        <div className="loading-spinner"></div>
        <p>Loading OHIF DICOM viewer...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`ohif-viewer error ${className}`}>
        <div className="error-message">
          <h3>Error Loading OHIF Viewer</h3>
          <p>{error}</p>
          <button onClick={() => window.location.reload()}>Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div className={`ohif-viewer ${className}`}>
      <div 
        ref={containerRef}
        className="ohif-container"
        style={{ width: '100%', height: '600px' }}
      />
    </div>
  );
};

>>>>>>> da6d34f279c03146f63538b30f43f508521da53d
export default OhifViewer; 