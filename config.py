# OAuth2 settings for communicating with clinical server
CLINICAL = {
    'client_id': '0d3665bd-0951-4737-bc2c-b20142ed6dcb',
    'redirect_uri': 'http://localhost:8000/',
    'scopes': [
        'launch',
        'launch/patient',
        'launch/encounter',
        'patient/*.read',
        'user/*.*',
        'openid',
        'profile'
    ]
}
# OAuth2 settings for communicating with genomic server
GENOMICS = {
    'client_id': '28c8949f-8887-4d2a-b270-74a189cf4ba9',
    'redirect_uri': 'http://localhost:8000/recv-redirect',
    'scopes': ['user/Sequence.read', 'user/Patient.read'],
    'oauth_base': 'http://genomics-advisor.smartplatforms.org:5000/auth',
    'api_base': 'http://genomics-advisor.smartplatforms.org:5000/api'
}
# choose a secret key here
SECRET_KEY = 'hello, world!'
GOOGLE_API_KEY = 'AIzaSyB01GeX_HiuZbHCkZ-P5hJ7yUHVkwFS07Q'
