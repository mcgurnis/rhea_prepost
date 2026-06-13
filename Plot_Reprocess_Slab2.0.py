#!/usr/bin/env python
#=====================================================================
#
#       Python Scripts for Geodynamics pre- and post- processing
#                  ---------------------------------
#
#                              Authors:
#                             Mike Gurnis
#          (c) California Institute of Technology 2013-2026
#
#               Free for non-commercial academic use ONLY.
#      This program is distributed WITHOUT ANY WARRANTY whatsoever.
#
#=====================================================================
#
#=====================================================================
#
# Last Update: Mike Gurnis, Jan. 24, 2013
#  MG Mar. 7, 2014
#  MG Mar 31, 2016
#  JH Sep 18, 2018
#  MG May 21, 2026  

#=====================================================================
"""
Usage:
Plot_Reprocess_Slab2.0.py

"""
#=====================================================================

from datetime import date

import Core_GMT, GMT_Utilities, Mat_Utilities, Earthquake_Utilities
import os, string, sys, math, time
from Plotting_Utilities import usage, make_pdf, shift_profile, overlay_plate_boundaries, new_point

#=====================================================================
#=====================================================================
# Global Parameters

d2r=math.pi/180.0
earth_radius = 6371.0

#Slab2_Age_Dir="/home/jiashun/Documents/scripts/gurnis/Slab2.0/Slab_Age_Grids/"
#For Mac
Slab2_Age_Dir="/Volumes/STORE01/Rhea/Slab2/Slab_Age_Grids/"

#For Mac
Orig_Slabs2_grids_dir="/Volumes/STORE01/Rhea/Slab2/"
#Orig_Slabs2_grids_dir="/home/jiashun/Documents/scripts/gurnis/Slab2.0/Slab2Distribute_Mar2018/"

#New_grids_dir="/home/jiashun/Documents/scripts/gurnis/Slab2.0/New_grids/"
#For Mac
New_grids_dir="/Volumes/STORE01/Rhea/Slab2/New_grids/"


#Contours_Slab_dir="/home/jiashun/Documents/scripts/gurnis/Slab2.0/Slab2Distribute_Mar2018/Slab2_CONTOURS/"
#New Dir on Mac
Contours_Slab_dir="/Volumes/STORE01/Rhea/Slab2/Slab2_CONTOURS/"


RUM_grids_dir="/net/holmes/home4/gurnis/Rhea_runs/RUM_Slabs/RUM_Slabs_Reformed/New_RUM_grids/"

Contours_RUM_dir="/net/holmes/home4/gurnis/Rhea_runs/RUM_Slabs/RUM_Slabs_Reformed/Contours/"

#XY_dir="/home/jiashun/Documents/scripts/gurnis/Slab2.0/Slab2Distribute_Mar2018/Slab2Clips/"
#New Dir on Mac
XY_dir="/Volumes/STORE01/Rhea/Slab2/Slab2Clips/"


RUM_XY_dir="/net/holmes/home4/gurnis/Rhea_runs/RUM_Slabs/RUM_Slabs_Reformed/XY/"

#age_grid="/net/beno/raid2/alisic/Rhea_input/Age_grids/new_age_042811.grd"
#age_grid="/net/beno/data1/alisic/raid2/Rhea_input/Age_grids/new_age_042811.grd"
# New age grid for Mac
age_grid="/Volumes/STORE01/Rhea/alisic/Rhea_input/Age_grids/new_age_042811.grd"

#topo_grid="/net/holmes/scratch2/gurnis/ETOPO-02/etopo2.grd"
#For Mac
topo_grid="/Users/gurnis/Desktop/Gurnis_Files/Working/Data_Sets/Large_Topo_and_Gravity_Files/etopo2.grd"

bird="bird_boundaries"

coastlines="/net/holmes/home4/gurnis/Global_Plate_Polygons/cs.lines.0.xy"

gplates_polygons="/net/holmes/home4/gurnis/Global_Plate_Polygons/g0.8.8.platepolygons.0.xy"

#dir_old_margins="/net/holmes/home4/gurnis/Rhea_runs/Plate_Margins/NewDataSet"
#New directory for Mac  
dir_old_margins="/Users/gurnis/Desktop/Gurnis_Files/Working/Current_Work/Rhea_global_runs/Slab2.0/Plate_Margins/NewDataSet"

trenches="%s/Trench-1-12-10.xy" % dir_old_margins

ridges="%s/Ridges-5-26-10.xy" % dir_old_margins

fractures="%s/Fractures-1-12-10.xy" % dir_old_margins

interface="%s/Interface-1-12-10.xy" % dir_old_margins

#working="working.xy"

rum_slab_contours="/net/holmes/home4/gurnis/Rhea_runs/Slabs/Level567/all_contours_567.xyz"


#=====================================================================
#=====================================================================
def usage():

    print(''' Plot_Reprocess_Slab2.0.py mode)

        where mode = S  : Summary Table of Slabs
                  C  : Contour files of slab depths
                  G  : Global plot
                  R  : A set of regional plots
                  P  : Process the data to create the regional Slab2
                      RUM files and associated individual plots
                  X  : Make summary cross section
    ''')

    sys.exit(0)
