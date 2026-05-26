#!/usr/bin/python
#=====================================================================
#                      Python Scripts for CitComS 
#         Preprocessing, Data Assimilation, and Postprocessing
#                  ---------------------------------
#             (c) California Institute of Technology 2007-2026
#                        ALL RIGHTS RESERVED
#=====================================================================
'''
NAME
    Mesh_Utilities.py 

SYNOPSIS
    test.py - 
       [-t]
       [-v]
       [-h]

DESCRIPTION

    Mesh_Utilities.py is a work in progress ... 

OPTIONS

    -h or --help       This help message

    -v or --verbose    Verbosely show processing steps

EXAMPLES:

    Mesh_Utilities.py -v -h
'''
#=====================================================================
#=====================================================================
# imports
import getopt, os, string, sys, math, time
from datetime import datetime as dt
import pprint

from Script_Utilities import now
from Script_Utilities import parse_control_file

import GMT_Utilities 
import PlotUtilities

#=====================================================================
# global variables
verbose = False
#=====================================================================
#=====================================================================
def main():
    '''main sequence of script actions'''

    print(dt.now(), 'Mesh_Utilities.py:')
    print(dt.now(), 'main:')

    # empty dictonary to hold script settings 
    settings = {}

    # populate the main settings dictionary with cmd line options 
    get_options( settings )

    # double check cmd line settings, 
    # compute derrived settings,
    check_settings( settings )

    # 
    # pre-process 
    # 
    
    # print all settings
    if verbose: 
        print(dt.now(), "main: settings=")
        pprint.PrettyPrinter(indent=2).pprint(settings)
        print(" ")

    if 'test_only' in list(settings.keys()) :
        print(dt.now(), 'main: test_only exit')
        sys.exit()
    
    # 
    # process 
    # 
    interpolate_to_plate_frame( settings )
 
    print(dt.now(), 'main: exit')
    sys.exit()
#=====================================================================
def usage():
    '''print a simple help message'''
    print("Please use -h for documentation")
    print(" ")
    #print __doc__ 
    print(" ")
#=====================================================================
def get_options( settings ) :
    '''process the comand line options and populate a dictionary with long option, argument key, value pairs'''

    # NOTE: 
    # The options that require cmd line arguments,
    # are postfixed with a ':' character for the short opt key,
    # and postfixed with a '=' character for the long opt value.
    #
    # example option that requires an argument:
    # options['o:'] = 'option=' 
    #
    # The long values (without the = character) 
    # are in turn used as keys for the main settings dictionary.
    # 

    # empty the dictionary
    options = {}

    # options with no arguments, general use
    options['h'] = 'help'
    options['v'] = 'verbose' 
    options['t'] = 'test_only' 
    options['f:'] = 'file=' 
    options['g:'] = 'globe_frame_mesh_prefix=' 
    options['p:'] = 'plate_frame_mesh_prefix=' 
    options['c:'] = 'citcoms_parameters=' 
 
    # more options go here

    # build the short string and long list 
    short_opts = "".join(list(options.keys()))
    long_opts = list(options.values())

    # use the getopt library
    try:
        opts, args = getopt.getopt(sys.argv[1:], short_opts, long_opts)

    except getopt.GetoptError:
        # print help information and exit:
        print("ERROR: Unknown cmd line options.\n")
        usage()
        sys.exit(2)

    # process options 
    for opt, value in opts:

        # remove prefixed '-' and '--' from opt
        opt = string.replace(opt, '-', '')

        # if short opt string given on cmd line
        # then get long value from options dictionary
        if len(opt) == 1: 
            if value == '':
                # opt has no value direct table look up
                opt = options[opt]
            else : 
                # opt needs colon for table lookup
                key = opt + ":"
                opt = options[ key ]

        # strip off any remaining '=' 
        opt = string.replace(opt, '=', '')

        # set the setting from the option and value
        settings[ opt ] = value

#=====================================================================
def check_settings( settings ):
    '''check the global settings'''

    global verbose

    if 'help' in list(settings.keys()) : 
        print(__doc__)
        sys.exit()
    
    if 'verbose' in list(settings.keys()):
        verbose = True
        # propagate verbosity to other modules
        GMT_Utilities.verbose = verbose
        PlotUtilities.verbose = verbose

    print(settings)

    # read settings from control file 
    if 'file' in list(settings.keys()) :
        parse_control_file( settings )

    # check required settings
    #if not 'time' in settings.keys() :
    #    usage()
    #    sys.exit()

    # add checks for other req. cmd line opts ... 
    # add checks / clean ups on other cmd line opts ... 

