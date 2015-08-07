from __future__ import division
import gevent.monkey; gevent.monkey.patch_all()
import gevent
import gevent.queue
import requests
import json
from collections import defaultdict
from snps import COORDINATES
from config import GOOGLE_API_KEY


OKG = '10473108253681171589' 
CONTENT_TYPE_HEADER = {'Content-Type': 'application/json; charset=UTF-8'} 
# NOTE only google's Variant API works properly
REPOSITORIES = {
   'google': 'https://www.googleapis.com/genomics/v1beta2',
   'ncbi': 'http://trace.ncbi.nlm.nih.gov/Traces/gg',
   'ebi': 'http://193.62.52.16',
   'ensembl': 'http://grch37.rest.ensembl.org/ga4gh'
}
# signal for worker thread being done
DONE = None


def search(endpoint, repo_id, **data):
    api_base = REPOSITORIES[repo_id]
    resp = requests.post('%s/%s/search?key=%s'% (api_base, endpoint, GOOGLE_API_KEY),
            data=json.dumps(data),
            headers=CONTENT_TYPE_HEADER)
    if resp.status_code != 200:
        raise Exception('Search on %s failed with arguments: %s -- %s'% (resp.url, data, resp.text))
    else:
        return resp.json()


def matches(a, b):
    '''
    check if two genotypes (array of bases, e.g. ['AGT', 'A']) are the same 
    '''
    if len(a) != len(b):
        return False
    a = sorted(a)
    b = sorted(b)
    for i in xrange(len(a)):
        if a[i] != b[i]:
            return False 
    return True


def pct(a, b):
    '''
    percentage of a/b
    '''
    return '%.2f%%'% (a/b*100)


def execute_search(queue, *args, **kwargs):
    '''
    execute search and shuff result into queue (if there's a result)
    '''
    try:
        while True:
            resp = search(*args, **kwargs)
            queue.put(resp)
            pageToken = resp.get('nextPageToken')
            if pageToken is not None:
                kwargs['pageToken'] = pageToken 
            else:
                queue.put(DONE)
                break
    except:
        queue.put(DONE)
        pass


def search_variants(genotypes, dataset, repo_id, callSetIds=None):
    '''
    yield genotypes within a dataset

    :param genotypes: dictionary mapping a variant name to a genotype
    :yield: GAVariant
    '''
    rsids_by_coords = {}
    rsids = set()
    for rsid in genotypes:
        rsids.add(rsid)
        coord = COORDINATES[rsid]
        chrom = coord['chromosome']
        end = coord['pos']
        start = end - 1
        rsids_by_coords['%s:%s-%s'% (chrom, start, end)] = rsid

    variantset_search_resp = search('variantsets', repo_id, datasetIds=[dataset])
    variant_set_ids = [vs['id'] for vs in variantset_search_resp['variantSets']]
    # queue to receive search responses
    search_resps = gevent.queue.Queue()
    # dispatch concurrent API calls
    variant_searches = [
        gevent.spawn(execute_search,
            search_resps,
            'variants',
            variantSetIds=[vsid],
            referenceName=COORDINATES[rsid]['chromosome'],
            start=COORDINATES[rsid]['pos']-1,
            end=COORDINATES[rsid]['pos'],
            repo_id=repo_id)
        for rsid in genotypes 
        for vsid in variant_set_ids
    ] 
    num_finished = 0
    while num_finished < len(variant_searches):
        resp = search_resps.get()
        if resp == DONE:
            num_finished += 1
            continue

        for variant in resp['variants']: 
            rsid = rsids_by_coords.get('%s:%s-%s'% (
                variant['referenceName'],
                variant['start'],
                variant['end']))
            if rsid is not None:
                yield rsid, variant


def get_frequencies(variants, genotypes, population=lambda _:True):
    '''
    get allele frequencies within a population

    :param genotypes: dictionary mapping a variant name to a genotype
    :parma population: function to check if a variant call falls in the population
    :return: a dictionary, key of which are variants, values of which are
    frequencies of variants
    '''
    matched_pops = defaultdict(int)
    total_pops = defaultdict(int) 
    for rsid, variant in variants:
        ref = [variant['referenceBases']]
        alts = variant['alternateBases']
        gts = ref + alts
        for call in variant['calls']:
            if not population(call):
                continue
            total_pops[rsid] += 1
            # convert genotype indices into genotypes
            gt = [gts[i] for i in call['genotype']]
            if matches(gt, genotypes[rsid]):
                matched_pops[rsid] += 1 
                match_rate = matched_pops[rsid] / total_pops[rsid]
                
    return {rsid: pct(matched_pops[rsid], total_pops[rsid])
            for rsid in genotypes
            if total_pops[rsid] != 0}