#=====================================================================
def summary_cross_section(slab_dict,slab_keys):

    print('summary_cross_section')

    psfile="summary_cross_section.ps"

    cmd="gmt gmtset FONT_ANNOT_PRIMARY Times-Roman FONT_LABEL Times-Roman"
    print(cmd)
    os.system(cmd)
 
    cmd='gmt psbasemap -JX6/2 -R0/300/-100/0 -B50f25:"Distance from Trench (km)":/50f10:"Depth (km)":WesN -X1.1 -Y6 -P -K > %s' % (psfile)
    print(cmd)
    os.system(cmd)

    for s in slab_keys:
        print(" ")
        print("SLAB: %s" % s)
        # Get a local copy of the sub dictionary
        sub_dict = slab_dict[s]
        # Get the sub level keys and sort them
        sub_keys = list(sub_dict.keys())
        sub_keys.sort()
        RUM=sub_dict['RUM']
        Sub_type=sub_dict['Sub_type']
        sub_color='black'
        if Sub_type == 'Ocean':
            sub_color='grey'
        if Sub_type == 'Cont':
            sub_color='grey'
        if RUM != 'only':
            i=1
            while i<=2:
                depth_profile="Profiles/%s_slab2_depth_profile_%d.xypd" % (s,i)
                shifted_profile_0=shift_profile(depth_profile,"P",0.0,0.0)
                shifted_profile=shift_profile(shifted_profile_0,"Z",0.0,0.0)
                #cmd="gmt psxy %s -JX -R -B -W5/black -O -K >> %s" % (shifted_profile,psfile)
                cmd="gmt psxy %s -JX -R -B -W2,%s -O -K >> %s" % (shifted_profile,sub_color,psfile)
                print(cmd)
                os.system(cmd)
                i += 1

    #cmd="gmt psxy %s -J -R -B -W5/black -O >> %s" % (shifted_profile,psfile)
    cmd="gmt psxy %s -J -R -B -W2%s -O >> %s" % (shifted_profile,sub_color,psfile)
    print(cmd)
    os.system(cmd)

    #Overlay some models for comparison
    #weak_zone_model="/net/holmes/home4/gurnis/Rhea_runs/Model_Tests/johann_model_1.dat"
    #cmd="gmt psxy %s -J -R -B -W4/red -O -K >> %s" % (weak_zone_model,psfile)
    #print(cmd)
    #os.system(cmd)

    #weak_zone_model="/net/holmes/home4/gurnis/Rhea_runs/Model_Tests/vish_model_1.dat"
    #cmd="gmt psxy %s -J -R -B -W4/black -O >> %s" % (weak_zone_model,psfile)
    #print(cmd)
    #os.system(cmd)

    make_pdf(psfile)

    return
#=====================================================================
def make_slab_depth_contous(slab_dict,slab_keys):

    print('make_slab_depth_contous')
    for s in slab_keys:
        print(" ")
        print("SLAB: %s" % s)
        print(" ")
        # Get a local copy of the sub dictionary
        sub_dict = slab_dict[s]
        # Get the sub level keys and sort them
        sub_keys = list(sub_dict.keys())
        sub_keys.sort()
        RUM=sub_dict['RUM']
        date=sub_dict['date']
        if RUM != 'only':
            depth_grids_dir=Orig_Slabs2_grids_dir
            grd_depth="%s%s_slab2_dep_%s.grd" % (depth_grids_dir,s,date)
            gmt_depth="%s%s_slab2_dep_%s_contours.in" % (Contours_Slab_dir,s,date)
        if RUM == 'only':
            depth_grids_dir=RUM_grids_dir
            grd_depth="%s%s_rum_clip.grd" % (depth_grids_dir,s)
            gmt_depth="%s%s_rum_contours_m.xy" % (Contours_RUM_dir,s)

        dict['grid']=grd_depth
        Core_GMT.grdinfo( dict )
        #print dict
        long_min = float(dict['west'])
        long_max = float(dict['east'])
        lat_min = float(dict['south'])
        lat_max = float(dict['north'])
        long_mean=(long_min+long_max)/2.0

        aspect_ratio=(long_max-long_min)/(lat_max-lat_min)
        if aspect_ratio<=1.0:
            width=3.0*aspect_ratio
        else:
            width=3.0
        proj="-JH%g/%g" % (long_mean,width)
        region="%g/%g/%g/%g" % (long_min,long_max,lat_min,lat_max)
    
        psfile="contours.ps"
        cmd="gmt grdcontour %s -C25.0 %s -D%s -m > %s" % (grd_depth,proj,gmt_depth,psfile)
        print(cmd)
        os.system(cmd)

        cmd="gmt psxy %s -Cslab_depth.cpt %s -R%s -m > %s" % (gmt_depth,proj,region,psfile)
        print(cmd)
        os.system(cmd)

    make_pdf(psfile)
    
    return
#=====================================================================
def make_regional_plots(slab_dict,slab_keys):

    region_name='western_pac'
    proj="-JH132.5/3.0"
    region='115/150/-10/35'
    x_start=2.5
    shift_scale=1.5
    COASTLINES=0
    RIDGES=1
    psfile="regional_%s.ps" % region_name
    make_summary_map(slab_dict,slab_keys,psfile,region,proj,x_start,shift_scale,COASTLINES,RIDGES)

    region_name='philippines'
    proj="-JH122.5/2.0"
    region='115/130/-6/25'
    x_start=2.5
    shift_scale=1.5
    COASTLINES=0
    RIDGES=1
    psfile="regional_%s.ps" % region_name
    make_summary_map(slab_dict,slab_keys,psfile,region,proj,x_start,shift_scale,COASTLINES,RIDGES)

    region_name='indonesia'
    proj="-JH112.5/5.0"
    region='90/135/-15/30'
    x_start=2.5
    shift_scale=2.5
    COASTLINES=0
    RIDGES=1
    psfile="regional_%s.ps" % region_name
    make_summary_map(slab_dict,slab_keys,psfile,region,proj,x_start,shift_scale,COASTLINES,RIDGES)

    region_name='sw_pacific'
    proj="-JH172.5/3.5"
    region='155/190/-55/-7.5'
    x_start=2.5
    shift_scale=1.75
    COASTLINES=1
    RIDGES=0
    psfile="regional_%s.ps" % region_name
    make_summary_map(slab_dict,slab_keys,psfile,region,proj,x_start,shift_scale,COASTLINES,RIDGES)


    region_name='melanesia'
    proj="-JH157.5/3.5"
    region='140/170/-15/0.0'
    x_start=2.5
    shift_scale=1.75
    COASTLINES=1
    RIDGES=0
    psfile="regional_%s.ps" % region_name
    make_summary_map(slab_dict,slab_keys,psfile,region,proj,x_start,shift_scale,COASTLINES,RIDGES)
    return
#=====================================================================
def make_global_plot(slab_dict,slab_keys):

    psfile="global_slab_depths.ps"

    width=10.0
    proj="-JH0.0/%g" % (width)

    region='g'
    x_start=0.5
    shift_scale=5.0
    COASTLINES=0
    RIDGES=1

    make_summary_map(slab_dict,slab_keys,psfile,region,proj,x_start,shift_scale,COASTLINES,RIDGES)
    #make_test_map(slab_dict,slab_keys,psfile,region,proj,x_start,shift_scale,COASTLINES,RIDGES)

    return
