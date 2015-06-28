'''
Read data from SNPData.csv, process them, and output snps.py for use later
'''
from pysam import TabixFile, asTuple
import csv

snps = set(row['SNP'] for row in csv.DictReader(open('SNPData.csv'))
        if row['Chromosome'] is not None)

if __name__ == '__main__':
    f = TabixFile('snps.sorted.txt.gz', parser=asTuple())
    
    snp_table = {}
    for row in f.fetch():
        _, snp, chrom, pos = row
        if snp in snps:
            snp_table[snp] = {
                'chromosome': chrom,
                'pos': int(pos)
            }
    
    with open('snps.py', 'w') as dump:
        dump.write("'''\nAuto-generated from SNPData.csv. Don't touch me.\n'''\n")
        dump.write('SNPS = %s'% snp_table)
