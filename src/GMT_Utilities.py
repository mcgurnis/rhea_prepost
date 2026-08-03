#!/usr/bin/env python2.7
#=====================================================================
#
#               Python Scripts for CitcomS Version 2.0.2
#                  ---------------------------------
#
#                              Authors:
#                            Mark Turner
#                           Michael Gurnis
#             (c) California Institute of Technology 2006-2026
#
#               Free for non-commercial academic use ONLY.
#      This program is distributed WITHOUT ANY WARRANTY whatsoever.
#
#=====================================================================
#
#  Copyright August 2013, by the California Institute of Technology.
#  ALL RIGHTS RESERVED. United States Government Sponsorship Acknowledged.
#
#=====================================================================

import sys, string, os, math
import subprocess
from datetime import datetime as dt
import Thermal_Utilities
import CitcomParser, Mesh_Utilities, PlotUtilities, zslice
import PlatesColorTable 

import numpy

import Core_Util, Core_File, Core_GMT, Core_Tomography

from Core_Util import now

# global variables
verbose = False

colors = {'black': '0/0/0', 'white':'255/255/255', 'red':'255/0/0', 'green':'0/255/0', 'blue':'0/0/255'}

#=====================================================================
#=====================================================================
def toggle_xy(xyfile_in):
    '''From a Multiple xy GMT file, toggle the lat, longs'''
    #Sets to long 0 to 360
    xyfile_out=xyfile_in.strip('.xy')+'.new.xy'
    IN=open(xyfile_in)
    OUT=open(xyfile_out,"w")
    while 1:
        line=IN.readline()
        if(line):
            c1 = line[0]
            if c1 == '>':
                OUT.write(">\n")
            else:
                s1,s2 = line.split()
                # NOTE : this is a tab in here
                OUT.write("%s\t%s\n" % (s2,s1))  
        else:
            break
    IN.close()
    OUT.close()
    return xyfile_out
#
#=====================================================================
#=====================================================================
def toggle_shift_xyz(xyzfile_in,shift):
    '''From a Multiple xyz GMT file, toggle the lat, longs'''
    #if shift S1, s1 is long and shift to 0-360
    #if shift S2, s2 is long and shift to 0-360
    #if shift S3, s3 is long and shift to 0-360, but keep long,lat on out
    #if shift S4, s1 is long and shift to -180 to 180, but keep long,lat on out
    xyzfile_out=xyzfile_in.strip('.xyz')+'.new.xyz'
    IN=open(xyzfile_in)
    OUT=open(xyzfile_out,"w")
    while 1:
        line=IN.readline()
        if(line):
            c1 = line[0]
            if c1 == '>':
                #OUT.write(">\n")
                OUT.write(line)
            else:
                s1,s2,s3 = line.split()
                f1=float(s1)
                f2=float(s2)
                f3=float(s3)
                if shift == 'S1' and f1 < 0.0:
                    f1=360+f1
                if shift == 'S2' and f2 < 0.0:
                    f2=360+f2
                if shift == 'S3' and f1 < 0.0:
                    f1=360+f1
                if shift == 'S4' and f1 > 180.0:
                    f1=f1-360.0
                if shift == 'S3' or shift == 'S4':
                    OUT.write("%g	%g	%g\n" % (f1,f2,f3)) # tabs
                else:
                    OUT.write("%g	%g	%g\n" % (f2,f1,f3)) # tabs
        else:
            break
    IN.close()
    OUT.close()
    return xyzfile_out
#=====================================================================
#=====================================================================
def toggle_shift_xy(xyfile_in,shift):
    '''From a Multiple xy GMT file, toggle the lat, longs'''
    #if shift S1, S1 is long and shift to 0-360
    #if shift S2, S2 is long and shift to 0-360
    #if shift S3, S3 is long and shift to 0-360, but keep long,lat on out
    xyfile_out=xyfile_in.strip('.xy')+'.new.xy'
    IN=open(xyfile_in)
    OUT=open(xyfile_out,"w")
    while 1:
        line=IN.readline()
        if(line):
            c1 = line[0]
            if c1 == '>':
                OUT.write(">\n")
            else:
                s1,s2 = line.split()
                f1=float(s1)
                f2=float(s2)
                if shift == 'S1' and f1 < 0.0:
                    f1=360+f1
                if shift == 'S2' and f2 < 0.0:
                    f2=360+f2
                if shift == 'S3' and f1 < 0.0:
                    f1=360+f1
                if shift == 'S3':
                    OUT.write("%g	%g\n" % (f1,f2)) # tabs
                else:
                    OUT.write("%g	%g\n" % (f2,f1)) # tabs
        else:
            break
    IN.close()
    OUT.close()
    return xyfile_out
#=====================================================================
#=====================================================================
def mk_grd(xyzfile, region, res, tension, grid_min, grid_max):
    '''From an xy data file, and other parameters, build a .grd file'''

    tmp = xyzfile.strip('.xyt')
    tmp = xyzfile.strip('.xyz')
    grdfile = "%s.grd" % tmp

    if verbose: print(dt.now(), "mk_grd: grdfile =", grdfile)

    mean_file="%s_median.xyz" % tmp
    cmd="rm -f %s" % mean_file
    cmd = "gmt blockmedian %s -V -I%s -R%s > %s" % (xyzfile,res,region,mean_file)
    if verbose: print(dt.now(), "mk_grd: cmd =", cmd)
    os.system(cmd)
    print('mk_grd: cmd =', cmd)

    if grid_min != 'none' or grid_max != 'none':
        #cmd = "gmt surface %(mean_file)s -V -G%(grdfile)s -I%(res)s -R%(region)s -T%(tension)g -Ll%(grid_min)g -Lu%(grid_max)g" % vars()
        cmd = "gmt surface %(mean_file)s -V -G%(grdfile)s -I%(res)s -R%(region)s -T%(tension)f -Ll%(grid_min)f -Lu%(grid_max)f" % vars()


    else: 
        cmd = "gmt surface %(mean_file)s -V -G%(grdfile)s -I%(res)s -R%(region)s -T%(tension)g" % vars()

    # TEST 
    # cmd = "gmt xyz2grd %(xyzfile)s -G%(grdfile)s -I%(res)s -R%(region)s " % vars()
    # TEST 

    if verbose: print(dt.now(), 'mk_grd: cmd =', cmd)
    os.system(cmd)
    print('mk_grd: cmd =', cmd)

    # clean up
    cmd = "rm -rf %(mean_file)s" % vars()
    if verbose: print(dt.now(), 'mk_grd: cmd =', cmd)
    os.system(cmd)

    return grdfile

#=====================================================================
#=====================================================================
def mk_xyp_files(section_defs,sec_res):
    '''return number of sections and lists of ids, files, etc.'''

    SDEF=open(section_defs)
    n=0
    sec_ids=[]
    lat_start_sec=[]
    lon_start_sec=[]
    lat_end_sec=[]
    lon_end_sec=[]

    while 1:
        line=SDEF.readline()
        if(line):
            s1=line.strip('\n')
            sec_ids.append(s1)
            line=SDEF.readline()
            s1,s2=line.split('	') # tabs
            lat_start_sec.append(float(s1))
            lon_start_sec.append(float(s2))
            line=SDEF.readline()
            s1,s2=line.split('	') # tabs
            lat_end_sec.append(float(s1))
            lon_end_sec.append(float(s2))
        else:
            break
        n += 1
    SDEF.close()
    number_sections=n

    if verbose:
        print(dt.now(), 'mk_xyp_files: number of sections',number_sections)

    # Use GMT to determine a set of lat,lon points along each section
    n=0
    sec_xyp_files=[]
    for id in sec_ids:
        sec_xyp_files.append("sec_%s.xyp" % sec_ids[n])
        if verbose: print(dt.now(), 'mk_xyp_files: id = %s; file = %s' % (id, sec_xyp_files[n]))

        cmd = "gmt project -C%f/%f -E%f/%f -Q -G%f > tmp.xyp" % ( \
            lon_start_sec[n], lat_start_sec[n],               \
            lon_end_sec[n], lat_end_sec[n],                   \
            sec_res)

        if verbose: print(dt.now(), 'mk_xyp_files: cmd = ', cmd)
        os.system(cmd)

        tmp=open("tmp.xyp")
        xyp_f=open(sec_xyp_files[n],"w")

        if verbose: print(dt.now(), 'mk_xyp_files: write %s' % xyp_f)

        while 1:
            line=tmp.readline()
            if(line):
                s1,s2,s3 = line.split('	') # tabs
                f1=float(s1)
                f2=float(s2)
                f3=float(s3)
                if(f1 < 0.0):
                    f1=f1+360.0
                xyp_f.write("%g	%g	%g\n" % (f1,f2,f3)) # tabs
            else:
                break             
        tmp.close()
        xyp_f.close()
        n += 1

        # clean up
        cmd = "rm -rf tmp.xyp" 
        if verbose: print(dt.now(), 'mk_xyp_files: cmd = ', cmd)
        os.system(cmd)

    # Create text file to label the x-sections at starting coor
    label_name='section_labels.txt'
    LT=open(label_name,"w")
    n=0
    for id in sec_ids:
        print("%g  %g 12 0 0 1 %s" % (lon_start_sec[n],lat_start_sec[n],id), file=LT)
        n+=1
    LT.close()

  
    if verbose: print(dt.now(), 'mk_xyp_files: number_sections:', number_sections)
    if verbose: print(dt.now(), 'mk_xyp_files: sec_ids: ', sec_ids)
    if verbose: print(dt.now(), 'mk_xyp_files: sec_xyp_files: ', sec_xyp_files)
    if verbose: print(dt.now(), 'mk_xyp_files: label_name: ', label_name)

    return number_sections, sec_ids, sec_xyp_files, label_name 

#=====================================================================
#=====================================================================
def mk_grd_sec(id, prefix, section_depth, depths, grd_input_files, xyp_file, grid_min, grid_max):
    '''create a 2D cross section grid from a list of z layer grids, and a track file'''

    xypz_file = xyp_file + '.' + prefix + '.grd_section.xypz'
    pdz_file_name = xyp_file + '.' + prefix + '.grd_section.pdz'
    pdz_file = open(pdz_file_name,"w")
   
    dist_max = 0.0 
    dist_min = 1.0e5 


    print('depths',depths)
    n=0
    for grd in grd_input_files:
        print(xypz_file)
        #cmd = "gmt grdtrack -V %s -G%s -Lg > %s" % (xyp_file,grd_input_files[n],xypz_file)
        cmd = "gmt grdtrack -V %s -G%s -fg > %s" % (xyp_file,grd_input_files[n],xypz_file)
        os.system(cmd)
        if verbose: print(dt.now(), "mk_grd_sec: cmd =", cmd)

        PZF=open(xypz_file)
        while 1:
            line=PZF.readline()
            if(line):
                s1,s2,s3,s4 = line.split('	') # tabs
                p=float(s3)
                if( p <= dist_min):
                    dist_min = p
                if( p >= dist_max):
                    dist_max = p
                z=float(s4)
                pdz_file.write("%g	%g	%g\n" % (p, depths[n], z)) # tabs
            else:
                break             

        n+=1
    pdz_file.close()

    sec_grd_tmp = pdz_file_name + '.tmp.grd'
    sec_grd     = pdz_file_name + '.grd'

    # NOTE: add r to end of R 
    #R = "0.0/%g/0.0/%dr" % (dist_max,section_depth)
    #R = "0.0/%g/0.0/%d" % (dist_max,section_depth)
    R = "%g/%g/0.0/%d" % (dist_min,dist_max,section_depth)
    #yres = 10.0
    #xres = dist_max/200.
    yres = 5.0
    xres = dist_max/400.
    print(dist_max)
    res = "%g/%g" % (xres,yres)
    print(R, res)

    if verbose: print(dt.now(), 'mk_grd_sec: R = ',R)

    cmd = "gmt surface -V %(pdz_file_name)s -G%(sec_grd_tmp)s -I%(res)s -R%(R)s" % vars()
    #cmd = "gmt surface -V %(pdz_file_name)s -G%(sec_grd_tmp)s -T1.0 -I%(res)s -R%(R)s" % vars()
    if verbose: print(dt.now(), "mk_grd_sec: cmd =", cmd)
    os.system(cmd) 

    if grid_min != 'none' or grid_max != 'none' :
        cmd = "gmt grdclip %(sec_grd_tmp)s -G%(sec_grd)s -Sa%(grid_max)g/%(grid_max)g -Sb%(grid_min)g/%(grid_min)g" % vars()
        if verbose: print(dt.now(), "mk_grd_sec: cmd =", cmd)
        os.system(cmd) 
    else:
        cmd = "mv %(sec_grd_tmp)s %(sec_grd)s" % vars()
        if verbose: print(dt.now(), "mk_grd_sec: cmd =", cmd)
        os.system(cmd)


    # clean up temporary files
    #cmd = "rm -rfv %(pdz_file_name)s %(sec_grd_tmp)s %(xypz_file)s" % vars()
    #if verbose: print now(), "mk_grd_sec: cmd =", cmd 
    #os.system(cmd)
    
    return sec_grd, R, dist_max

#=====================================================================
#=====================================================================
def mk_partial_annular_grd_sec(id, prefix, r_inner,r_outer, depths, grd_input_files, xyp_file, grid_min, grid_max):
    '''create a 2D cross section annular grid from a list of z layer grids, and a track file for range smaller than 360 degrees'''

    xypz_file = xyp_file + '.' + prefix + '.grd_section.xypz'
    pdz_file_name = xyp_file + '.' + prefix + '.grd_section.pdz'
    pdz_file = open(pdz_file_name,"w")
   
    dist_max = 0.0 
    dist_min = 1.0e5 


    print('depths',depths)
    n=0
    for grd in grd_input_files:
        print(xypz_file)
        cmd = "gmt grdtrack -V %s -G%s -fg > %s" % (xyp_file,grd_input_files[n],xypz_file)
        os.system(cmd)
        if verbose: print(dt.now(), "mk_grd_sec: cmd =", cmd)

        PZF=open(xypz_file)
        while 1:
            line=PZF.readline()
            if(line):
                s1,s2,s3,s4 = line.split('	') # tabs
                p=float(s3)
                if( p <= dist_min):
                    dist_min = p
                if( p >= dist_max):
                    dist_max = p
                z=float(s4)
                pdz_file.write("%g	%g	%g\n" % (p, depths[n], z)) # tabs
            else:
                break             

        n+=1
    pdz_file.close()

    sec_grd_tmp = pdz_file_name + '.tmp.grd'
    sec_grd     = pdz_file_name + '.grd'

    # NOTE: add r to end of R 
    #R = "0.0/%g/0.0/%dr" % (dist_max,section_depth)
    #R = "0.0/%g/0.0/%d" % (dist_max,section_depth)
    R = "%g/%g/%g/%g" % (dist_min,dist_max,r_inner,r_outer)
    #yres = 10.0
    #xres = dist_max/200.
    #yres = (r_outer-r_inner)/200.
    yres = (r_outer-r_inner)/400.
    #yres = (r_outer-r_inner)/500.
    #xres = (dist_max-dist_min)/400.
    xres = (dist_max-dist_min)/2000.
    res = "%g/%g" % (xres,yres)
    print(R, res)


    if verbose: print(dt.now(), 'mk_grd_sec: R = ',R)

    pdz_median_file_name=pdz_file_name+".median.pdz"

    cmd = "gmt blockmedian %(pdz_file_name)s -V -I%(res)s -R%(R)s > %(pdz_median_file_name)s" % vars()
    print(dt.now(), "mk_grd_sec: cmd =", cmd)
    os.system(cmd) 

    tension=0.0
    #cmd = "gmt surface -V %(pdz_file_name)s -G%(sec_grd_tmp)s -I%(res)s -R%(R)s" % vars()
    cmd = "gmt surface -V %(pdz_median_file_name)s -G%(sec_grd_tmp)s -T%(tension)s -I%(res)s -R%(R)s" % vars()
    if verbose: print(dt.now(), "mk_grd_sec: cmd =", cmd)
    os.system(cmd) 

    if grid_min != 'none' or grid_max != 'none' :
        cmd = "grdclip %(sec_grd_tmp)s -G%(sec_grd)s -Sa%(grid_max)g/%(grid_max)g -Sb%(grid_min)g/%(grid_min)g" % vars()
        if verbose: print(dt.now(), "mk_grd_sec: cmd =", cmd)
        os.system(cmd) 
    else:
        cmd = "mv %(sec_grd_tmp)s %(sec_grd)s" % vars()
        if verbose: print(dt.now(), "mk_grd_sec: cmd =", cmd)
        os.system(cmd)


    # clean up temporary files
    #cmd = "rm -rfv %(pdz_file_name)s %(sec_grd_tmp)s %(xypz_file)s" % vars()
    #if verbose: print now(), "mk_grd_sec: cmd =", cmd 
    #os.system(cmd)
    
    return sec_grd, R, dist_min, dist_max

