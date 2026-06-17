#!/usr/bin/env python
#=====================================================================
#
#       Python Scripts for Geodynamics pre- and post- processing
#                  ---------------------------------
#
#                              Authors:
#                             Mike Gurnis
#          (c) California Institute of Technology 2015-2026
#
#               Free for non-commercial academic use ONLY.
#      This program is distributed WITHOUT ANY WARRANTY whatsoever.
#
#=====================================================================
#
#  Copyright June 2026, by the California Institute of Technology.
#
#=====================================================================
"""
Usage:
Create_Global_fom_Regional_Slabs.py

"""
#=====================================================================

import Core_GMT, GMT_Utilities, Mat_Utilities, Earthquake_Utilities
#import Rhea_Utilities
import Thermal_Utilities
import os, string, sys, math, time, datetime, random
import scipy as sp

#=====================================================================
#=====================================================================
# Global Parameters

d2r=math.pi/180.0
r2d=1.0/d2r

depth_max=660.0
earth_radius = 6371.0
therm_diff=1e-06
kappa=therm_diff
layer_km=earth_radius
scalet = layer_km*1e3*layer_km*1e3/(therm_diff*1.e6*365.25*24.*3600.)
km_per_degree=2.0*earth_radius*math.pi/360.0
kappa=therm_diff/(layer_km*1e3*layer_km*1e3) # in units of rad**2/s
s_yr = 60.0*60.0*24.0*365.0


# Declare some variables:
# r is radius with r=1 the outer radius
# theta is the co-latitude in radians
# phi is the longitude in radians

resolution_in_km=25.0 #At the equator
dr=resolution_in_km/earth_radius
dtheta=resolution_in_km/km_per_degree*d2r
dphi=resolution_in_km/km_per_degree*d2r
# Redundant:
dx=dphi        # Interval size in x-direction.
dy=dtheta      # Interval size in y-direction.
dz=dr
dx2=dx**2
dy2=dy**2
dz2=dz**2
# For stability, this is the largest interval possible
# for the size of the time-step:
dtxy = dx2*dy2/( 2*kappa*(dx2+dy2) )
dtz = dz**2/( 2*kappa )
dt=min(dtxy,dtz)/2.0
print('dt=',dt,' this should be in seconds')
dt=0.5*dt # This is a factor to avoid instability

timesteps=1  # Number of time-steps to evolve system.

T_min=0.0
T_max=1.0

nx=None
ny=None
nz=None
T=None
Tf=None
Th=None
Theta=None
CosTheta=None
SinTheta=None
R=None
layer_depths=None
#=====================================================================
# Directories for data sets

#For Mac
rhea_depths="/Users/gurnis/Desktop/Gurnis_Files/Working/Current_Work/Rhea_global_runs/Rhea2/Rhea_meshes/shell_k2_ll5678_2016-03/depth_listing-l5678.dat"


#rhea_depths="/net/beno/raid1/gurnis/Rhea_Input/Temp_2_rhea/shell_temperature_k2_ll456_z_June2015.txt"
#rhea_depths="/net/beno/data1/gurnis/Rhea_meshes/shell_k2_ll5678_2016-03/depth_listing-l5678.dat"
#rhea_depths="/net/beno/raid1/gurnis/Rhea_meshes/shell_k2_ll5678_2016-03/tmp_truncated-l5678.dat"


Orig_Slabs1_grids_dir="/net/holmes/home4/gurnis/Rhea_runs/Slab1.0/Orig_grids/"

Contours_Slab_dir="/net/holmes/home4/gurnis/Rhea_runs/Slab1.0/Contours/"

RUM_grids_dir="/net/holmes/home4/gurnis/Rhea_runs/RUM_Slabs/RUM_Slabs_Reformed/New_RUM_grids/"
Slab1_grids_dir="/net/holmes/home4/gurnis/Rhea_runs/Slab1.0/Orig_grids/"

RUM_XY_dir="/net/holmes/home4/gurnis/Rhea_runs/RUM_Slabs/RUM_Slabs_Reformed/XY/"
Slab1_XY_dir="/net/holmes/home4/gurnis/Rhea_runs/Slab1.0/XY/"

