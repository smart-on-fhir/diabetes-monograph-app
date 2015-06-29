'''
Read data from SNPData.csv, process them, and output snps.py for use later
'''
from pysam import TabixFile, asTuple
import csv

snps = {}
with open('SNPData.csv') as src:
    disease = None
    for row in csv.DictReader(src):
        if row['Chromosome'] is None:
            disease = row['SNP']
            continue
        row['disease'] = disease[0:-1]
        snps[row['SNP']] = row 

with open('DrugInfo.csv') as src:
    drug_info = {row['SNP']: row for row in csv.DictReader(src)} 

if __name__ == '__main__':
    f = TabixFile('snps.sorted.txt.gz', parser=asTuple())
    
    snp_table = {}
    for row in f.fetch():
        _, snp, chrom, pos = row
        if snp in snps or snp in drug_info:
            snp_table[snp] = {
                'chromosome': chrom,
                'pos': int(pos)
            }
    
    with open('snps.py', 'w') as dump:
        dump.write("'''\nAuto-generated from SNPData.csv. Don't touch me.\n'''\n")
        dump.write('COORDINATES = %s\n'% snp_table)
        dump.write('DATA = %s\n'% snps)
        dump.write('DRUG_INFO = %s\n'% drug_info)