#=====================================================================
#=====================================================================
def interpolate_to_plate_frame(settings):
    '''interpolate data from globe frame to plate frame as a grd file'''

    # empty clean up list
    settings['rm_list'] = []

    # determine basic parameters of model run
    time = settings['time']
    iage = settings['iage']
    level = settings['level']

    GMT_Utilities.set_model_region(settings)

    # plate frame mesh file 
    plate_frame_prefix = settings.get('interpolate_to_plate_frame_prefix')
    if plate_frame_prefix == None:
        plate_frame_prefix = './'
    plate_frame_mesh = settings['interpolate_to_plate_frame_mesh']
    mesh_xy = os.path.join( \
        plate_frame_prefix, \
        '%(plate_frame_mesh)s.%(iage)s.xy' % vars() )
    settings['mesh_xy'] = mesh_xy

    # plate polygon boundary mask 
    mask = settings.get('interpolate_to_plate_frame_mask')
    if mask != None:
        mask_prefix = settings['overlay_gplates_xy_path']
        mask_xy = os.path.join( \
            mask_prefix, \
            '%(mask)s.0.xy' % vars() )
        # NOTE: always use iage == 0 for the mask
        settings['mask_xy'] = mask_xy

    # 1. 
    # create a grid of the globe frame citcoms data
    GMT_Utilities.set_grid_parameters(settings)
    GMT_Utilities.make_grid(settings)
    grid = settings['grid_file']
    grid_min = settings['grid_min']
    grid_max = settings['grid_max']
    grid_increment = settings['grid_increment']
    grid_ten = settings['grid_tension']

    # temporary file produced from grdtrack of mesh on grid
    track = '%(grid)s.track.xyz' % vars()

    # temporary xyz file produced from slicing out coordinates
    cut_xyz = '%(grid)s.track.cut.xyz' % vars()

    # temporary median file 
    med_xyz= '%(grid)s.track.cut.median.xyz' % vars()

    # final output grid
    grd = '%(grid)s.%(plate_frame_mesh)s.grd' % vars()


    # 2. 
    if verbose: print(dt.now(), 'interpolate_to_plate_frame: 2.')

    if settings.get('force360'):
        force_xy = '%(mesh_xy)s.force360.xy' %vars()
        cmd = "cat %(mesh_xy)s | awk '{if (($2<0) && ($4<0)) print ($1, $2 + 360, $3, $4 + 360); else if ($2<0) print ($1, $2 + 360, $3, $4); else if ($4<0) print ($1, $2, $3, $4 + 360); else print ($0)} ' > %(force_xy)s" % vars()
        if verbose: print(dt.now(), 'interpolate_to_plate_frame: cmd =', cmd)
        os.system(cmd)
        mesh_xy = force_xy

    if settings.get('force180'):
        force_xy = '%(mesh_xy)s.force180.xy' %vars()
        cmd = "cat %(mesh_xy)s | awk '{if (($2>180) && ($4>180)) print ($1, $2 - 360, $3, $4 - 360); else if ($2>180) print ($1, $2 - 360, $3, $4); else if ($4>180) print ($1, $2, $3, $4 - 360); else print ($0)} ' > %(force_xy)s" % vars()
        if verbose: print(dt.now(), 'interpolate_to_plate_frame: cmd =', cmd)
        os.system(cmd)
        mesh_xy = force_xy


    # Sample the original citcoms grid at the mesh on plate points
    cmd = 'grdtrack %(mesh_xy)s -V -Lg -: -G%(grid)s > %(track)s' % vars()
    if verbose: print(dt.now(), 'interpolate_to_plate_frame: cmd=', cmd)
    os.system(cmd)

    # 3. 
    if verbose: print(dt.now(), 'interpolate_to_plate_frame: 3.')
    # Cut out and save only three columns: lat lon field

    # select globe or plate frame coordinates 
    col_spec = '3-'
    if settings.get('globe_coordinates'):
        col_spec = '1-2,4-'
   
    cmd = 'cut -f %(col_spec)s %(track)s > %(cut_xyz)s' % vars()
    if verbose: print(dt.now(), 'interpolate_to_plate_frame: cmd=', cmd)
    os.system(cmd)


    # 4. 
    if verbose: print(dt.now(), 'interpolate_to_plate_frame: 4.')
    # reset region to user values
    region = settings.get('interpolate_to_plate_frame_region')
    settings['region'] = region
    if verbose: 
        print(dt.now(), "interpolate_to_plate_frame: region =", region)


    # 5. 
    if verbose: print(dt.now(), 'interpolate_to_plate_frame: 5.')
    # create a median file from cut file
    cmd = "blockmedian %(cut_xyz)s -V -: -I%(grid_increment)s -R%(region)s > %(med_xyz)s" % vars()
    if verbose: print(dt.now(), "interpolate_to_plate_frame: cmd =", cmd)
    os.system(cmd)


    # 6. 
    if verbose: print(dt.now(), 'interpolate_to_plate_frame: 6.')
    # create a surface grid from median file
    if grid_min != 'none' or grid_max != 'none':
        cmd = "surface %(med_xyz)s -V -: -G%(grd)s -I%(grid_increment)s -R%(region)s -T%(grid_ten)g -Ll%(grid_min)g -Lu%(grid_max)g" % vars()
    else:
        cmd = "surface %(med_xyz)s -V -: -G%(grd)s -I%(grid_increment)s -R%(region)s -T%(grid_ten)g" % vars()

    if verbose: print(dt.now(), 'interpolate_to_plate_frame: cmd =', cmd)
    os.system(cmd)


    # 7.
    if verbose: print(dt.now(), 'interpolate_to_plate_frame: 7.')
    # check for masking of grid
    if mask != None:
        # output masking grid file
        msk = '%(plate_frame_mesh)s.%(time)s.%(level)s.mask.grd' % vars()
        # filter with awk
        # | awk '{if ($2<0) print ($1, 360 + $2); else print ($0)} '
        # 

        #
        # Check for forcing of coordinates
        #
        if settings.get('force360'):
            force_xy = '%(mask_xy)s.force360.xy' %vars()
            cmd = "cat %(mask_xy)s | awk '{if ($2<0) print ($1, $2 + 360); else print ($0)} ' > %(force_xy)s" % vars()
            if verbose: print(dt.now(), 'interpolate_to_plate_frame: cmd =', cmd)
            os.system(cmd)
            mask_xy = force_xy

        if settings.get('force180'):
            force_xy = '%(mask_xy)s.force180.xy' %vars()
            cmd = "cat %(mask_xy)s | awk '{if ($2>180) print ($1, $2 - 360); else print ($0)} ' > %(force_xy)s" % vars()
            if verbose: print(dt.now(), 'interpolate_to_plate_frame: cmd =', cmd)
            os.system(cmd)
            mask_xy = force_xy


        # -N outside/edge/inside polygon boundary
        cmd = "grdmask %(mask_xy)s -V -NNaN/0/0 -M -: -G%(msk)s -I%(grid_increment)s -R%(region)s" % vars()
        if verbose: print(dt.now(), 'interpolate_to_plate_frame: cmd =', cmd)
        os.system(cmd)
        # grdmath to mask the grid
        src = grd
        grd = '%(plate_frame_mesh)s.%(time)s.%(level)s.grd' % vars()
        cmd = "grdmath -N -V %(src)s %(msk)s OR = %(grd)s" % vars()
        if verbose: print(dt.now(), 'interpolate_to_plate_frame: cmd =', cmd)
        os.system(cmd)
        settings['rm_list'] += [ msk ]

    # 8. finish up 
    if verbose: print(dt.now(), 'interpolate_to_plate_frame: 8.')

    # save the new grid file 
    settings['grid_file'] = grd

    # adjust the projection
    if settings['zone'] == 'global':
        settings['projection'] = 'M%f' % ( settings['mapwidth'] / 3 ) 

    # clean up
    settings['rm_list'] += [ track, cut_xyz, med_xyz ]

    # final clean up
    # final clean up taken care of by caller
    cmd ='rm -vrf ' + ' '.join( settings['rm_list'] )
    if verbose: print(dt.now(), 'interpolate_to_plate_frame: cmd=', cmd)
    os.system(cmd)

#=====================================================================
#=====================================================================
if __name__ == "__main__":
    main ()
#=====================================================================
#=====================================================================
