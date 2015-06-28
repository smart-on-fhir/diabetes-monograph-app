from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from urllib import urlencode
import pickle
from datetime import datetime, timedelta
import requests
from pysam import asTuple, TabixFile
from snps import SNPS
from config import CLINICAL, GENOMICS, SECRET_KEY

app = Flask(__name__)
app.secret_key = SECRET_KEY
SNP_TRANSLATION_FNAME = 'snps.sorted.txt.gz'


def call_api(url, args={}):
    # who even uses xml..
    args['_format'] = 'json'
    resp = requests.get(
            '%s%s?%s'% (GENOMICS['api_base'], url, urlencode(args)),
            headers={'Authorization': 'Bearer %s'% session['access_token']})
    return resp.json()


@app.route('/')
def index():
    # expiration date of access token for genomics api
    token_expires_at = session.get('token_expires_at')
    if token_expires_at is None or pickle.loads(token_expires_at) <= datetime.now():
        # token expired
        return redirect(url_for('prompt_genomics_auth'))
    return render_template('index.html') 


@app.route('/fhir-app/launch.html')
def launch():
    return render_template(
            'launch.html',
            client_id=CLINICAL['client_id'],
            scope=' '.join(CLINICAL['scopes']),
            redirect_uri=CLINICAL['redirect_uri']) 


@app.route('/prompt-genomics-auth')
def prompt_genomics_auth():
    redirect_args = {
        'client_id': GENOMICS['client_id'],
        'redirect_uri': GENOMICS['redirect_uri'],
        'scope': ' '.join(GENOMICS['scopes']),
        'response_type': 'code'
    }
    return redirect('%s/authorize?%s'% (GENOMICS['oauth_base'], urlencode(redirect_args))) 


@app.route('/recv-redirect')
def recv_genomics_auth_redirect():
    # exchange code for access token
    exchange_data = {
        'code': request.args['code'],
        'grant_type': 'authorization_code',
        'client_id': GENOMICS['client_id'],
        'redirect_uri': GENOMICS['redirect_uri']
    }
    exchange_resp = requests.post('%s/token'% GENOMICS['oauth_base'], data=exchange_data)
    exchanged = exchange_resp.json()
    session['access_token'] = exchanged['access_token']
    session['token_expires_at'] = pickle.dumps(datetime.now()+timedelta(seconds=exchanged['expires_in']))

    # prompt user to select a patient, which we will use in our analysis
    patient_bundle = call_api('/Patient')
    patients = [{'name': to_full_name(pt['content']['name'][0]), 'id': pt['id'].split('/')[-1]}
            for pt in patient_bundle['entry']]
    return render_template('get_patient.html', patients=patients)


@app.route('/select-patient/<pid>')
def select_patient(pid):
    session['pid'] = pid
    return redirect(url_for('index')) 


@app.route('/snps')
def get_snps():
    '''
    return sequences mentioned in SNPData.csv
    '''
    coords = map(make_coord_string, SNPS.values())
    search_args = {
        'coordinate': ','.join(coords),
        'patient': session['pid']
    }
    seq_bundle = call_api('/Sequence', search_args) 
    seqs = (entry['content'] for entry in seq_bundle['entry'])
    translation_f = TabixFile(SNP_TRANSLATION_FNAME, parser=asTuple()) 
    return jsonify({
        get_rsid(translation_f, seq): seq['observedSeq']
        for seq in seqs
    })


def make_coord_string(coordinate):
    chrom = coordinate['chromosome']
    pos = coordinate['pos']
    start = pos - 1
    end = pos + 1
    return '%s:%s-%s'% (chrom, start, end) 


def to_full_name(name):
    '''
    convert a FHIR name type into fullname
    '''
    if 'text' in name:
        return name['text']

    family = ' '.join(name.get('family', []))
    given = ' '.join(name.get('given', []))
    return ' '.join((given, family))


def get_rsid(translation_f, seq):
    '''
    get rsid of a sequence
    '''
    _, rsid, _, _ = translation_f.fetch(
        str(seq['chromosome']),
        seq['startPosition']-1,
        seq['endPosition']+1).next()
    return rsid


if __name__ == '__main__':
    app.run(port=8000, debug=True)