#=====================================================================
def make_test_map(slab_dict,slab_keys,psfile,region,proj,x_start,shift_scale,COASTLINES,RIDGES):

    print('make_test_map')
    s="alu"
    sub_dict = slab_dict[s]
    date=sub_dict['date']
    print("date=%s" % date)
    print("sub_dict=%s" % sub_dict)

    gmt_depth="%s%s_slab2_dep_%s_contours.in" % (Contours_Slab_dir,s,date)
    perimeter="%s%s_slab2_clp_%s.csv" % (XY_dir,s,date)
    print("gmt_depth=%s" % gmt_depth)
    print("perimeter=%s" % perimeter)

    cmd="gmt psbasemap %s -R%s -B90/90/wesn -X%g -Y%g -K > %s" % (proj,region,x_start,x_start,psfile)
    print(cmd)
    os.system(cmd)

    cmd="gmt psxy %s -Cslab_depth.cpt %s -B90/90/wesn -R%s -K -O >> %s" % (gmt_depth,proj,region,psfile)
    print(cmd)
    os.system(cmd)

    cmd="gmt psxy %s -J -W0.5p,128 -R -B -O >> %s" % (perimeter,psfile)
    print(cmd)
    os.system(cmd)

    make_pdf(psfile)

    return

#=====================================================================
def make_summary_map(slab_dict,slab_keys,psfile,region,proj,x_start,shift_scale,COASTLINES,RIDGES):

    start_plot_with_blank_map(psfile,region,proj,x_start)

    for s in slab_keys:
        sub_dict = slab_dict[s]
        RUM=sub_dict['RUM']
        date=sub_dict['date']
        plot_slab(s,date,psfile)

    #overlay_RUM_slabs(psfile)

    overlay_plate_boundaries(psfile,RIDGES)

    if (COASTLINES):
        overlay_coastlines(psfile)

    finalize_plot_with_scale(psfile,shift_scale)

    make_pdf(psfile)

    return
#=====================================================================
def start_plot_with_blank_map(psfile,region,proj,x_start):

    cmd="gmt psbasemap %s -R%s -B90/90/wesn -X%g -Y2.5 -K > %s" % (proj,region,x_start,psfile)
    print(cmd)
    os.system(cmd)

    return
#=====================================================================
def start_plot_with_contours(psfile,region,proj,x_start):
    #Original RUM Slab contours
    cmd="gmt psxy %s %s -R%s -B90/90/wesn -W1/200/200/200 -M -X%g -Y2.5 -K > %s" % (rum_slab_contours,proj,region,x_start,psfile)
    print(cmd)
    os.system(cmd)

    return
#=====================================================================
def finalize_plot_with_scale(psfile,shift_scale):
    cmd="gmt psscale -Cslab_depth.cpt -D%g/-0.5/4.0/0.25h -B100::/:depth: -O >> %s" % (shift_scale,psfile)
    print(cmd)
    os.system(cmd)

    return
#=====================================================================
def make_pdf(psfile):
    print ("\n    Converting file to pdf ...")
    cmd = "gmt psconvert %s -A -Tf -E200" % (psfile)
    os.system(cmd)

    cmd='rm -f *.ps'
    os.system(cmd)
    cmd='mv *.pdf PDF'
    os.system(cmd)

    return
#=====================================================================
def overlay_RUM_slabs(psfile):

    cmd="gmt psxy %s -J -R -B -W1/128/128/128 -M -P -O -K >> %s" % (rum_slab_contours,psfile)
    print(cmd)
    os.system(cmd)

    return
#=====================================================================
def plot_slab(s,date,psfile):

    RUM='NONE'
    if RUM != 'only':
        grd_depth="%s%s_slab2_%s.grd" % (Orig_Slabs2_grids_dir,s,date)
        gmt_depth="%s%s_slab2_dep_%s_contours.in" % (Contours_Slab_dir,s,date)
        perimeter="%s%s_slab2_clp_%s.csv" % (XY_dir,s,date)
    if RUM == 'only':
        grd_depth="%s%s_rum_clip.grd" % (RUM_grids_dir,s)
        gmt_depth="%s%s_rum_contours_m.xy" % (Contours_RUM_dir,s)
        perimeter="%s%s_rum.clip.xy" % (RUM_XY_dir,s)
    #cmd="gmt grdimage %s -Cslab_depth.cpt -J -R -B -P -O -K >> %s" % (grd_depth,psfile)
    cmd="gmt psxy %s -Cslab_depth.cpt -J -R -P -O -K >> %s" % (gmt_depth,psfile)
    print(cmd)
    os.system(cmd)
    cmd="gmt psxy %s -J -W0.5p,128 -R -B -K -O >> %s" % (perimeter,psfile)
    print(cmd)
    os.system(cmd)

    return
#=====================================================================
def overlay_coastlines(psfile):

    cmd="gmt pscoast -J -R -B -Di -W -P -O -K >> %s" % (psfile)
    print(cmd)
    os.system(cmd)

    return
#=====================================================================
def overlay_plate_boundaries(psfile,RIDGES):

    #Position of the trench
    teeth="0.2/0.07lt"
    teeth="0.1/0.035lt"
    cmd="gmt psxy %s -J -R -B -W1,100/100/255 -Sf%s -G100/100/255 -P -O -K >> %s" % (trenches,teeth,psfile)
    print(cmd)  
    os.system(cmd)

    #Ridges
    if (RIDGES):
        cmd="gmt psxy %s -J -R -B -W1,255/0/0 -V -P -O -K >> %s" % (ridges,psfile)
        print(cmd) 
        os.system(cmd)
        cmd="gmt psxy %s -J -R -B -W0.5,255/255/255 -V -P -O -K >> %s" % (ridges,psfile)
        print(cmd)
        os.system(cmd)

    #Fractures
    cmd="gmt psxy %s -J -R -B -W1,128/128/128 -V -P -O -K >> %s" % (fractures,psfile)
    print(cmd)
    os.system(cmd)
    #Interface between Trenches and Fractures (mostly)
    cmd="gmt psxy %s -J -R -B -W1,0/255/0 -Sf0.1/0.035lt -G0/255/0 -V -P -O -K >> %s" % (interface,psfile)
    print(cmd)
    os.system(cmd)


    return