#=====================================================================

def mk_grd_expected_sec(scalet,layer_km,id,section_depth,depths,grd_input_file,xyp_file,R):

    xypa_file="section_tmp.xypa"
    pdz_file_name="section_expected.pdz"
    pdz_file=open(pdz_file_name,"w")

    cmd = "gmt grdtrack -V %s -G%s > %s" % (xyp_file,grd_input_file,xypa_file)
    if verbose: print(dt.now(), "mk_grd_expected_sec: cmd =", cmd)
    os.system(cmd)

    dist_max = 0.0 
   
    n=0
    for dd in depths:
        PZA=open(xypa_file)
        while 1:
            line=PZA.readline()
            if(line):
                s1,s2,s3,s4 = line.split('	') # tabs
                p=float(s3)
                if  p>= dist_max:
                    dist_max=p
                s5=s4.strip('\n')
                a=float(s5)
                non_dim_dd=dd/layer_km
                #if a<=0.0:
                #    print 'lith age=',a
                #    a=0.01
                #if a>200.0:
                #    print 'lith age=',a
                #    a=200.0
                etemp = Thermal_Utilities.expected_temp(non_dim_dd,a,scalet)
                pdz_file.write("%g	%g	%g\n" % (p, dd, etemp)) # tabs
            else:
                break             
        if verbose: print(dt.now(), "mk_grd_expected_sec: cmd =", cmd)
        os.system(cmd)
        PZA.close()
        n+=1
    pdz_file.close()

    sec_grd = "expected_sec_%s.grd" % id
    yres = 10.0
    xres = dist_max/200.
    res = "%g/%g" % (xres,yres)
    cmd = "gmt surface %(pdz_file_name)s -G%(sec_grd)s -I%(res)s -R%(R)s" % vars()
    if verbose: print(dt.now(), "mk_grd_expected_sec: cmd =", cmd)
    os.system(cmd) 

    return sec_grd

#=====================================================================
def mk_contour_int(cmin,cmax,number):
    contour_file_name = "cont.ci"
    TCI = open(contour_file_name,'w')
    ci = (cmax-cmin)/number
    c=cmin
    while c<cmax:
        #TCI.write("%g   C\n" % c)
        TCI.write("%1.1f   A\n" % c)
        c+=ci
    TCI.close()

    return contour_file_name
#=====================================================================
def xy2xyz(xy_file,zvalue,spacing,zback):

    XYF=open(xy_file)
    xyz_file="tmp.xyz"
    XYZF=open(xyz_file,"w")
    while 1:
        line=XYF.readline()
        if(line):
            c1 = line[0]
            if c1 == '>':
                XYZF.write(line)
            elif c1 != '#':
                s1=line.strip('\n')
                XYZF.write("%s  %g\n" % (s1,zvalue))
        else:
            break             

    XYF.close()
    XYZF.close()

    if spacing != 'NONE':
        # create a uniformly spaced background with zback
        if spacing > 0:
            xyz_file_2="tmp_2.xyz"
            XYZF=open(xyz_file_2,"w")
            XYZF.write(">\n")
            imax=360/spacing
            jmax=179/spacing
            i=-179
            while i <180: 
                j=-89
                while j < 89:
                    XYZF.write("%d  %d  %g\n" % (j,i,zback))
                    j+=1
                i+=1
        XYZF.close()
    
        cmd = "cat %s %s >> %s" % (xyz_file,xyz_file_2,xyz_file)
        os.system(cmd)

        # clean up
        cmd = "rm -f %s" % (xyz_file_2)
        os.system(cmd)

    return xyz_file
#=====================================================================
#=====================================================================
#=====================================================================
#=====================================================================
#=====================================================================
#=====================================================================
def make_psbasemap(figure): 
    '''make a GMT psbasemap cmd from the figure data'''

    B = figure.get('boundary')
    J = figure.get('projection')
    R = figure.get('region')

    X = figure.get('X')
    Y = figure.get('Y')

    ko = figure.get('gmt_ko')

    file = figure.get('output_file')
    
    cmd += '-X%(X)s -Y%(Y)s ' % vars()
    cmd += '%(ko)s %(file)s' % vars()


    return cmd

#=====================================================================
#=====================================================================
def make_figure(figure):
    '''make the figure from the dictionary enries'''

    # clear out working directory of intermediate files
    PlotUtilities.clean_dir_of_z_data(figure)

    if figure['type'] == 'map':
        make_map(figure)

    elif figure['type'] == 'cross_section':
        make_cross_sections(figure)

    elif figure['type'] == 'annulus':
        make_annulus(figure)

#=====================================================================
#=====================================================================
def make_map(figure):
    '''make a map'''


    # set the model region
    set_model_region(figure)

    # check what type of grid to plot 
    if 'interpolate_to_plate_frame_mesh' in list(figure.keys()) :
        Mesh_Utilities.interpolate_to_plate_frame( figure ) 
    else: 
        set_grid_parameters(figure)
        make_grid(figure)

    # make the color palette table file
    make_cpt(figure)

    # make pslegend text file
    if verbose: print(dt.now(), 'make_pslegend_file: txt=')
    make_pslegend_file(figure)

    # plot the data
    make_ps_plot(figure)

    # final clean up
    if not ( figure.get("keep_tmp_files") ): 
        cmd ='rm -vrf ' + ' '.join( figure['rm_list'] )
        if verbose: print(dt.now(), 'make_map: cmd=', cmd)
        os.system(cmd)
    else:
        if verbose: print(dt.now(), "make_map: DO NOT remove temporary files:")
        print("rm_list = ", figure['rm_list'])

#=====================================================================
def make_grid(figure):
    '''make a grid for the figure'''

    if verbose: print(dt.now(), "make_grid: START")

    # get field
    field = figure['field']

    # get time
    time = str( figure['time'] )

    # convert time to step, if needed
    if time.endswith('Ma'):
        figure['iage'] = int(time[0:-2])
        if figure.get('parameters'):
            time = PlotUtilities.get_step_from_age(figure['parameters'], float(time[0:-2]) )

    # get level
    level = str( figure['level'] ) 

    # convert depth to level, if needed
    if level.endswith('km'):
        figure['depth'] = level[0:-2]
        if figure.get('parameters'):
            level = PlotUtilities.get_level_from_depth(figure['parameters'], float(level[0:-2]) )
            n = int(level) - 1
            figure['n'] = n 
        else: 
            figure['depth'] = level[0:-2]
    else:
        n = int(level) - 1
        figure['n'] = n 

    if verbose: print(dt.now(), "make_grid: field =", field)
    if verbose: print(dt.now(), "make_grid: time =", time)
    if verbose: print(dt.now(), "make_grid: level =", level)
    if verbose: print(dt.now(), "make_grid: n =", n)

    # map settings
    region = figure['region']
 
    # set defaults
    xyz_file = None
    grid_file = None

    grid_min = figure['grid_min']
    grid_max = figure['grid_max']
    grid_cpt_delta = figure['grid_cpt_delta']

    grid_tension = figure['grid_tension']

    # check for overlay of CitComS velocity and make that xy
    if figure.get('overlay_velocity') :

        incr = figure.get('overlay_velocity_increment')
        if verbose: print(dt.now(), "make_grid: overlay_velocity_increment=", incr)
        if not incr : 
            if figure.get('nodex') <= 32:
                incr = 1.0
            else : 
                incr = 0.001
        if verbose: print(dt.now(), "make_grid: sub-sample incr=", incr)

        vs = figure.get('overlay_velocity_vector_scale')
        if not vs : vs = 1.0
        if verbose: print(dt.now(), "make_grid: overlay_velocity_vector_scale=", vs)

        xy = PlotUtilities.cap_to_xyVelocity(figure['parameters'], time, n, incr, vs)
        if verbose: print(dt.now(), "make_grid: xy file =", xy)

        # double check a velocity file was created
        cmd = 'wc -l %(xy)s' % vars()
        if verbose: print(dt.now(), "make_grid: cmd =", cmd)
        info = subprocess.getoutput( cmd )
        length=info.split(' ')[0]
        if verbose: print(dt.now(), "make_grid: xy file length =", length)
        if length == 0:
            print(dt.now(), 'cap_to_xyVelocity: ERROR: "overlay_velocity" file is zero length!')
            print(dt.now(), 'cap_to_xyVelocity: ERROR: removing empty overlay_velocity file.')
            cmd = 'rm -fv %(xy)s' % vars()
            if verbose: print(dt.now(), cmd)
            os.system( cmd )
            print(dt.now(), 'cap_to_xyVelocity: ERROR: removing overlay_velocity option from figure.')
            del figure['overlay_velocity'] # remove this option from the figure 
        else: 
            # call minmax
            cmd = 'minmax -C %(xy)s' % vars()
            if verbose: print(dt.now(), cmd)
            minmax = os.popen(cmd)
            line = minmax.readline()
            cols = line.split()
            vmin = cols[-2]
            vmax = cols[-1]
            figure['overlay_velocity_xyz'] = xy
            figure['overlay_velocity_min'] = vmin
            figure['overlay_velocity_max'] = vmax


    # check for overlay of GPlates velocity and make that xy file
    if figure.get('overlay_gplates_velocity') :

        if not figure.get('overlay_gplates_velocity_vector_increment'):
            figure['overlay_gplates_velocity_vector_increment'] = 0.001

        if not figure.get('overlay_gplates_velocity_vector_scale'):
            figure['overlay_gplates_velocity_vector_scale'] = 1.0

        overlay_gplates_velocity_xyz = Core_File.gplates_velocity_to_xyz( figure )

        # call minmax
        cmd = 'minmax -C %(xy)s' % vars()
        if verbose: print(dt.now(), cmd)
        minmax = os.popen(cmd)
        line = minmax.readline()
        cols = line.split()
        vmin = cols[-2]
        vmax = cols[-1]
        figure['overlay_gplates_velocity_xyz'] = overlay_gplates_velocity_xyz
        figure['overlay_gplates_velocity_min'] = vmin
        figure['overlay_gplates_velocity_max'] = vmax

    # 
    # make grid , depending on field type
    # 
    if field.startswith('none'):
        figure['grid_file'] = None
        return

    # read the citcom cap data into xyz format
    elif field.startswith('temp'):
        xy = PlotUtilities.cap_to_xyTemperature(figure['parameters'],time,n)
        figure['rm_list'] += [xy]
        xyz_file = xy

    elif field.startswith('visc'):
        xy = PlotUtilities.cap_to_xyViscosity(figure['parameters'],time,n)
        figure['rm_list'] += [xy]
        xyz_file = xy

    elif field.startswith('phase'):
        # NOTE : phase is computed from temperature grid later 
        xy = PlotUtilities.cap_to_xyTemperature(figure['parameters'],time,n)
        figure['rm_list'] += [xy]
        xyz_file = xy

    elif field.startswith('age'):
        # check for user selected age grid location
        if figure.get('age_grid_files'):
            age_grid_files = figure.get('age_grid_files')
            grid_file = age_grid_files % figure['iage']
        else:
            # locate the age grid
            #grid_file = '/net/sierra/raid2/mturner/agegrids/Agegrids/agegrid_final_mask_%d.grd' % iage
            #HACKED
            #grid_file = '/net/holmes/scratch2/gurnis/Agegrids/Remasked_0.8.6_0-360/agegrid_masked_by_platepolygons_%d.grd' % figure['iage']
            grid_file = '/net/beno/raid2/marias/Agegrids/20100803_0_360/Mask/agegrid_final_mask_%d.grd' % figure['iage']
        # end of check on user selected age grid locations 

        figure['grid_file'] = grid_file
        return # no need to call mk_grd

    elif field.startswith('comp'): 
        xyz_file = PlotUtilities.cap_to_xyComposition(figure['parameters'],time,n)
        figure['rm_list'] += [xyz_file]
      
    elif field.startswith('surftopo'):
        # NOTE : phase is computed from temperature grid later 
        xy = PlotUtilities.cap_to_xySurfTopo(figure['parameters'],time)
        figure['rm_list'] += [xy]
        xyz_file = xy

    elif field.startswith('grand_tomography'):
        xyz_file = Core_File.find_grand_tomography_file(figure)

    elif field.startswith('S20RTS'):
        xyz_file = Core_Tomography.S20RTS_to_xyz(figure)

    else :
        msg = 'Unknown field type: Please use -h for help.'
        raise ValueError(msg)

    if verbose: print(dt.now(), "make_grid: xyz_file=", xyz_file)

    if figure.get('force360'):
        force_xy = '%(xyz_file)s.force360.xyz' %vars()

        if figure.get('file_in_latlon'):
            cmd = "cat %(xyz_file)s | awk '{if ($2<0) print ($1, $2 + 360, $3); else print ($0)} ' > %(force_xy)s" % vars()
        else: 
            cmd = "cat %(xyz_file)s | awk '{if ($1<0) print ($1 + 360, $2, $3); else print ($0)} ' > %(force_xy)s" % vars()

        if verbose: print(dt.now(), 'make_grid: cmd =', cmd)
        os.system(cmd)
        xyz_file = force_xy

    if figure.get('force180'):
        force_xy = '%(xyz_file)s.force180.xyz' %vars()
        if figure.get('file_in_latlon'):
            cmd = "cat %(xyz_file)s | awk '{if ($2>180) print ($1, $2 - 360, $3); else print ($0)} ' > %(force_xy)s" % vars()
        else :
            cmd = "cat %(xyz_file)s | awk '{if ($1>180) print ($1 - 360, $2, $3); else print ($0)} ' > %(force_xy)s" % vars()
        if verbose: print(dt.now(), 'make_grid: cmd =', cmd)
        os.system(cmd)
        xyz_file = force_xy

    # update figure data  
    # NOTE: The region may have changed via xyz file selection above 

    figure['xyz_file'] = xyz_file

    figure['R'] = figure['region']

    # create the grid
    grid_file = Core_GMT.xyz2grd(figure)

    # update figure data
    figure['grid_file'] = grid_file
    figure['rm_list'] += [grid_file]
    figure['rm_list'] += [xyz_file]

