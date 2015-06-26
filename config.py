# OAuth2 settings for communicating with clinical server
CLINICAL = {
    'client_id': '9af27c81-077d-4cf2-857a-f6d08aa040e5',
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
