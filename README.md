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

# gibs-imagestat
The purpose of this application is to generate statistics from the GIBS imagery files. The API maps the GIBS layers to its corresponding color map and generates the source data values. The output JSON file is then used to generate statistics. 

## Parameters
The following is a list of accepted parameters and information about them. 

#### timestamp - string
The date that information will be pulled from. When multiple dates are pulled it is used as the start date. This parameter is required. e.g. '2016-06-09T00:00:00Z'

#### end_timestamp - string 
Can be ignored for a single date. Acts as an end date when data from multiple dates are pulled. - e.g. 2016-06-09T00:00:00Z 

#### _type - string 
Allows you to pick between three types of data pull. Use 'date' for a single date, 'range' for a summary of a range, 'series' for data from a sample of dates within a range. e.g. 'date'

#### steps - integer 
This allows you to set the number of days selected within a given range or series. Use '1' for just the start and end date, '2' for start date, end date and middle date, etc.. e.g. '1' 

#### layer - string
Layer to be pulled from gibs api. e.g. 'GHRSST_L4_MUR_Sea_Surface_Temperature'

#### colormap - string
Colormap to use to decipher layer. e.g. 'GHRSST_Sea_Surface_Temperature.xml', 

#### _scale - integer
Currently unused.

#### bbox - string
Bounding box of latitude and longitude. For whole earth use '-90,-180,90,180'. e.g. '-90,-180,90,180'

#### bins - string
Number of bins to used in returned histogram. e.g. 10

## Example calls with preview
Note the 'raw' field is also returned by the api but it not shown here for readability as it contains all the raw data from the days selected.

#### api 'date' request: 
http://localhost:9000/get_stats?timestamp=2016-06-09T00:00:00Z&bins=10&format=json&layer=AIRS_L2_Cloud_Top_Height_Day&colormap=AIRS_Cloud_Top_Height.xml&bbox=-90,-180,90,180

preview:
- median 4.38
- mean 5.28590618816008
- max 14.94
- min 0
- stdev 3.4770038986513576
- hist [['0.06', '14155'], ['1.548', '33573'], ['3.036', '23432'], ['4.524', '15970'], ['6.012', '14780'], ['7.499999999999999', '12397'], ['8.988000000000001', '9070'], ['10.476', '7156'], ['11.964', '4988'], ['13.452', '2436']]


#### api 'range' request: 
http://localhost:9000/get_stats?_type=range&timestamp=2016-06-09T00:00:00Z&end_timestamp=2016-06-19T00:00:00Z&steps=5&bins=10&format=json&layer=GHRSST_L4_MUR_Sea_Surface_Temperature&colormap=GHRSST_Sea_Surface_Temperature.xml&bbox=-90,-180,90,180

preview:
- mean 17.395363124119577
- median 19.5
- max 32.0
- min -0.0
- stdev 10.077515383483478
- stderr 0.010580175057874699
- hist [['0.0', '120170'], ['3.2', '59597'], ['6.4', '74991'], ['9.600000000000001', '65541'], ['12.8', '60379'], ['16.0', '68958'], ['19.200000000000003', '79530'], ['22.400000000000002', '100380'], ['25.6', '155301'], ['28.8', '122391']]


#### api 'series' request: 
http://localhost:9000/get_stats?_type=series&timestamp=2016-06-09T00:00:00Z&end_timestamp=2017-06-09T00:00:00Z&steps=12&bins=10&format=json&layer=GHRSST_L4_MUR_Sea_Surface_Temperature&colormap=GHRSST_Sea_Surface_Temperature.xml&bbox=-90,-180,90,180

preview:
- mean {'2016-06-09T00:00:00Z': 17.32474322754396, '2016-07-09T00:00:00Z': 17.665906548206642, '2016-08-08T00:00:00Z': 17.728115451343935, '2016-09-07T00:00:00Z': 17.244833381959328, '2016-10-07T00:00:00Z': 16.980553890382172, '2016-11-06T00:00:00Z': 16.71904675809654, '2016-12-06T00:00:00Z': 16.50353370262353, '2017-01-05T00:00:00Z': 16.410877542257097, '2017-02-04T00:00:00Z': 16.431548467569495, '2017-03-06T00:00:00Z': 16.532497842554413, '2017-04-05T00:00:00Z': 16.66627242908261, '2017-05-05T00:00:00Z': 16.951879966321105, '2017-06-04T00:00:00Z': 17.210895698447306}
- median {'2016-06-09T00:00:00Z': '19.35', '2016-07-09T00:00:00Z': '19.65', '2016-08-08T00:00:00Z': '19.65', '2016-09-07T00:00:00Z': '18.9', '2016-10-07T00:00:00Z': '18.6', '2016-11-06T00:00:00Z': '18.6', '2016-12-06T00:00:00Z': '18.9', '2017-01-05T00:00:00Z': '19.05', '2017-02-04T00:00:00Z': '19.05', '2017-03-06T00:00:00Z': '19.05', '2017-04-05T00:00:00Z': '19.05', '2017-05-05T00:00:00Z': '19.05', '2017-06-04T00:00:00Z': '19.5'}
- max {'2016-06-09T00:00:00Z': 32.0, '2016-07-09T00:00:00Z': 32.0, '2016-08-08T00:00:00Z': 32.0, '2016-09-07T00:00:00Z': 32.0, '2016-10-07T00:00:00Z': 32.0, '2016-11-06T00:00:00Z': 32.0, '2016-12-06T00:00:00Z': 32.0, '2017-01-05T00:00:00Z': 31.65, '2017-02-04T00:00:00Z': 31.8, '2017-03-06T00:00:00Z': 32.0, '2017-04-05T00:00:00Z': 31.65, '2017-05-05T00:00:00Z': 32.0, '2017-06-04T00:00:00Z': 32.0}
- min {'2016-06-09T00:00:00Z': 0, '2016-07-09T00:00:00Z': 0, '2016-08-08T00:00:00Z': 0, '2016-09-07T00:00:00Z': 0, '2016-10-07T00:00:00Z': 0, '2016-11-06T00:00:00Z': 0, '2016-12-06T00:00:00Z': 0, '2017-01-05T00:00:00Z': 0, '2017-02-04T00:00:00Z': 0, '2017-03-06T00:00:00Z': 0, '2017-04-05T00:00:00Z': 0, '2017-05-05T00:00:00Z': 0, '2017-06-04T00:00:00Z': 0}
- stdev {'2016-06-09T00:00:00Z': 10.15225326173492, '2016-07-09T00:00:00Z': 9.762619448287914, '2016-08-08T00:00:00Z': 9.686404881121135, '2016-09-07T00:00:00Z': 9.873811359202964, '2016-10-07T00:00:00Z': 10.084375552147325, '2016-11-06T00:00:00Z': 10.164998448092403, '2016-12-06T00:00:00Z': 10.430839441428844, '2017-01-05T00:00:00Z': 10.334445977645107, '2017-02-04T00:00:00Z': 10.479286537902569, '2017-03-06T00:00:00Z': 10.642235138541267, '2017-04-05T00:00:00Z': 10.67460649311405, '2017-05-05T00:00:00Z': 10.532436896027676, '2017-06-04T00:00:00Z': 10.131610724391171}
- stderr 0.007240811223997395
- hist [['0.0', '303030'], ['3.2', '148094'], ['6.4', '154982'], ['9.600000000000001', '135103'], ['12.8', '124583'], ['16.0', '142251'], ['19.200000000000003', '165566'], ['22.400000000000002', '223174'], ['25.6', '380157'], ['28.8', '223612']]




