# IGV Snapshotter
Given VCF and Bam files and other input files (BED file, other vcf files, gtf files, etc), will load all files into IGV track, and will take snapshot and save image as a command line without having a GUI IGV session opened. 

```bash
$ python vcf2snapshot.py -h
usage: vcf2snapshot.py [-h] -l LOAD_FILES [LOAD_FILES ...] -v VCF_FILE
                       [-o OUTPUT_DIR] [-r REFERENCE]
                       [--view_preference {squish,collapse}]
                       [--sort_preference {strand,base,position}]
                       [--height HEIGHT] [--prefix PREFIX] [-w WINDOW]
                       [-p {0,1}] [-t {0,1}]

Takes in vcf file, creates bat files for IGV batch snapshot, and takes
snapshot without opening an IGV window by utilizing xvfb

optional arguments:
  -h, --help            show this help message and exit
  -l LOAD_FILES [LOAD_FILES ...], --load_files LOAD_FILES [LOAD_FILES ...]
                        Bam/bed.gz files to load
  -v VCF_FILE, --vcf_file VCF_FILE
                        vcf files to take IGV batch snapshot on
  -o OUTPUT_DIR, --output_dir OUTPUT_DIR
                        Output directory where snapshot files will be saved.
                        Default=current working directory
  -r REFERENCE, --reference REFERENCE
                        Reference genome to be loaded to IGV. Default=hg19
  --view_preference {squish,collapse}
                        Preference on how reads will be displayed.
                        Default=squish
  --sort_preference {strand,base,position}
                        Preference on how reads will be sorted. Defulat=strand
  --height HEIGHT       Panel height for snapshot images
  --prefix PREFIX       Prefix for snapshot outputs. If not specified, will
                        default to the basename of the input vcf
  -w WINDOW, --window WINDOW
                        Window size to be displayed. For example, setting
                        w=100, will extend so that snapshot displays 100bp
                        upstream and 100bp downstream. Default=100
  -p {0,1}, --pair {0,1}
                        If set to 1, view as pair. If set to 0, will not view
                        as pair. Default=view as pair
  -t {0,1}, --textfile {0,1}
                        If set to 1, then input --vcf_file can take a plain
                        text file with regions as input
```