#=====================================================================
def make_cpt(figure):
    '''make a cpt file for the figure, set the cpt lable string'''

    # get figure data
    field = figure['field']
   
    grid_max = figure['grid_max']
    grid_min = figure['grid_min']
    grid_cpt_delta = figure['grid_cpt_delta']

    # set defaults
    cpt_label = None
    cpt_file = None
    cpt_file = ".".join([ figure['modelname'], str(figure['time']), str(field), str(figure['level']) , "cpt"])

    # update the figure data with defaults
    figure['cpt_file'] = cpt_file
    figure['cpt_label'] = cpt_label

    if field.startswith('none'):
        # no action needed
        return

    elif field.startswith('temp'):
        cpt_label = 'a0.2f%(grid_cpt_delta)s::/:Temp:' % vars()
        cmd="gmt makecpt -M -V -Cpolar -T%(grid_min)s/%(grid_max)s/%(grid_cpt_delta)s > %(cpt_file)s" % vars()
       
    elif field.startswith('visc'):
        if str(grid_max) == str(5000):
            cpt_label = 'a500f500::/:Visc:'
        else :
            cpt_label = 'a0.5f0.25::/:Visc:'

        cmd="gmt makecpt -M -V -D -Cpolar -I -T%(grid_min)s/%(grid_max)s/%(grid_cpt_delta)s > %(cpt_file)s" % vars()

    elif field.startswith('age'):
        cpt_label = 'a50f25:Age:/:Ma:'

        if figure.get('age_cpt'):
            f = figure.get('age_cpt')
            cmd="cp -v %(f)s %(cpt_file)s" % vars()
        else:
            # FIX : LOCAL
            cmd="cp /net/holmes/home4/gurnis/Global_Plate_Polygons/age_scale.cpt .; mv age_scale.cpt %(cpt_file)s" % vars()

    elif field.startswith('phase'):
        cpt_label = 'a0.5f%(grid_cpt_delta)s:Phase:/:Phase:' % vars()
        cmd="gmt makecpt -M -V -Cpolar -T%(grid_min)s/%(grid_max)s/%(grid_cpt_delta)s > %(cpt_file)s" % vars()
        cmd="gmt makecpt -V -Cpolar -T%(grid_min)s/%(grid_max)s/%(grid_cpt_delta)s -Z > %(cpt_file)s" % vars()

    elif field.startswith('comp'):
        cpt_label = 'a0.2f%(grid_cpt_delta)s::/:Composition:' % vars()
        cmd="gmt makecpt -M -V -Cpolar -T%(grid_min)s/%(grid_max)s/%(grid_cpt_delta)s > %(cpt_file)s" % vars()

    elif field.startswith('surftopo'):
        cpt_label = 'a1.0f%(grid_cpt_delta)s::/:"Surface Topography":' % vars()
        cmd="gmt makecpt -M -V -Cpolar -T%(grid_min)s/%(grid_max)s/%(grid_cpt_delta)s > %(cpt_file)s" % vars()

    elif field.startswith('grand_tomography'):
        cpt_label = 'a1.0f%(grid_cpt_delta)s::/:"Velocity Anomaly":' % vars()
        cmd="gmt makecpt -M -V -I -Cpolar -T%(grid_min)s/%(grid_max)s/%(grid_cpt_delta)s -Z > %(cpt_file)s" % vars()

    elif field.startswith('S20RTS'):
        cpt_label = 'a1.0f%(grid_cpt_delta)s::/:"Velocity Anomaly":' % vars()
        cmd="gmt makecpt -M -V -I -Cpolar -T%(grid_min)s/%(grid_max)s/%(grid_cpt_delta)s -Z > %(cpt_file)s" % vars()
       
    else:
        cpt_label = 'a0.2f0.1:UNK:/:UNKNOWN:'
        cmd="gmt makecpt -M -V -Cpolar -T%(grid_min)s/%(grid_max)s/%(grid_cpt_delta)s > %(cpt_file)s" % vars()

    # make the cpt file 
    if verbose: print(now(), "make_cpt: cmd=", cmd)
    os.system(cmd)

    # update the figure data with real values
    figure['cpt_file'] = cpt_file
    figure['cpt_label'] = cpt_label
    figure['rm_list'] += [cpt_file]
    
    # create cpt file for overlay 
    if figure.get('overlay_temperature'):
        grid_min = figure['overlay_temperature_grid_min']
        grid_max = figure['overlay_temperature_grid_max']

        cpt_delta = figure['overlay_temperature_grid_cpt_delta']
        cpt_label = 'a0.2f0.1::/:Temp:'
        cpt_file = '.'.join([ figure['modelname'], str(figure['time']), str(field), str(figure['level']) , "overlay_temp", "cpt"])

        cmd="gmt makecpt -V -Cpolar -T%(grid_min)s/%(grid_max)s/%(cpt_delta)s > %(cpt_file)s" % vars()
        if verbose: print(dt.now(), "make_cpt: overlay_temperature: cmd=", cmd)
        os.system(cmd)

        figure['overlay_temperature_cpt_file'] = cpt_file
        figure['rm_list'] += [cpt_file]

    # create cpt file for overlay 
    if figure.get('overlay_phase'):
        grid_min = figure['overlay_phase_grid_min']
        grid_max = figure['overlay_phase_grid_max']
        cpt_delta = figure['overlay_phase_grid_cpt_delta']

        cpt_label = 'a0.2f0.01::/:Phase:'
        cpt_file = '.'.join([ figure['modelname'], str(figure['time']), str(field), str(figure['level']) , "overlay_phase", "cpt"])

        cmd="gmt makecpt -V -Cpolar -T%(grid_min)s/%(grid_max)s/%(cpt_delta)s -Z > %(cpt_file)s" % vars()
        if verbose: print(dt.now(), "make_cpt: overlay_phase: cmd=", cmd)
        os.system(cmd)

        figure['overlay_phase_cpt_file'] = cpt_file
        #figure['rm_list'] += [cpt_file]

#=====================================================================
def make_pslegend_file(figure):
    '''write a .txt file with map legend information'''

    id = figure['id']
    m = figure['modelname']
    t = figure['time']
    l = figure['level']
    R = figure['region']
    J = figure['projection']

    # compute the height of the legend as items are added 
    h = 0.0

    # assemble the full pslegend text string 
    txt = '' % vars()
    if verbose: print(dt.now(), 'make_pslegend_file: txt=', txt)

    # Run info 
    if figure.get('overlay_legend_info'): 
        txt += '''# info line
L 9 Helvetica L Figure %(id)s: %(m)s, time=%(t)s, level=%(l)s
G 0.05i
D 0 1p,black,
''' % vars()
        h += 0.20

    # Velocity vector
    if figure.get('overlay_velocity_vector_legend'): 
        s = figure.get('overlay_velocity_vector_scale') or 1.0
        txt += '''# velocity vector
S 0.5 v 1.0/0.015/0.06/0.05 0/0/0 1,black, 1.3i Velocity scale: %(s)s cm per year 
G 0.05i
D 0 1p,black,
''' % vars()
        h += 0.25

    # Velocity vector
    if figure.get('overlay_gplates_velocity_vector_legend'): 
        s = figure.get('overlay_gplates_velocity_vector_scale') or 1.0
        txt += '''# velocity vector
S 0.5 v 1.0/0.015/0.06/0.05 0/0/0 1,black, 1.3i Velocity scale: %(s)s cm per year 
G 0.05i
D 0 1p,black,
''' % vars()
        h += 0.25



    # Feature data 
    if figure.get('overlay_feature_legend'):
        # start legend section
        txt += '''# feature types
''' % vars()

        # all line data
        if figure.get('overlay_lines'):
            txt += '''# line data
S 0.1i - 0.15i - 3p,black, 0.3i Feature Data
D 0 1p,black,
''' % vars()
            h += 0.20

        # all plate polygon data
        if figure.get('overlay_platepolygons'):
            txt += '''# feature types
S 0.1i - 0.15i - 3p,green, 0.3i Plate Polygons 
D 0 1p,black,
''' % vars()
            h += 0.20

        # boundary types
        if \
        figure.get('overlay_subduction_boundaries_sL') or \
        figure.get('overlay_subduction_boundaries_sR') or \
        figure.get('overlay_ridge_transform_boundaries'): 
            txt += '''# plate boundary types
N 3
V 0 1p,black,
S 0.1i - 0.15i - 3p,black, 0.3i sR
S 0.1i - 0.15i - 3p,black, 0.3i sL
S 0.1i - 0.15i - 3p,green, 0.3i Ridge/Trans.
V 0 1p,black,
D 0 1p,black,
N 1
''' % vars()
            h += 0.20

        # individual plate polygon outlines
        if figure.get('overlay_platepolygon_boundaries') :
            # parse string for plate ids
            list = figure['overlay_platepolygon_boundaries'].split(',')
            txt += '''# plate polygons
N 3
V 0 1p,black,
''' % vars()
            i = 0
            for prefix in list:
                i += 1

                # locate the color
                pid = prefix[ prefix.rfind('.')+1: ]
                color = PlatesColorTable.get_color(pid)

                # COLOR Correct 
                if color.upper() == 'YELLOW':
                    color = 'dark' + color 

                # add a line for each plate polygon
                txt += '''S 0.1i - 0.15i - 3p,%(color)s, 0.3i Plate Id %(pid)s
''' % vars()
                # add a new height delta every 3 plate id's 
                if i % 4 == 0: 
                   h += 0.20

            # finish out plate polygon section
            txt += '''V 0 1p,black,
D 0 1p,black,
N 1
G 0.05i
''' % vars()
        # little padding for feature section
        h += 0.05

    # Custom text from .cfg file 
    if figure.get('overlay_legend_text'):
        str = figure.get('overlay_legend_text')
        txt += '''# custom text
L 9 Helvetica L %(str)s
G 0.05i
D 0 1p,black,
''' % vars()
        h += 0.25

    # mape scale 
    if figure.get('overlay_legend_scale'): 
        txt += '''# map scale
G 0.05i
M 0 0 10000:km:l f -R%(R)s -J%(J)s
G 0.05i
''' % vars()
        h += 0.50

    if verbose: print(dt.now(), 'make_pslegend_file: txt=', txt)

    # check for empty txt
    if txt == '':
        return

    # set args
    file_name = 'figure_%s.pslegend.txt' % figure['id']
    file = open(file_name,'w')
    file.write('%s' % txt)
    file.close()
    figure['pslegend_file'] = file_name

    dy = h + 0.2
    figure['pslegend_D'] = 'x0i/-%(dy)f/3.5/%(h)f/BL' % vars()

    figure['rm_list'] += [ file_name ] # WWWW 

#=====================================================================
# sample strings:
# S 0.1i v 0.25i/0.02/0.06/0.05 255/0/255 0.25p 0.3i This is a vector
## len/aw/hl/hw,
## arrowwidth/headlength/headwidth [Default is 0.075c/0.3c/0.25c (or 0.03i/0.12i/0.1i)]
#=====================================================================
def extra_ps_cmd(figure):
    '''check for extra ps cmds...'''

    R = figure['region']
    J = figure['projection']
    ps = figure['output_file']

    if figure.get('number_sections'):
        for i,id in enumerate( figure.get('sec_ids') ):
            f = figure['sec_xyp_files'][i] 
            cmd = 'gmt psxy %(f)s -A -R%(R)s -J%(J)s -B -W3.0/0 -O -K >> %(ps)s' % vars()
            if verbose: print(dt.now(), 'extra_ps_cmd: cmd=', cmd)
            os.system(cmd)

        if figure.get('label_name'):
            f = figure['label_name']
            cmd="gmt pstext %(f)s -R%(R)s -J%(J)s -B -W255 -G0 -O -K >> %(ps)s" % vars()
            if verbose: print(dt.now(), 'extra_ps_cmd: cmd=', cmd)
            os.system(cmd)

            # clean up 
            figure['rm_list'] += [ '%(f)s' % vars() ]

    if figure.get('great_circle_file'):
        f = figure['great_circle_file']
        cmd = 'gmt psxy %(f)s -R%(R)s -J%(J)s -B -W3.0/0 -O -K >> %(ps)s' % vars()
        if verbose: print(dt.now(), 'extra_ps_cmd: cmd=', cmd)
        os.system(cmd)

#=====================================================================
#=====================================================================
def make_ps_plot(figure):
    '''make the plot calling psbasemap or grdimg, then psscale, various psxy cmds for overlays, pslegend'''
    # get figure data
    field = figure['field']
    grid = figure['grid_file']
    C = figure['cpt_file']
    l = figure['cpt_label']
    B = figure['boundary']
    R = figure['region']
    J = figure['projection']
    X = figure['X']
    Y = figure['Y']
    D = figure['D']
    ps = figure['output_file'] 

    mask = figure.get('interpolate_to_mesh_mask')

    # create base empty map or base grdimage map 

    if field.startswith('none'):
        cmd = 'gmt psbasemap -B%(B)s -J%(J)s -R%(R)s -X%(X)s -Y%(Y)s -K -O >> %(ps)s' % vars()
        if verbose: print(dt.now(), 'make_ps_plot: cmd=', cmd)
        os.system(cmd)

        # call any extra ps cmds
        extra_ps_cmd(figure)

        # check for and plot overlays
        make_overlay_ps(figure)

        # plot the legend 
        if figure.get('pslegend_file'): 
            txt = figure['pslegend_file'] # ZZZZ
            pD = figure.get('pslegend_D')
            if verbose: print(dt.now(), 'make_ps_plot: cmd=', cmd)
            os.system(cmd)

    elif field.startswith('temp') or \
       field.startswith('visc') or \
       field.startswith('comp') or \
       field.startswith('surftopo') or \
       field.startswith('grand_tomography') or \
       field.startswith('S20RTS') or \
       field.startswith('age') :

        # plot main image
        cmd = 'gmt grdimage %(grid)s -V -C%(C)s -B%(B)s -R%(R)s -J%(J)s -X%(X)s -Y%(Y)s -K -O >> %(ps)s' % vars()
        if verbose: print(dt.now(), 'make_ps_plot: cmd =', cmd)
        os.system(cmd)

        # plot the cpt scale bar
        cmd = 'gmt psscale -C%(C)s -D%(D)s -B%(l)s -K -O >> %(ps)s' % vars()
        if verbose: print(dt.now(), 'make_ps_plot: cmd=', cmd)
        os.system(cmd)

        # call any extra ps cmds
        extra_ps_cmd(figure)

        # check for and plot overlays
        make_overlay_ps(figure)

        # plot the legend 
        if figure.get('pslegend_file'): 
            txt = figure['pslegend_file'] # ZZZZ
            pD = figure.get('pslegend_D')
            cmd = 'pslegend -V -R0/9/0/0.5 -Jx1i -F -Gwhite -D%(pD)s -K -O %(txt)s >> %(ps)s' % vars() 
            if verbose: print(dt.now(), 'make_ps_plot: cmd=', cmd)
            #FIXME: os.system(cmd)

    else :
        msg = 'Unknown field: Please use -h for help.'
        raise ValueError(msg)