RUM_Slab_Edge_dir="/net/holmes/home4/gurnis/Rhea_runs/RUM_Slabs/RUM_Slabs_Reformed/XY/Edges/"

age_grid="/net/beno/raid2/alisic/Rhea_input/Age_grids/new_age_042811.grd"

topo_grid="/net/holmes/scratch2/gurnis/ETOPO-02/etopo2.grd"

bird="bird_boundaries"

coastlines="/net/holmes/home4/gurnis/Global_Plate_Polygons/cs.lines.0.xy"

gplates_polygons="/net/holmes/home4/gurnis/Global_Plate_Polygons/g0.8.8.platepolygons.0.xy"

dir_old_margins="/net/holmes/home4/gurnis/Rhea_runs/Plate_Margins/NewDataSet"

trenches="%s/Trench-1-12-10.xy" % dir_old_margins

ridges="%s/Ridges-5-26-10.xy" % dir_old_margins

fractures="%s/Fractures-1-12-10.xy" % dir_old_margins

interface="%s/Interface-1-12-10.xy" % dir_old_margins

rum_slab_contours="/net/holmes/home4/gurnis/Rhea_runs/Slabs/Level567/all_contours_567.xyz"

profile_dir="/net/holmes/home4/gurnis/Rhea_runs/Slab1.0/Profiles/"

#=====================================================================
#=====================================================================
def usage():

    print(''' Create_Global_from_Regional_Slabs.py

''')

    sys.exit(0)
#=====================================================================
def get_layer_depths():
    RD=open(rhea_depths)
    tmp_depths=[]
    while 1:
        line=RD.readline()
        if(line):
            idepth=int(line)
            if(idepth <=int(depth_max)):
                tmp_depths.append(idepth)
        else:
            break
    RD.close()
    tmp_depths.reverse()
    layer_depths=tmp_depths
    return layer_depths
#=====================================================================
def get_layer_depths_rhea2():
    RD=open(rhea_depths)
    tmp_depths=[]
    while 1:
        line=RD.readline()
        if(line):
            depth=float(line)
            if(depth <=depth_max):
                tmp_depths.append(depth)
        else:
            break
    RD.close()
    tmp_depths.reverse()
    layer_depths=tmp_depths
    return layer_depths
#=====================================================================
def make_pdf(psfile,slab):
    print("\n    Converting file to pdf ...")
    cmd = "gmt psconvert %s -A -Tf -E200" % (psfile)
    os.system(cmd)

    cmd='rm -f *.ps'
    os.system(cmd)
    cmd="mkdir PDF/"+slab
    os.system(cmd)
    cmd='mv *.pdf PDF/%s/' % slab
    os.system(cmd)

    return
#=====================================================================
def overlay_plate_boundaries(psfile,RIDGES,CLOSEGMT):

    #Position of the trench
    teeth="0.2i/0.07i+l+t"
    teeth="0.1i/0.035i+l+t"
    if (CLOSEGMT):
        cmd="gmt psxy %s -J -R -B -W2p,black -Sf%s -Gblack -M -P -O >> %s" % (trenches,teeth,psfile)
    else:
        cmd="gmt psxy %s -J -R -B -W2p,black -Sf%s -Gblack -M -P -O -K >> %s" % (trenches,teeth,psfile)
    print(cmd)
    os.system(cmd)

    #Ridges
    if (RIDGES):
        cmd="gmt psxy %s -J -R -B -W4p,255/0/0 -V -M -P -O -K >> %s" % (ridges,psfile)
        #print(cmd)
        #os.system(cmd)
        cmd="gmt psxy %s -J -R -B -W2p,255/255/255 -V -M -P -O -K >> %s" % (ridges,psfile)
        #print(cmd)
        #os.system(cmd)

    #Fractures
    cmd="gmt psxy %s -J -R -B -W6p,128/128/128 -V -M -P -O -K >> %s" % (fractures,psfile)
    #print(cmd)
    #os.system(cmd)
    #Interface between Trenches and Fractures (mostly)
    cmd="gmt psxy %s -J -R -B -W6p,0/255/0 -Sf0.2i/0.07i+l+t -G0/255/0 -V -M -P -O -K >> %s" % (interface,psfile)
    #print(cmd)
    #os.system(cmd)


    return