#=====================================================================
def reprocess_plot_each_slab_individually(slab_dict,slab_keys):

    print('reprocess_plot_each_slab_individually')
    
    for s in slab_keys:
        print(" ")
        print("SLAB: %s" % s)
        print(" ")
        # Get a local copy of the sub dictionary
        sub_dict = slab_dict[s]
        # Get the sub level keys and sort them
        sub_keys = list(sub_dict.keys())
        sub_keys.sort()

        trench_age_dist=sub_dict['off_age']
        trench_dep_dist=sub_dict['off_dep']
        Nan_age=sub_dict['Nan_age']
        RUM=sub_dict['RUM']
        date=sub_dict['date']

        print("RUM=%s" % RUM)
        
        if RUM == 'NONE':
            depth_grids_dir=Orig_Slabs2_grids_dir
            grd_depth_slab2="%s%s_slab2_dep_%s.grd" % (depth_grids_dir,s,date)
            grd_dip_slab2="%s%s_slab2_dip_%s.grd" % (depth_grids_dir,s,date)
            grd_str_slab2="%s%s_slab2_str_%s.grd" % (depth_grids_dir,s,date)
            grd_age_slab2="%s%s_age.grd" % (Slab2_Age_Dir,s)
            perimeter="%s%s_slab2_clp_%s.csv" % (XY_dir,s,date)
            grd_depth=grd_depth_slab2
            grd_dip=grd_dip_slab2
            grd_str=grd_str_slab2
            grd_age=grd_age_slab2
        #if RUM != 'NONE':
        #    if RUM == 'only':
        #        sn=s
        #    if RUM != 'only':
        #        sn=RUM
        #        depth_grids_dir=Orig_Slabs2_grids_dir
        #        grd_depth_slab2="%s%s_slab2.0_clip.grd" % (depth_grids_dir,s)
        #        grd_dip_slab2="%s%s_slab2.0_dipclip.grd" % (depth_grids_dir,s)
        #        grd_str_slab2="%s%s_slab2.0_strclip.grd" % (depth_grids_dir,s)
        #        grd_age_slab2="%s%s_age.grd" % (Slab2_Age_Dir,s)
        #    depth_grids_dir=RUM_grids_dir
        #    XY_dir="/net/holmes/home4/gurnis/Rhea_runs/RUM_Slabs/RUM_Slabs_Reformed/XY/"
        #    grd_depth_rum="%s%s_rum_clip.grd" % (depth_grids_dir,sn)
        #    grd_dip_rum="%s%s_rum_dipclip.grd" % (depth_grids_dir,sn)
        #    grd_str_rum="%s%s_rum_strclip.grd" % (depth_grids_dir,sn)
        #    grd_age_rum="%s%s_age.grd" % (RUM_Age_Dir,s)
        #    perimeter="%s%s_rum.clip.xy" % (XY_dir,sn)
        #    grd_depth=grd_depth_rum
        #    grd_dip=grd_dip_rum
        #    grd_str=grd_str_rum
        #    grd_age=grd_age_rum

        ps_name_prefix="%s_slab_depth%d_width%d" % (s,int(slab_transition_depth),int(slab_transition_width))
        psfile ="%s_1.ps" % ps_name_prefix
        dict['grid']=grd_depth
        Core_GMT.grdinfo( dict )


        grd_slab_age, trench, trench_outside, trench_inside, slab_depth_correction_grd=make_slab_age_depth_correction_grd(s,dict,XY_dir,age_grid,grd_depth,grd_str,trench_age_dist,trench_dep_dist,Nan_age)
        print("slab_depth_correction_grd", slab_depth_correction_grd)
        cmd="cp %s %s" % (grd_slab_age,grd_age)
        print(cmd)
        os.system(cmd)

        # depth_correction cpt
        dict['grid']=slab_depth_correction_grd
        Core_GMT.grdinfo( dict )
        dict['dz']=1.0
        dict['C']='rainbow'
        Core_GMT.makecpt( dict )
        cmd="mv %s depth_correction.cpt" % (dict['C'])
        print(cmd)
        os.system(cmd)


        if RUM == 'NONE':
            #new_grd_depth=new_slab_depth(grd_depth_slab1,grd_dip_slab1,grd_str_slab1,grd_slab_age,dict,slab_transition_depth,slab_transition_width)
            new_grd_depth=simple_slab_depth_correction(grd_depth_slab2,slab_depth_correction_grd)
            new_grd_depth_name="%s%s_slab2.0_new_depth.grd" % (New_grids_dir,s)
            cmd="mv %s %s" % (new_grd_depth,new_grd_depth_name)
            print(cmd)
            os.system(cmd)
        if RUM != 'NONE':
            #new_grd_depth=new_slab_depth(grd_depth_rum,grd_dip_rum,grd_str_rum,grd_slab_age,dict,slab_transition_depth,slab_transition_width)
            new_grd_depth=simple_slab_depth_correction(grd_depth_rum,slab_depth_correction_grd)
            #new_grd_depth_name="%s%s_rum_new_depth.grd" % (New_grids_dir,sn)
            new_grd_depth_name="%s%s_rum_new_depth.grd" % (RUM_grids_dir,sn)
            cmd="mv %s %s" % (new_grd_depth,new_grd_depth_name)
            print(cmd)
            os.system(cmd)

        long_min = float(dict['west'])
        long_max = float(dict['east'])
        lat_min = float(dict['south'])
        lat_max = float(dict['north'])
        long_mean=(long_min+long_max)/2.0

        aspect_ratio=(long_max-long_min)/(lat_max-lat_min)
        print(aspect_ratio)

        if aspect_ratio<=1.0:
            width=3.0*aspect_ratio
        else:
            width=3.0
        proj="-JH%g/%g" % (long_mean,width)
        region="%g/%g/%g/%g" % (long_min,long_max,lat_min,lat_max)

        if RUM == 'NONE':
            cmd="gmt grdimage %s -Cslab_depth.cpt %s -R%s -B10f2/10f2WeSn -X0.75 -Y7.5 -P -K > %s" % (grd_depth_slab2,proj,region,psfile)
        elif RUM != 'NONE':
            cmd="gmt grdimage %s -Cslab_depth.cpt %s -R%s -B10f2/10f2WeSn -X0.75 -Y7.5 -P -K > %s" % (grd_depth_rum,proj,region,psfile)
        print(cmd)
        os.system(cmd)
        cmd="gmt psxy %s %s -W1,1 -R%s -B -K -O >> %s" % (perimeter,proj,region,psfile)
        print(cmd)
        os.system(cmd)

        cmd="gmt psscale -Cslab_depth.cpt -D1.0/-0.4/2.0/0.15h -B200::/:km: -X0. -Y0 -O -K >> %s" % (psfile)
        print(cmd)
        os.system(cmd)


        #cmd="gmt grdimage %s -Cage.cpt %s -R%s -B10f2/10f2WeSn -X0.0 -Y-4.0 -P -O -K >> %s" % (grd_age,proj,region,psfile)
        cmd="gmt grdimage %s -Cdepth_correction.cpt %s -R%s -B10f2/10f2WeSn -X0.0 -Y-4.0 -P -O -K >> %s" % (slab_depth_correction_grd,proj,region,psfile)
        print(cmd)
        os.system(cmd)
      

        # Make sections
        i=1
        while i<=2:
            profile="Profiles/%s_profile_%d.xyp" % (s,i)
            center=sub_dict['C%d' % i]
            endpoint=sub_dict['E%d' % i]
            cmd="gmt project -C%s -E%s -Dg -G10 -Q > %s" % (center,endpoint,profile)
            print(cmd)
            os.system(cmd) 
            i += 1

    
        project_earthquakes2xsection(eq_simple,sub_dict,s)

        i=1
        while i<=2:
            profile="Profiles/%s_profile_%d.xyp" % (s,i)
            cmd="gmt psxy %s %s -W3,1 -R%s -B -K -O >> %s" % (profile,proj,region,psfile)
            print(cmd)
            os.system(cmd) 
            events_on_profile="Events/%s_%d.rs" % (s,i)
            cmd="gmt psxy %s %s -R%s -B -Sc0.02 -Gblue -K -O >> %s" % (profile,proj,region,psfile)
            print(cmd)
            os.system(cmd) 
            i += 1

        cmd="gmt psxy %s %s -W3,1 -R%s -B10/10WeSn -O -K >> %s" % (perimeter,proj,region,psfile)
        print(cmd)
        os.system(cmd)

        x_move=[]
        y_move=[]
        x_move.append("4.0")
        y_move.append("3.0")
        x_move.append("0.0")
        y_move.append("-3.0")
        # Generate & Plot profiles for slab depths (Slab2, RUM, & new) & topography
        i=1
        while i<=2:

            profile="Profiles/%s_profile_%d.xyp" % (s,i)

            # First plot hypocenters
            events_on_section="Events/%s_%d.pd" % (s,i)
            cmd="gmt psxy %s -JX3/2 -R-100/1200/-800/50 -B400f100/200f100WesN -Sc0.0125 -Gblue -X%s -Y%s -O -K >> %s" % (events_on_section,x_move[i-1],y_move[i-1],psfile)
            print(cmd)
            os.system(cmd)
            
            #Depth Profile: Slab 2
            if RUM == 'NONE' or RUM != 'only':
                profile_scaling=1.0
                tmp_profile=get_profile(profile,grd_depth_slab2,profile_scaling)
                depth_profile="Profiles/%s_slab2_depth_profile_%d.xypd" % (s,i)
                TP=open(tmp_profile)
                sxs,szs=TP.readline().split()
                xs=float(sxs)
                zs=float(szs)
                TP.close()
                cmd="mv %s %s" % (tmp_profile,depth_profile)
                os.system(cmd)
                cmd="gmt psxy %s -JX -R -B -W1,black -X0 -Y0 -O -K >> %s" % (depth_profile,psfile)
                print(cmd)
                os.system(cmd)

            #Depth Profile: RUM
            if RUM == 'only':
                profile_scaling=1.0
                tmp_profile=get_profile(profile,grd_depth_rum,profile_scaling)
                depth_profile="Profiles/%s_rum_depth_profile_%d.xypd" % (s,i)
                TP=open(tmp_profile)
                sxs,szs=TP.readline().split()
                xs=float(sxs)
                zs=float(szs)
                TP.close()
                cmd="mv %s %s" % (tmp_profile,depth_profile)
                os.system(cmd)
                cmd="gmt psxy %s -JX -R -B -W1,black -X0 -Y0 -O -K >> %s" % (depth_profile,psfile)
                print(cmd)
                os.system(cmd)
            if RUM != 'NONE' and RUM != 'only' :
                rum_depth_profile="Profiles/%s_rum_depth_profile_%d.xypd" % (s,i)
                profile_scaling=1.0
                tmp_profile=get_profile(profile,grd_depth_rum,profile_scaling)
                cmd="mv %s %s" % (tmp_profile,rum_depth_profile)
                os.system(cmd)
                
                cmd="gmt psxy %s -JX3/2 -R -B -W1,red -X0.0 -Y0 -O -K >> %s" % (rum_depth_profile,psfile)
                print(cmd)
                os.system(cmd)

            #Depth Profile: new
            new_depth_profile="Profiles/%s_new_depth_profile_%d.xypd" % (s,i)
            profile_scaling=1.0
            tmp_profile=get_profile(profile,new_grd_depth_name,profile_scaling)
            cmd="mv %s %s" % (tmp_profile,new_depth_profile)
            os.system(cmd)
            cmd="gmt psxy %s -JX -R -B -W1,orange -X0.0 -Y0.0 -O -K >> %s" % (new_depth_profile,psfile)
            print(cmd)
            os.system(cmd)

            # Make topo profile
            topo_profile="Profiles/%s_topo_profile_%d.xypd" % (s,i)
            profile_scaling=200.0
            tmp_profile=get_profile(profile,topo_grid,profile_scaling)
            tmp_profile_1=shift_profile(tmp_profile,"Z",xs,zs)
            cmd="mv %s %s" % (tmp_profile_1,topo_profile)
            os.system(cmd)
            cmd="gmt psxy %s -JX3/2 -R -B -W1,green -X0.0 -Y0 -O -K >> %s" % (topo_profile,psfile)
            print(cmd)
            os.system(cmd)

            i += 1

        #cmd="gmt psscale -Cage.cpt -D3.0/-0.4/2.0/0.15h -B100::/:Ma: -U -X-4. -Y0 -O -K >> %s" % (psfile)
        cmd='gmt psscale -Cdepth_correction.cpt -D3.0/-0.4/2.0/0.15h -Ba10f2::/:"correction (km)": -U -X-4. -Y0 -O -K >> %s' % (psfile)
        print(cmd)
        os.system(cmd)

        #label info
        LAB = open('label.txt','w')
        print("3.2 6.00 12 0 1 1 Trench: %s" %  (s), file=LAB)
        if RUM == 'only':
            print(" 3.2 5.7 10 0 1 1 Only RUM Slab (black) & New f RUM (Orange)", file=LAB)
        if RUM != 'only':
            if RUM == 'NONE':
                print(" 3.2 5.7 10 0 1 1 Only Slab2 (black)& New f Slab2 (Orange)", file=LAB)
            if RUM != 'NONE':
                print(" 3.2 5.7 10 0 1 1 Slab2 (black), RUM (Red) & New f RUM (Orange)", file=LAB)
        #print >> LAB, "3.2 5.40 10 0 1 1 Slab Transition: Depth=%g km  Width=%g km" %  (slab_transition_depth,slab_transition_width)
        LAB.close()
        cmd="gmt pstext label.txt -Jx1 -R0/8.5/0/11 -X0.0 -Y0.0 -O >> %s" % (psfile)
        print(cmd)
        os.system(cmd)


        make_pdf(psfile)

        psfile ="%s_2.ps" % ps_name_prefix

        # Maps for plate age, slab strike and slab dip
        cmd="rm tmp*.cpt"
        os.system(cmd)
        dict['grid']=grd_str
        Core_GMT.grdinfo( dict )
        dict['dz']=5.0
        dict['C']='rainbow'
        Core_GMT.makecpt( dict )
        print(dict)

        cmd="gmt grdimage %s -Cage.cpt %s -R%s -B10f2/10f2WeSn -X0.75 -Y8.0 -P -K > %s" % (age_grid,proj,region,psfile)
        print(cmd)
        os.system(cmd)
        cmd="gmt psxy %s %s -W3,blue -R%s -B -K -O -M >> %s" % (trench,proj,region,psfile)
        print(cmd)
        os.system(cmd)
        cmd="gmt psxy %s %s -W3,blue -R%s -B -K -O >> %s" % (trench_outside,proj,region,psfile)
        print(cmd)
        os.system(cmd)
        cmd="gmt psxy %s %s -W3,blue -R%s -B -K -O >> %s" % (trench_inside,proj,region,psfile)
        print(cmd)
        os.system(cmd)
        cmd="gmt psxy %s %s -W3,1 -R%s -B -K -O >> %s" % (perimeter,proj,region,psfile)
        print(cmd)
        os.system(cmd)
        cmd='gmt psscale -Cage.cpt -D3.0/-0.5/4.0/0.25h -B100::/:"Slab age (Ma)": -X0.0 -Y0 -O -K >> %s' % (psfile)
        print(cmd)
        os.system(cmd)


        # Stike
        #cmd="gmt grdimage %s -C%s %s -R%s -B10f2/10f2WeSn -X0.0 -Y-3.0 -P -O -K >> %s" % (grd_str,dict['C'],proj,region,psfile)
        # New age grid for slab
        cmd="gmt grdimage %s -Cage.cpt %s -R%s -B10f2/10f2WeSn -X0.0 -Y-3.0 -P -O -K >> %s" % (grd_age,proj,region,psfile)
        print(cmd)
        os.system(cmd)
        cmd="gmt psxy %s %s -W1,1 -R%s -B -K -O >> %s" % (perimeter,proj,region,psfile)
        print(cmd)
        os.system(cmd)

        cmd="gmt psscale -C%s -D3.0/-0.5/4.0/0.25h -B20::/:strike: -O -K >> %s" % (dict['C'],psfile)
        print(cmd)
        os.system(cmd)

        cmd="gmt grdimage %s -Cslab_dip.cpt %s -R%s -B10f2/10f2WeSn -X0.0 -Y-4.0 -P -O -K >> %s" % (grd_dip,proj,region,psfile)
        print(cmd)
        os.system(cmd)

        cmd="gmt psxy %s %s -W1,1 -R%s -B -K -O >> %s" % (perimeter,proj,region,psfile)
        print(cmd)
        os.system(cmd)

        cmd="gmt psscale -Cslab_dip.cpt -D3.0/-0.5/4.0/0.25h -B10::/:dip: -U -O >> %s" % (psfile)
        print(cmd)
        os.system(cmd)

        #====================================================================
        make_pdf(psfile)
        

        # Plot the epicentral locations on a map
        psfile ="%s_3.ps" % ps_name_prefix
        cmd="gmt psxy %s %s -R%s -B10f2/10f2WeSn -Sc0.02 -Ggreen -X0.75 -Y7.5 -P -K > %s" % (eq_simple,proj,region,psfile)
        print(cmd)
        os.system(cmd)

        events_in_section="Events/%s_1.xydm" % (s)
        cmd="gmt psxy %s %s -R%s -B -Sc0.02 -Gred -X0 -Y0 -P -O -K >> %s" % (events_in_section,proj,region,psfile)
        print(cmd)
        os.system(cmd)
        events_on_section="Events/%s_1.rs" % (s)
        cmd="gmt psxy %s %s -R%s -B -Sc0.02 -Gblue -X0 -Y0 -P -O -K >> %s" % (events_on_section,proj,region,psfile)
        print(cmd)
        os.system(cmd)

        events_in_section="Events/%s_2.xydm" % (s)
        cmd="gmt psxy %s %s -R%s -B -Sc0.02 -Gred -X0 -Y0 -P -O -K >> %s" % (events_in_section,proj,region,psfile)
        print(cmd)
        os.system(cmd)

        events_on_section="Events/%s_2.rs" % (s)
        cmd="gmt psxy %s %s -R%s -B -Sc0.02 -Gblue -X0 -Y0 -P -O >> %s" % (events_on_section,proj,region,psfile)
        print(cmd)
        os.system(cmd)

        #====================================================================
        make_pdf(psfile)
        


    # Clean up
    cmd = "rm *.grd *.xy *.xya *.xyz *.xydds *.xys tmp.xypd blend.job tmp.*.cpt"
    os.system(cmd)
    print(" ")

    return