#=====================================================================
#=====================================================================
def make_overlay_ps(figure):
    '''call psxy for overlay line data'''

    # get figure data
    #field = figure['field']
    #grid = figure['grid_file']
    #C = figure['cpt_file']
    #l = figure['cpt_label']
    #D = figure['D']
    B = figure['boundary']
    R = figure['region']
    J = figure['projection']
    X = figure['X']
    Y = figure['Y']
    ps = figure['output_file'] 
    iage = figure['iage']

    # Generic XY file 
    if figure.get('overlay_xy') :
        list = figure['overlay_xy'].split(',')
        for file in list:
            cmd='gmt psxy %(file)s -R%(R)s -J%(J)s -W5/black -m -O -K >> %(ps)s' % vars()
            if verbose: print(dt.now(), 'make_overlay_ps: cmd =', cmd)
            os.system(cmd)


    # Generic XY vectors
    if figure.get('overlay_xy_vectors') :
        list = figure['overlay_xy_vectors'].split(',')
        for file in list:
            cmd='gmt psxy -V %(file)s -R%(R)s -J%(J)s -B%(B)s -SV0.015i/0.06i/0.05i -G255 -: -O -K >> %(ps)s' % vars()
            if verbose: print(dt.now(), 'make_overlay_ps: cmd =', cmd)
            os.system(cmd)

    # GMT Coast lines built-in GMT xy data
    if figure.get('overlay_coast') :
        cmd='gmt pscoast -R%(R)s -J%(J)s -W -Dc -K -O >> %(ps)s' % vars()
        if verbose: print(dt.now(), 'make_overlay_ps: cmd =', cmd)
        os.system(cmd)

    #
    # CitComS data 
    #

    # Tracer dat
    if figure.get('overlay_tracers') :
        make_overlay_tracers(figure)

    # Velocity vectors 
    if figure.get('overlay_velocity'):
        overlay_velocity_xyz = figure['overlay_velocity_xyz']
        cmd = 'gmt psxy -V %(overlay_velocity_xyz)s -R%(R)s -J%(J)s -B%(B)s -SV0.015i/0.06i/0.05i -G0 -O -K >> %(ps)s' % vars()
        if verbose: print(dt.now(), 'make_overlay_ps: cmd =', cmd)
        os.system(cmd)
        figure['rm_list'] += [ overlay_velocity_xyz ] # clean up 

    #
    # GPlates Velocity vectors 
    #
    if figure.get('overlay_gplates_velocity'):
        overlay_gplates_velocity_xyz = figure['overlay_gplates_velocity_xyz']
        cmd = 'gmt psxy -V %(overlay_gplates_velocity_xyz)s -R%(R)s -J%(J)s -B%(B)s -SV0.015i/0.06i/0.05i -G0 -O -K >> %(ps)s' % vars()
        if verbose: print(dt.now(), 'make_overlay_ps: cmd =', cmd)
        os.system(cmd)
        figure['rm_list'] += [ overlay_gplates_velocity_xyz ] # clean up 

    #
    # GPlates produced xy data 
    # 

    # set initial path, and file
    # both will be replaced multiple times below
    path = figure.get('overlay_gplates_xy_path')
    if path == None:
        path = './'

    file = '' 

    # Lines
    if figure.get('overlay_lines') :
        prefix = figure['overlay_lines']

        if prefix.startswith('/'):
            file = os.path.join('', prefix + '.lines.%d.xy' % iage)
        else:
            file = os.path.join(path, prefix + '.lines.%d.xy' % iage)
        if not os.path.exists(file):
            print(dt.now(), 'make_overlay_ps: WARN: file missing: %(file)s' % vars())
        else:
            cmd='gmt psxy -V %(file)s -R%(R)s -J%(J)s -B%(B)s -W3/0 -m -K -O >> %(ps)s' % vars()
            if verbose: print(dt.now(), 'make_overlay_ps: cmd =', cmd)
            os.system(cmd)

    # Platepolygons
    if figure.get('overlay_platepolygons') :
        prefix = figure['overlay_platepolygons']

        if prefix.startswith('/'):
            file = os.path.join('', prefix + '.platepolygons.%d.xy' % iage)
        else:
            file = os.path.join(path, prefix + '.platepolygons.%d.xy' % iage)
        if not os.path.exists(file):
            print(dt.now(), 'make_overlay_ps: WARN: file missing: %(file)s' % vars())
        else:  
            cmd='gmt psxy -V %(file)s -R%(R)s -J%(J)s -B%(B)s -W5/green -m -K -O >> %(ps)s' % vars()
            if verbose: print(dt.now(), 'make_overlay_ps: cmd =', cmd)
            os.system(cmd)

    # Slab Polygon
    if figure.get('overlay_slab_polygons') :
        prefix = figure['overlay_slab_polygons']

        if prefix.startswith('/'):
            file = os.path.join('', prefix + '.slab_polygons.%d.xy' % iage)
        else:
            file = os.path.join(path, prefix + '.slab_polygons.%d.xy' % iage)
        if not os.path.exists(file):
            print(dt.now(), 'make_overlay_ps: WARN: file missing: %(file)s' % vars())
        else:  
            cmd='gmt psxy -V %(file)s -R%(R)s -J%(J)s -B%(B)s -W5/green -m -K -O >> %(ps)s' % vars()

    # Network Polygon
    if figure.get('overlay_network_polygons') :
        prefix = figure['overlay_network_polygons']

        if prefix.startswith('/'):
            file = os.path.join('', prefix + '.network_polygons.%d.xy' % iage)
        else:
            file = os.path.join(path, prefix + '.network_polygons.%d.xy' % iage)
        if not os.path.exists(file):
            print(dt.now(), 'make_overlay_ps: WARN: file missing: %(file)s' % vars())
        else:  
            cmd='gmt psxy -V %(file)s -R%(R)s -J%(J)s -B%(B)s -W5/green -m -K -O >> %(ps)s' % vars()


    # Subductions for all types of Topologies 
    if figure.get('overlay_subduction_boundaries') :
        prefix = figure['overlay_subduction_boundaries']

        # platepolygons
        if prefix.startswith('/'):
            file = os.path.join('', prefix + '.subduction_boundaries.%d.xy' % iage)
        else:
            file = os.path.join(path, prefix + '.subduction_boundaries.%d.xy' % iage)
        if not os.path.exists(file):
            print(dt.now(), 'make_overlay_ps: WARN: file missing: %(file)s' % vars())
        else:
            cmd='gmt psxy -V %(file)s -R%(R)s -J%(J)s -B%(B)s -W3/0/0/0 -m -K -O >> %(ps)s' % vars()
            if verbose: print(dt.now(), 'make_overlay_ps: cmd =', cmd)
            os.system(cmd)

        # slab
        if prefix.startswith('/'):
            file = os.path.join('', prefix + '.slab_edges_trench.%d.xy' % iage)
        else:
            file = os.path.join(path, prefix + '.slab_edges_trench.%d.xy' % iage)
        if not os.path.exists(file):
            print(dt.now(), 'make_overlay_ps: WARN: file missing: %(file)s' % vars())
        else:
            cmd='gmt psxy -V %(file)s -R%(R)s -J%(J)s -B%(B)s -W3/0/0/0 -m -K -O >> %(ps)s' % vars()
            if verbose: print(dt.now(), 'make_overlay_ps: cmd =', cmd)
            os.system(cmd)

        # network
        if prefix.startswith('/'):
            file = os.path.join('', prefix + '.network_subduction_boundaries.%d.xy' % iage)
        else:
            file = os.path.join(path, prefix + '.network_subduction_boundaries.%d.xy' % iage)
        if not os.path.exists(file):
            print(dt.now(), 'make_overlay_ps: WARN: file missing: %(file)s' % vars())
        else:
            cmd='gmt psxy -V %(file)s -R%(R)s -J%(J)s -B%(B)s -W3/0/0/0 -m -K -O >> %(ps)s' % vars()
            if verbose: print(dt.now(), 'make_overlay_ps: cmd =', cmd)
            os.system(cmd)


    # sR for all types of Topologies
    if figure.get('overlay_subduction_boundaries_sR') :
        prefix = figure['overlay_subduction_boundaries_sR']

        # platepolygons
        if prefix.startswith('/'):
            file = os.path.join('', prefix + '.subduction_boundaries_sR.%d.xy' % iage)
        else: 
            file = os.path.join(path, prefix + '.subduction_boundaries_sR.%d.xy' % iage)
        if not os.path.exists(file):
            print(dt.now(), 'make_overlay_ps: WARN: file missing: %(file)s' % vars())
        else:
            cmd='gmt psxy -V %(file)s -R%(R)s -J%(J)s -B%(B)s -W5/black -Sf0.2i/0.05irt -m -K -O >> %(ps)s' % vars()
            if verbose: print(dt.now(), 'make_overlay_ps: cmd =', cmd)
            os.system(cmd)

        # slab
        if prefix.startswith('/'):
            file = os.path.join('', prefix + '.slab_edges_leading_sR.%d.xy' % iage)
        else: 
            file = os.path.join(path, prefix + '.slab_edges_leading_sR.%d.xy' % iage)
        if not os.path.exists(file):
            print(dt.now(), 'make_overlay_ps: WARN: file missing: %(file)s' % vars())
        else:
            cmd='gmt psxy -V %(file)s -R%(R)s -J%(J)s -B%(B)s -W5/red -Sf0.2i/0.05irt -m -K -O >> %(ps)s' % vars()
            if verbose: print(dt.now(), 'make_overlay_ps: cmd =', cmd)
            os.system(cmd)

        # network
        if prefix.startswith('/'):
            file = os.path.join('', prefix + '.network_subduction_boundaries_sR.%d.xy' % iage)
        else: 
            file = os.path.join(path, prefix + '.network_subduction_boundaries_sR.%d.xy' % iage)
        if not os.path.exists(file):
            print(dt.now(), 'make_overlay_ps: WARN: file missing: %(file)s' % vars())
        else:
            cmd='gmt psxy -V %(file)s -R%(R)s -J%(J)s -B%(B)s -W5/black -Sf0.2i/0.05irt -m -K -O >> %(ps)s' % vars()
            if verbose: print(dt.now(), 'make_overlay_ps: cmd =', cmd)
            os.system(cmd)

    # sL for all types of Topologies
    if figure.get('overlay_subduction_boundaries_sL') :
        prefix = figure['overlay_subduction_boundaries_sL']

        # platepolygons
        if prefix.startswith('/'):
            file = os.path.join('', prefix + '.subduction_boundaries_sL.%d.xy' % iage)
        else:
            file = os.path.join(path, prefix + '.subduction_boundaries_sL.%d.xy' % iage)
        if not os.path.exists(file):
            print(dt.now(), 'make_overlay_ps: WARN: file missing: %(file)s' % vars())
        else:
            cmd='gmt psxy -V %(file)s -R%(R)s -J%(J)s -B%(B)s -W5/black -Sf0.2i/0.05ilt -m -K -O >> %(ps)s' % vars()
            if verbose: print(dt.now(), 'make_overlay_ps: cmd =', cmd)
            os.system(cmd)

        # slab
        if prefix.startswith('/'):
            file = os.path.join('', prefix + '.slab_edges_leading_sL.%d.xy' % iage)
        else: 
            file = os.path.join(path, prefix + '.slab_edges_leading_sL.%d.xy' % iage)
        if not os.path.exists(file):
            print(dt.now(), 'make_overlay_ps: WARN: file missing: %(file)s' % vars())
        else:
            cmd='gmt psxy -V %(file)s -R%(R)s -J%(J)s -B%(B)s -W5/red -Sf0.2i/0.05ilt -m -K -O >> %(ps)s' % vars()
            if verbose: print(dt.now(), 'make_overlay_ps: cmd =', cmd)
            os.system(cmd)

        # network
        if prefix.startswith('/'):
            file = os.path.join('', prefix + '.network_subduction_boundaries_sL.%d.xy' % iage)
        else: 
            file = os.path.join(path, prefix + '.network_subduction_boundaries_sL.%d.xy' % iage)
        if not os.path.exists(file):
            print(dt.now(), 'make_overlay_ps: WARN: file missing: %(file)s' % vars())
        else:
            cmd='gmt psxy -V %(file)s -R%(R)s -J%(J)s -B%(B)s -W5/black -Sf0.2i/0.05ilt -m -K -O >> %(ps)s' % vars()
            if verbose: print(dt.now(), 'make_overlay_ps: cmd =', cmd)
            os.system(cmd)

    # Ridges and Transforms
    if figure.get('overlay_ridge_transform_boundaries') :
        prefix = figure['overlay_ridge_transform_boundaries']

        # platepolygons
        if prefix.startswith('/'):
            file = os.path.join('', prefix + '.ridge_transform_boundaries.%d.xy' % iage)
        else:
            file = os.path.join(path, prefix + '.ridge_transform_boundaries.%d.xy' % iage)

        if not os.path.exists(file):
            print(dt.now(), 'make_overlay_ps: WARN: file missing: %(file)s' % vars())
        else:
            cmd='gmt psxy -V %(file)s -R%(R)s -J%(J)s -B%(B)s -W3/green -m -K -O >> %(ps)s' % vars()
            if verbose: print(dt.now(), 'make_overlay_ps: cmd =', cmd)
            os.system(cmd)

        # slab
        if prefix.startswith('/'):
            file = os.path.join('', prefix + '.slab_edges_side.%d.xy' % iage)
        else:
            file = os.path.join(path, prefix + '.slab_edges_side.%d.xy' % iage)

        if not os.path.exists(file):
            print(dt.now(), 'make_overlay_ps: WARN: file missing: %(file)s' % vars())
        else:
            cmd='gmt psxy -V %(file)s -R%(R)s -J%(J)s -B%(B)s -W3/green -m -K -O >> %(ps)s' % vars()
            if verbose: print(dt.now(), 'make_overlay_ps: cmd =', cmd)
            os.system(cmd)

        # network
        if prefix.startswith('/'):
            file = os.path.join('', prefix + '.network_ridge_transform_boundaries.%d.xy' % iage)
        else:
            file = os.path.join(path, prefix + '.network_ridge_transform_boundaries.%d.xy' % iage)

        if not os.path.exists(file):
            print(dt.now(), 'make_overlay_ps: WARN: file missing: %(file)s' % vars())
        else:
            cmd='gmt psxy -V %(file)s -R%(R)s -J%(J)s -B%(B)s -W3/green -m -K -O >> %(ps)s' % vars()
            if verbose: print(dt.now(), 'make_overlay_ps: cmd =', cmd)
            os.system(cmd)



    #
    # GPlates velocity xy data vector
    #
    if figure.get('overlay_gplates_velocity_xy') :
        prefix = figure['overlay_gplates_velocity_xy']
        if prefix.startswith('/'):
            file = os.path.join('', prefix + '.%d.xy' % iage)
        else:
            file = os.path.join(path, prefix + '.%d.xy' % iage)
        if not os.path.exists(file):
            print(dt.now(), 'make_overlay_ps: WARN: file missing: %(file)s' % vars())
        cmd='gmt psxy -V %(file)s -R%(R)s -J%(J)s -B%(B)s -W3/green -m -K -O >> %(ps)s' % vars()
        if verbose: print(dt.now(), 'make_overlay_ps: cmd =', cmd)
        os.system(cmd)

    # 
    # Mesh on plate frame coordinates; mesh moves with plate
    # 
    if figure.get('overlay_mesh_on_plates') :
        # set path
        path = figure.get('overlay_gplates_xy_path')
        if path == None:
            path = './'
        # parse string for plate ids
        list = figure['overlay_mesh_on_plates'].split(',')
        for prefix in list:

            if prefix.startswith('/'):
               path = ''

            # create full file path
            file = os.path.join(path, prefix + '.%d.xy' % iage)
            if not os.path.exists(file):
                print(dt.now(), 'make_overlay_ps: WARN: file missing: %(file)s' % vars())
                continue # to next file

            # locate the color
            pid = prefix[ prefix.rfind('.')+1: ]
            color = PlatesColorTable.get_color(pid)

            # color correct 
            if color.upper() == 'YELLOW':
                color = 'dark' + color 

            if file.find('plate_frame') != -1:
                cmd_prefix = 'cut -d" " -f 1-2 %(file)s | ' % vars()
                cmd= cmd_prefix + 'psxy -V -R%(R)s -J%(J)s -B%(B)s -Sd3p -W2/%(color)s -m -K -O >> %(ps)s' % vars()
                if verbose: print(dt.now(), 'make_overlay_ps: cmd =', cmd)
                os.system(cmd)
            else:
                cmd= 'gmt psxy -V %(file)s -R%(R)s -J%(J)s -B%(B)s -Sd3p -W2/%(color)s -m -K -O >> %(ps)s' % vars()
                if verbose: print(dt.now(), 'make_overlay_ps: cmd =', cmd)
                os.system(cmd)

    # 
    # mesh on globe frame coordinates ; fixed citcoms mesh
    # 
    if figure.get('overlay_citcoms_mesh'):
        # set path
        path = figure.get('overlay_gplates_xy_path')
        if path == None:
            path = './'
        # parse string for plate ids
        list = figure['overlay_citcoms_mesh'].split(',')
        for prefix in list:
            if prefix.startswith('/'):
               path = ''
            # create full file path
            file = os.path.join(path, prefix + '.%d.xy' % iage)
            if not os.path.exists(file):
                print(dt.now(), 'make_overlay_ps: WARN: file missing: %(file)s' % vars())
                continue # to next file

            # locate the color
            pid = prefix[ prefix.rfind('.')+1: ]
            color = PlatesColorTable.get_color(pid)

            # color correct 
            if color.upper() == 'YELLOW':
                color = 'dark' + color 

            if file.find('plate_frame') != -1:
                cmd_prefix = 'cut -d" " -f 3-4 %(file)s | ' % vars()
                cmd= cmd_prefix + 'psxy -V -R%(R)s -J%(J)s -B%(B)s -Sc3p -W2/%(color)s -m -K -O >> %(ps)s' % vars()
                if verbose: print(dt.now(), ' FIX FIX FIX ')
                if verbose: print(dt.now(), 'make_overlay_ps: cmd =', cmd)
                if verbose: print(dt.now(), ' FIX FIX FIX ')
                os.system(cmd)
            else:
                print(dt.now(), 'make_overlay_ps: WARN: file not in proper format: %(file)s' % vars())
                continue # to next file
   
    #
    # Plate Polygons
    #
    if figure.get('overlay_platepolygon_boundaries'):
        # set path
        path = figure.get('overlay_gplates_xy_path')
        if path == None:
            path = './'

        # parse string for plate ids
        list = figure['overlay_platepolygon_boundaries'].split(',')
        for prefix in list:

            # create full file path
            file = os.path.join(path, prefix + '.%d.xy' % iage)
            if not os.path.exists(file):
                print(dt.now(), 'make_overlay_ps: WARN: file missing: %(file)s' % vars())
                continue # to next file

            # locate the color
            pid = prefix[ prefix.rfind('.')+1: ]
            color = PlatesColorTable.get_color(pid)

            # COLOR Correct 
            if color.upper() == 'YELLOW':
                color = 'dark' + color 

            # COLOR Correct 
            if figure.get('overlay_platepolygon_color'):
                color = figure.get('overlay_platepolygon_color')
            
            cmd='gmt psxy -V %(file)s -R%(R)s -J%(J)s -B%(B)s -W2/%(color)s -m -K -O >> %(ps)s' % vars()
            if verbose: print(dt.now(), 'make_overlay_ps: cmd =', cmd)
            os.system(cmd)

