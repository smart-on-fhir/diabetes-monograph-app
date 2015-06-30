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
3. If you modified `SNPData.csv` or `DrugInfo.csv`, after doing so, you should use command below to update
	
	```
	$ python process_data.py
	```
