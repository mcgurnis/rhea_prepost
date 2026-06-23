#!/usr/bin/env python
#=====================================================================
#
#       Python Scripts for Geodynamics pre- and post- processing
#                  ---------------------------------
#
#                              Authors:
#                             Mike Gurnis
#          (c) California Institute of Technology 2009 - 2026
#
#               Free for non-commercial academic use ONLY.
#      This program is distributed WITHOUT ANY WARRANTY whatsoever.
#
#=====================================================================
#
#=====================================================================
#
# Last Update: Mike Gurnis, June 23, 2026


import sys, string, os, math
import Mat_Utilities, GMT_Utilities, Rhea_Utilities

r2d = 180.0/math.pi
d2r=1.0/r2d
earth_radius = 6371.0
therm_diff=1e-06
layer_km=earth_radius
depth_lower_mantle = 670
depth_lithosphere = 400 # This is just a lower limit


#=====================================================================
#rhea_depths="/net/beno/raid1/gurnis/Rhea_Input/Temp_2_rhea/shell_temperature_k2_ll456_z_June2015.txt"
rhea_depths="/net/beno/data1/gurnis/Rhea_meshes/shell_k2_ll5678_2016-03/depth_listing-l5678.dat"
#rhea_depths="/net/beno/raid1/gurnis/Rhea_meshes/shell_k2_ll5678_2016-03/tmp_truncated-l5678.dat"

#=====================================================================
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
def interpolate_2_Rhea_mesh(grd_name,code_grd_name,nodes,id,radius):

    print("Inside interpolate_2_Rhea_mesh")
    print("id",id)
    print('grd_name',grd_name)
    print('code_grd_name',code_grd_name)
    print('nodes', nodes)
    interpolated_file="interpolated.xyzt"
    interpolated_code_file="interpolated_code.xyzt"
    new_rhea_file_name="rhea_temp.nrxytc"
    #sample grd at points in node file
    cmd="gmt grdtrack %s -G%s > %s" % (nodes,grd_name,interpolated_file)
    os.system(cmd)
    cmd="gmt grdtrack %s -G%s > %s" % (nodes,code_grd_name,interpolated_code_file)
    os.system(cmd)


    mesh_interp=open(interpolated_file)
    mesh_code_interp=open(interpolated_code_file)
    rhea=open(new_rhea_file_name,"w")
    while 1:
        line=mesh_interp.readline()
        line_code=mesh_code_interp.readline()
        if(line):
            v1, v2, v3, v4 =line.split()
            vc1, vc2, vc3, vc4 =line_code.split()
            long=float(v1)
            lat=float(v2)
            n=int(v3)
            temp=float(v4)
            slab=float(vc4)

            code=0
            if id < 100 and slab < 0.8:
                code=1
            elif id >= 100 and slab < 0.8:
                code=2

            phi = d2r*(long-180.0)
            theta = -1.0*d2r*(lat-90.0)
            rhea.write("%d %f %f %f %f %d\n" %(n, radius, phi,theta,temp,code))

        else:
            break
    mesh_interp.close()
    rhea.close()
    return new_rhea_file_name

#=====================================================================
#=====================================================================
def mk_tomography_weights(radii_depths_list):

    depth_1 = 550.0
    #depth_1 = 650.0
    width_1 = 150.0
    #width_1 = 75.0

    weights = {}

    for r in radii_depths_list:
        id=int(r.split()[1])

        arg = (float(id) - depth_1)/width_1
        weight_tomo = (1.0 + math.tanh(arg))/2.0
        weight_slab = 1.0 - weight_tomo
        #weight_slab = 1.0
        #print id, weight_slab, weight_tomo
        weights[id] = weight_slab, weight_tomo


    return weights
#=====================================================================
#=====================================================================
def get_lith_temp_grd(z,age_grd,scalet):
    lfile_name="lith.grd"
    print('z=',z)
    print('scalet',scalet)

    cmd="gmt grdmath %s %e DIV = scaled_age.grd" % (age_grd,scalet)
    print(cmd)
    os.system(cmd)
    cmd="gmt grdmath scaled_age.grd SQRT = arg1.grd"
    print(cmd)
    os.system(cmd)
    cmd="gmt grdmath 0.5 %e MUL arg1.grd DIV = arg2.grd" % z
    print(cmd)
    os.system(cmd)
    cmd="gmt grdmath arg2.grd ERF = %s" % lfile_name
    print(cmd)
    os.system(cmd)

    return lfile_name
#=====================================================================
#=====================================================================
def mk_const_grd(grd_res,const,tension, grid_min, grid_max):

    bounds = '0/360/-90/90'
    file_name="const.xyt"
    xyzfile=open(file_name,"w")
    flong=0.0
    while flong<360.0:
        flat=-90.0
        while flat<90.0:
            xyzfile.write("%f %f %f\n" % (flong,flat,const) )
            flat+=grd_res
        flong+=grd_res

    xyzfile.close()

    grdfile = GMT_Utilities.mk_grd(file_name, bounds, grd_res, tension, grid_min, grid_max)

    new_grdfile = "const_%f.grd" % const
    cmd="mv %s %s" % (grdfile,new_grdfile)
    print(cmd)
    os.system(cmd)

    return new_grdfile

