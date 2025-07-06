import React, { useEffect, useRef, useState, useCallback, useMemo } from 'react';
import * as cornerstone from 'cornerstone-core';
import * as cornerstoneTools from 'cornerstone-tools';
import * as cornerstoneWADOImageLoader from 'cornerstone-wado-image-loader';
import * as dicomParser from 'dicom-parser';
import * as dcmjs from 'dcmjs';
import * as Hammer from 'hammerjs';

// Configure Cornerstone with error handling
try {
  cornerstoneWADOImageLoader.external.cornerstone = cornerstone;
  cornerstoneWADOImageLoader.external.dicomParser = dicomParser;
  cornerstoneTools.external.cornerstone = cornerstone;
  cornerstoneTools.external.Hammer = Hammer;

  // Configure WADO image loader
  cornerstoneWADOImageLoader.webWorkerManager.initialize({
    maxWebWorkers: navigator.hardwareConcurrency || 1,
    startWebWorkersOnDemand: true,
    taskConfiguration: {
      decodeTask: {
        initializeCodecsOnStartup: true,
        usePDFJS: false,
        strict: false
      }
    }
  });

  // Initialize tools
  cornerstoneTools.init();
  
  console.log('Cornerstone initialized successfully');
} catch (error) {
  console.warn('Failed to initialize Cornerstone tools:', error);
}

interface DicomViewerProps {
  caseId?: string;
  className?: string;
}

interface DicomSlice {
  id: string;
  url: string;
  index: number;
  metadata?: any;
}

interface SeriesInfo {
  id: string;
  name: string;
  uid: string;
  sliceCount: number;
  orientation: string;
}

