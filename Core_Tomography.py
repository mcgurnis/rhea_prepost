#!/usr/bin/python
#=====================================================================
#                      Python Scripts for CitComS 
#         Preprocessing, Data Assimilation, and Postprocessing
#                  ---------------------------------
#             (c) California Institute of Technology 2007
#                        ALL RIGHTS RESERVED
#=====================================================================
'''A set of functions for working with various tomography models.

This module has functions to read and process various tomography models.

Most functions take a dictionary of arguments to pass and adjust paramters.
'''
#=====================================================================
#=====================================================================
# imports
import getopt, os, string, sys, math, time, pprint
from datetime import datetime as dt

from Core_Util import now
#=====================================================================
#=====================================================================
# global variables
verbose = False
#=====================================================================
#=====================================================================
def S20RTS_to_xyz( args ):
    '''Read the S20RTS model for a specific depth, generate an .xyz file; 

Required arguments:
 args['depth'] = depth of S20RTS model to make xyz file for
 args['xyz'] = output filename
 
Optional arguments:
 args['resolution'] = resolution of lat lon spacing in the final xyz file
 default is 1.0

Output arguments:
 none

Return value:
 xyz file; naming convetion is: S20RTS.sph.depth.xyz
'''

    # settings from caller 
    depth = args['depth']
    if depth.endswith('km'): depth = depth[:-2]

    # resolution in lat lon of file
    if args.get('resolution') : 
        isp = args['resolution'] 
    else:
        isp = 1.0

    # the base model file name
    tomography_model = 'S20RTS.sph'

    # temporary working file 
    raw_file = tomography_model.replace('.sph', '.raw')

    # final output file name, generated and returned by this function
    #xyz = tomography_model + '.' + depth + '.xyz'
    xyz = args['xyz']

    # remove any pre-existing generated raw file;
    if os.path.exists(raw_file):
        cmd = 'rm -rfv %(raw_file)s' % vars()
        if verbose: print(dt.now(), "S20RTS_to_xyz: cmd =", cmd)
        os.system(cmd)

    # call to read the model for a specific depth
    #    Calculate the spline basis functions at a regular grid
    cmd = './depmaphj_jr <<END > /dev/null\n'
    cmd += '%(tomography_model)s\n' % vars()
    cmd += '%(depth)s\n' % vars()
    cmd +='END'

    if verbose: print(dt.now(), "S20RTS_to_xyz: cmd =", cmd)
    os.system(cmd)

    if not os.path.exists(raw_file):
        msg = 'File not found: %(file)s; "depmaphj_jr may have failed"'
        raise Exception(msg)

    # These settings come directly from S20RTS code plmap:
    # #-- spherical harmonics
    # # -- (lmin=1: takes out spherical average)
    lmin = '1'
    lmax = '20'

    # NOTE: former hard coded value ; now a parameter passed in args
    # isp = '1' # this values controls the lat lon spacing of the xyzfile
    
    xmin = '-180'

    # call to process the raw file
    cmd = './raw2xyz_jr <<END > /dev/null\n'
    cmd += '%(raw_file)s\n' % vars()
    cmd += '%(xyz)s\n' % vars()
    cmd += '%(isp)s\n' % vars()
    cmd += '1.00\n' % vars()
    cmd += '%(lmin)s %(lmax)s\n' % vars()
    cmd += '%(xmin)s\n' % vars()
    cmd +='END'

    if verbose: print(dt.now(), "S20RTS_to_xyz: cmd =", cmd)
    os.system(cmd)

    if not os.path.exists(xyz):
        msg = 'File not found: %(xyz)s; "raw2xyz_jr may have failed"'
        raise Exception(msg)

    return xyz
#=====================================================================
def find_grand_tomography_file(args):
    '''parse a set of processed Grand Tomography model files given in 
args['file_prefix'], and return the filename that matches the depth 
given in args['depth'].

Required arguments:
 args['depth'] = depth to search for
 args['file_prefix'] = prefix of files names to search
 
Output arguments:
 none

Output arguments:
 args['xyz_file'] = name of xyz file found

Return value:
 none
'''
    # requested depth 
    d = args['depth']
    if verbose: print(dt.now(), 'find_grand_tomography_file: depth=', d)

    # prefix for file names 
    if not args.get('file_prefix'):
        msg = 'Must set "file_prefix=string" in control file'
        raise ValueError(msg)
    else : 
        prefix = args.get('file_prefix')

    import glob
    str =  prefix + '*'
    list = glob.glob( str )
    print(dt.now(), 'find_grand_tomography_file: str =', str)
    print(dt.now(), 'find_grand_tomography_file: list =', list)

    for f in list:
        # query original grid for -I values
        cmd = 'head -1 %(f)s' % vars()
        pipe = os.popen(cmd)
        line = pipe.readline()
        pipe.close()
        (min, max) = line.split()
        if verbose: print(dt.now(), 'find_grand_tomography_file: %(f)s: min/max = %(min)s %(max)s' % vars())
 
        if float(min) < float(d) <= float(max): 
            if verbose: print(dt.now(), 'find_grand_tomography_file: file =', f)
            # copy file 
            tmp = f + '.tmp.xyz' 
            cmd = 'cp -v %(f)s %(tmp)s' % vars()
            os.system(cmd)
            if verbose: print(dt.now(), "find_grand_tomography_file: cmd =", cmd)

            # set file 
            args['xyz_file'] = tmp

            # return file
            return tmp

    # file not found, raise exception   
    msg = 'ERROR: no tomography file found'
    raise ValueError(msg)

#=====================================================================
#=====================================================================
def test_S20RTS():
    '''test reading the S20RTS model for a few resolutions, over all valid depths'''

    dict = {} 


    res_list = ['1.0', '0.5', '0.1']

    # depth_list = range(100,200,100) short list to test 
    depth_list = range(100,2900,100) # full list for production

    # loop over resolutions 
    for r in res_list: 

        # loop over depths 
        for d in depth_list:

            xyz = 'S20RTS.sph_at_res%(r)s_depth%(d)s.xyz' % vars()

            dict['resolution'] = r
            dict['depth'] = str(d)
            dict['xyz'] = xyz 

            print(dt.now(), 'test_S20RTS: resolution = %(r)s' % vars())
            print(dt.now(), 'test_S20RTS: depth = %(d)s' % vars())
            print(dt.now(), 'test_S20RTS: xyz = %(xyz)s' % vars())

            # create xyz file 
            S20RTS_to_xyz(dict) 

#=====================================================================
def test( argv ):
    '''self test'''
    global verbose
    verbose = True 

    print(dt.now(), 'test:')

    model_name = argv[1]

    if model_name == 'S20RTS':
        test_S20RTS()

#=====================================================================
#=====================================================================
if __name__ == "__main__":
    import Core_Tomography

    if len( sys.argv ) > 1:
        # process sys.arv as file names for testing 
        test( sys.argv )
    else:
        # print module documentaiton and exit
        help(Core_Tomography)
#=====================================================================
#=====================================================================
