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
    parser.add_argument('-v', '--vcf_file', required=True, help='vcf files to take IGV batch snapshot on')
    parser.add_argument('-o', '--output_dir', required=False, default=os.getcwd(), help='Output directory where snapshot files will be saved. Default=current working directory')
    parser.add_argument('-r', '--reference', required=False, default='hg19', help='Reference genome to be loaded to IGV. Default=hg19')
    parser.add_argument('--view_preference', required=False, default='squish', choices=['squish', 'collapse'], help='Preference on how reads will be displayed. Default=squish')
    parser.add_argument('--sort_preference', required=False, default='strand', choices=['strand', 'base', 'position'], help='Preference on how reads will be sorted. Defulat=strand')

    parser.add_argument('--height', required=False, default=500, type=int, help='Panel height for snapshot images')
    parser.add_argument('--prefix', required=False, default='', help='Prefix for snapshot outputs. If not specified, will default to the basename of the input vcf')
    parser.add_argument('-w', '--window', required=False, default=100, type=int, help='Window size to be displayed. For example, setting w=100, will extend so that snapshot displays 100bp upstream and 100bp downstream. Default=100')
    parser.add_argument('-p', '--pair', required=False, default=1, type=int, choices=[0,1], help='If set to 1, view as pair. If set to 0, will not view as pair. Default=view as pair')
    parser.add_argument('-t', '--textfile', type=int, required=False, default=0, choices=[0,1], help='If set to 1, then input --vcf_file can take a plain text file with regions as input')
    args = vars(parser.parse_args())

    return os.path.abspath(args['vcf_file']), args['load_files'], args['output_dir'], args['reference'], args['view_preference'], args['height'], args['sort_preference'], args['prefix'], args['window'], args['pair'], args['textfile']

def execute(cmd):
    execution = subprocess.Popen(shlex.split(cmd))
    execution.wait()

    return 0

def bat_configure(vcf_file, load_files, reference, snapshot_dir, height, istextfile):
    """configures bat file by loading referene genome, bam file, and vcf file"""
    batfile = (vcf_file) + '.bat' 
    with open(batfile, 'w') as f:
        f.write('new\n') # new bat file
        f.write('genome ' + reference + '\n') # load genome
        for file in load_files:
            f.write('Load ' + file + '\n') # load bam files
        if istextfile == 0:
            f.write('Load ' + vcf_file + '\n') # load Vcf files
        f.write('maxPanelHeight ' + str(height) + '\n') # set snapshot image height
        f.write('snapshotDirectory ' + os.path.abspath(snapshot_dir) + '\n') # set up snapshot output directory

    return batfile


def position_from_vcf(vcf_file, istextfile):
    if istextfile == 0:
        for variant in vcf.Reader(filename=vcf_file):
            if re.search(string=str(variant.ALT[0]), pattern=r'\[|\]') != None:
                bp1String = variant.CHROM + ':' + str(variant.POS)
                bp2String = re.search(pattern=r'[A-Za-z0-9]+:[0-9]+', string=str(variant.ALT[0])).group(0)
                yield ( 'BND', [bp1String, bp2String])

            elif re.search(string=str(variant.ALT[0]), pattern=r'<|>') != None:
                bp1String = variant.CHROM + ':' + str(variant.POS)
                bp2String = variant.CHROM + ':' + str(variant.INFO['END'])
                yield (variant.INFO['SVTYPE'], [bp1String, bp2String])

            else:
                positionString = variant.CHROM + ':' + str(variant.POS)
                yield ('SNV', [positionString])

    else:
        with open(vcf_file, 'r') as f:
            for line in f:
                positionString = line.strip()
                yield ('SNV', [positionString])


def extend_position(snapshot_position, window): 
    """for a given snapshot position, extend and return region with flanking base pairs"""
    chromosome, position = snapshot_position.split(':')
    upstream = max(0, int(position) - window)
    downstream = int(position) + window 
    return chromosome + ':' + str(upstream) + '-' + str(downstream)


