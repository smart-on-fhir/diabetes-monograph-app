### Genomics Advisor (adapted from [Diabetes Monograph](https://github.com/smart-on-fhir/diabetes-monograph-app))
### Usage
1. Install dependencies

	```
	$ pip install -r requirements.txt
	```

2. Run the server locally with

	```
	# WSGI object is web:app
	$ python web.py
	```
3. If you modified one of `SNPData.csv` and `DrugInfo.csv` or you wish to update comparison between genotypes in these two files and data from 1000 Genomes, you should use command below to update your changes. Note that this requires you to modify config.py and set `GOOGLE_API_KEY` to your API key, because `load_data.py` relies on Google Genomics API for getting data from 1000 Genomes. Currently we only support Goolge Genomics because other implementations of *GA4GH*'s *Variant* API haven't conformed fully to the *GA4GH*'s documentations yet.
	
	```
	$ python load_data.py
	```