#=====================================================================
def make_summary_table(slab_dict,slab_keys):

    OF=open("slab_summary.txt","w")
    OF.write("  slab   RUM\n")
    OF.write("________________\n")
    for s in slab_keys:
        sub_dict = slab_dict[s]
        RUM=sub_dict['RUM']
        OF.write("  %s    %s\n" % (s,RUM))

    OF.close()
    return
#=====================================================================
def shift_profile(profile,shift_dir,xs,zs):
    print("Shifting profile %s in direction %s" % (profile,shift_dir))
    PR=open(profile)
    if shift_dir == "Z":
        while 1:
            line=PR.readline()
            if(line):
                sx1,sz1=line.split()
                fx1=float(sx1)
                if(fx1 >= xs):
                    zoff=float(sz1)
                    break
            else:
                break
    elif shift_dir == "P":
        print("P")  
        line=PR.readline()
        sx1,sz1=line.split()
        poff=float(sx1)
    PR.close()
    shifted_profile='tmp_%s.pz' % shift_dir
    PR=open(profile)
    PS=open(shifted_profile,"w")
    while 1:
        line=PR.readline()
        if(line):
            sx1,sz1=line.split()
            fx1=float(sx1)
            fz1=float(sz1)
            if shift_dir == "Z":
                PS.write("%s  %g\n" % (sx1,fz1-zoff+zs))
            elif shift_dir == "P":
                PS.write("%g  %s\n" % (fx1-poff,sz1))
        else:
            break
    PR.close()
    PS.close()
    return shifted_profile
