#!/usr/bin/env python
#=====================================================================
#
#       Python Scripts for Geodynamics pre- and post- processing
#                  ---------------------------------
#
#                              Authors:
#                             Mike Gurnis
#          (c) California Institute of Technology 2013-2016
#
#               Free for non-commercial academic use ONLY.
#      This program is distributed WITHOUT ANY WARRANTY whatsoever.
#
#=====================================================================
#
#  Copyright April 2016, by the California Institute of Technology.
#
#=====================================================================
"""
Usage:
Diagnose_Regional_Slab_temp.py

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

resolution_in_km=10.0 #At the equator
#resolution_in_km=25.0 #At the equator
#resolution_in_km=100.0 #At the equator
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
print 'dt=',dt,' this should be in seconds'
dt=0.5*dt # This is a factor to avoid instability

timesteps=1  # Number of time-steps to evolve system.

T_min=0.0
T_max=1.0

#=====================================================================
# Directories for data sets

rhea_depths="/net/beno/raid1/gurnis/Rhea_meshes/shell_k2_ll5678_2016-03/depth_listing-l5678.dat"

Orig_Slabs1_grids_dir="/net/holmes/home4/gurnis/Rhea_runs/Slab1.0/Orig_grids/"

Contours_Slab_dir="/net/holmes/home4/gurnis/Rhea_runs/Slab1.0/Contours/"

RUM_grids_dir="/net/holmes/home4/gurnis/Rhea_runs/RUM_Slabs/RUM_Slabs_Reformed/New_RUM_grids/"
Slab1_grids_dir="/net/holmes/home4/gurnis/Rhea_runs/Slab1.0/Orig_grids/"

RUM_XY_dir="/net/holmes/home4/gurnis/Rhea_runs/RUM_Slabs/RUM_Slabs_Reformed/XY/"
Slab1_XY_dir="/net/holmes/home4/gurnis/Rhea_runs/Slab1.0/XY/"

RUM_Slab_Edge_dir="/net/holmes/home4/gurnis/Rhea_runs/RUM_Slabs/RUM_Slabs_Reformed/XY/Edges/"

age_grid="/net/beno/raid2/alisic/Rhea_input/Age_grids/new_age_042811.grd"

Slab1_Age_Dir="/net/holmes/home4/gurnis/Rhea_runs/Slab1.0/Slab_Age_Grids/"

RUM_Age_Dir="/net/holmes/home4/gurnis/Rhea_runs/RUM_Slabs/Slab_Age_Grids/"

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

    print ''' Diagnose_Regional_Slab_temp.py

'''

    sys.exit(0)
#=====================================================================
def plot_map_temperature(sn,psfile,gmt_dict,grd_file,x_move,y_move):

    long_min = float(gmt_dict['west'])
    long_max = float(gmt_dict['east'])
    lat_min = float(gmt_dict['south'])
    lat_max = float(gmt_dict['north'])
    long_mean=(long_min+long_max)/2.0

    aspect_ratio=(long_max-long_min)/(lat_max-lat_min)
    if aspect_ratio<=1.0:
        width=4.0*aspect_ratio
    else:
        width=4.0
    proj="-JH%g/%g" % (long_mean,width)
    region="%g/%g/%g/%g" % (long_min,long_max,lat_min,lat_max)

    cmd="makecpt -Cpolar -T%f/%f/0.1 -D > temp.cpt" % (T_min,T_max)
    print cmd
    os.system(cmd)
    cmd="grdimage %s %s -Ctemp.cpt -R%s -Ba20f5/a20f5::WeSn -X%g -Y%g -P -O -K >> %s" % (grd_file,proj,region,x_move,y_move,psfile)
    print cmd
    os.system(cmd)

    Profiles=[]
    for ii in range(1,3):
        print 'ii=',ii
        profile="%s%s_profile_%d.xyp" % (profile_dir,sn,ii)
        Profiles.append(profile)
        cmd="psxy %s %s -W3/1 -R%s -B -K -O >> %s" % (profile,proj,region,psfile)
        print cmd
        os.system(cmd)

    overlay_plate_boundaries(psfile,0,0)

        
    return Profiles
#=====================================================================
def make_pdf(psfile,slab):
    print "\n    Converting file to pdf ..."
    cmd = "ps2raster %s -A -Tf -E200" % (psfile)
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
    teeth="0.2/0.07lt"
    teeth="0.1/0.035lt"
    if (CLOSEGMT):
        cmd="psxy %s -J -R -B -W2/black -Sf%s -Gblack -M -P -O >> %s" % (trenches,teeth,psfile)
    else:
        cmd="psxy %s -J -R -B -W2/black -Sf%s -Gblack -M -P -O -K >> %s" % (trenches,teeth,psfile)
    print cmd 
    os.system(cmd)

    #Ridges
    if (RIDGES):
        cmd="psxy %s -J -R -B -W4/255/0/0 -V -M -P -O -K >> %s" % (ridges,psfile)
        #print cmd 
        #os.system(cmd)
        cmd="psxy %s -J -R -B -W2/255/255/255 -V -M -P -O -K >> %s" % (ridges,psfile)
        #print cmd
        #os.system(cmd)

    #Fractures
    cmd="psxy %s -J -R -B -W6/128/128/128 -V -M -P -O -K >> %s" % (fractures,psfile)
    #print cmd
    #os.system(cmd)
    #Interface between Trenches and Fractures (mostly)
    cmd="psxy %s -J -R -B -W6/0/255/0 -Sf0.2/0.07lt -G0/255/0 -V -M -P -O -K >> %s" % (interface,psfile)
    #print cmd
    #os.system(cmd)


    return
#=====================================================================
def get_integrate_profiles(Profiles,Grds):

    Temp_profiles=[]
    Dist_temp=[]
    for i in range(len(Profiles)):
        for j in range(len(Grds)):
            temp_profile="temp_profile_Pro%d_Grd%d.dT" % (i,j)
            Temp_profiles.append(temp_profile) 
            cmd="grdtrack %s -G%s > tmp.xydT" % (Profiles[i],Grds[j]) 
            print cmd
            os.system(cmd)
            IF=open("tmp.xydT")
            OF=open(temp_profile,"w")
            Dist=[] 
            Temp=[]
            while 1:
                line=IF.readline()
                if(line):
                    x,y,d,T=line.split()
                    OF.write("%s %s\n" % (d,T))
                    Dist.append(float(d))
                    Temp.append(float(T))
                else:
                    break
            IF.close()
            OF.close()
            dist_temp=0.0
            # Note the temperature used is 1-T
            for id in range(len(Dist)-1):
                dist_temp=dist_temp + 0.5*(Dist[id+1]-Dist[id])*(2.0-Temp[id]-Temp[id+1])
            Dist_temp.append(dist_temp)
    
    return Temp_profiles,Dist_temp
#=====================================================================
def plot_temp_profile(psfile,np,Temp_profiles,Dist_temp,d1,d2,x_move,y_move,GMTCLOSE):

    cmd="gmtset ANNOT_FONT_SIZE_PRIMARY	10p  LABEL_FONT_SIZE 12p"
    os.system(cmd)
    j=np
    
    cmd='psxy %s -JX4.0/0.9 -R%g/%g/0/1.1 -Ba100f25::/a0.5f0.1:Temp:Wesn -W1 -X%g -Y%g -K -O >> %s' % (Temp_profiles[j],d1,d2,x_move,y_move,psfile)
    print cmd
    os.system(cmd)

    j=np+1
    cmd='psxy %s -JX -R%g/%g/0/1.1 -Ba100f25:"Distance (km)":/a0.5f0.1:Temp:WeSn -W1/red -X0. -Y0. -K -O >> %s' % (Temp_profiles[j],d1,d2,psfile)
    print cmd
    os.system(cmd)

    percent_difference=2.0*100.0*(Dist_temp[np+1]-Dist_temp[np])/(Dist_temp[np]+Dist_temp[np+1])
    print 'Percent Difference ',percent_difference, '%'
    LAB = open('label.txt','w')
    xlabel=d1+10
    print >> LAB, "%d 0.1 8 0 1 1 Integrated difference = %g \\045" % (xlabel,percent_difference)
    LAB.close()

    GMTEND="-K -O"
    if GMTCLOSE == 1:
        GMTEND="-O"
    cmd="pstext label.txt -JX -R -X0 -Y0 %s -P >> %s" % (GMTEND,psfile)
    print cmd
    os.system(cmd)

    return
#=====================================================================
def clean_up_and_finish():

    print "Clean up"
    print ""
    cmd="rm -f *.eps *.grd *.xyz *.xy *.tmp *.txt"
    print cmd
    os.system(cmd)
    print ""
    print ""
    print "Done!"
    print ""
#=====================================================================
#=====================================================================
#    TOP OF MAIN
#=====================================================================
#=====================================================================
from Slab_Dictionary_Slab1_RUM import slab_dict
gmt_dict = {}

#if len(sys.argv) != 2:
#    usage()
#
#mode=sys.argv[1]


# Get the top level keys and sort them
slab_keys = slab_dict.keys();
slab_keys.sort()

#=====================================================================
#sn='sam'
#sn='izu'
sn='sol'
#depth=125
#depth=154
#depth=204
#depth=304
#depth=403
depth=500
#depth=608

psfile="temperature_diagnostic_%s_depth_%03d.ps" % (sn,depth)
cmd="gmtset PAPER_MEDIA letter MEASURE_UNIT inch"
os.system(cmd)
temp_grd_ic = "GRD_IC/%s/layer_%03d.grd" % (sn,depth)
temp_grd_diffuse = "GRD_FINAL/%s/layer_%03d.grd" % (sn,depth)
gmt_dict['grid']=temp_grd_ic
Core_GMT.grdinfo( gmt_dict )
print gmt_dict
#=====================================================================

LAB = open('label.txt','w')
print >> LAB, "2.0 0.0 12 0 1 1 %s depth = %d km" % (sn,depth)
LAB.close()

cmd="pstext label.txt -JX8 -R0/8/0/11.5 -X1 -Y10 -K -P > %s" % (psfile)
print cmd
os.system(cmd)
#=====================================================================
x_move=0.5
y_move=-4.5
Profiles=plot_map_temperature(sn,psfile,gmt_dict,temp_grd_ic,x_move,y_move)
 
x_move=3.5
y_move=0.0
Profiles=plot_map_temperature(sn,psfile,gmt_dict,temp_grd_diffuse,x_move,y_move)
 
Grds=[]
Grds.append(temp_grd_ic)
Grds.append(temp_grd_diffuse)
Temp_profiles, Dist_temp = get_integrate_profiles(Profiles,Grds)
print 'Temp_profiles',Temp_profiles
print 'Dist_temp ',Dist_temp

x_move=-2.5
y_move=-2
plot_temp_profile(psfile,0,Temp_profiles,Dist_temp,200,600,x_move,y_move,0)
x_move=0.0
y_move=-1.75
plot_temp_profile(psfile,2,Temp_profiles,Dist_temp,0,400,x_move,y_move,1)


make_pdf(psfile,sn)
#clean_up_and_finish()

# EOF