#=====================================================================
def make_pdf(psfile):
    print("\n    Converting file to pdf ...")
    cmd = "gmt psconvert %s -A -Tf -E200" % (psfile)
    os.system(cmd)

    cmd='rm -f *.ps'
    os.system(cmd)
    cmd='mv *.pdf PDF'
    os.system(cmd)

    return
#=====================================================================

#tomo_dir="/net/holmes/home4/gurnis/Rhea_runs/Tomography/S20RTS_Mesh_Level5678/"
#tomo_dir="/net/beno/raid1/gurnis/Tomography/S20RTS_Mesh_Level58/"
#tomo_dir="/net/holmes/home4/gurnis/Rhea_runs/Tomography/S20RTS_Rhea2_Test/"
#tomo_dir="/net/holmes/home4/gurnis/Rhea_runs/Tomography/S20RTS_k2_l5678/"
#tomo_name="s20rts"
#tomo_name="Li"
tomo_dir="/net/beno/data1/gurnis/Tomography/LLNL_k2_l5678/"
tomo_name="LLNL"

#slab_temp_dir="/net/beno/data1/gurnis/Rhea_Input/XSectional_Rhea_Data/k2l5678_VariableDescent/Slabs/GRD_GLOBAL"
#slab_temp_dir="/net/beno/data1/gurnis/Rhea_Input/XSectional_Rhea_Data/k2l5678_Test_FD_2.5cmyr/Slabs/GRD_GLOBAL"
#slab_temp_dir="/net/beno/data1/gurnis/Rhea_Input/XSectional_Rhea_Data/k2l5678_Test_Filter_0.05/Slabs/GRD_GLOBAL"
#slab_temp_dir="/net/beno/data1/gurnis/Rhea_Input/Global_Rhea2_Data_VariableDescent/Slabs/GRD_GLOBAL"
slab_temp_dir="/net/beno/data1/gurnis/Rhea_Input/Global_Rhea_April_2022/Slabs/GRD_GLOBAL"


#rheamesh_dir="/net/beno/raid1/gurnis/Rhea_meshes/Mesh_R2_low_res/"
#slab_age_dir="/net/beno/raid2/alisic/Rhea_input/Slabs/Level5678_2/"
#tomo_dir="/net/beno/raid2/alisic/Rhea_input/Tomography/S20RTS_Mesh_Level5678/"
#age_grid="/net/beno/raid2/alisic/Rhea_input/Age_grids/new_age_075_125_300_Tonga_1-28.grd"
#age_grid="/net/beno/raid2/alisic/Rhea_input/Age_grids/new_age_042811.grd"
age_grid="/net/holmes/home4/gurnis/Rhea_runs/Cratons_Tectonic_Regionalization/Sonja/new_age_050_125_300_5-5-16.grd"

#===============================================================
#      Parameters controlling the construction of the grd pts
#===============================================================
temperature_min = 0.
temperature_mantle = 1.
grd_min = temperature_min
grd_max = temperature_mantle
tension=0.2
tension=0.1
grd_res_global=0.05
#grd_res=0.025  # In degrees
#grd_res=0.05  # In degrees
#grd_res=0.1  # In degrees
#grd_res=1.0  # In degrees
grd_res=grd_res_global
#spacing_bkg_pts=5.0*grd_res
spacing_bkg_pts=10.0*grd_res
#min_deg_pts_on_line=0.25*grd_res
min_deg_pts_on_line=0.1*grd_res


#Information about the map
bounds = '0/360/-90/90'
#the next values in inches
mapwidth = 6.0
proj = 'H180/%f' % mapwidth
map_info="-B90 -X0.5 -Y7.0"


T_surface=0.0
T_mantle=1.0
age_min=0.1
age_max=300.0

scalet = layer_km*1e3*layer_km*1e3/(therm_diff*1.e6*365.25*24.*3600.)
#===============================================================
#cmd="gmt grdsample %s -Gtmp1.grd -I%f -R%s" % (age_grid,grd_res,bounds)
cmd="gmt grdsample %s -Gtmp1.grd -I%f" % (age_grid,grd_res)
os.system(cmd)
cmd="gmt grdclip tmp1.grd -Gtmp2.grd -Sb%f/%f" % (age_min,age_min)
os.system(cmd)
cmd="gmt grdmath tmp2.grd %f AND = age.grd " % (age_max)
os.system(cmd)
#===============================================================
depth_max = 2900 # Whole mantle

#layer_depths=get_layer_depths()
#In rhea2 these values are now floats, before they were ints
layer_depths=get_layer_depths_rhea2()



rheamesh_used=[] #  this is a dummy list
radii_depths_list = []
for ld in layer_depths:
    radius = (earth_radius-ld)/earth_radius
    rheamesh_used.append("1 dummy %d %f" % (ld,radius))
    radii_depths_list.append("%f %d" % (radius,ld))