#=====================================================================
def project_earthquakes2xsection(all_quakes,sub_dict,s):

    i=1
    while i<=2:
        pro_center=sub_dict['C%d' % i]
        pro_end=sub_dict['E%d' % i]
        profile="Profiles/%s_profile_%d.xyp" % (s,i)
        events_in_section="Events/%s_%d.xydm" % (s,i)
        events_on_section="Events/%s_%d.rs" % (s,i)
        depth_section="Events/%s_%d.pd" % (s,i)
        cmd="gmt gmtselect %s -fg -L%s+d50000 > %s" % (all_quakes,profile,events_in_section)
        print(cmd)
        os.system(cmd)
        cmd="gmt project %s -C%s -E%s -Q > tmp.xyzpqrs" % (events_in_section,pro_center,pro_end)
        print(cmd)
        os.system(cmd)
        XS=open("tmp.xyzpqrs")
        EOS=open(events_on_section,"w")
        DS=open(depth_section,"w")
        while 1:
            line=XS.readline()
            if(line):
                s1,s2,s3,s4,s5,s6,s7,s8=line.split()
                fdepth=-float(s3)
                EOS.write("%s %s\n" % (s7,s8))
                DS.write("%s %g\n" % (s5,fdepth))
            else:
                break
        EOS.close()
        DS.close()

        i+=1

    return