#=====================================================================
def clean_up_and_finish():

    print("Clean up")
    print("")
    cmd="rm -f *.eps *.grd *.xyz *.xy *.tmp *.txt"
    print(cmd)
    os.system(cmd)
    print("")
    print("")
    print("Done!")
    print("")
#=====================================================================
#=====================================================================
#    TOP OF MAIN
#=====================================================================
#=====================================================================
from Slab_Dictionary_Slab2 import slab_dict
gmt_dict = {}

#if len(sys.argv) != 2:
#    usage()
#
#mode=sys.argv[1]

#For the Global grd files
bounds = '0/360/-90/90'
#grd_res=0.1  # In degrees
#grd_res=1.0  # In degrees
grd_res=0.05
#grd_res=0.025

T_mantle=1.0

# Info on the global maps
mapwidth = 6.0
proj = 'H180/%f' % mapwidth

cmd="mkdir GRD_GLOBAL"
print(cmd)
os.system(cmd)


# Get the top level keys and sort them
slab_keys = sorted(slab_dict.keys())


cmd="gmt gmtset PS_MEDIA letter PROJ_LENGTH_UNIT inch"
os.system(cmd)


#layer_depths=get_layer_depths()
#In rhea2 these values are now floats, before they were ints
layer_depths=get_layer_depths_rhea2()

print('layer_depths: ',layer_depths)


for layer in layer_depths:
    print('layer: ',layer)

    files_to_blend_0="blend_0.dat"
    files_to_blend="blend.dat"
    BF0=open(files_to_blend_0,"w")
    BF0.write("GRD_FINAL/sco/layer_%03d.grd - 1.0" % (int(layer)))
    #BF0.write("GRD_FINAL/sol/layer_%03d.grd - 1.0" % (int(layer)))
#    #BF0.write("GRD_IC/sol/layer_%03d.grd - 1.0" % (int(layer)))
    BF0.close()
    global_grd_file_0="GRD_GLOBAL/N0_layer_%03d.grd" % (int(layer))
    print('global_grd_file: ',global_grd_file_0)
    cmd="gmt grdblend %s -G%s -I%f -R%s -N%f" % (files_to_blend_0,global_grd_file_0,grd_res,bounds,T_mantle)
    print(cmd)
    os.system(cmd)

    for s in slab_keys:
        print("SLAB: %s" % s)
        # Get a local copy of the sub dictionary
        sub_dict = slab_dict[s]
        # Get the sub level keys and sort them
        sub_keys = sorted(sub_dict.keys())


        grd_file="GRD_FINAL/%s/layer_%03d.grd" % (s,int(layer))
        #grd_file="GRD_IC/%s/layer_%03d.grd" % (s,int(layer))

        BF=open(files_to_blend,"w")
        BF.write("%s  -  1.0\n" % (grd_file))
        BF.close()

        global_grd_file="GRD_GLOBAL/tmp_layer_%03d.grd" % (int(layer))
        print(global_grd_file)
        # Blend the regional to global essential to create a global grd
        cmd="gmt grdblend %s -G%s -I%f -R%s -N%f" % (files_to_blend,global_grd_file,grd_res,bounds,T_mantle)
        print(cmd)
        os.system(cmd)

 
    
        #Merge the cummulative global grd with the current one
        cmd="gmt grdmath %s %s MIN = tmp.grd" % (global_grd_file_0,global_grd_file)
        print(cmd)
        os.system(cmd)
        cmd="mv tmp.grd %s" % (global_grd_file_0)
        print(cmd)
        os.system(cmd)


    cmd="mv %s %s" % (global_grd_file_0,global_grd_file)
    print(cmd)
    os.system(cmd)
    # Make a map to check the blended global grd file
    psfile="slab_temp_%03d.ps" % (int(layer))
    cmd = 'gmt grdimage -JH0/7 %s -Ctemp.cpt -R0/360/-90/90 -P -X1.0 -Y7 > %s' % (global_grd_file,psfile)
    print(cmd)
    os.system(cmd)
    make_pdf(psfile,"Global")



clean_up_and_finish()

# EOF