#=====================================================================
def make_overlay_tracers(figure):
    '''from figure data, process tracer options, and call psxy to plot ddots'''

    R = figure['region']
    J = figure['projection']
    ps = figure['output_file'] 

    # read in all tracer data
    tracer_dict = \
        PlotUtilities.read_citcoms_tracers_into_dictionary(figure)

    # set colors 
    color_list = []
    if figure.get('overlay_tracers_flavor_color_list'):
        color_list = figure.get('overlay_tracers_flavor_color_list').split(',')
        if len(color_list) != len( list(tracer_dict.keys()) ):
            msg = 'Only %d color entry found in "overlay_tracers_flavor_color_list".  Expected %d, one per tracer flavor.' % (len(color_list), len( list(tracer_dict.keys()) ))
            raise IndexError(msg)
    else:
        color_list = [ 'green' for i in list(tracer_dict.keys()) ]

    # set sizes
    size_list = []
    if figure.get('overlay_tracers_flavor_size_list'):
        size_list = figure.get('overlay_tracers_flavor_size_list').split(',')
        if len(size_list) != len( list(tracer_dict.keys()) ):
            msg = 'Only %d size entry found in "overlay_tracers_flavor_size_list".  Expected %d, one per tracer flavor.' % (len(size_list), len( list(tracer_dict.keys()) ))
            raise IndexError(msg)
    else:
        size_list = [ '1' for i in list(tracer_dict.keys()) ]



    map_type_list_key = None

    if figure['type'] == 'map':
        map_type_list_key = 'latlon'

    elif figure['type'] == 'cross_section':
        map_type_list_key = None
        return

    elif figure['type'] == 'annulus':
        return

    else : 
        return

    # loop over tracer dictionary
    for (n, i) in enumerate( tracer_dict.keys() ): 

        # set color value from list
        W = '%s/%s' % ( size_list[n], color_list[n] )

        # if this tracer flavor is empty , continue 
        if tracer_dict[i]['flavor'] == None:
            continue # to next index

        list = tracer_dict[i][map_type_list_key]

        # write the filtered results an xy file
        name = 'tracer_tmp.xy'
        out = open(name, 'w')
        for t in list:
            out.write('%f %f\n' % ( t[0], t[1] ) ) # lat lon
        out.close()

        # build cmd
        cmd = 'gmt psxy %(name)s -R%(R)s -J%(J)s -Sc1p -W%(W)s -K -O >> %(ps)s' % vars()
        if verbose: print(dt.now(), 'make_overlay_tracers: cmd =', cmd)
        os.system(cmd)

        # remove tmp file
        cmd = 'rm -rf %(name)s' % vars()
        if verbose: print(dt.now(), 'make_overlay_tracers: cmd =', cmd)
        os.system(cmd)

#=====================================================================
#=====================================================================
def make_annulus(figure):
    '''make an annular plot'''

    set_grid_parameters(figure)
    set_radial_info(figure)
    make_annular_section(figure)
    make_cpt(figure)
    make_annular_plot(figure)

    # final clean up
    if not ( figure.get("keep_tmp_files") ): 
        cmd ='rm -vrf ' + ' '.join( figure['rm_list'] )
        if verbose: print(dt.now(), 'make_annulus: cmd=', cmd)
        os.system(cmd)
    else:
        if verbose: print(dt.now(), "make_annulus: DO NOT remove temporary files:")
        print("rm_list = ", figure['rm_list'])

#=====================================================================
def make_cross_sections_from_defs(figure):
    '''make a vertical Z vs Line section for any line'''

    section_defs = figure.get('cross_section_defs')
    sec_res = float(figure.get('sec_res'))

    # Read section definitions
    number_sections, sec_ids, sec_xyp_files, label_name = \
        mk_xyp_files(section_defs, sec_res)

    figure['number_sections'] = number_sections
    figure['sec_ids'] = sec_ids
    figure['sec_xyp_files'] = sec_xyp_files
    figure['label_name'] = label_name

    figure['rm_list'] += sec_xyp_files
    figure['rm_list'] += [ label_name ]

    if (figure['zone'] == '2D'):
        make_grids_from_slices(figure)
    else :
        make_xyz_and_grd_files_per_level(figure)
        make_cross_section_grd_files(figure)

#=====================================================================
def make_cross_sections_from_slice(figure):
    '''make a vertical Z vs. line section along a node line'''

    cap_list = figure.get('cap_list')
    xlist = figure.get('xlist')
    ylist = figure.get('ylist')
    zlist = figure.get('zlist')

    
#=====================================================================
def make_cross_sections(figure):
    '''make one or more cross section plots'''
    
    set_grid_parameters(figure)

    # check which type of section to make
    if figure.get('cross_section_defs'):
        make_cross_sections_from_defs(figure)
    elif figure.get('cap_list'):
        make_cross_sections_from_slice(figure)


    # color palet table
    make_cpt(figure)

    # plot the grid
    make_cross_section_plots(figure)

    # final clean up
    if not ( figure.get("keep_tmp_files") ): 
        cmd ='rm -vrf ' + \
         ' '.join( figure['rm_list'] ) + \
         ' '.join( figure['sec_xyp_files'] ) + \
         ' ' + figure['label_name']
        if verbose: print(dt.now(), 'make_cross_sections: cmd=', cmd)
        os.system(cmd)
    else:
        if verbose: print(dt.now(), "make_cross_sections: DO NOT remove temporary files:")
        print("rm_list = ", figure['rm_list'])

#=====================================================================
#=====================================================================
#=====================================================================
def make_xyz_and_grd_files_per_level(figure):
    '''create and return lists of GMT created files: ct, cv, gt, gv; and depths in km, and levels in node number + 1:'''
    # FIX: the looping 

    parameters = figure['parameters']
    parser = CitcomParser.Parser()
    parser.read( parameters )

    nodez = parser.getint('nodez')
    nodey = parser.getint('nodey')
    nodex = parser.getint('nodex')

    field = figure['field']  

    time = figure['time']  

    level = figure['level']
 
    # ensure that level depth is not 0
    if level == nodez:
        msg = 'Requested figure level (%s) == nodez (%s).' % (level, nodez)
        msg += 'Cannot process cross section data for depth of 0.'
        raise IndexError(msg)

    # compute section depth
    section_depth = PlotUtilities.get_depth_from_level(parameters,level)

    figure['section_depth'] = section_depth
    figure['zmax'] = 0
    figure['zmin'] = section_depth
   
    # empty lists
    ctfiles=[]
    cvifiles=[]
    cvefiles=[]
    gtfiles=[]
    gvifiles=[]
    gvefiles=[]
    depths=[]

    # defaults : FIX ?
    tension=0.1 # tension for GMT surface command

    grid_min = figure['grid_min']
    grid_max = figure['grid_max']

    bounds = figure['region']  # FIX RENAME

    res = '%(nodex)g+/%(nodey)g+' % vars()
    res = 1.0
    # NEEDS FIXING this should be controlable from input and sec_res/2
    res = 0.25

    # get vertical structure of model: list of tuples: (level,z,depth)
    # level ranges from 1 to nodez
    # z is the decimal fraction from bottom (< 1.0) to top (== 1.0)
    # depth is in km below surface.
    z_list = PlotUtilities.read_citcoms_coor_file_into_zlist(parameters)

    # loop over the vertical levels
    #i=0
    #while i < nodez:
    #    test_level = nodez-i 
    #    n = test_level - 1

    # loop over levels, downward
    z_list.reverse
    for (l,z,d) in z_list:

        if level <= l :

            depths.append(d)

            if verbose: 
                print(dt.now(), 'make_xyz_and_grd_files_per_level:',                     'level', level, '(', section_depth, 'km)',                    '<=',                    'level', l, '(', d, 'km)')


            if field.startswith('none'):
                continue # to next level

            if field.startswith('temp') \
            or field.startswith('visc') \
            or field.startswith('phase') \
            or figure.get('overlay_temperature'):

                # make xyz files:
                n = l - 1
                ctfile, cvifile, cvefile = \
                    PlotUtilities.read_combine_caps(parameters,time,n,field)

                ctfiles.append(ctfile)
                cvifiles.append(cvifile)
                cvefiles.append(cvefile)

            # make Temperature grd file:
            if field.startswith('temp'): 
                gtfile = mk_grd(ctfile, bounds, res, tension, grid_min, grid_max)
                gtfiles.append(gtfile)

            # make Viscosity grd file:
            if field.startswith('visc'): 
                gvifile = mk_grd(cvifile, bounds, res, tension, grid_min, grid_max)
                gvifiles.append(gvifile)

            # make Temperature grd file:
            if field.startswith('phase'): 
                gtfile = mk_grd(ctfile, bounds, res, tension, grid_min, grid_max)
                gtfiles.append(gtfile)

        # update counter
        #i += 1

    # update the figure data with depths used
    figure['depths'] = depths

    # update the figure data with lists of file names
    figure['ctfiles'] = ctfiles
    figure['cvifiles'] = cvifiles
    figure['cvefiles'] = cvefiles
    figure['gtfiles'] = gtfiles
    figure['gvifiles'] = gvifiles

    figure['rm_list'] += ctfiles + cvifiles + cvefiles + \
                         gtfiles + gvifiles

#=====================================================================
#=====================================================================
def make_cross_section_grd_files(figure):

    # figure details
    field = figure['field'] 
    section_depth = figure['section_depth'] 
    number_sections = figure['number_sections']  
    sec_ids = figure['sec_ids']  
    sec_xyp_files = figure['sec_xyp_files']  

    gtfiles = figure['gtfiles'] 
    gvifiles = figure['gvifiles'] 

    grid_min = figure['grid_min'] 
    grid_max = figure['grid_max'] 

    depths = figure['depths'] 

    # empty lists
    temp_sec_grd_files=[]
    visc_sec_grd_files=[]
    phase_sec_grd_files=[]

    figure['R']=[]
    figure['distances']=[]
    figure['ymax'] = [] 
    figure['ymin'] = []
    figure['zmin'] = []
    figure['zmax'] = []

    dist_max = 0.0

    # loop over cross sections
    for n in range(number_sections):

        xyp_file=sec_xyp_files[n]
        id = sec_ids[n]

        file = open(xyp_file)
        lines = file.read().splitlines()
        (lon, lat, dist) = lines[-1].split()
        dist = float(dist)
        if verbose: print(dt.now(), 'make_cross_section_grd_files: dist = %(dist)f' % vars())
        figure['distances'].append(dist)

        if(dist >= dist_max):
            dist_max=dist

        figure['ymin'].append(0)
        figure['ymax'].append(dist)
        figure['zmin'].append(0)
        figure['zmax'].append(section_depth)

        R = "0.0/%g/0.0/%d" % (dist_max,section_depth)
        figure['R'].append(R)

        if verbose: print(dt.now(), 'make_cross_section_grd_files: R = %s' % figure['R'] )
        
        # create a phase cross section grid
        if field.startswith('none'):
            continue # to next section

        # create a phase cross section grid
        elif field.startswith('phase'):
            print("ERROR.")

        # create temperature cross section grid
        elif field.startswith('temp'):
            prefix='temp'
            temp_sec_grd, temp_R, dist = mk_grd_sec( \
                id, prefix, section_depth, depths, gtfiles,   \
                xyp_file, grid_min, grid_max)

            temp_sec_grd_files.append(temp_sec_grd)
            figure['R'].append(temp_R)

        # create a viscosity cross section grid
        if field.startswith('visc'):
            prefix='visc'

            visc_sec_grd, visc_R, dist = mk_grd_sec( \
                id, prefix, section_depth, depths, gvifiles,  \
                xyp_file, grid_min, grid_max)

            visc_sec_grd_files.append(visc_sec_grd)
            figure['R'].append(visc_R)

        # overlay
        if figure.get('overlay_temperature'):
            prefix='temp'
            temp_sec_grd, temp_R, dist = mk_grd_sec( \
                id, prefix, section_depth, depths, gtfiles,   \
                xyp_file, grid_min, grid_max)
            temp_sec_grd_files.append(temp_sec_grd)

        # create a phase cross section grid
        if figure.get('overlay_phase'):
            print("ERROR.")

        # END of loop over sections

    if verbose: print(dt.now(), 'make_cross_section_grd_files: dist_max = %(dist_max)f' % vars())
  
    # update figure 
    figure['temp_sec_grd_files'] = temp_sec_grd_files
    figure['visc_sec_grd_files'] = visc_sec_grd_files
    figure['phase_sec_grd_files'] = phase_sec_grd_files
    figure['dist_max'] = dist_max

    figure['rm_list'] += temp_sec_grd_files + visc_sec_grd_files + phase_sec_grd_files 