#=====================================================================
def make_slab_age_depth_correction_grd(s,dict,XY_dir,age_grid,grd_depth,grd_str,trench_age_dist,trench_dep_dist,Nan_age):

    
    slab_NAN_age=Nan_age

    trench="%s%s_trench_0.xy" % (XY_dir,s)
    print('trench',trench)
    trench_for_age='%s%s_age_0.xy' % (XY_dir,s)
    print('trench for age', trench_for_age)
    trench_age_sampled="trench_age.xya"
    shifted_age='shifted_ages.xyz'
    shifted_str='shifted_str.xyz'
    trench_slab_depth_sampled="trench_slab_depth.xyd"
    slab_str_sampled="slab_str.xys"
    ofile="slab_ages.xya"
    slab_depth_correction="slab_depth_correction.xyd"
    slab_depth_correction_grd="slab_depth_correction.grd"

    spacing='NONE'
    print('xy_file ', trench_for_age)
    xyz_file=GMT_Utilities.xy2xyz(trench_for_age,0.0,spacing,0.0)
    print('xyz_file ',xyz_file)
    #sample age grid just outside of the trench
    dist=-1.0*trench_age_dist
    outside=Mat_Utilities.mk_parallel_line(xyz_file,0,dist)
    GMT_Utilities.remove_gmt_char(outside,shifted_age,"xyz")
    cmd="gmt grdtrack %s -G%s > %s" % (shifted_age,age_grid,trench_age_sampled)
    print(cmd)
    os.system(cmd)
    #sample str (strike of slab) grid just inside of the trench
    dist=1.0*trench_dep_dist
    xyz_file=GMT_Utilities.xy2xyz(trench,0.0,spacing,0.0)
    inside=Mat_Utilities.mk_parallel_line(xyz_file,0,dist)
    print('inside ',inside)
    GMT_Utilities.remove_gmt_char(inside,shifted_str,"xyz")
    cmd="gmt grdtrack %s -G%s > %s" % (shifted_str,grd_str,slab_str_sampled)
    print(cmd)
    os.system(cmd)
    cmd="gmt grdtrack %s -G%s > %s" % (shifted_str,grd_depth,trench_slab_depth_sampled)
    print(cmd)
    os.system(cmd)

    #print 'trench_age_sampled',trench_age_sampled
    #print 'slab_str_sampled',slab_str_sampled
    #print 'grd_str',grd_str
    #print 'age_grd ',age_grid
    AT=open(trench_age_sampled)
    DT=open(trench_slab_depth_sampled)
    SS=open(slab_str_sampled)
    SA=open(ofile,"w")
    SDC=open(slab_depth_correction,"w")
    d_prior_in_list=-10.0
    
    while 1:
        line1=AT.readline()
        line2=SS.readline()
        line3=DT.readline()
        if(line1):
            s1,s2,s3,s4=line1.split()
            flon=float(s1)
            flat=float(s2)
            fage=float(s4)
            #if fage >= slab_NAN_age:
            #    fage=slab_NAN_age
            s1,s2,s3,s4=line2.split()
            flon=float(s1)
            flat=float(s2)
            fazim=float(s4)+90.0
            s1,s2,s3,s4=line3.split()
            fdepth_c=float(s4)
            if s4 == 'NaN':
                fdepth_c=d_prior_in_list
            d_prior_in_list=fdepth_c
            cmd="gmt project -C%g/%g -A%g -L0/1000 -G10 -Q > trench_projected.xy" % (flon,flat,fazim)
            os.system(cmd)
            TP=open("trench_projected.xy")
            while 1:
                line3=TP.readline()
                if(line3):
                    ss1,ss2,ss3=line3.split()
                    fs1=float(ss1)
                    if fs1 < 0.0:
                        fs1=360.0+fs1
                    SA.write("%g %s %g\n" % (fs1,ss2,fage))
                    SDC.write("%g %s %g\n" % (fs1,ss2,fdepth_c))
                else:
                    break
            TP.close()
        else:
            break
    AT.close()
    SS.close()
    SA.close()
    SDC.close()
    
    tension=0.5
    age_min=0.1
    age_max=200.0
    tmp_grd=GMT_Utilities.mk_grd(ofile, dict['R'], dict['dx'], tension, age_min, age_max) 
    slab_age_grd="slab_age.grd"
    cmd="gmt grdmath %s %s OR = %s" % (tmp_grd,grd_depth,slab_age_grd)
    print(cmd)
    os.system(cmd)

    depth_c_min=-50.0
    depth_c_max=0.0
    tmp_grd=GMT_Utilities.mk_grd(slab_depth_correction, dict['R'], dict['dx'], tension, depth_c_min, depth_c_max) 
    cmd="mv %s %s" % (tmp_grd,slab_depth_correction_grd)
    print(cmd)
    os.system(cmd)

    return slab_age_grd, trench, shifted_age, shifted_str, slab_depth_correction_grd