const DicomViewer: React.FC<DicomViewerProps> = ({ caseId = 'case001', className = '' }) => {
  const canvasRef = useRef<HTMLDivElement>(null);
  const [slices, setSlices] = useState<DicomSlice[]>([]);
  const [currentSliceIndex, setCurrentSliceIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [windowCenter, setWindowCenter] = useState(40);
  const [windowWidth, setWindowWidth] = useState(400);
  const [isViewerInitialized, setIsViewerInitialized] = useState(false);
  const [currentSeries, setCurrentSeries] = useState<string>('axial');
  const [seriesList, setSeriesList] = useState<SeriesInfo[]>([]);

  // Series information from metadata
  const SERIES_INFO: SeriesInfo[] = [
    {
      id: 'axial',
      name: 'Axial CT',
      uid: '1.3.6.1.4.1.14519.5.2.1.7695.4007.115512319570807352125051359179',
      sliceCount: 268, // 18 rows with varying columns (15+15+15+11+15+15+15+15+15+15+15+15+15+15+15+15+15+15)
      orientation: 'Axial'
    },
    {
      id: 'delayed',
      name: 'Delayed CT',
      uid: '1.3.6.1.4.1.14519.5.2.1.7695.4007.290560597213035590678005726868',
      sliceCount: 20,
      orientation: 'Axial'
    },
    {
      id: 'scout',
      name: 'Scout',
      uid: '1.3.6.1.4.1.14519.5.2.1.7695.4007.335478662210512911160907262491',
      sliceCount: 1,
      orientation: 'Scout'
    }
  ];

  // Generate slice URLs for the selected series
  const generateSliceUrls = useCallback((caseId: string, seriesId: string): DicomSlice[] => {
    const sliceUrls: DicomSlice[] = [];
    const series = SERIES_INFO.find(s => s.id === seriesId);
    
    if (!series) return sliceUrls;
    
    const baseUrl = `/demo_cases/${caseId}/slices`;
    
    if (seriesId === 'axial') {
      // Axial series: files are named 01-01.dcm, 01-02.dcm, etc.
      // Based on the actual files, there are 18 rows with varying columns
      const rowCounts = [15, 15, 15, 11, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15];
      
      let sliceIndex = 0;
      for (let row = 1; row <= 18; row++) {
        const colCount = rowCounts[row - 1] || 1;
        for (let col = 1; col <= colCount; col++) {
          sliceUrls.push({
            id: `axial_${row.toString().padStart(2, '0')}-${col.toString().padStart(2, '0')}`,
            url: `${baseUrl}/${series.uid}/${row.toString().padStart(2, '0')}-${col.toString().padStart(2, '0')}.dcm`,
            index: sliceIndex++
          });
        }
      }
    } else if (seriesId === 'delayed') {
      // Delayed series: 20 slices named 01-01.dcm, 02-01.dcm, etc.
      for (let i = 1; i <= 20; i++) {
        sliceUrls.push({
          id: `delayed_${i.toString().padStart(2, '0')}`,
          url: `${baseUrl}/${series.uid}/${i.toString().padStart(2, '0')}-01.dcm`,
          index: sliceUrls.length
        });
      }
    } else if (seriesId === 'scout') {
      // Scout series: 1 slice named 1-1.dcm
      sliceUrls.push({
        id: 'scout_1',
        url: `${baseUrl}/${series.uid}/1-1.dcm`,
        index: 0
      });
    }
    
    return sliceUrls;
  }, []);

  // Load DICOM slice - memoized to prevent useEffect dependency issues
  const loadDicomSlice = useMemo(() => {
    return async (slice: DicomSlice): Promise<any> => {
      try {
        console.log('Loading DICOM slice:', slice.url);
        
        // Test if file exists first
        const response = await fetch(slice.url, { method: 'HEAD' });
        if (!response.ok) {
          throw new Error(`File not found: ${slice.url} (${response.status})`);
        }
        
        // Load actual DICOM file using cornerstone-wado-image-loader
        const imageId = `wadouri:${slice.url}`;
        console.log('Image ID:', imageId);
        
        // Return a promise that resolves with the image object
        return new Promise((resolve, reject) => {
          console.log('Starting Cornerstone loadImage...');
          
          cornerstone.loadImage(imageId).then((image) => {
            console.log('Successfully loaded image:', image);
            console.log('Image properties:', {
              rows: image.rows,
              columns: image.columns,
              windowCenter: image.windowCenter,
              windowWidth: image.windowWidth,
              slope: image.slope,
              intercept: image.intercept
            });
            resolve(image);
          }).catch((error) => {
            console.error('Error loading DICOM file with Cornerstone:', error);
            
            // Try alternative loading method
            console.log('Attempting alternative loading method...');
            const alternativeImageId = slice.url;
            cornerstone.loadImage(alternativeImageId).then((image) => {
              console.log('Alternative method succeeded:', image);
              resolve(image);
            }).catch((altError) => {
              console.error('Alternative method also failed:', altError);
              reject(error);
            });
          });
        });
      } catch (err) {
        console.error('Error loading DICOM slice:', err);
        throw err;
      }
    };
  }, []);

  // Initialize Cornerstone viewer
  const initializeViewer = useCallback(async () => {
    if (!canvasRef.current || isViewerInitialized) return;

    try {
      const element = canvasRef.current;
      console.log('Initializing viewer with element:', element);
      
      // Test canvas functionality first
      const testCanvas = element.querySelector('canvas') || element;
      if (testCanvas && testCanvas.getContext) {
        const ctx = testCanvas.getContext('2d');
        if (ctx) {
          console.log('Canvas test: Drawing test pattern...');
          ctx.fillStyle = '#333';
          ctx.fillRect(0, 0, testCanvas.width || 500, testCanvas.height || 500);
          ctx.fillStyle = '#4299e1';
          ctx.font = '14px Arial';
          ctx.textAlign = 'center';
          ctx.fillText('Canvas Test - Loading DICOM...', (testCanvas.width || 500) / 2, (testCanvas.height || 500) / 2);
        }
      }
      
      // Enable the element for Cornerstone
      cornerstone.enable(element);
      console.log('Element enabled for Cornerstone');

      // Add basic tools with proper configuration
      try {
        // Temporarily disable tools to prevent mouse event errors
        // We'll re-enable them once image loading is working properly
        console.log('Tools temporarily disabled to prevent mouse event errors');
        
        /*
        // Add tools with error handling
        if (cornerstoneTools.PanTool) {
          cornerstoneTools.addTool(cornerstoneTools.PanTool);
        }
        if (cornerstoneTools.ZoomTool) {
          cornerstoneTools.addTool(cornerstoneTools.ZoomTool);
        }
        if (cornerstoneTools.WwwcTool) {
          cornerstoneTools.addTool(cornerstoneTools.WwwcTool);
        }
        
        // Set tool modes with proper mouse button configuration
        // Use a more conservative approach to prevent mouse event errors
        try {
          cornerstoneTools.setToolActive('Pan', { mouseButtonMask: 2 }); // Right mouse button
        } catch (e) {
          console.warn('Failed to set Pan tool:', e);
        }
        
        try {
          cornerstoneTools.setToolActive('Zoom', { mouseButtonMask: 4 }); // Middle mouse button
        } catch (e) {
          console.warn('Failed to set Zoom tool:', e);
        }
        
        try {
          cornerstoneTools.setToolActive('Wwwc', { mouseButtonMask: 1 }); // Left mouse button
        } catch (e) {
          console.warn('Failed to set Wwwc tool:', e);
        }
        */
        
        console.log('Cornerstone tools temporarily disabled');
      } catch (toolError) {
        console.warn('Some tools failed to initialize:', toolError);
      }

      setIsViewerInitialized(true);
      console.log('Viewer initialization complete - isViewerInitialized set to true');
    } catch (err) {
      console.error('Error initializing viewer:', err);
      setError('Failed to initialize DICOM viewer');
    }
  }, [isViewerInitialized]);

  // Load slice when current slice index changes
  useEffect(() => {
    console.log('Slice index changed to:', currentSliceIndex);
    console.log('Viewer initialized:', isViewerInitialized);
    console.log('Slices length:', slices.length);
    console.log('Condition check:', isViewerInitialized && slices.length > 0);
    
    if (isViewerInitialized && slices.length > 0) {
      console.log('✅ Condition met - starting image loading...');
      // Add a small delay to prevent rapid loading
      const timer = setTimeout(async () => {
        try {
          const currentSlice = slices[currentSliceIndex];
          console.log('Loading current slice:', currentSlice);
          console.log('Canvas element:', canvasRef.current);
          console.log('Viewer initialized:', isViewerInitialized);
          
          // Re-enable the element in case React re-rendered it
          try {
            cornerstone.enable(canvasRef.current);
            console.log('Element re-enabled for Cornerstone');
          } catch (enableError) {
            console.log('Element already enabled or enable failed:', enableError);
          }
          
          const image = await loadDicomSlice(currentSlice);
          console.log('Image loaded successfully, attempting to display...');
          
          // Display the image
          await cornerstone.displayImage(canvasRef.current, image);
          console.log('Image displayed successfully');
          console.log('Image display complete');
          
        } catch (err) {
          console.error('Error loading current slice:', err);
          setError(`Failed to load DICOM slice: ${err.message}`);
        }
      }, 100);
      
      return () => clearTimeout(timer);
    } else {
      console.log('❌ Condition not met - skipping image loading');
      console.log('  - isViewerInitialized:', isViewerInitialized);
      console.log('  - slices.length:', slices.length);
    }
  }, [currentSliceIndex, isViewerInitialized, slices.length, loadDicomSlice]);

  // Handle slice navigation
  const navigateSlice = useCallback((direction: 'next' | 'prev') => {
    console.log('Navigation requested:', direction);
    console.log('Current slice index:', currentSliceIndex);
    console.log('Total slices:', slices.length);
    
    if (direction === 'next' && currentSliceIndex < slices.length - 1) {
      console.log('Moving to next slice:', currentSliceIndex + 1);
      setCurrentSliceIndex(prev => prev + 1);
    } else if (direction === 'prev' && currentSliceIndex > 0) {
      console.log('Moving to previous slice:', currentSliceIndex - 1);
      setCurrentSliceIndex(prev => prev - 1);
    } else {
      console.log('Navigation blocked - at boundary');
    }
  }, [currentSliceIndex, slices.length]);

  // Handle series change
  const handleSeriesChange = useCallback((seriesId: string) => {
    setCurrentSeries(seriesId);
    setCurrentSliceIndex(0);
    const newSlices = generateSliceUrls(caseId, seriesId);
    setSlices(newSlices);
  }, [caseId, generateSliceUrls]);

  // Handle keyboard navigation
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      switch (event.key) {
        case 'ArrowUp':
        case 'ArrowLeft':
          event.preventDefault();
          navigateSlice('prev');
          break;
        case 'ArrowDown':
        case 'ArrowRight':
          event.preventDefault();
          navigateSlice('next');
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [navigateSlice]);

  // Handle mouse wheel navigation
  useEffect(() => {
    const handleWheel = (event: WheelEvent) => {
      event.preventDefault();
      if (event.deltaY > 0) {
        navigateSlice('next');
      } else {
        navigateSlice('prev');
      }
    };

    const element = canvasRef.current;
    if (element) {
      element.addEventListener('wheel', handleWheel);
      return () => element.removeEventListener('wheel', handleWheel);
    }
  }, [navigateSlice]);

  // Test DICOM file accessibility
  const testDicomAccess = useCallback(async (caseId: string) => {
    const testUrl = `/demo_cases/${caseId}/slices/1.3.6.1.4.1.14519.5.2.1.7695.4007.115512319570807352125051359179/01-01.dcm`;
    try {
      const response = await fetch(testUrl, { method: 'HEAD' });
      console.log('DICOM file test:', testUrl, response.status, response.ok);
      
      if (response.ok) {
        // Also test if we can read the file content
        const contentResponse = await fetch(testUrl);
        const arrayBuffer = await contentResponse.arrayBuffer();
        console.log('DICOM file content test: File size =', arrayBuffer.byteLength, 'bytes');
        return true;
      }
      return false;
    } catch (error) {
      console.error('DICOM file test failed:', error);
      return false;
    }
  }, []);

  // Initialize component
  useEffect(() => {
    const initializeComponent = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Test DICOM file accessibility
        const filesAccessible = await testDicomAccess(caseId);
        if (!filesAccessible) {
          setError('DICOM files not accessible. Please check file paths.');
          setLoading(false);
          return;
        }
        
        setSeriesList(SERIES_INFO);
        
        // Generate slice URLs for axial series by default
        const sliceUrls = generateSliceUrls(caseId, 'axial');
        console.log('Generated slice URLs:', sliceUrls.length, 'slices');
        setSlices(sliceUrls);
        console.log('Slices state set - length:', sliceUrls.length);
        
        // Initialize viewer
        console.log('Starting viewer initialization...');
        await initializeViewer();
        console.log('Viewer initialization completed in component init');
        
        setLoading(false);
      } catch (err) {
        console.error('Error initializing component:', err);
        setError('Failed to initialize DICOM viewer');
        setLoading(false);
      }
    };

    initializeComponent();
  }, [caseId, generateSliceUrls, initializeViewer, testDicomAccess]);

  // Note: Window/level is handled by the WwwcTool, so we don't need to update it manually

  if (loading) {
    return (
      <div className={`dicom-viewer loading ${className}`}>
        <div className="loading-spinner"></div>
        <p>Loading DICOM viewer...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`dicom-viewer error ${className}`}>
        <div className="error-message">
          <h3>Error Loading DICOM Viewer</h3>
          <p>{error}</p>
          <button onClick={() => window.location.reload()}>Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div className={`dicom-viewer ${className}`}>
      {/* Series Selection */}
      <div className="series-selection">
        <label>Series:</label>
        <select 
          value={currentSeries} 
          onChange={(e) => handleSeriesChange(e.target.value)}
          className="series-select"
        >
          {seriesList.map((series) => (
            <option key={series.id} value={series.id}>
              {series.name} ({series.sliceCount} slices)
            </option>
          ))}
        </select>
      </div>

      {/* Viewer Controls */}
      <div className="viewer-controls">
        <div className="slice-navigation">
          <button 
            onClick={() => navigateSlice('prev')}
            disabled={currentSliceIndex === 0}
            className="nav-btn"
          >
            ← Previous
          </button>
          <span className="slice-info">
            Slice {currentSliceIndex + 1} of {slices.length}
          </span>
          <button 
            onClick={() => navigateSlice('next')}
            disabled={currentSliceIndex === slices.length - 1}
            className="nav-btn"
          >
            Next →
          </button>
        </div>

        <div className="tool-controls">
          <button 
            onClick={() => alert('Tools temporarily disabled for debugging')}
            className="tool-btn"
            disabled
            title="Tools temporarily disabled for debugging"
          >
            Pan (Disabled)
          </button>
          <button 
            onClick={() => alert('Tools temporarily disabled for debugging')}
            className="tool-btn"
            disabled
            title="Tools temporarily disabled for debugging"
          >
            Zoom (Disabled)
          </button>
          <button 
            onClick={() => alert('Tools temporarily disabled for debugging')}
            className="tool-btn"
            disabled
            title="Tools temporarily disabled for debugging"
          >
            Window/Level (Disabled)
          </button>
        </div>
      </div>

      {/* DICOM Canvas */}
      <div className="viewer-canvas-container">
        <div 
          ref={canvasRef}
          className="viewer-canvas"
          style={{ width: '100%', height: '500px' }}
        />
      </div>

      {/* Instructions */}
      <div className="viewer-instructions">
        <p>
          <strong>Navigation:</strong> Use arrow keys, mouse wheel, or navigation buttons
        </p>
        <p>
          <strong>Tools:</strong> Temporarily disabled for debugging. Focus on image loading and navigation.
        </p>
        <p>
          <strong>Series:</strong> Select different CT series (Axial, Delayed, Scout)
        </p>
      </div>
    </div>
  );
};

export default DicomViewer; 