#=====================================================================
#=====================================================================
#=====================================================================
def make_grids_from_slices( figure ):
    ''' FIX '''

    if verbose: print(dt.now(), 'make_grids_from_slices')

    # get a slice, make and set xslice_xyFOO files
    PlotUtilities.xslice_regional(figure)

    xyt = figure['xslice_xyt']
    xyv = figure['xslice_xyv']
    xyp = figure['xslice_xyp']

    rm_list = [xyt, xyv, xyp]

    nodez = figure['nodez']
    nodey = figure['nodey']
    nodex = figure['nodex']

    T = figure['grid_tension']
    field = figure['field']
    gmin = figure['grid_min'] 
    gmax = figure['grid_max']

    lon_min = figure['xslice_lon_min']
    lon_max = figure['xslice_lon_max']
    ymin = figure['xslice_ymin']
    ymax = figure['xslice_ymax']
    zmin = figure['xslice_zmin']
    zmax = figure['xslice_zmax']
    rmin = figure['xslice_rmin']
    rmax = figure['xslice_rmax']

    # empty lists
    figure['temp_sec_grd_files'] = []
    figure['visc_sec_grd_files'] = []
    figure['phase_sec_grd_files'] = []
    figure['ymin'] = []
    figure['ymax'] = []
    figure['zmin'] = []
    figure['zmax'] = []
    figure['rmin'] = []
    figure['rmax'] = []
    figure['R'] = []

    # loop over cross sections
    for n in range( figure['number_sections'] ):

        id = figure['sec_ids'][n]

        figure['ymin'].append(ymin)
        figure['ymax'].append(ymax)
        figure['zmin'].append(zmin)
        figure['zmax'].append(zmax)
        figure['rmin'].append(rmin)
        figure['rmax'].append(rmax)

        R = '%(lon_min)g/%(lon_max)g/%(rmin)g/%(rmax)g' % vars()
        figure['R'].append(R)

        plot_xres = .10 
        #plot_yres = .10
        #I = '%(plot_xres)g/%(plot_yres)g' % vars()
        I = '%(nodey)g+/%(nodez)g+' % vars()

        if field.startswith('temp') or figure.get('overlay_temperature'):

            # create the cross section temp grid
            xytm="%(xyt)s_median.xyz" % vars()
            cmd = "gmt blockmedian %(xyt)s -V -I%(I)s -R%(R)s > %(xytm)s" % vars()
            if verbose: print(dt.now(), 'make_grids_from_slices: temperature:')
            if verbose: print(dt.now(), 'make_grids_from_slices: cmd =', cmd)
            os.system(cmd)

            tgrd = xytm + '.grd'
            cmd = "gmt surface %(xytm)s -V -G%(tgrd)s -I%(I)s -R%(R)s -T%(T)g -Ll%(gmin)g -Lu%(gmax)g" % vars()
            if verbose: print(dt.now(), 'make_grids_from_slices: cmd =', cmd)
            os.system(cmd)

            rm_list += [xytm]

            figure['temp_sec_grd_files'].append(tgrd)

        if field.startswith('visc') or figure.get('overlay_viscosity'):
            # create the cross section visc grid 
            xyvm="%(xyv)s_median.xyz" % vars()
            cmd = "gmt blockmedian %(xyv)s -V -I%(I)s -R%(R)s > %(xyvm)s" % vars()
            if verbose: print(dt.now(), 'make_grids_from_slices: viscosity:')
            if verbose: print(dt.now(), 'make_grids_from_slices: cmd =', cmd)
            os.system(cmd)

            vgrd = xyvm + '.grd'
            if gmin != 'none' or gmax != 'none':
                cmd = "gmt surface %(xyvm)s -V -G%(vgrd)s -I%(I)s -R%(R)s -T%(T)g -Ll%(gmin)g -Lu%(gmax)g" % vars()
            else:
                cmd = "gmt surface %(xyvm)s -V -G%(vgrd)s -I%(I)s -R%(R)s -T%(T)g" % vars()
            if verbose: print(dt.now(), 'make_grids_from_slices: cmd =', cmd)
            os.system(cmd)

            figure['visc_sec_grd_files'].append(vgrd)
            rm_list += [xyvm]

        if field.startswith('phase') or figure.get('overlay_phase'):
            if verbose: print(dt.now(), 'make_grids_from_slices: phase:')
            # create the cross section phase grid 
            xypm="%(xyp)s_median.xyz" % vars()
            cmd = "gmt blockmedian %(xyp)s -V -I%(I)s -R%(R)s > %(xypm)s" % vars()
            if verbose: print(dt.now(), 'make_grids_from_slices: cmd =', cmd)
            os.system(cmd)
            gmin = figure['overlay_phase_gmin']
            gmax = figure['overlay_phase_gmax']

            pgrd = xypm + '.grd'
            cmd = "gmt surface %(xypm)s -V -G%(pgrd)s -I%(I)s -R%(R)s -T%(T)g -Ll%(gmin)g -Lu%(gmax)g" % vars()
            if verbose: print(dt.now(), 'make_grids_from_slices: cmd =', cmd)
            os.system(cmd)

            figure['phase_sec_grd_files'].append(pgrd)
            rm_list += [xypm]

    # clean up
    figure['rm_list'] += rm_list
#=====================================================================
#=====================================================================
#=====================================================================
#=====================================================================
#=====================================================================
#=====================================================================
def make_cross_section_plots(figure):
    '''invoke the GMT commands to draw the cross sections'''

    # get figure data
    field = figure['field']

    number_sections = figure['number_sections']  
    sec_ids = figure['sec_ids']  
    R = figure['R']  
    sec_xyp_files = figure['sec_xyp_files']  

    width = figure['mapwidth']
    section_height = 1.
    section_offset = 0.5
    section_shift = -1.0*(section_height + section_offset)

    # correction for square plots
    if figure.get('zone') == 'regional': 
        section_shift -= 1.5

    if figure['zone'] == '2D': 
        section_shift -= 3.5

    if figure.get('zone') == 'global': 
        section_shift -= 0.20

    B = figure['boundary']
    J = figure['projection']
    R = figure['region']

    rm_list = []

    title = figure['figure_title']

    # loop over cross sections
    for n in range(number_sections):

        id = sec_ids[n]

        dist_scale = 6.0 / figure['ymax'][n]
        dist_scale = 6.0 / figure['dist_max']
        #J = "x%g/%g" % (dist_scale,-1.*dist_scale)

        # NOTE : this might have to be changed , fixed , removed at some point ?
        # leave here for now ...
        #az_resolution = 0.5
        # grid_inc_az = figure.get('grid_increment_azimuth', 0.5)
        #r_resolution = (1.0 - .55) / 100
        #I = '%f/%f' % (az_resolution, r_resolution)

        if figure['zone'] == '2D':
            J = 'P%fa/-90' % figure['mapwidth']  # Polar
            B = 'a30f30/a0.05:.%(title)s:WeSN' % vars()
        else :
            J = "x%g/%g" % ( dist_scale/2, (-1.*dist_scale)/2)
            B = 'f200a1000/f50a400:%(id)s:WeSn' % vars()
        figure['J'] = J
        figure['B'] = B

        C = figure['cpt_file']
        l = figure['cpt_label']
        D = figure['D']
        R = figure['R'][n]
        X = figure['X']
        Y = section_shift
        ps = figure['output_file'] 

        # build cmd for base image
        if field.startswith('none'):
            cmd_prefix = 'psbasemap '

        elif field.startswith('temp'):
            f = figure['temp_sec_grd_files'][n]
            cmd_prefix = 'grdimage %(f)s -C%(C)s ' % vars()
            figure['rm_list'] += [f, C]

        elif field.startswith('visc'):
            f = figure['visc_sec_grd_files'][n]
            cmd_prefix = 'grdimage %(f)s -C%(C)s ' % vars()
            figure['rm_list'] += [f, C]

        elif field.startswith('phase'):
            f = figure['phase_sec_grd_files'][n]
            cmd_prefix = 'grdimage %(f)s -C%(C)s ' % vars()
            figure['rm_list'] += [f, C]

        # call cmd 
        cmd = cmd_prefix + '-B%(B)s -R%(R)s -J%(J)s -X%(X)s -Y%(Y)s -K -O >> %(ps)s' % vars()
        if verbose: 
            print(dt.now(), 'make_cross_section_plots: cmd=', cmd)
        os.system(cmd)


        # plot the cpt scale bar
        if n == 0 and not field.startswith('none'): 
            D = '6.85/0.5/3.25/0.2' # x/y/l/w of mid point

            if figure['zone'] == '2D':
                D = '6.85/0.0/3.25/0.2' # x/y/l/w of mid point

            cmd = 'gmt psscale -C%(C)s -D%(D)s -B%(l)s -K -O >> %(ps)s' % vars()
            if verbose: print(dt.now(), 'make_ps_plot: cmd=', cmd)
            os.system(cmd)
            figure['rm_list'] += [f, C]

        # overlay tests
        if figure.get('overlay_temperature'):
            d = id + '-temperature-contours.xy'
            f = figure['temp_sec_grd_files'][n]
            C = figure['overlay_temperature_cpt_file']

            cmd ='gmt grdcontour %(f)s -D%(d)s -M -C%(C)s -B%(B)s -R%(R)s -J%(J)s -W > /dev/null' % vars()
            if verbose: print(dt.now(), 'make_cross_section_plots: cmd=', cmd)
            os.system(cmd)

            cmd ='gmt psxy %(d)s -m -W3.0/0 -R%(R)s -J%(J)s -K -O >> %(ps)s' % vars()
            if verbose: print(dt.now(), 'make_cross_section_plots: cmd=', cmd)
            os.system(cmd)

            figure['rm_list'] += [d, f, C]


        if figure.get('overlay_phase'):
            d = id + '-phase-contours.xy'
            f = figure['phase_sec_grd_files'][n]
            C = figure['overlay_phase_cpt_file']

            cmd ='gmt grdcontour %(f)s -D%(d)s -M -C%(C)s -B%(B)s -R%(R)s -J%(J)s -V > /dev/null' % vars()
            if verbose: print(dt.now(), 'make_cross_section_plots: cmd=', cmd)
            os.system(cmd)

            cmd ='gmt psxy %(d)s -m -W3.0/0 -R%(R)s -J%(J)s -K -O >> %(ps)s' % vars()
            if verbose: 
                print(dt.now(), 'make_cross_section_plots: cmd=', cmd)
            os.system(cmd)

            figure['rm_list'] += [d, f, C]

       
        if figure.get('overlay_tracers'):
            make_cross_section_overlay_tracers( figure, n )

#=====================================================================

def make_cross_section_overlay_tracers(figure, index):
    '''Make ... '''

    J = figure['J']
    R = figure['R'][index]
    ps = figure['output_file']

    # create a (lon, lat) line from the section file
    line = 'tracer_tmp_line.d'
    line_out = open (line, 'w')
    sec_xyp_file = figure['sec_xyp_files'][index]
    file = open(sec_xyp_file)
    lines = file.read().splitlines()
    (lon0, lat0, dist0) = lines[0].split()
    (lon1, lat1, dist1) = lines[-1].split()
    for l in lines:
        (lon, lat, r) = l.split()
        line_out.write('%f %f\n' % (float(lon), float(lat)) )
    line_out.close()
    file.close()

    # distance from line to keep tracers
    dist = figure['overlay_tracers_dist_from_section']

    # read in all tracer data
    tracer_dict = \
        PlotUtilities.read_citcoms_tracers_into_dictionary(figure)

    # set colors 
    color_list = []
    if figure.get('overlay_tracers_flavor_color_list'):
        color_list = figure.get('overlay_tracers_flavor_color_list').split(',')
    else:
        color_list = [ 'black' for i in list(tracer_dict.keys()) ]

    # set sizes
    size_list = []
    if figure.get('overlay_tracers_flavor_size_list'):
        size_list = figure.get('overlay_tracers_flavor_size_list').split(',')
    else:
        size_list = [ '1' for i in list(tracer_dict.keys()) ]

    # loop over tracer dictionary flavors
    for (n, flav) in enumerate( tracer_dict.keys() ): 
        print(dt.now(), 'make_cross_section_overlay_tracers: flavor id =', flav)

        if tracer_dict[flav]['flavor'] == None:
            continue # to next flavor

        W = '%s/%s' % ( size_list[n], color_list[n] )

        # get list of tuples
        list = tracer_dict[flav]['latlondepth']
        print(dt.now(), 'make_cross_section_overlay_tracers: number of tracers =', len(list))

        tmp1 = 'tracer_tmp1'
        tmp2 = 'tracer_tmp2'
        tmp3 = 'tracer_tmp3'

        # write raw tracer list files
        tmp1_out = open (tmp1, 'w')
        for i in list:
            # switch to lon lat
            tmp1_out.write('%f %f %f\n' % (i[1], i[0], i[2]) )
        tmp1_out.close()

        # filter list with GMT select
        cmd = 'gmt gmtselect -V %(tmp1)s -L%(dist)s/%(line)s > %(tmp2)s' % vars()
        if verbose: 
            print(dt.now(), 'make_cross_section_overlay_tracers: cmd=', cmd)
        os.system(cmd)
        
        # project the tracers onto the section plane
        cmd = 'gmt project %(tmp2)s -C%(lon0)s/%(lat0)s -E%(lon1)s/%(lat1)s -Q -Fpz > %(tmp3)s' % vars()
        if verbose:
            print(dt.now(), 'make_cross_section_overlay_tracers: cmd=', cmd)
        os.system(cmd)
        
        # write the filtered results an xy file
        # build cmd
        cmd = 'gmt psxy -V %(tmp3)s -R%(R)s -J%(J)s -Sc1p -W%(W)s -K -O >> %(ps)s' % vars()
        if verbose: print(dt.now(), 'make_cross_section_overlay_tracers: cmd =', cmd)
        os.system(cmd)

        # clean up 
        cmd = 'rm -rf %(tmp1)s %(tmp2)s %(tmp3)s' % vars()
        if verbose: print(dt.now(), 'make_cross_section_overlay_tracers: cmd =', cmd)
        os.system(cmd)

    cmd = 'rm -rf %(line)s' % vars()
    if verbose: print(dt.now(), 'make_cross_section_overlay_tracers: cmd =', cmd)
    os.system(cmd)

#===================================================================== #=====================================================================
#=====================================================================
def make_cross_section_lines(figure):
    '''create line data for plotting lith_age_depth & temp sections'''
    x_lad_1 = 0.0
    z_lad_1 = lith_age_depth
    x_lad_2 = dist_max
    z_lad_2 = lith_age_depth
    LAD = open('lad.xy','w')
    print(">", file=LAD)
    print("%g %g" % (x_lad_1,z_lad_1), file=LAD)
    print("%g %g" % (x_lad_2,z_lad_2), file=LAD)
    LAD.close()
