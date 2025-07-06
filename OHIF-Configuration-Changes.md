# OHIF Configuration Changes Documentation

## Problem Fixed
The OHIF viewer was connecting to CloudFront URLs instead of the local Orthanc server, causing "Studies Not Available" errors.

## Root Cause
The `app-config.js` file at `/var/www/viewer/app-config.js` contained hardcoded CloudFront URLs:
- `https://d14fa38qiwhyfd.cloudfront.net/dicomweb`
- `https://dd14fa38qiwhyfd.cloudfront.net/dicomweb`
- `https://d3t6nz73ql33tx.cloudfront.net/dicomweb`

## Solution Applied
Replaced the CloudFront configuration with a clean, single datasource pointing to the Orthanc server.

## Key Changes Made

### 1. Datasource Configuration
**Before:** Multiple datasources with CloudFront URLs
**After:** Single datasource with correct Orthanc URL

```javascript
dataSources: [
  {
    namespace: "@ohif/extension-default.dataSourcesModule.dicomweb",
    sourceName: "dicomweb",
    configuration: {
      friendlyName: "Casewise Orthanc DICOMWeb Server",
      name: "orthanc",
      wadoUriRoot: "https://api.casewisemd.org/orthanc/dicom-web",
      qidoRoot: "https://api.casewisemd.org/orthanc/dicom-web",
      wadoRoot: "https://api.casewisemd.org/orthanc/dicom-web",
      // ... other settings
    }
  }
]
```

### 2. Important Display Settings Preserved
- `staticWado: true` - For proper image handling
- `singlepart: "bulkdata,video"` - For correct data transfer
- `supportsFuzzyMatching: true` - For search functionality
- `qidoSupportsIncludeField: true` - For Orthanc compatibility
- `bulkDataURI` with `transform` function - For image processing
- `omitQuotationForMultipartRequest: true` - For Orthanc compatibility

### 3. Configuration Structure
- Kept all essential OHIF settings (multimonitor, worker limits, etc.)
- Maintained proper error handling
- Preserved all image rendering settings

## Files Modified
- **Main config:** `/var/www/viewer/app-config.js`
- **Backup created:** `/var/www/viewer/app-config-working-backup.js`

## Restoration Instructions
If you need to restore this configuration:

### From VPS backup:
```bash
ssh root@143.244.154.89 "cp /var/www/viewer/app-config-working-backup.js /var/www/viewer/app-config.js"
```

### From local backup:
```bash
scp ohif-working-config-backup.js root@143.244.154.89:/var/www/viewer/app-config.js
```

## Testing
After applying these changes:
1. OHIF viewer loads cases automatically
2. Images display with proper contrast/windowing
3. No more CloudFront errors in console
4. All requests go to `api.casewisemd.org/orthanc/dicom-web`

## Date Applied
January 6, 2025

## Status
✅ **WORKING** - Complete medical education platform is now fully functional 