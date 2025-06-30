# DICOM Viewer Component

## Overview

The `DicomViewer` component provides a professional-grade medical imaging viewer for CasewiseMD, built using CornerstoneJS and integrated with the diagnostic workflow.

## Features

### Current Features
- **Slice Navigation**: Navigate through axial CT slices using arrow keys, mouse wheel, or navigation buttons
- **Window/Level Controls**: Adjust brightness and contrast with real-time sliders
- **Measurement Tools**: Basic length and probe measurements
- **Pan & Zoom**: Interactive panning and zooming with mouse controls
- **Responsive Design**: Adapts to different screen sizes
- **Error Handling**: Graceful error handling for missing files or loading issues

### Technical Implementation
- **CornerstoneJS**: Industry-standard medical imaging library
- **React Integration**: Fully integrated with React component lifecycle
- **TypeScript**: Type-safe implementation
- **Modular Design**: Easy to extend and maintain

## Usage

```tsx
import DicomViewer from './components/DicomViewer';

// Basic usage
<DicomViewer caseId="case001" />

// With custom styling
<DicomViewer caseId="case001" className="custom-viewer" />
```

## File Structure

```
public/demo_cases/
  case001/
    slices/
      slice001.dcm
      slice002.dcm
      ...
    metadata.json
```

## Controls

### Navigation
- **Arrow Keys**: Previous/Next slice
- **Mouse Wheel**: Previous/Next slice
- **Navigation Buttons**: Previous/Next slice

### Tools
- **Left Click**: Pan (when Pan tool active)
- **Right Click**: Zoom (when Zoom tool active)
- **Middle Click**: Window/Level adjustment
- **Tool Buttons**: Switch between measurement tools

### Window/Level
- **Sliders**: Adjust window center and width
- **Real-time Updates**: Changes apply immediately

## Future Enhancements

### Phase 2 Features
- **WADO Integration**: Support for DICOM web services
- **Advanced Measurements**: Area, angle, and ROI measurements
- **Annotations**: Text and arrow annotations
- **Multi-planar Reconstruction**: Coronal and sagittal views
- **3D Rendering**: Volume rendering capabilities

### Phase 3 Features
- **Comparison Tools**: Side-by-side image comparison
- **Advanced Filters**: Edge enhancement, noise reduction
- **Export Features**: Save measurements and annotations
- **Integration APIs**: Connect with PACS systems

## Dependencies

- `cornerstone-core`: Core imaging functionality
- `cornerstone-tools`: Measurement and interaction tools
- `cornerstone-wado-image-loader`: DICOM file loading
- `dicom-parser`: DICOM file parsing
- `dcmjs`: DICOM JavaScript utilities
- `hammerjs`: Touch gesture support

## Browser Support

- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

## Performance Considerations

- **Lazy Loading**: Slices loaded on demand
- **Memory Management**: Proper cleanup of Cornerstone resources
- **Responsive Canvas**: Optimized for different screen sizes
- **Error Recovery**: Graceful handling of loading failures

## Development Notes

### Adding New Cases
1. Create case directory in `public/demo_cases/`
2. Add DICOM files to `slices/` subdirectory
3. Create `metadata.json` with case information
4. Update component to reference new case ID

### Customization
- Modify `DicomViewer.css` for styling changes
- Extend component props for additional configuration
- Add new tools by importing from `cornerstone-tools`

### Testing
- Test with various DICOM file formats
- Verify responsive behavior on different devices
- Check error handling with missing files
- Validate measurement accuracy

## Troubleshooting

### Common Issues
1. **Files Not Loading**: Check file paths and CORS settings
2. **Performance Issues**: Verify image sizes and loading strategy
3. **Tool Not Working**: Ensure Cornerstone tools are properly initialized
4. **Display Issues**: Check CSS and canvas sizing

### Debug Mode
Enable debug logging by setting `localStorage.debug = 'cornerstone*'` in browser console. 