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
    Script_Utilities.py 

SYNOPSIS
    A set of general purpose functions common to several scripts.
'''
#=====================================================================
#=====================================================================
# imports
import getopt, os, string, sys, math, time, subprocess
import datetime
import pprint
#=====================================================================
#=====================================================================
# global variables
verbose = False
#=====================================================================
#=====================================================================
def now():
    '''redefine now() with short format yyyy-mm-dd hh:mm:ss'''
    return str(datetime.datetime.now())[:19]
#=====================================================================
#=====================================================================
def parse_control_file( settings ):
    '''Parse a key=value style control file, and return a dictionary of those settings.'''

    # section flag 
    section = None
    num_sections = 0

    filename = settings.get('file')
    file = open(filename)

    try : 
        # read into a list of lines
        lines = file.read().splitlines()
    finally:
        file.close()

    if verbose:
        print(dt.now(), 'parse_control_file: read: %(filename)s' % vars())

    # read
    for line in lines:

        # skip blank lines
        if string.strip(line) == '':
            continue # to next line in control file

        # skip lines starting with '#'
        if line.startswith('#'):
            continue # to next line in control file

        # re-set the section flag on end of section lines
        if line.startswith('[END') : 
            section = None
            if verbose:
                print(dt.now(), 'parse_control_file: END section = ', section)

            continue # to next line in control file

        # process section boundary into new key 
        if line.startswith('[') :
            line = line.rstrip()
            line = line.replace('[','')
            line = line.replace(']','')
            section = line
            num_sections += 1
            if verbose:
                print(dt.now(), 'parse_control_file: section = ', section)

            # establish an empty map for this section
            settings[section] = {}

            continue # to next line in control file

        # key/value pairs can be seperated by whitespaces
        opt = line.rstrip()
        opt = opt.replace(' ','') # remove any spaces padding

        # isolate the key and value
        (key,val) = string.split(opt, '=')

        if verbose:
            print(dt.now(), 'parse_control_file: key , val = ',key,',',val)

        if (section) :
            # this key val pair is part of a figure spec
            settings[section][key] = val

        else : 
            # this key val pair is a general setting
            settings[key] = val

    if verbose:
        print(dt.now(), 'parse_control_file: settings =\n', \
            pprint.PrettyPrinter(indent=2).pprint(settings))
#=====================================================================
#=====================================================================
#=====================================================================
def animate( settings ):
    '''Animate a sequece of image files into a .gif file'''

    # test input 
    if settings.get('inp_list') == None:
        raise ValueError('No image files given.')   

    # defaults
    loop = 1
    delay = 100
    rotate = False
    inp_list = None 
    gif_list = [] 
    animation = 'animation.gif'

    # re-set defaults
    if settings.get('loop') != None:
       loop = int ( settings.get('loop') )

    if settings.get('delay') != None:
       delay = int( settings.get('delay') )

    if settings.get('rotate') != None:
       rotate = True

    if settings.get('animation') != None:
        animation = settings.get('animation')

    # test each input file 
    for file in settings.get('inp_list'):
        # check for file existance
        if not os.path.exists(file):
            raise ValueError('File "%(file)s" not found.' % vars())
        # FIX - probably should check if the file is an image file?

    # Convert each input file to a .gif file 
    for file in settings.get('inp_list'):

        pos = file.rfind('.')
        ext = file[pos:]

        # short cut for gifs
        if ext == '.gif':
            gif_list.append(file)
            continue # to next file 

        # new file name
        gif = file.replace(ext, '.gif')
        gif_list.append(gif)

        if ( rotate ) : 
           cmd = 'convert -rotate 90 %(file)s %(gif)s' % vars()
        else :
           cmd = 'convert %(file)s %(gif)s' % vars()

        if verbose: print(dt.now(), "animate: cmd =", cmd)
        os.system(cmd)
        # end of loop over input files

    # build and call final cmd string
    cmd = 'convert -loop %(loop)s -delay %(delay)s ' % vars()
    for gif in gif_list:
        cmd += '%(gif)s ' % vars()
    cmd += ' %(animation)s' % vars()
    if verbose: print(dt.now(), "animate: cmd =", cmd)
    os.system(cmd)

    # clean up
    for gif in gif_list:
       os.system('rm -rf %(gif)s' % vars() )
#=====================================================================
#=====================================================================
if __name__ == "__main__":
    verbose = True

    # generate a list of input files
    cmd = "ls -r1t raster_*"
    if verbose: print(dt.now(), "main: cmd =", cmd)
    ret = subprocess.getoutput( cmd )
    list = ret.split()

    # empty settings dict
    s = {}
    s['inp_list'] = list
    # call the animate function
    animate( s )

#=====================================================================