def go_to_regions(vcf_file, batfile, view_preference, sort_preference, prefix, window, pair, istextfile):
    """Once bat file is configured appends to the bat fle to take snapshots"""
    if prefix == '': # if no prefix is specified, then use vcf file base name as prefix
        vcf_prefix = re.sub(string=re.sub(string=os.path.basename(vcf_file), pattern=r'.vcf.*', repl=''), pattern=r'\.', repl='_')
    else:
        vcf_prefix = prefix
    with open(batfile, 'a') as f:
        for var_type, positions_to_snapshot in position_from_vcf(vcf_file, istextfile):        
            if len(positions_to_snapshot) == 1: # if SNV
                snapshot_region = extend_position(positions_to_snapshot[0], window)

                f.write('goto ' + snapshot_region + '\n')
                f.write('sort base\n')
                f.write(view_preference + '\n')
                if pair == 1:
                    f.write('viewaspairs\n')
                f.write('snapshot ' + vcf_prefix + '_' + var_type + '_' + str(positions_to_snapshot[0]) + '\n')
            else:
                # if variant is a structural variation need to take snapshot at the second breakpoint
                # snapshot first breakpoint
                snapshot_region_bp1 = extend_position(positions_to_snapshot[0], window)

                f.write('goto ' + snapshot_region_bp1 + '\n') 
                f.write('sort base\n') 
                f.write(view_preference + '\n')
                if pair == 1:
                    f.write('viwaspairs\n')
                f.write('snapshot ' + vcf_prefix + '_' + var_type + '_' + str(positions_to_snapshot[0]) + '_' + str(positions_to_snapshot[1]) + '_bp1' + '\n')

                # snapshot second breakpoint
                snapshot_region_bp2 = extend_position(positions_to_snapshot[1], window)

                f.write('goto ' + snapshot_region_bp2 + '\n') 
                f.write('sort base\n') 
                f.write(view_preference + '\n')
                if pair == 1:
                    f.write('viwaspairs\n')
                f.write('snapshot ' + vcf_prefix + '_' + var_type + '_' + str(positions_to_snapshot[0]) + '_' + str(positions_to_snapshot[1]) + '_bp2' + '\n')

        f.write('exit\n')

    return batfile


def run_IGV_script(batch_script, igv_jar, memMB):
    '''
    Run an IGV batch script
    '''
    import datetime
    # get the X11 Xvfb port number
    # x_serv_port = get_open_X_server()
    # print(f'\nOpen Xvfb port found on:\n{x_serv_port}\n')
    # build the system command to run IGV
    igv_command = f"xvfb-run --auto-servernum --server-num=1 /home/users/kjyi/bin/java -Xmx{memMB}m -jar {igv_jar} -b {batch_script}"
    print(f'\nIGV command is:\n{igv_command}\n')
    # get current time; command can take a while to finish
    startTime = datetime.datetime.now()
    print(f"\nCurrent time is:\n{startTime}\n")
    # run the IGV command
    print("\nRunning the IGV command...")
    execute(igv_command)
    elapsed_time = datetime.datetime.now() - startTime
    print(f"\nIGV finished; elapsed time is:\n{elapsed_time}\n")


def main():
    vcf_file, load_files, output_dir, reference, view_preference, height, sort_preference, prefix, window, pair, textfile= argument_parser()
    # create/configure batfile
    batfile = bat_configure(vcf_file, load_files, reference, output_dir, height, textfile)
    # append regions to the configured batfile
    batfile = go_to_regions(vcf_file, batfile, view_preference, sort_preference, prefix, window, pair, textfile)

    # now bat file is ready
    # run IGV batch mode without GUI display!
    run_IGV_script(batfile, '/home/users/cjyoon/tools/IGV_2.4.5/igv.jar', 4000)

if __name__ == "__main__":
    main()

