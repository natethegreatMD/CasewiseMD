window.config = {
  name: "config/default.js",
  routerBasename: null,
  extensions: [],
  modes: [],
  customizationService: {},
  showStudyList: true,
  maxNumberOfWebWorkers: 3,
  showWarningMessageForCrossOrigin: true,
  showCPUFallbackMessage: true,
  showLoadingIndicator: true,
  experimentalStudyBrowserSort: false,
  strictZSpacingForVolumeViewport: true,
  groupEnabledModesFirst: true,
  allowMultiSelectExport: false,
  maxNumRequests: {
    interaction: 100,
    thumbnail: 75,
    prefetch: 25
  },
  multimonitor: [
    {
      id: "split",
      test: ({ multimonitor: o }) => "split" === o,
      screens: [
        {
          id: "ohif0",
          screen: null,
          location: { screen: 0, width: .5, height: 1, left: 0, top: 0 },
          options: "location=no,menubar=no,scrollbars=no,status=no,titlebar=no"
        },
        {
          id: "ohif1",
          screen: null,
          location: { width: .5, height: 1, left: .5, top: 0 },
          options: "location=no,menubar=no,scrollbars=no,status=no,titlebar=no"
        }
      ]
    },
    {
      id: "2",
      test: ({ multimonitor: o }) => "2" === o,
      screens: [
        {
          id: "ohif0",
          screen: 0,
          location: { width: 1, height: 1, left: 0, top: 0 },
          options: "fullscreen=yes,location=no,menubar=no,scrollbars=no,status=no,titlebar=no"
        },
        {
          id: "ohif1",
          screen: 1,
          location: { width: 1, height: 1, left: 0, top: 0 },
          options: "fullscreen=yes,location=no,menubar=no,scrollbars=no,status=no,titlebar=no"
        }
      ]
    }
  ],
  defaultDataSourceName: "dicomweb",
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
        qidoSupportsIncludeField: true,
        imageRendering: "wadors",
        thumbnailRendering: "wadors",
        enableStudyLazyLoad: true,
        supportsFuzzyMatching: true,
        supportsWildcard: false,
        staticWado: true,
        singlepart: "bulkdata,video",
        bulkDataURI: {
          enabled: true,
          relativeResolution: "studies",
          transform: (o) => o.replace("/pixeldata.mp4", "/rendered")
        },
        omitQuotationForMultipartRequest: true
      }
    }
  ],
  httpErrorHandler: (error) => {
    console.warn(error.status);
    console.warn("Error connecting to Casewise DICOMweb server");
  }
}; 
