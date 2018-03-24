"""IGV screenshot of regions indicated by vcf file. 
This script will create IGV batch file from a given vcf, 
load other miscellaneous files including bam/vcf/bed files along with reference genome

This script runs on command line without needing to open an X11 to run IGV batch script.

January 30 2018 Jongsoo Yoon (cjyoon@kaist.ac.kr)
"""
import os
import sys
import vcf
import argparse
import subprocess
import shlex
import re

def argument_parser():
    parser = argparse.ArgumentParser(description='Takes in vcf file, creates bat files for IGV batch snapshot, and takes snapshot without opening an IGV window by utilizing xvfb')
    parser.add_argument('-l', '--load_files', required=True, nargs='+', help='Bam/bed.gz files to load')
    parser.add_argument('-o', '--output_dir', required=False, default=os.getcwd(), help='Output directory where snapshot files will be saved. Default=current working directory')
    parser.add_argument('-r', '--reference', required=False, default='hg19', help='Reference genome to be loaded to IGV. Default=hg19')
    parser.add_argument('-p', '--prefix', required=True, help='Prefix to be added to the bat file')

    args = vars(parser.parse_args())

    return args['load_files'], args['output_dir'], args['reference'], args['prefix']

def execute(cmd):
    execution = subprocess.Popen(shlex.split(cmd))
    execution.wait()

    return 0

def bat_configure(load_files, reference, output_dir, prefix):
    """configures bat file by loading referene genome, bam file, and vcf file"""
    batfile = prefix  + '.bat' 
    with open(batfile, 'w') as f:
        f.write('new\n') # new bat file
        f.write('genome ' + reference + '\n') # load genome
        for file in load_files:
            f.write('Load ' + file + '\n') # load bam files
        #f.write('maxPanelHeight ' + str(height) + '\n') # set snapshot image height
        #f.write('snapshotDirectory ' + os.path.abspath(snapshot_dir) + '\n') # set up snapshot output directory

    return batfile



def main():
    load_files, output_dir, reference, prefix = argument_parser()
    # create/configure batfile
    batfile = bat_configure(load_files, reference, output_dir, prefix)

if __name__ == "__main__":
    main()