#=====================================================================
def get_profile(profile,grd,scale):

    tmp_name="tmp.pd"
    cmd="gmt grdtrack %s -G%s -S > tmp.xypd" % (profile,grd)
    print(cmd)
    os.system(cmd)
    IP=open("tmp.xypd")
    OP=open(tmp_name,"w")
    k=0
    poff=0.0
    while 1:
        k += 1
        line=IP.readline()
        if (line):
            x,y,p,d=line.split()
            fp=float(p)
            fd=float(d)/scale
            if k==1:
                poff=fp
            #OP.write("%g %g\n" % (fp-poff,fd))
            OP.write("%g %g\n" % (fp,fd))
        else:
            break
    IP.close()
    OP.close() 

    return tmp_name
#=====================================================================
def new_point(x1,y1,depth,dip,str,slab_width):
 
    old_x=float(x1)
    old_y=float(y1)
    old_depth=float(depth)
    old_dip=float(dip)
    old_str=float(str)
    #colatitude
    theta=90.0-old_y
    new_depth=old_depth-slab_width*math.sin( d2r*(90.-old_dip) )
    #distance is distance in map view
    distance=slab_width*math.cos( d2r*(90.-old_dip) )
    ss=old_str-90.0
    dx=distance*math.sin(d2r*ss)
    dy=distance*math.cos(d2r*ss)
    dlon=dx*180.0/(math.sin(d2r*theta)*math.pi*earth_radius)
    dlat=dy*180.0/(math.pi*earth_radius)
    new_x=old_x+dlon
    new_y=old_y+dlat
    return new_x,new_y,new_depth

#=====================================================================
def simple_slab_depth_correction(depth_grd,correction_grd):
    print('depth_grd, correction_grd: ',depth_grd,correction_grd)
    new_grd_depth="new_depth.grd"

    cmd="gmt grdmath %s %s SUB = %s" % (depth_grd,correction_grd,new_grd_depth)
    print(cmd)
    os.system(cmd)
    return new_grd_depth
#=====================================================================
def new_slab_depth(grd_depth,grd_dip,grd_str,grd_slab_age,dict,slab_transition_depth,slab_transition_width):


    xyz_depth="depth.xyz"
    xyz_dip="dip.xyz"
    xyz_str="str.xyz"
    xyz_slab_age="slab_age.xyz"
    
    #Set this so half-thickness is 50 km for 150 Ma old lithosphere
    thickness_factor=50.0/math.sqrt(150.0)

    cmd="gmt grd2xyz %s -S > %s" % (grd_depth,xyz_depth)
    print(cmd)
    os.system(cmd)
    cmd="gmt grd2xyz %s -S > %s" % (grd_dip,xyz_dip)
    print(cmd)
    os.system(cmd)
    cmd="gmt grd2xyz %s -S > %s" % (grd_str,xyz_str)
    print(cmd)
    os.system(cmd)
    cmd="gmt grd2xyz %s -S > %s" % (grd_slab_age,xyz_slab_age)
    print(cmd)
    os.system(cmd)
    I_DEPTH=open(xyz_depth)
    I_DIP=open(xyz_dip)
    I_STR=open(xyz_str)
    I_AGE=open(xyz_slab_age)
    OUT=open("tmp.xydds","w")
    O_DEPTH=open("new_depth.xyz","w")
    while 1:
        depth_line=I_DEPTH.readline()
        dip_line=I_DIP.readline()
        str_line=I_STR.readline()
        age_line=I_AGE.readline()
        if(depth_line and dip_line and str_line):
            x1,y1,depth=depth_line.split()
            x2,y2,dip=dip_line.split()
            x3,y3,str=str_line.split()
            x4,y4,s4=age_line.split()
            s_age=float(s4)
            s_depth=float(depth)
            #slab_width is half thickness of the slab
            slab_width = thickness_factor*math.sqrt(s_age)*(1.0+math.tanh((s_depth+slab_transition_depth)/slab_transition_width))/2.0
            OUT.write("%s %s %s %s %s\n" % (x1,y1,depth,dip,str) )
            if (x1 != x2 or x1 != x3 or y1 != y2 or y1 != y3 or y1 != y4):
                print('ERROR')
                print(x1,y1,x2,y2,x3,y3,x4,y4)
                print(' xyz data from grd misalligned')
            new_x,new_y,new_depth=new_point(x1,y1,depth,dip,str,slab_width)
            O_DEPTH.write("%g %g %g\n" % (new_x,new_y,new_depth))
        else:
            break
    I_DEPTH.close()
    I_DIP.close()
    I_STR.close()
    OUT.close()
    O_DEPTH.close()


    cmd="gmt xyz2grd new_depth.xyz -Gtmp.grd -I%s/%s -R%s" % (dict['dx'],dict['dy'],dict['R'])
    print(cmd)
    os.system(cmd)
    new_grd_depth='tmp.grd'

    return new_grd_depth
#=====================================================================
#=====================================================================
#    TOP OF MAIN
#=====================================================================
#=====================================================================
from Slab_Dictionary_Slab2 import slab_dict
dict = {}

if len(sys.argv) != 2:
    usage()

mode=sys.argv[1]


# Get the top level keys and sort them
slab_keys = list(slab_dict.keys());
slab_keys.sort()

cmd="gmt gmtset PS_MEDIA letter PROJ_LENGTH_UNIT inch"
os.system(cmd)

#=============================================================
#Key parameters governing the transition from the plate interface
# to the center of the thermal slab 
slab_transition_depth=80.0
slab_transition_width=40.0

#==================================================================
#Resample all of the of sub-regions onto global grd files
#grd_global_depth="%s_global_depth.grd" % (subduction_prefix)
#cmd="grdblend blend.job -G%s -I0.02/0.02 -R120/150/10/40" %(grd_global_depth)
#print cmd
#os.system(cmd)


if mode == 'S':
    make_summary_table(slab_dict,slab_keys)
elif mode == 'C':
    make_slab_depth_contous(slab_dict,slab_keys)
elif mode == 'R':
    make_regional_plots(slab_dict,slab_keys)
elif mode == 'G':
    make_global_plot(slab_dict,slab_keys)
elif mode == 'P':
    #eq_simple=Earthquake_Utilities.get_CMT_Catalog(1)
    eq_simple=Earthquake_Utilities.get_EHB_Catalog(1)
    reprocess_plot_each_slab_individually(slab_dict,slab_keys)
elif mode == 'X':
    summary_cross_section(slab_dict,slab_keys)

#====================================================================
    
print("\n \n Done! \n \n")

# EOF

