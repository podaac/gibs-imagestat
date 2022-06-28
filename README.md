# gibs-imagestat
Calculate statistics on GIBS hosted imagery

## Initial Implementation Use Cases & Exchange Data Specification
 ### 1. Imagery Spatial Summary Statistics – single (current) Time Step. 
**Input Parameters** (from Worldview UI passed to Imagery Analysis tool for execution):
- Spatial Bounding Box: Lat_min, Lat_max, Lon_min, Lon_max  (in -90 to 90, -180 to 180 format)
- Time range: Time_min, Time_max (to keep this general, but for this particular use case just the current time step from the Worldview data picker will be passed into Imagery Analysis tool for imagery value extraction and analysis.  ie. Time_min = Time_max
- Satellite Dataset(s) shortname:  list of one or more imagery dataset shortnames selected and being visualized in Worldview for imagery value extraction/analysis in Imagery Analysis tool
- Analysis Type: “Spatial summary statistics” (standard label that we will define to describe the analysis to be conducted for handling by both Imagery Analysis tool and Worldview).
- Analysis sub-Type: “Time Step” (standard label that we will define to describe the analysis to be conducted for handling by both Imagery Analysis tool and Worldview)
- Analysis shortname: “spatial_summary_stats”

For this use case “Spatial summary – Time Step” Imagery Analysis tool will extract values for each specified imagery dataset for just the single time over the spatial domain defined.  Imagery Analysis tool will then compute and return mean, variance, standard error and pixel count statistics, plus a frequency distribution of geophysical values for each specified imagery dataset again for just the single time for the spatial domain specified.

**Output Data** (passed from Imagery Analysis tool to Worldview -UI for display):
- Numerical statistical summary data: Spatial mean, variance, standard error and pixel count for each dataset for tabular output.
- Summary plot data: frequency distribution of geophysical values for each dataset for charting as one or more histograms.

### 2. Imagery Spatial Summary Statistics – Time Range (summary over multiple time steps of imagery).
**Input Parameters** (from Worldview UI passed to Imagery Analysis tool for execution):
- Spatial Bounding Box: Lat_min, Lat_max, Lon_min, Lon_max  (in -90 to 90, -180 to 180 format)
- Time range: Time_min, Time_max (user to specify a start and end time range over which the spatio-temporal summary statistics will be computed)
- Satellite Dataset(s) shortname:  list of one or more imagery dataset shortnames selected and being visualized in Worldview for imagery value extraction/analysis in Imagery Analysis tool
- Analysis Type: “Spatial summary statistics”
- Analysis sub-Type: “Time Range”
- Analysis shortname: “spatiotemporal_summary_stats”

For this use case “Spatial summary – Time Range” Imagery Analysis tool will extract values for each specified imagery dataset for the spatial domain defined for the range of times.  Imagery Analysis tool will then compute and return a single set of mean, variance, standard error and pixel count statistics, plus a frequency distribution of geophysical values for each specified imagery dataset again across time for the spatial domain specified.

**Output Data** (passed from Imagery Analysis tool to Worldview -UI for display):
- Numerical statistical summary data: Spatial mean, variance, standard error and pixel count that integrated across time for each dataset for tabular output.
- Summary plot data: frequency distribution of geophysical values for each dataset for charting as one or more histograms.