#=====================================================================
def lith_age_depth(figure):
    x_lad_1 = 0.0
    z_lad_1 = lith_age_depth
    x_lad_2 = dist_max
    z_lad_2 = lith_age_depth
    LAD = open('lad.xy','w')
    print(">", file=LAD)
    print("%g %g" % (x_lad_1,z_lad_1), file=LAD)
    print("%g %g" % (x_lad_2,z_lad_2), file=LAD)
    LAD.close()
#=====================================================================
#=====================================================================
def get_great_circle_proj(gcspec):
    '''parse a slash delimited great circle specification: if three values are found, interpret as point and angle: lon/lat/azimuth; if four values are found, interpret as two points: p1lon/p1lat/p2lon/p2lat.'''

    from math import pi, sin, cos, tan, atan

    # parse great circle spec into list of values
    list = gcspec.split('/')
    
    lon = float(list[0])
    lat = float(list[1])
    # build intinal string for GMT's project cmd
    spoint = '-C%f/%f -L-180/180' % (lon, lat)

    # compute azimuth from value or p2

    if len(list) == 3 : 
        az = float(list[2])
        # complete cmd option string
        proj = '%s -A%f' % (spoint, az)

    elif len(list) == 4 : 
        elon = float(list[2])
        elat = float(list[3])
        r2d = 180.0 / pi
        ## transfer to azimuth mode
        b = (90 - elat) / r2d
        a = (90 - lat) / r2d
        delta = (elon - lon) / r2d
        if abs(lat) == 90:
            ## on the pole
            print('pole cannot be the starting point.')
        elif (elon - lon) % 180 == 0:
            ## on the same meridian
            az = 0
        elif lat == 0 and elat == 0:
            ## on the equator
            az = 90
        else:
            az = atan((sin(a)/tan(b) - cos(a)*cos(delta)) / sin(delta))
            az = 90 - r2d * az

        # complete cmd option string
        proj = '%s -A%f' % (spoint, az)

        # TEST code
        # p1 = (lon, lat)
        # p2 = (elon, elat)
        # res = .5
        # out = 'GC-OUT-FILE-TEST.xy'
        # make_great_circle_arc(p1,p2,res,out)

    # return command line option string 
    return proj

#=====================================================================

def get_capfile(modelname, cap, step):
    '''generate a capfile name'''
    return '%s.cap%02d.%d' % (modelname, cap, int(step))

#=====================================================================

def get_optfile(modelname, cap, step):
    '''generate an opt name'''
    return '%s.opt%02d.%d' % (modelname, cap, step)

#=====================================================================

def get_radii_list(modelname, step):
    '''get and return a list of model radii'''

    ### get nodez ###
    capfile = get_capfile(modelname, 0, step)
    data = open(capfile)
    header = data.readline()
    nodex, nodey, nodez = header.split('x')
    nodez = int(nodez)

    ### read z coordinate ###
    radii_list = list(range(nodez))
    for i in range(nodez):
        radii_list[i] = float(data.readline().split()[2])

    data.close()

    return radii_list

#=====================================================================
def set_radial_info(figure):
    '''set radial info'''

    modelname = figure['modelname']
    step = figure['time']
    nodez = figure['nodez']

    # set min and max
    min = 1
    max = int(nodez)

    if figure.get('level_min') != None:
        min = int(figure.get('level_min'))
    else :
        figure['level_min'] = min 

    if figure.get('level_max') != None:
        max = int(figure.get('level_max'))
    else :
        figure['level_max'] = max

    if verbose: 
        print(dt.now(), 'set_radial_info: level_min = %(min)s' % vars())
        print(dt.now(), 'set_radial_info: level_max = %(max)s' % vars())

    # get the full radii_list 
    radii_list = get_radii_list(modelname, figure['time'])
    if verbose: 
        print(dt.now(), 'set_radial_info: radii_list values =', radii_list)
    figure['radii_list'] = radii_list
 
#=====================================================================

def make_great_circle_path(gcproj, grid_increment_azimuth):
    '''from a projection string, create a full globe great circle path file'''

    # NOTE: for km, please see -Q option of project

    # output file 
    gcfile = 'circle.xyp'

    # create great circle path #
    cmd = 'gmt project %(gcproj)s -G%(grid_increment_azimuth)s > %(gcfile)s' % vars()
    if verbose: 
        print(dt.now(), 'make_great_circle_path: cmd=', cmd)
    os.system(cmd)

    return gcfile
    
#=====================================================================
def make_great_circle_arc(p1, p2, resolution, outfile):
    '''from two end points, tuples of (lon/lat), and a resolution value generate a great circle limited arc file'''

    # get lon/lat components 
    p1lon = p1[0]
    p1lat = p1[1]

    p2lon = p2[0]
    p2lat = p2[1]

    cmd = 'gmt project -C%(p1lon)s/%(p1lat)s -E%(p2lon)s/%(p2lat)s -G%(resolution)s > %(outfile)s' % vars()
    if verbose: 
        print(dt.now(), 'make_great_circle_arc: cmd=', cmd)
    os.system(cmd)

#=====================================================================

def make_annular_section(figure):
    '''create cross section along the great circle'''

    modelname = figure['modelname']
    parameters = figure['parameters']
    field = figure['field']
    time = figure['time']
    nodez = figure['nodez']
    gcfile = figure['great_circle_file']
    radii_list = figure['radii_list']

    # set grid info 
    grid_inc_az = figure.get('grid_increment_azimuth', 0.5)
    grid_min = figure['grid_min']
    grid_max = figure['grid_max']

    # set min and max
    min = 0
    max = int(nodez)

    if figure.get('level_min') != None:
        min = int(figure.get('level_min'))

    if figure.get('level_max') != None:
        max = int(figure.get('level_max'))

    if verbose: 
        print(dt.now(), 'make_annular_section: level_min = %(min)s' % vars())
        print(dt.now(), 'make_annular_section: level_max = %(max)s' % vars())

    figure['botlayer'] = min - 1
    figure['toplayer'] = max - 1

    xsectfile = '%s.xsect.%d.xy%s' % (modelname, int(time), field)
    bounds = '0/360/-90/90'

    # clean up
    figure['rm_list'] += [gcfile]
    # FIX : add  xsectfile to remove list ? 


    # super short cut for field == none
    if field.startswith('none'): 
        figure['annular_xsection_file'] = None
        return

    # open cross section file
    out = open(xsectfile,'w')
    if verbose: print(dt.now(), 'open %(xsectfile)s' % vars())

    # loop over levels
    for z in range(min - 1 , max, 1):
        if verbose: print()
        if verbose: print(dt.now(), 'make_annular_section: LOOP over levels: z = ', z)

        # create a combined file, a meadian file and grdfile 
        xyzfile = '%s.%d.z%03d.xyz' % (modelname, int(time), z)
        medfile = '%s.%d.z%03d.median' % (modelname, int(time), z)
        grdfile = '%s.%d.z%03d.grd' % (modelname, int(time), z)

        # determine how to build the xyz_file from field type

        if field.startswith('temp'): 
            xyzfile = PlotUtilities.cap_to_xyTemperature(parameters,time,z)
        elif field.startswith('visc'): 
            xyzfile = PlotUtilities.cap_to_xyViscosity(parameters,time,z)
        elif field.startswith('comp'): 
            xyzfile = PlotUtilities.cap_to_xyComposition(parameters,time,z)
        else :
            msg = 'Unknown field name: cannot greate grids. '
            msg += 'Please use -h for help.'
            raise ValueError(msg)

        # smooth the data
        cmd = 'gmt blockmedian %(xyzfile)s -V -I%(grid_inc_az)s -R%(bounds)s > %(medfile)s' % vars()
        if verbose: print(dt.now(), 'make_annular_section: cmd =', cmd)
        os.system(cmd)


        # surface the data
        cmd = 'gmt surface %(medfile)s -V -I%(grid_inc_az)s -G%(grdfile)s -R%(bounds)s -N1 -Ll%(grid_min)s -Lu%(grid_max)s' % vars()
        if verbose: print(dt.now(), 'make_annular_section: cmd =', cmd)
        os.system(cmd)

        # sample the level grdfile along the great circle
        cmd = 'gmt grdtrack -V %(gcfile)s -G%(grdfile)s -Lg' % vars()
        if verbose: print(dt.now(), cmd)
        xyptfp = os.popen(cmd)

        # clean up
        figure['rm_list'] += [medfile, grdfile, xyzfile]
         
        # write the sampled results (azimuth, r, temp) to an xect file
        for line in xyptfp.readlines():
            xypt = line.split()
            out.write('%s\t%f\t%s\n' % (xypt[2],radii_list[z],xypt[3]) )
        xyptfp.close()

        # end of loop over levels

    out.close()

    figure['annular_xsection_file'] = xsectfile

#=====================================================================
#=====================================================================
def make_annular_plot(figure):
    '''create a polar coordinate plot of the xsection
       ## TODO: there is always a gap on the left side of the annulus. 
       ## How to fix it?'''

    radii_list = figure['radii_list']
    toplayer = figure['toplayer']
    botlayer = figure['botlayer']

    grid_min = figure['grid_min']
    grid_max = figure['grid_max']

    C = figure['cpt_file']
    l = figure['cpt_label']
    B = figure['boundary']
    R = figure['region']
    J = figure['projection']

    mw = (figure['mapwidth'] * 0.70)

    X = figure['X'] 
    Y = float(figure['Y'])

    if figure['id'] == 'B' :
        Y = (float(figure['Y']) - 1.00)
    if figure['id'] == 'D' :
        Y = (float(figure['Y']) - 1.00)

    #yshift = mapwidth * 1.2
    D = figure['D']
    ps = figure['output_file']
    xs = figure['annular_xsection_file']

    # super short cut
    if xs == None:
        return

    # the output grid
    grdfile2 = 'xsection.grd'

    # set the mixed grid increment values for azimuth ... 
    grid_inc_az = figure.get('grid_increment_azimuth', 0.5)

    # ... and radial directions
    grid_inc_r_def = (radii_list[toplayer] - radii_list[botlayer]) / 100
    grid_inc_r = figure.get('grid_increment_radial', grid_inc_r_def)

    I = '%f/%f' % ( float(grid_inc_az), float(grid_inc_r) )

    # set the region to be an annular ring
    R = '-180/180/%f/%f' % (radii_list[botlayer], radii_list[toplayer])

    # surface the grid
    cmd = 'gmt surface %(xs)s -V -G%(grdfile2)s -I%(I)s -R%(R)s -Ll%(grid_min)s -Lu%(grid_max)s' % vars()
    if verbose: print(dt.now(), 'make_annular_plot: cmd=', cmd)
    os.system(cmd)

    cmd = 'gmt grdimage %(grdfile2)s -V -C%(C)s -JP%(mw)fa -B%(B)s -R%(R)s -X%(X)s -Y%(Y)s -P -O -K >> %(ps)s' % vars()
    if verbose: print(dt.now(), 'make_annular_plot: cmd=', cmd)
    os.system(cmd)

    # plot the cpt scale bar
    cmd = 'gmt psscale -C%(C)s -D%(D)s -B%(l)s -K -O >> %(ps)s' % vars()
    if verbose: print(dt.now(), 'make_ps_plot: cmd=', cmd)
    os.system(cmd)

    # clean up
    figure['rm_list'] += [grdfile2, xs]

#=====================================================================
#=====================================================================
#=====================================================================
def start_gmt(settings, page):
    '''establish or adjust gmt defaults'''

    title = page['page_title']
    n = page['page_number']
    out = page['output_file']

    # clean up
    # remove default .gmt* files from local directory
    cmd = "rm -rf .gmt*"

    if verbose: print(dt.now(), 'start_gmt:')
    if verbose: print(dt.now(), cmd)
    os.system(cmd)


    # preliminary GMT cmds
    cmd = ''
    cmd += 'gmtset PAPER_MEDIA letter'
    if 'eps' in list(settings.keys()):
        cmd += '+'
    cmd += '\n'
    cmd += 'gmtset MEASURE_UNIT inch\n'
    cmd += 'gmtset X_ORIGIN 0\n'
    cmd += 'gmtset Y_ORIGIN 0\n'


    cmd += 'gmtset ANNOT_FONT_SIZE 9\n'
    cmd += 'gmtset ANNOT_FONT_SIZE_PRIMARY 9\n'
    cmd += 'gmtset ANNOT_FONT_SIZE_SECONDARY 9\n'
    cmd += 'gmtset HEADER_FONT_SIZE 9\n'
    cmd += 'gmtset LABEL_FONT_SIZE 9\n'

    if page.get('page_orientation') == 'portrait':
        cmd += 'gmtset PAGE_ORIENTATION portrait\n'
        cmd += 'gmtset X_AXIS_LENGTH 8.0\n'
        cmd += 'gmtset Y_AXIS_LENGTH 11.0\n'
    else:
        cmd += 'gmtset Y_AXIS_LENGTH 8.0\n'
        cmd += 'gmtset X_AXIS_LENGTH 11.0\n'

    cmd += 'gmtset UNIX_TIME FALSE\n'
    cmd += 'gmtset UNIX_TIME_POS 0/0\n'
    cmd += 'gmtset HISTORY FALSE\n'
     
    # colors
    cmd += 'gmtset COLOR_BACKGROUND green\n'
    cmd += 'gmtset COLOR_FOREGROUND orange\n'
    cmd += 'gmtset COLOR_NAN purple\n'

    if verbose: print(dt.now(), 'start_gmt:\n')
    if verbose: print(dt.now(), cmd)
    os.system(cmd)

    # create a simple .txt file
    if page.get('ouput_file_add_page_number') :
        # page number already in out
        name = '.'.join([out, 'header', 'txt'])
    else: 
        # page number needed
        name = '.'.join([out, 'header_page_%06d' % n, 'txt'])

    # open the file 
    if verbose: print(dt.now(), 'start_gmt:\n')
    if verbose: print(dt.now(), 'write:', name)
    
    try:
        file = open(name, 'w')
    except Exception as e:
        print("I/O error: {}".format(e))
        raise

    # write the text file
    if page.get('page_orientation') == 'landscape':
        print('5.5 8.0 18 0 0 CT %(title)s' % vars(), file=file)
    elif page.get('page_orientation') == 'portrait':
        print('4.25 10.5 18 0 0 CT %(title)s' % vars(), file=file)

    file.close()
 
    # call pstext with the txt file 
    cmd = 'gmt pstext %(name)s -N -G0 -W255 -Jx1.0/1.0 ' % vars()

    if page.get('page_orientation') == 'portrait':
        cmd += '-R0/8.5/0/11.0 -P '
    else: 
        cmd += '-R0/11.0/0/8.5 '

    cmd += '-K > %(out)s' % vars()

    if verbose: print(dt.now(), 'start_gmt: cmd=', cmd)
    os.system(cmd)

    # clean up 
    cmd = 'rm -rf %(name)s' % vars()
    if verbose: print(dt.now(), 'end_gmt: cmd =', cmd)
    os.system(cmd)

#=====================================================================

