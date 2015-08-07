from flask import Flask, render_template, request, jsonify, url_for, session, redirect
import json
from functools import wraps
from urllib import urlencode
import snps
import freq
import ga4gh
import config

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

SNP_TRANSLATION_FNAME = 'snps.sorted.txt.gz'
YEAR = 31536000
GENOTYPES = {snp: snp_data['Code'] for snp, snp_data in snps.DATA.iteritems()} 


def cache(max_age):
    def decorator(view_func):
        @wraps(view_func)
        def decorated(*args, **kwargs):
            resp = view_func(*args, **kwargs)
            resp.cache_control.max_age = max_age
            return resp
        return decorated
    return decorator 


@app.route('/prompt-select-sample')
def prompt_select_sample():
    return render_template('select.html')


@app.route('/select-sample')
def select_sample():
    launch_args = json.loads(session['launch_args'])
    launch_args['selected'] = ''
    session['sample_id'] = request.args['sample_id']
    return redirect('%s?%s'% (
        url_for('launch'),
        urlencode(launch_args)))


@app.route('/')
def index():
    return render_template('index.html', sample_id=session['sample_id'])


@app.route('/fhir-app/launch.html')
def launch():
    if 'selected' not in request.args:
        session['launch_args'] = json.dumps(request.args)
        return redirect(url_for('prompt_select_sample'))

    return render_template(
            'launch.html',
            client_id=config.CLINICAL['client_id'],
            scope=' '.join(config.CLINICAL['scopes']),
            redirect_uri=config.CLINICAL['redirect_uri']) 


@app.route('/snps/<sample_id>')
@cache(3600)
def get_snps(sample_id):
    '''
    return sequences mentioned in SNPData.csv
    '''
    variants = ga4gh.search_variants(
            GENOTYPES,
            ga4gh.OKG,
            callSetIds=[sample_id],
            repo_id='google')
    snps = {}
    for rsid, variant in variants:
        gts = [variant['referenceBases']]
        gts.extend(variant['alternateBases']) 
        for call in variant['calls']:
            if call.get('callSetId') != sample_id:
                continue
            snps[rsid] = [gts[i] for i in call['genotype']]
    return jsonify(snps)
            

@app.route('/snp-data')
@cache(YEAR)
def get_snp_data():
    '''
    render SNPData.csv as json
    '''
    return jsonify(snps.DATA)


@app.route('/drug-info')
@cache(YEAR)
def get_drug_info():
    '''
    render DrugInfo.csv as json
    '''
    return jsonify(snps.DRUG_INFO) 


@app.route('/frequencies')
@cache(YEAR)
def get_frequencies():
    return jsonify(freq.FREQUENCIES) 


@app.route('/callsets')
def get_callsets(): 
    vset_search = ga4gh.search('variantsets', datasetIds=[ga4gh.OKG], repo_id='google') 
    vset_id = vset_search['variantSets'][0]['id']
    callset_search = ga4gh.search(
            'callsets',
            variantSetIds=[vset_id],
            repo_id='google',
            pageSize=10,
            **request.args)
    return jsonify(callset_search)


if __name__ == '__main__':
    app.run(port=8000, debug=True)
