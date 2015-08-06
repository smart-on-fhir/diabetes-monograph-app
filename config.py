# OAuth2 settings for communicating with clinical server
CLINICAL = {
    'client_id': '87ceed4d-02d5-4aa6-ba9b-61e17fb1d803',
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
# choose a secret key here
SECRET_KEY = 'hello, world!'
GOOGLE_API_KEY = 'AIzaSyB01GeX_HiuZbHCkZ-P5hJ7yUHVkwFS07Q'