weights = mk_tomography_weights(radii_depths_list)
background_temp_grd = mk_const_grd(grd_res,T_mantle,tension, grd_min, grd_max)

surface_temp_grd = mk_const_grd(grd_res,T_surface,tension, grd_min, grd_max)
cmd="mkdir PDF"
os.system(cmd)
#===============================================================
#   Main loop through each depth which exists in Rhea mesh
#===============================================================
rheamesh_used.reverse()
for rm in rheamesh_used:
    print('rm',rm)
    ir=int(rm.split()[0])
    id=int(rm.split()[2])
    print(' id=',id)
    radius=float(rm.split()[3])

    # Establish File names
    temp_file_name = "temperature_%04d.dat" % id
    temp_grd_name = "temperature_%04d.grd" % id

    cmd="cp %s %s" % (background_temp_grd,temp_grd_name)
    os.system(cmd)

    slab_file_name = background_temp_grd
    if id < depth_lower_mantle:
        # Use existing precomputed slabs
        original_slab_file_name="%s/tmp_layer_%03d.grd" % (slab_temp_dir,id)
        slab_file_name="slab_tmp.grd"
        cmd="gmt grdsample %s -G%s -I%g" % (original_slab_file_name,slab_file_name,grd_res)
        print(cmd)
        os.system(cmd)
        cmd="cp %s %s" % (slab_file_name,temp_grd_name)
        print(cmd)
        os.system(cmd)

    # Assemble Tomography to grd's and mix with slabs
    if id > depth_lithosphere:
        tomo_xyz = "%s%s_%04d.xyz" % (tomo_dir,tomo_name,id)
        xyz_file=GMT_Utilities.toggle_shift_xyz(tomo_xyz,'S3')
        grdtmpfile  = GMT_Utilities.mk_grd(xyz_file,bounds,grd_res,tension,grd_min,grd_max)
        tomo_grd = "tomo_temp_%04d.grd" % id
        ##cmd="gmt grdmath %s -1.5 MUL 1.0 ADD = %s" % (grdtmpfile,tomo_grd)
        #cmd="gmt grdmath %s -1.0 MUL 1.0 ADD = %s" % (grdtmpfile,tomo_grd)
        cmd="gmt grdmath %s -0.5 MUL 1.0 ADD = %s" % (grdtmpfile,tomo_grd)
        #cmd="gmt grdmath %s -0.25 MUL 1.0 ADD = %s" % (grdtmpfile,tomo_grd)
        #cmd="gmt grdmath %s -0.1 MUL 1.0 ADD = %s" % (grdtmpfile,tomo_grd)
        # Zero out tomo, i.e. make 1 everywhere
        #cmd="gmt grdmath %s 0.0 MUL 1.0 ADD = %s" % (grdtmpfile,tomo_grd)
        print(cmd)
        os.system(cmd)
        print('tomo_grd',tomo_grd)
        #cmd="mv %s tmp.grd" % (temp_grd_name)
        #os.system(cmd)
        weight_slab = weights[id][0]
        weight_tomo = weights[id][1]
        cmd="gmt grdmath %s %f MUL = tmp1.grd" % (slab_file_name,weight_slab)
        os.system(cmd)
        cmd="gmt grdmath %s %f MUL = tmp2.grd" % (tomo_grd,weight_tomo)
        os.system(cmd)
        cmd="gmt grdmath tmp1.grd tmp2.grd ADD = tmp3.grd"
        os.system(cmd)
        cmd="gmt grdclip tmp3.grd -G%s -Sa1.0/1.0 -Sb0.0/0.0" % (temp_grd_name)
        os.system(cmd)


    if id <= depth_lithosphere and id > 0:
        nondim_depth=1.0-radius
        print('nondim_depth, radius ', nondim_depth, radius)
        lith_grd=get_lith_temp_grd(nondim_depth,"age.grd",scalet)
        cmd="mv %s tmp.grd" % (temp_grd_name)
        print(cmd)
        os.system(cmd)
        #cmd="gmt grdmath tmp.grd %s MUL = %s" % (lith_grd,temp_grd_name)
        #print(cmd)
        #os.system(cmd)

        cmd="gmt grdmath tmp.grd %s MIN = %s" % (lith_grd,temp_grd_name)
        print(cmd)
        os.system(cmd)

    elif id == 0:
        cmd="cp %s %s" % (surface_temp_grd,temp_grd_name)
        os.system(cmd)

    cmd="gmt gmtset PS_MEDIA letter PROJ_LENGTH_UNIT inch"
    os.system(cmd)

    psfile="temperature_%04d.ps" % id

    cmd = 'gmt grdimage -JH0/7 %s -Ctemp.cpt -R0/360/-90/90 -P -X1.0 -Y7 > %s' % (temp_grd_name,psfile)
    print(cmd)
    os.system(cmd)

    cmd='mkdir GRD'
    os.system(cmd)
    cmd='mv %s GRD/' % (temp_grd_name)
    os.system(cmd)

    make_pdf(psfile)

#Make clean
cmd="rm -f *.grd *.xyz"
print('clean up')
os.system(cmd)