def end_gmt(settings, page):
    '''add text to the page and close off ps drawing with final -O'''

    n = page['page_number']
    out = page['output_file']

    # create a simple .txt file
    if page.get('ouput_file_add_page_number') :
        # page number already in out
        name = '.'.join([out, 'footer', 'txt'])
    else: 
        # page number needed
        name = '.'.join([out, 'footer_page_%06d' % n, 'txt'])

    # open the file 
    if verbose: print(dt.now(), 'write:', name)
    try :
        file = open(name, 'w')
    except IOError as e:
        print("I/O error({}): {}".format(e.errno, e.strerror))
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise

    # position the text relative to the last figure drawn
    x = '0'
    y = '0'
    if page.get('page_orientation') == 'landscape':
        if len(page['figure_keys']) == 1:
            x = '9.0'
            y = '-1.75'
        elif len(page['figure_keys']) == 4:
            x = '0.0'
            y = '-1.0'
    elif page.get('page_orientation') == 'portrait':
        if len(page['figure_keys']) == 2:
            x = '7.0'
            y = '-0.5'
        elif len(page['figure_keys']) == 4:
            x = '-2.5'
            y = '-0.5'


    # write the text file
    print('%(x)s %(y)s 12 0 0 CB Page %(n)s' % vars(), file=file)

    file.close()
 
    # call pstext with the txt file 
    cmd = 'gmt pstext %(name)s -N -G0 -W255 -Jx1.0/1.0 ' % vars()

    if page.get('page_orientation') == 'portrait':
        cmd += '-R0/8.5/0/11.0 -P '
    else: 
        cmd += '-R0/11.0/0/8.5 '

    cmd += '-O >> %(out)s' % vars()

    if verbose: print(dt.now(), 'end_gmt:', cmd)
    os.system(cmd)

    # clean up 
    cmd = 'rm -rf %(name)s' % vars()
    if verbose: print(dt.now(), 'end_gmt:', cmd)
    os.system(cmd)

#=====================================================================
def citcoms_tracer_2_gmt(citcoms_tracer_file_name):

    r2d = 180.0/math.pi
    d2r = 1.0/r2d

    print(citcoms_tracer_file_name)

    gmt_tracer_file_name = "%s.xy" % citcoms_tracer_file_name

    ifile=open(citcoms_tracer_file_name)
    ofile=open(gmt_tracer_file_name,"w")

    line=ifile.readline()
    #snstep, sntracers, sncol, stime = line.split()
    sntracers, sncol = line.split()
    ncol = int(sncol)
    print(' ncol = ', ncol)
    while 1:
        line=ifile.readline()
        if(line):
            if(ncol == 3):
                stheta, sphi, sradius = line.split()
                lat = 90. - float(stheta)*r2d
                lon = float(sphi)*r2d
                ofile.write(">\n")
                ofile.write("%g  %g  %s\n" % (lon,lat,sradius) )
            if(ncol == 4):
                stheta, sphi, sradius, szvalue = line.split()
                lat = 90. - float(stheta)*r2d
                lon = float(sphi)*r2d
                ofile.write(">\n")
                ofile.write("%g  %g  %s  %s\n" % (lon,lat,sradius,szvalue) )
        else:
            break

    ifile.close()
    ofile.close()

    return gmt_tracer_file_name
#=====================================================================
#=====================================================================
def check_figure_references(page):
    '''check for inter figure references'''

    figure_keys = page['figure_keys']

    if verbose: print(dt.now(), 'check_figure_references:', figure_keys)

    A = page['figure_A']

    # initialize A 
    for key in figure_keys :

        if page[key]['type'] == 'cross_section':
            A['number_sections'] = 0
            A['sec_ids'] = []
            A['sec_xyp_files'] = []

        if page[key]['type'] == 'annulus':
            A['great_circle_file'] = None

    # loop over figures
    for key in figure_keys :
        if key == 'figure_A': continue # shortcut to skip A

        if verbose: print(dt.now(), 'check_figure_references: key=', key)

        if page[key]['type'] == 'cross_section':
            section_defs = page[key].get('cross_section_defs')
            sec_res = float( page[key].get('sec_res') )

            number_sections, sec_ids, sec_xyp_files, label_name = mk_xyp_files(section_defs, sec_res)

            A['number_sections'] += number_sections
            A['sec_xyp_files'] += sec_xyp_files
            A['sec_ids'] += sec_ids
            A['label_name'] = label_name

        if page[key]['type'] == 'annulus':

            gcspec = page[key]['great_circle_spec']

            # build the cmd line option string
            gcproj = get_great_circle_proj(gcspec)

            # call the project cmd with the string
            grid_inc_az = page[key].get('grid_increment_azimuth', 0.5)
            gcfile = make_great_circle_path(gcproj, grid_inc_az)

            page[key]['great_circle_proj'] = gcproj
            page[key]['great_circle_file'] = gcfile

            A['great_circle_spec'] = gcspec
            A['great_circle_proj'] = gcproj
            A['great_circle_file'] = gcfile

#=====================================================================
#=====================================================================
def set_grid_parameters(figure):
    '''set the grid min, max, and color palett delta values'''

    field = figure['field']

    # 
    # NOTE : user settings from field dictionary are double checked below these defaults
    # 

    # set default grid incrment
    grid_increment = set_grid_increment(figure)

    # determine grid min, max and cpt settings from field type
    if field.startswith('none'):
        grid_min = 'none'
        grid_max = 'none'
        grid_cpt_delta = 'none'

    elif field.startswith('temp'):
        grid_min = 0.0
        grid_max = 1.0
        grid_cpt_delta = 0.15
        grid_cpt_delta = 0.10 # FIX ? 

    elif field.startswith('phase'):
        grid_min = 0.0
        grid_max = 2.0
        grid_cpt_delta = 0.5

    elif field.startswith('age'):
        grid_min = 'none'
        grid_max = 'none'
        grid_cpt_delta = 'none'

    elif field.startswith('visc'):
        parameters = figure['parameters'] 
        parser = CitcomParser.Parser()
        parser.read( parameters )
        if parser.getint('VMIN') != 0:
            grid_min = math.log10(parser.getfloat('visc_min'))
            grid_cpt_delta = 0.10
        else: 
            grid_min = 0.1
            grid_cpt_delta = 100

        if parser.getint('VMAX') != 0:
            grid_max = math.log10(parser.getfloat('visc_max'))
            grid_cpt_delta = 0.10
        else: 
            grid_max = 5000
            grid_cpt_delta = 100

    elif field.startswith('comp'):
        grid_min = 0.0
        grid_max = 1.0
        grid_cpt_delta = 0.10 

    elif field.startswith('surftopo'):
        grid_min = -1.5
        grid_max = 1.5
        grid_cpt_delta = 0.1

    elif field.startswith('grand_tomography'):
        grid_min = -5
        grid_max = 5
        grid_cpt_delta = 0.2
        grid_increment = 2.0

    elif field.startswith('S20RTS'):
        grid_min = -5
        grid_max = 5
        grid_cpt_delta = 0.2
        grid_increment = 2.0

    else:
        msg = "Unknown field name: cannot set grid min/max. Please use -h for help."
        raise ValueError(msg)

    # check for user over rides and update figure data

    if not figure.get('grid_min'):
        figure['grid_min'] = grid_min

    if not figure.get('grid_max'):
        figure['grid_max'] = grid_max

    if not figure.get('grid_cpt_delta'):
        figure['grid_cpt_delta'] = grid_cpt_delta

    if not figure.get('grid_increment'):
        figure['grid_increment'] = grid_increment

    if not figure.get('grid_tension'):
        figure['grid_tension'] = 0.1


    # set specialized mins and maxes
    if figure.get('overlay_temperature'):
        figure['overlay_temperature_grid_min'] = 0.0
        figure['overlay_temperature_grid_max'] = 1.0
        figure['overlay_temperature_grid_cpt_delta'] = 0.15
        figure['overlay_temperature_grid_cpt_delta'] = 0.10
    
    if figure.get('overlay_phase'):
        figure['overlay_phase_gmin'] = 0.0
        figure['overlay_phase_gmax'] = 2.0
        figure['overlay_phase_grid_min'] = 0.5
        figure['overlay_phase_grid_max'] = 2.5
        figure['overlay_phase_grid_cpt_delta'] = 1.0
    
    if figure.get('overlay_viscosity'):
        parameters = figure['parameters'] 
        parser = CitcomParser.Parser()
        parser.read( parameters )
        if parser.getint('VMIN') != 0:
            min = math.log10(parser.getfloat('visc_min'))
            grid_cpt_delta = 0.10
        else: 
            min = 0.1
            grid_cpt_delta = 100

        if parser.getint('VMAX') != 0:
            max = math.log10(parser.getfloat('visc_max'))
            grid_cpt_delta = 0.10
        else: 
            max = 5000
            grid_cpt_delta = 100

        figure['overlay_viscosity_grid_min'] = min
        figure['overlay_viscosity_grid_max'] = max 
        figure['overlay_viscosity_grid_cpt_delta'] = grid_cpt_delta

#=====================================================================
def set_grid_increment(figure):
    '''set grid resolution (GMT's -I)'''

    # double check 
    if not figure.get('parameters') :
        print(dt.now(), 'set_grid_increment: WARNING: figure has no "parameters" set!')
        print(dt.now(), 'set_grid_increment: grid_increment =', 1.0)
        return 1.0

    parameters = figure['parameters'] 
    parser = CitcomParser.Parser()
    parser.read( parameters )
    nodex = parser.getint('nodex')
    nodey = parser.getint('nodey')

    # get defaults
    zone = figure['zone']
    print(dt.now(), 'set_grid_increment: zone =', zone)
    print(dt.now(), 'set_grid_increment: nodex =', nodex)
    print(dt.now(), 'set_grid_increment: nodey =', nodey)

    if zone == 'global':

        if nodex <= 32:
            return nodex # match grid increment to nodex 

        else :
            factor1 = 4.0 # 4 cap sides per grate circle ?
            factor2 = 60.0 / float( '%(nodex)g' % vars() ) # caps are 60degrees from the lat lon grid ?
            grid_increment = factor1 * factor2

    elif zone == 'regional' or zone == '2D':

        r2d = 180./math.pi
        theta_min = 90.0 - ( r2d * parser.getfloat('theta_min') )
        theta_max = 90.0 - ( r2d * parser.getfloat('theta_max') )
        fi_min =           ( r2d * parser.getfloat('fi_min') )
        fi_max =           ( r2d * parser.getfloat('fi_max') )

        theta = math.fabs( theta_max - theta_min )
        fi = math.fabs( fi_max - fi_min )

        mean = ( theta + fi ) / 2 

        factor1 = 0.5 # for regional grids scale down ...
        factor2 = mean / float( '%(nodex)g' % vars() )
        grid_increment = factor1 * factor2

    else:
        msg = "Unknown type of CitComS run."
        raise ValueError(msg)
    
    print(dt.now(), 'set_grid_increment: grid_increment =', grid_increment)
    return grid_increment

#=====================================================================
def set_model_region(settings):
    '''from citcoms parameters, determine model region'''

    # short cut for non citcoms data
    if not settings.get('parameters'):
        settings['region'] = '0/360/-90/90'
        settings['zone'] = 'global'
        print(dt.now(), 'set_model_region: modelname =', settings['modelname'])
        print(dt.now(), 'set_model_region: zone =', settings['zone'])
        print(dt.now(), 'set_model_region: region =', settings['region'])
        return

    # parse the parameter file; CitcomParser checks for existance
    parser = CitcomParser.Parser()
    parser.read(settings['parameters'])

    settings['modelname'] = parser.getstr('datafile')
    settings['nproc_surf'] = parser.getint('nproc_surf')
    settings['nodex'] = parser.getint('nodex')
    settings['nodey'] = parser.getint('nodey')
    settings['nodez'] = parser.getint('nodez')

    # determine type of CitComS run:
    settings['nproc_surf'] = parser.getint('nproc_surf')
    if parser.getint('nproc_surf') == 1:
        settings['zone'] = 'regional'

        settings['theta_min'] = parser.getfloat('theta_min')
        settings['theta_max'] = parser.getfloat('theta_max')
        settings['fi_min'] = parser.getfloat('fi_min')
        settings['fi_max'] = parser.getfloat('fi_max')

        r2d = 180./math.pi

        settings['latmax'] = 90.0 - ( r2d * settings['theta_min'] )
        settings['latmin'] = 90.0 - ( r2d * settings['theta_max'] )

        settings['lonmin'] = ( r2d * settings['fi_min'] )
        settings['lonmax'] = ( r2d * settings['fi_max'] )

        # correct bounds 
        if settings.get('force360'):
            if settings['lonmin'] < 0:
                settings['lonmin'] = settings['lonmin'] + 360
            if settings['lonmax'] < 0:
                settings['lonmax'] = settings['lonmax'] + 360

        # correct bounds 
        if settings.get('force180'):
            if settings['lonmin'] > 180:
                settings['lonmin'] = settings['lonmin'] - 360
            if settings['lonmax'] > 180:
                settings['lonmax'] = settings['lonmax'] - 360

        settings['region'] = "%g/%g/%g/%g" % ( \
            settings['lonmin'], settings['lonmax'], \
            settings['latmin'], settings['latmax'] )

    elif parser.getint('nproc_surf') == 12:
        settings['zone'] = 'global'
        settings['region'] = '0/360/-90/90'

    else:
        settings['zone'] = None
        msg = 'Unable to determine model type: gloabal or regional.'
        raise ValueError(msg)

    # re-set the zone to 2D for 'thin' models 
    if settings['nodex'] <= 3 or settings['nodey'] <= 3 :
        settings['zone'] = '2D'

    if verbose: 
        print(dt.now(), 'set_model_region: modelname =', settings['modelname'])
        print(dt.now(), 'set_model_region: zone =', settings['zone'])
        print(dt.now(), 'set_model_region: region =', settings['region'])
#=====================================================================
def points_on_sphere(dlon):
# Form an equal area distributions on the surface of the sphere and 
# write to a GMT xy file
    r2d = 180.0/math.pi
    d2r=1.0/r2d
    Points=numpy.zeros((1,2),'float')
    T12=numpy.zeros((1,2),'float')
    i=0
    dlat=dlon
    lat=-89.9
    while lat <=89.9:
        lon=0.0
        while lon <= 360.0:
            T12[0][0]=lat;T12[0][1]=lon;
            if i==0:
                Points[0][0]=lat;Points[0][1]=lon;
            else:
                Points=numpy.append(Points,T12,axis=0)
            i+=1
            lon+=dlon/math.sin(d2r*(90-lat))
        lat+=dlat

    sp_name = "sphere_points.xy"
    SPF=open(sp_name,"w")
    i=0
    while i < numpy.alen(Points):
        lat=Points[i][0]
        lon=Points[i][1]
        #SPF.write(">\n")
        SPF.write("%f  %f\n" % (lon, lat) )
        i+=1

    SPF.close()
    return sp_name
#=====================================================================
#=====================================================================
def remove_gmt_char(ifile,ofile,file_type):
    '''From a Multiple xy or xyz GMT file, remove the multiple segment char, i.e. >'''
    IN=open(ifile)
    OUT=open(ofile,"w")
    while 1:
        line=IN.readline()
        if(line):
            c1 = line[0]
            if c1 != '>':
                if file_type == 'xy':
                    s1,s2 = line.split()
                    OUT.write("%s  %s\n" % (s1,s2))  
                elif file_type == 'xyz':
                    s1,s2,s3 = line.split()
                    OUT.write("%s  %s  %s\n" % (s1,s2,s3))  
                else:
                    print("ERROR -- Unsupported file type in GMT_Utilities.remove_gmt_char.   file_type=", file_type)
                    sys.exit(0)
        else:
            break
    IN.close()
    OUT.close()
    return
#
#=====================================================================
#=====================================================================
#=====================================================================
#=====================================================================
