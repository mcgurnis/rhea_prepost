#!/usr/bin/env python
# #=====================================================================
#
#       Python Scripts for Geodynamics pre- and post- processing
#                  ---------------------------------
#
#                              Authors:
#                             Mike Gurnis
#          (c) California Institute of Technology 2013-2015
#
#               Free for non-commercial academic use ONLY.
#      This program is distributed WITHOUT ANY WARRANTY whatsoever.
#
#=====================================================================
#
#  Copyright July 2015, by the California Institute of Technology.
#
#=====================================================================
"""
Usage:
Generate_Regional_Thermal_Slab.py

"""
#=====================================================================

import Core_GMT, GMT_Utilities, Mat_Utilities, Earthquake_Utilities
#import Rhea_Utilities
import Thermal_Utilities
import os, string, sys, math, time, datetime, random
import numpy as np

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

grd_res_global=0.05

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
print('dt=',dt,' this should be in seconds')
dt=0.5*dt # This is a factor to avoid instability

timesteps=1  # Number of time-steps to evolve system.
#reset timesteps later

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
Slab2_grids_dir="/Volumes/STORE01/Rhea/Slab2/"
Slab2_Age_Dir="/Volumes/STORE01/Rhea/Slab2/Slab_Age_Grids/"

rhea_depths="/Users/gurnis/Desktop/Gurnis_Files/Working/Current_Work/Rhea_global_runs/Rhea2/Rhea_meshes/shell_k2_ll5678_2016-03/depth_listing-l5678.dat"
Slab2_XY_dir="/Volumes/STORE01/Rhea/Slab2/Slab2Clips/"
profile_dir="/Users/gurnis/Desktop/Gurnis_Files/Working/Current_Work/Rhea_global_runs/Slab2.0/Profiles/"

global_convergence_grd_file="/Users/gurnis/Desktop/Gurnis_Files/Working/Current_Work/Rhea_global_runs/Convergence_Velocity/convergence_extrapolated.grd"

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

Slab1_Age_Dir="/net/holmes/home4/gurnis/Rhea_runs/Slab1.0/Slab_Age_Grids/"

RUM_Age_Dir="/net/holmes/home4/gurnis/Rhea_runs/RUM_Slabs/Slab_Age_Grids/"

topo_grid="/net/holmes/scratch2/gurnis/ETOPO-02/etopo2.grd"

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

rum_slab_contours="/net/holmes/home4/gurnis/Rhea_runs/Slabs/Level567/all_contours_567.xyz"

#profile_dir="/net/holmes/home4/gurnis/Rhea_runs/Slab1.0/Profiles/"

#global_convergence_grd_file="/net/holmes/home4/gurnis/Rhea_runs/Convergence_Velocity/convergence_extrapolated.grd"

#=====================================================================
#=====================================================================
def usage():

    print(''' Generate_Regional_Thermal_Slab.py)

    where mode =


''')

    sys.exit(0)
#=====================================================================
def update_array_for_variable_descent(sn,xy_file_name,proj,region):
    global nx,ny,nz,T,Tf,Th,Theta,CosTheta,SinTheta,R,Alpha,DeltaT,Duration, layer_depths

    psfile=sn+"_convergence.ps"

    cpt_file="/Users/gurnis/Desktop/Gurnis_Files/Working/Current_Work/Rhea_global_runs/Convergence_Velocity/convergence.cpt"

    cmd="gmt grdimage %s %s -C%s -R%s -Ba10f1/a10f1 -P -K > %s" % (global_convergence_grd_file,proj,cpt_file,region,psfile)
    print(cmd)
    os.system(cmd)
    overlay_plate_boundaries(psfile,0,1)

    make_pdf(psfile,sn)


    Two_D_Array=np.zeros([nx,ny])

    convergence_xyz="convergence.xyz"
    cmd="gmt grdtrack %s -G%s > %s" % (xy_file_name,global_convergence_grd_file,convergence_xyz)
    print(cmd)
    os.system(cmd)

    XYZ_FILE=open(convergence_xyz)
    duration_max=-10000.0
    for i in range(nx):
        for j in range(ny):
            line=XYZ_FILE.readline()
            if(line):
                s1,s2,s3=line.split() 
                #convergence=float(s3)/(100.0*s_yr)
                convergence=2.5/(100.0*s_yr)
                Two_D_Array[i,j]=convergence
            else:
                break
    XYZ_FILE.close()

    for k, layer_depth in enumerate(layer_depths):
        print(' layer_depth=',layer_depth) 
        #duration_in_sec 
        Duration[:,:,k]=(layer_depth*1000)/Two_D_Array[:,:]
        #DeltaT[:,:,k]=Two_D_Array[:,:]


    print('dt',dt)
    print('depth_max',depth_max)
    print('Duration.max=',Duration.max)

    timesteps=int(Duration.max()/dt)
    print('timesteps=',timesteps)
    DeltaT=Duration/timesteps
    print('DeltaT.min',DeltaT.min())
    print('DeltaT.max',DeltaT.max())

    return
#=====================================================================
def diffuse_with_filter(sn,layer_depths,ic_grd_file_names,convergence_vel):

    vel = convergence_vel/(100.0*s_yr)

    directory="GRD_FINAL/"+sn
    cmd="mkdir %s" % (directory)
    print(cmd)
    os.system(cmd)

    grd_file_names=[]
    for i in range(len(layer_depths)):
        layer=layer_depths[i]
        in_grd_file=ic_grd_file_names[i]
        out_grd_file="GRD_FINAL/%s/layer_%03d.grd" % (sn,int(layer))
        grd_file_names.append(out_grd_file)

        time_in_sec = (layer*1000)/vel
        #dt_kappa = time_in_sec*therm_diff
        # 6 times the normal distance in a Gaussian Filter
        diff_dist=0.001 + 9.0*math.sqrt(therm_diff*time_in_sec)/1000.0
        cmd = "gmt grdfilter %s -D1 -Fg%s -G%s" % (in_grd_file,diff_dist,out_grd_file)
        # CURV(T) = Laplacian(T)
        #cmd = "gmt grdmath %s CURV %g MUL = %s" % (in_grd_file,dt_kappa,out_grd_file)
        print(cmd)
        os.system(cmd)

        #Make a plot of the temperature with overlays for each depth
        psfile="temp_final_%03d.ps" % int(layer)
        cmd="gmt makecpt -Cpolar -T0.0/1.0/0.1 -D > temp.cpt"
        print(cmd)
        os.system(cmd)
        cmd="gmt grdimage %s %s -Ctemp.cpt -R%s -Ba10f1/a10f1 -P -K > %s" % (out_grd_file,proj,region,psfile)
        print(cmd)
        os.system(cmd)

        overlay_plate_boundaries(psfile,0,1)

        make_pdf(psfile,sn)

    return grd_file_names
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
def positive_depths_limit(p1,limit):

    IF=open(p1)
    p2="p2.tmp"
    OF=open(p2,"w")

    while 1:
        line=IF.readline()
        if(line):
            x,y=line.split()
            fy=float(y)
            if(abs(fy) < abs(limit)):
                OF.write("%s    %f\n" % (x,-fy))
        else:
            break
    IF.close()
    OF.close()
    return p2
#=====================================================================
def check_for_existence_grd_ic_files(grd_file_names): 
    check=1
    for file_name in grd_file_names:
        if not os.path.exists(file_name):
            check=0
    return check
#=====================================================================
def Horizontal_Sph_Diffuse():
    """ 
    This function uses a numpy expression to
    evaluate the derivatives in the Laplacian
    within a spherical geometry, but only those
    terms acting in the theta and phi directions, and
    calculates Th[i,j,k] based on T[i,j,k].
    """
    global nx,ny,nz,T,Tf,Th,Theta,CosTheta,SinTheta,R,Alpha,DeltaT,Duration, layer_depths
    #Th=T
    Th[1:-1, 1:-1, 1:-1] = T[1:-1, 1:-1, 1:-1] + kappa*DeltaT[1:-1, 1:-1, 1:-1]*( (T[2:, 1:-1, 1:-1] - 2*T[1:-1, 1:-1, 1:-1] + T[:-2, 1:-1, 1:-1])/(dx2*(R[1:-1, 1:-1, 1:-1]**2)*(SinTheta[1:-1, 1:-1, 1:-1]**2)) + (CosTheta[1:-1, 1:-1, 1:-1]*(T[2:, 1:-1, 1:-1] - T[:-2, 1:-1, 1:-1])/(2*dy*(R[1:-1, 1:-1, 1:-1]**2)*(SinTheta[1:-1, 1:-1, 1:-1])) ) + (T[1:-1, 2:, 1:-1] - 2*T[1:-1, 1:-1, 1:-1] + T[1:-1, :-2, 1:-1])/(dy2*(R[1:-1, 1:-1, 1:-1]**2)) )

    #delete below
    #Th[1:-1, 1:-1, 1:-1] = T[1:-1, 1:-1, 1:-1] + kappa*dt*( (T[2:, 1:-1, 1:-1] - 2*T[1:-1, 1:-1, 1:-1] + T[:-2, 1:-1, 1:-1])/(dx2*(R[1:-1, 1:-1, 1:-1]**2)*(SinTheta[1:-1, 1:-1, 1:-1]**2)) + (CosTheta[1:-1, 1:-1, 1:-1]*(T[2:, 1:-1, 1:-1] - T[:-2, 1:-1, 1:-1])/(2*dy*(R[1:-1, 1:-1, 1:-1]**2)*(SinTheta[1:-1, 1:-1, 1:-1])) ) + (T[1:-1, 2:, 1:-1] - 2*T[1:-1, 1:-1, 1:-1] + T[1:-1, :-2, 1:-1])/(dy2*(R[1:-1, 1:-1, 1:-1]**2)) )

#=====================================================================
def Full_Sph_Diffuse():
    """ 
    This function uses a numpy expression to
    evaluate the derivatives in the Laplacian
    within a spherical geometry, and
    calculates Tf[i,j,k] based on T[i,j,k].
    """
    global nx,ny,nz,T,Tf,Th,Theta,CosTheta,SinTheta,R,Alpha,DeltaT,Duration, layer_depths
    Tf[1:-1, 1:-1, 1:-1] = T[1:-1, 1:-1, 1:-1] + kappa*DeltaT[1:-1, 1:-1, 1:-1]*( (T[2:, 1:-1, 1:-1] - 2*T[1:-1, 1:-1, 1:-1] + T[:-2, 1:-1, 1:-1])/(dx2*(R[1:-1, 1:-1, 1:-1]**2)*(SinTheta[1:-1, 1:-1, 1:-1]**2)) + (CosTheta[1:-1, 1:-1, 1:-1]*(T[2:, 1:-1, 1:-1] - T[:-2, 1:-1, 1:-1])/(2*dy*(R[1:-1, 1:-1, 1:-1]**2)*(SinTheta[1:-1, 1:-1, 1:-1])) ) + (T[1:-1, 2:, 1:-1] - 2*T[1:-1, 1:-1, 1:-1] + T[1:-1, :-2, 1:-1])/(dy2*(R[1:-1, 1:-1, 1:-1]**2) ) + (T[1:-1, 1:-1, 2: ] - T[1:-1, 1:-1, :-2])/(dz*R[1:-1, 1:-1, 1:-1]) + (T[1:-1, 1:-1, 2:] - 2*T[1:-1, 1:-1, 1:-1] + T[1:-1, 1:-1, :-2])/(dz2) )
    #Tf[1:-1, 1:-1, 1:-1] = T[1:-1, 1:-1, 1:-1] + kappa*dt*( (T[2:, 1:-1, 1:-1] - 2*T[1:-1, 1:-1, 1:-1] + T[:-2, 1:-1, 1:-1])/(dx2*(R[1:-1, 1:-1, 1:-1]**2)*(SinTheta[1:-1, 1:-1, 1:-1]**2)) + (CosTheta[1:-1, 1:-1, 1:-1]*(T[2:, 1:-1, 1:-1] - T[:-2, 1:-1, 1:-1])/(2*dy*(R[1:-1, 1:-1, 1:-1]**2)*(SinTheta[1:-1, 1:-1, 1:-1])) ) + (T[1:-1, 2:, 1:-1] - 2*T[1:-1, 1:-1, 1:-1] + T[1:-1, :-2, 1:-1])/(dy2*(R[1:-1, 1:-1, 1:-1]**2) ) + (T[1:-1, 1:-1, 2: ] - T[1:-1, 1:-1, :-2])/(dz*R[1:-1, 1:-1, 1:-1]) + (T[1:-1, 1:-1, 2:] - 2*T[1:-1, 1:-1, 1:-1] + T[1:-1, 1:-1, :-2])/(dz2) )

#=====================================================================
def T_grd2array(nx,ny,grdfile,xyfile_name):

    Two_D_Array=np.zeros([nx,ny])

    tmp_file_name="tmp"+(str(datetime.datetime.now())[18:26])+".xyz"
    cmd="gmt grdtrack %s -G%s > %s" % (xyfile_name,grdfile,tmp_file_name)
    print(cmd)
    os.system(cmd)

    XYZ_FILE=open(tmp_file_name)
    for i in range(nx):
        for j in range(ny):
            line=XYZ_FILE.readline()
            if(line):
                s1,s2,s3=line.split() 
                temperature=float(s3)
                if(temperature < T_min):
                    temperature=T_min
                if(temperature > T_max):
                    temperature=T_max
                Two_D_Array[i,j]=temperature
            else:
                break
    XYZ_FILE.close()

    return Two_D_Array
#=====================================================================
def load_T_from_grd_2_3DArray(grd_file_names):
    global nx,ny,nz,T,Tf,Th,Theta,CosTheta,SinTheta,R,Alpha,DeltaT,Duration, layer_depths

    long_min = float(gmt_dict['west'])
    lat_max = float(gmt_dict['north'])

    xy_file_name="coords_2d.xy"
    XY_FILE=open(xy_file_name,"w")
    print('nx, ny',nx, ny)
    for i in range(nx):
        for j in range(ny):
            theta=(90.0-lat_max)+j*dtheta*r2d
            lat=90-theta
            lon=long_min+i*dphi*r2d
            XY_FILE.write("%f  %f\n" % (lon,lat) )
    XY_FILE.close()
            
    for k, layer_depth in enumerate(layer_depths):
        print(' layer_depth=',layer_depth) 

        grdfile=grd_file_names[k]

        T_2D_tmp=T_grd2array(nx,ny,grdfile,xy_file_name)

        T[:,:,k]=T_2D_tmp[:,:]

    return xy_file_name
#=====================================================================
def generate_arrays(depth_trans_diff,width_trans_diff,convergence_vel):
    global nx,ny,nz,T,Tf,Th,Theta,CosTheta,SinTheta,R,Alpha,DeltaT,Duration, layer_depths

    # Limit the layer depths to only Rhea-2 depths, which would be
    # uneven and limit the diffusion to only the horizontal direction
    print('layer_depths',layer_depths)

    long_min = float(gmt_dict['west'])
    long_max = float(gmt_dict['east'])
    lat_min = float(gmt_dict['south'])
    lat_max = float(gmt_dict['north'])
    nx = int(d2r*(long_max-long_min)/dphi)
    ny = int(d2r*(lat_max-lat_min)/dtheta)
    #nz = int((depth_max/earth_radius)/dr)
    nz=len(layer_depths)

    # Start Tf,Th & T, Theta off as zero matrices:
    T = np.zeros([nx,ny,nz])
    Tf = np.zeros([nx,ny,nz])
    Th = np.zeros([nx,ny,nz])
    Theta=np.zeros([nx,ny,nz])
    CosTheta=np.zeros([nx,ny,nz])
    SinTheta=np.zeros([nx,ny,nz])
    R=np.zeros([nx,ny,nz])
    Alpha=np.zeros([nx,ny,nz])
    DeltaT=np.zeros([nx,ny,nz])
    Duration=np.zeros([nx,ny,nz])

    # Now, set the initial conditions (T) and coordinte arrays.
    for i in range(nx):
        for j in range(ny):
            for k in range(nz):
                #R[i,j,k]=1.0-dr*(nz-k-1)
                R[i,j,k]=earth_radius-layer_depths[k]
                Theta[i,j,k]=d2r*(90.0-lat_max)+j*dtheta
                CosTheta[i,j,k]=math.cos(Theta[i,j,k])
                SinTheta[i,j,k]=math.sin(Theta[i,j,k])
                #d=int(dr*(nz-k-1)*earth_radius)
                d=layer_depths[k]
                Alpha[i,j,k]=0.5*(1.0+math.tanh((d-depth_trans_diff)/width_trans_diff))
                DeltaT[i,j,k]=dt*d/depth_max
  
    #layer_depths=[]
    #for k in range(nz):
    #    d=int(dr*(nz-k-1)*earth_radius)
    #    print 'd:',d
    #    layer_depths.append(d)
    print('layer_depths',layer_depths)

    return
#=====================================================================
def diffuse():
    global nx,ny,nz,T,Tf,Th,Theta,CosTheta,SinTheta,R,Alpha,DeltaT,Duration, layer_depths

    for n in range(1, timesteps+1):
        print("Computing Tf & Th for n =", n)
        Horizontal_Sph_Diffuse()
        #Full_Sph_Diffuse()
        #T=(1.0-Alpha)*Th+Alpha*Tf
        T=Th

    return
#=====================================================================
def TwoD_Array2xyz(array,nx,ny,nz,dx,dy):
    long_min = float(gmt_dict['west'])
    lat_max = float(gmt_dict['north'])
    file_name="file1%s.xyz" % (str(datetime.datetime.now())[18:26])
    FI=open(file_name,"w")
    mid_nz=(int(nz/2))
    #mid_nz=nz-6
    for i in range(nx):
        for j in range(ny):
            theta=(90.0-lat_max)+j*dy*r2d
            lat=90-theta
            lon=long_min+i*dx*r2d
            FI.write("%f  %f  %f\n" % (lon,lat,array[i,j,mid_nz]))
    FI.close()

    return file_name
#=====================================================================
def Plot_two_times(Ta,Tb,nx,ny,nz,proj,region,slab):

    filea=TwoD_Array2xyz(Ta,nx,ny,nz,dx,dy)
    fileb=TwoD_Array2xyz(Tb,nx,ny,nz,dx,dy)

    psfile="temp_two_times.ps"
    tension=0.25
    res=r2d*dx
    grd_a=GMT_Utilities.mk_grd(filea, region, res, tension, T_min, T_max)
    grd_b=GMT_Utilities.mk_grd(fileb, region, res, tension, T_min, T_max)

    cmd="gmt grdimage %s %s -R%s -Ctemp.cpt -B10/10 -P -X1.0 -Y7.0 -K  > %s" % (grd_a,proj,region,psfile)
    print(cmd)
    os.system(cmd)
    cmd="gmt grdimage %s -J -R%s -Ctemp.cpt -B -P -X0.0 -Y-4.0 -O >> %s" % (grd_b,region,psfile)
    print(cmd)
    os.system(cmd)

    make_pdf(psfile,slab)

    return
#=====================================================================
def make_section(id,temp_grd_files,slab,depths,label,T_use,W_use):

    profile="%s%s_profile_%d.xyp" % (profile_dir,slab,id+1)

    prefix=slab+"_temp"
    if W_use == 'Slab1':
        w_model="slab1"
    elif W_use == 'RUM': 
        w_model="rum"

    grid_min = 0.0
    grid_max = 1.0

    section_depth=700.0
    psfile="%s_section_%d.%s.ps" % (slab,id+1,label)

    print('temp_grd_files',temp_grd_files)
    temp_sec_grd, R, dist_max = GMT_Utilities.mk_grd_sec(id, prefix, section_depth, depths, temp_grd_files, profile, grid_min, grid_max)

    print("temp_sec_grd, R, dist_max=",temp_sec_grd, R, dist_max)

    cmd="gmt grdimage %s -Jx0.005/-0.005 -Ctemp.cpt -R%s -B200f50/200f100WeSn -X1.0 -Y3.0 -K -P > %s" % (temp_sec_grd,R,psfile)
    print(cmd)
    os.system(cmd)

    # Plot the plate interface on sections
    #depth_profile="%s%s_%s_depth_profile_%d.xypd" % (profile_dir,slab,w_model,id+1)
    depth_profile="%s%s_new_depth_profile_%d.xypd" % (profile_dir,slab,id+1)
    tmp_profile=positive_depths_limit(depth_profile,100)
    cmd = "gmt psxy %s -R -J -K -O -K -W1,1 >> %s" % (tmp_profile,psfile)
    print(cmd)
    os.system(cmd)
    #label info
    LAB = open('label.txt','w')
    print("0.0 4.10 12 0 1 1 %s     Profile: %d" %  (slab,id+1), file=LAB)
    print("0.0 3.80 12 0 1 1 Thermal: %s     Fault: %s" %  (T_use,W_use), file=LAB)
    LAB.close()

    cmd="gmt pstext label.txt -Jx1 -R0/8.8/0/11 -O >> %s"  % (psfile)
    print(cmd)
    os.system(cmd)



    print('R:',R)

    make_pdf(psfile,slab)

    return
#=====================================================================
#def generate_edge_interior_points(long_min,long_max,lat_min,lat_max,slab_edge):
def generate_edge_interior_points(long_min,long_max,lat_min,lat_max):
    gmt_char = '>'
    edge_points="edge_points.xyz"
    EP=open(edge_points,"w")
    nlong=int((long_max-long_min)/(dtheta*r2d))
    nlat=int((lat_max-lat_min)/(dphi*r2d))
    # edge points 
    for i in range(nlong):
        long=(long_min+i*dphi*r2d)
        EP.write("%f  %f   %f\n" % (long,lat_min+dtheta*r2d,T_max))
        EP.write("%f  %f   %f\n" % (long,lat_max-dtheta*r2d,T_max))
    for j in range(nlat):
        lat=(lat_min+j*dtheta*r2d)
        EP.write("%f  %f   %f\n" % (long_min+dphi*r2d,lat,T_max))
        EP.write("%f  %f   %f\n" % (long_max-dphi*r2d,lat,T_max))
    # interior points
    #for i in range(nlong/5):
    #    for j in range(nlat/5):
    #        long=(long_min+i*5*dphi*r2d)
    #        lat=(lat_min+j*5*dtheta*r2d)
    #        EP.write("%f  %f   %f\n" % (long,lat,T_max))

    #SE=open(slab_edge)
    #while 1:
    #    line=SE.readline()
    #    if(line):
    #        if line[0] != gmt_char: 
    #            newline=line[:-1]+"   1.00\n"
    #            EP.write(newline)
    #    else:
    #        break
    #SE.close()

    EP.close()
    return edge_points
#=====================================================================
def generate_perimeter_points(perimeter,proj,region,res):
    slab_mask_grd="slab_mask.grd"
    #perimeter_xyz_file="perimeter.xyz"
    #PF=open(perimeter_file_name)
    #OPF=open(perimeter_xyz_file,"w")
    #while 1:
    #    line=PF.readline()
    #    if(line):
    #        newline=line[:-1]+"   1.00\n"
    #        OPF.write(newline)
    #    else:
    #        break
    #PF.close()
    #OPF.close()
    cmd="gmt grdmask %s -G%s -I%f -R%s -N%f/NaN/NaN" % (perimeter,slab_mask_grd,res,region,T_max)
    print(cmd)
    os.system(cmd)
    #return perimeter_xyz_file
    return slab_mask_grd
#=====================================================================
def generate_thermal_final_grd_files(sn,region):

    long_min = float(gmt_dict['west'])
    long_max = float(gmt_dict['east'])
    lat_min = float(gmt_dict['south'])
    lat_max = float(gmt_dict['north'])

    directory="GRD_FINAL/"+sn
    cmd="mkdir %s" % (directory)
    print(cmd)
    os.system(cmd)

    xyz_file_names=[]
    grd_file_names=[]
    xyz_file_handles=[]
    #Create an xyz file for each layer depth
    for layer in layer_depths:
        file_layer_xyz_name="final_%03d.xyz" % int(layer)
        xyz_file_names.append(file_layer_xyz_name)
        xyz_file_handles.append( open(file_layer_xyz_name,"w") )
        grd_file_names.append("GRD_FINAL/%s/layer_%03d.grd" % (sn,int(layer)))


    for i in range(nx):
        for j in range(ny):
            for k in range(nz):
                print('nx, ny, nz: ',nx,ny,nz)
                print('len(xyz_file_handles): ',len(xyz_file_handles))
                print('i,j,k: ',i,j,k)
                theta=(90.0-lat_max)+j*dtheta*r2d
                lat=90-theta
                lon=long_min+i*dphi*r2d
                xyz_file_handles[k].write("%f  %f  %f\n" % (lon,lat,T[i,j,k]) )


    tension=0.25
    res=r2d*dx
    #grd_res=0.025
    grd_res=grd_res_global
    #grd_res=1.0
    for k, layer in enumerate(layer_depths):
        xyz_file_name=xyz_file_names[k]

        print('xyz_file_name',xyz_file_name)
        print('region',region)
        grd_file=GMT_Utilities.mk_grd(xyz_file_name, region, grd_res, tension, T_min, T_max)
        print('grd_file',grd_file)

        cmd="mv %s %s" % (grd_file,grd_file_names[k])
        print(cmd)
        os.system(cmd)

        #Make a plot of the temperature with overlays for each depth
        psfile="temp_final_%03d.ps" % int(layer)
        cmd="gmt makecpt -Cpolar -T0.0/1.0/0.1 -D > temp.cpt"
        print(cmd)
        os.system(cmd)
        cmd="gmt grdimage %s %s -Ctemp.cpt -R%s -Ba10f1/a10f1 -P -K > %s" % (grd_file_names[k],proj,region,psfile)
        print(cmd)
        os.system(cmd)

        overlay_plate_boundaries(psfile,0,1)

        make_pdf(psfile,sn)

    return grd_file_names
#=====================================================================
def generate_thermal_ic(sn,slab_Nan_age,T_use,depth_grids_dir,age_grids_dir,model):

    cmd="mkdir GRD_IC/"+sn
    print(cmd)
    os.system(cmd)

    #grd_depth="%s%s_%s_clip.grd" % (depth_grids_dir,sn,model)
    #grd_depth="%s%s_%s_new_depth.grd" % (depth_grids_dir,sn,model)
    #grd_dip="%s%s_%s_dipclip.grd" % (depth_grids_dir,sn,model)
    #grd_str="%s%s_%s_strclip.grd" % (depth_grids_dir,sn,model)
    grd_depth="%s%s_slab2_dep_%s.grd" % (Slab2_grids_dir,s,date)
    grd_dip="%s%s_slab2_dip_%s.grd" % (Slab2_grids_dir,s,date)
    grd_str="%s%s_slab2_str_%s.grd" % (Slab2_grids_dir,s,date)
  
    grd_age="%s%s_age.grd" % (age_grids_dir,sn)
    print('grd_age',grd_age)

    if T_use == 'RUM':
        perimeter="%s%s_rum.clip.xy" % (RUM_XY_dir,sn)
    if T_use == 'Slab1':
        perimeter="%s%s_slab1.0.clip.xy" % (Slab1_XY_dir,sn)
    if T_use == 'Slab2':
        perimeter="%s%s_slab2_clip.xy" % (Slab2_XY_dir,sn)
    #slab_edge="%s%s_rum.edges.xy" % (RUM_Slab_Edge_dir,sn)

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

    #set lower res of grd for the thermal ic
    #res=1.25*float(gmt_dict['dx'])
    res=grd_res_global

    edge_points=generate_edge_interior_points(long_min,long_max,lat_min,lat_max)

 
    slab_mask_grd=generate_perimeter_points(perimeter,proj,region,res)

    xyz_N_file_names=[]
    xyz_N_file_handles=[]
    xyz_H_file_names=[]
    xyz_H_file_handles=[]
    grd_file_names=[]
    #Create an xyz file for each layer depth
    for layer in layer_depths:
        print(' layer=',layer) 
        # N=normal (that is normal to slab surface) and H=horizontal
        file_layer_N_xyz_name="layer_N_%03d.xyz" % int(layer)
        xyz_N_file_names.append(file_layer_N_xyz_name)
        xyz_N_file_handles.append( open(file_layer_N_xyz_name,"w") )
        file_layer_H_xyz_name="layer_H_%03d.xyz" % int(layer)
        xyz_H_file_names.append(file_layer_H_xyz_name)
        xyz_H_file_handles.append( open(file_layer_H_xyz_name,"w") )
        grd_file_names.append("GRD_IC/%s/layer_%03d.grd" % (sn,int(layer)))


    if not check_for_existence_grd_ic_files(grd_file_names): 
        print('Generating ic grd files')

        generate_points_around_slab(sn,slab_Nan_age,grd_age,grd_depth,grd_dip,grd_str,gmt_dict,layer_depths,xyz_N_file_handles,xyz_H_file_handles)

        for i, layer in enumerate(layer_depths):
            xyz_N_file_handles[i].close()
            xyz_H_file_handles[i].close()
            print('i,layer:',i,layer)


        #xyz_file_name=xyz_N_file_names[24]
        #xyz_file_name=xyz_N_file_names[13]
        xyz_file_name=xyz_N_file_names[3]
        #cmd="gmt psxy %s %s -Sc0.001 -Gblack -R%s -B10/10 -P -K > out_points.ps" % (xyz_file_name,proj,region)
        #print cmd
        #os.system(cmd)
        cmd="gmt psxy out_points.xy %s -Sc -Gred -R%s -B10/10 -P -K > out_points.ps" % (proj,region)
        print(cmd)
        os.system(cmd)
        overlay_plate_boundaries("out_points.ps",0,1)
        make_pdf("out_points.ps",sn)

        #test the points
        tension=0.25
        for i, layer in enumerate(layer_depths):
            #First Create the GRD file for the slab Temperature
            #Based on normals to the slab surface
            xyz_file_name=xyz_N_file_names[i]
            cmd="cat %s %s > tmp.xyz" % (edge_points,xyz_file_name)
            print(cmd)
            os.system(cmd)
            #if(layer <= 75):
            #    cmd="cat tmp.xyz %s > slab_with_edge_data.xyz" % (perimeter_xyz_file)
            #    print cmd
            #    os.system(cmd)
            #else:
            cmd="mv tmp.xyz slab_with_edge_data.xyz"
            print(cmd)
            os.system(cmd)
                #cmd="mv tmp.xyz slab_with_edge_data.xyz"
                #print cmd
                #os.system(cmd)

            cmd="gmt blockmedian slab_with_edge_data.xyz -I%f -R%s > median.xyz" % (res,region)
            print(cmd)
            os.system(cmd)
            cmd="gmt surface median.xyz -Gtemp_N.grd -I%f -R%s -T%f -Ll%f -Lu%f" % (res,region,tension,T_min,T_max)
            print(cmd)
            os.system(cmd)

            #Second Create the GRD file for the slab Temperature
            #Based on horizontals to the slab surface
            xyz_file_name=xyz_H_file_names[i]
            cmd="cat %s %s > tmp.xyz" % (edge_points,xyz_file_name)
            print(cmd)
            os.system(cmd)
            #if(layer <= 75):
            #    cmd="cat tmp.xyz %s > slab_with_edge_data.xyz" % (perimeter_xyz_file)
            #    print cmd
            #    os.system(cmd)
            #else:
            #    cmd="mv tmp.xyz slab_with_edge_data.xyz"
            #    print cmd
            #    os.system(cmd)

            cmd="gmt blockmedian tmp.xyz -I%f -R%s > median.xyz" % (res,region)
            print(cmd)
            os.system(cmd)
            cmd="gmt surface median.xyz -Gtemp_H.grd -I%f -R%s -T%f -Ll%f -Lu%f" % (res,region,tension,T_min,T_max)
            print(cmd)
            os.system(cmd)

            w_h=0.5*(1.0+math.tanh((layer-300.00)/50.0))
            #w_h=1.0
            #w_h=0.0
            w_n=1.0-w_h
            print('layer, wn, wh: ',layer,w_n,w_h)
            cmd="gmt grdmath %f temp_N.grd MUL = wN.grd" % w_n
            print(cmd)
            os.system(cmd)
            cmd="gmt grdmath %f temp_H.grd MUL = wH.grd" % w_h
            print(cmd)
            os.system(cmd)
            cmd="gmt grdmath wN.grd wH.grd ADD = tmp.grd"
            print(cmd)
            os.system(cmd)
            cmd="gmt grdmath %s tmp.grd AND = %s" % (slab_mask_grd,grd_file_names[i])
            print(cmd)
            os.system(cmd)

            #Make a plot of the temperature with overlays for each depth
            psfile="temp_%03d.ps" % int(layer)
            cmd="gmt makecpt -Cpolar -T%f/%f/0.1 -D > temp.cpt" % (T_min,T_max)
            print(cmd)
            os.system(cmd)
            cmd="gmt grdimage %s %s -Ctemp.cpt -R%s -Ba10f1/a10f1 -P -K > %s" % (grd_file_names[i],proj,region,psfile)
            print(cmd)
            os.system(cmd)

            ii=1  
            while ii<=2:
                profile="%s%s_profile_%d.xyp" % (profile_dir,sn,ii)
                cmd="gmt psxy %s %s -W1,black -R%s -B -K -O >> %s" % (profile,proj,region,psfile)
                print(cmd)
                os.system(cmd)
                ii += 1

            overlay_plate_boundaries(psfile,0,1)

            print('layer', layer)
            make_pdf(psfile,sn)
        
    return grd_file_names, proj, region
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


    #Ridges
    if (RIDGES):
        cmd="gmt psxy %s -J -R -B -W4/255/0/0 -V -M -P -O -K >> %s" % (ridges,psfile)
        #print cmd 
        #os.system(cmd)
        cmd="gmt psxy %s -J -R -B -W2/255/255/255 -V -M -P -O -K >> %s" % (ridges,psfile)
        #print cmd
        #os.system(cmd)

    #Fractures
    cmd="gmt psxy %s -J -R -B -W6/128/128/128 -V -M -P -O -K >> %s" % (fractures,psfile)
    #print cmd
    #os.system(cmd)
    #Interface between Trenches and Fractures (mostly)
    cmd="gmt psxy %s -J -R -B -W6/0/255/0 -Sf0.2i/0.07i+l+t -G0/255/0 -V -M -P -O -K >> %s" % (interface,psfile)
    #print cmd
    #os.system(cmd)

    #Position of the trench
    teeth="0.2i/0.07i+l+t"
    teeth="0.1i/0.035i+l+t"
    if (CLOSEGMT):
        cmd="gmt psxy %s -J -R -B -W1,black -Sf%s -Gblack -P -O >> %s" % (trenches,teeth,psfile)
    else:
        cmd="gmt psxy %s -J -R -B -W1,black -Sf%s -Gblack -P -O -K >> %s" % (trenches,teeth,psfile)
    print(cmd) 
    os.system(cmd)

    return
#=====================================================================
def shift_profile(profile,shift_dir,xs,zs):
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
def make_slab_age_grd(s,gmt_dict,XY_dir,age_grid,grd_depth,grd_str,trench_age_dist,Nan_age):

    
    slab_NAN_age=Nan_age

    trench="%s%s_trench_0.xy" % (XY_dir,s)
    print('trench',trench)
    trench_age_sampled="trench_age.xya"
    slab_str_sampled="slab_str.xys"
    ofile="slab_ages.xya"

    spacing='NONE'
    xyz_file=GMT_Utilities.xy2xyz(trench,0.0,spacing,0.0)
    #print 'xyz_file ',xyz_file
    #sample age grid just outside of the trench
    dist=-1.0*trench_age_dist
    outside=Mat_Utilities.mk_parallel_line(xyz_file,0,dist)
    GMT_Utilities.remove_gmt_char(outside,"shifted_ages.xyz","xyz")
    cmd="gmt grdtrack shifted_ages.xyz -G%s > %s" % (age_grid,trench_age_sampled)
    print(cmd)
    os.system(cmd)
    #sample str (strike of slab) grid just inside of the trench
    dist=0.25
    inside=Mat_Utilities.mk_parallel_line(xyz_file,0,dist)
    #print 'inside ',inside
    GMT_Utilities.remove_gmt_char(inside,"shifted_str.xyz","xyz")
    cmd="gmt grdtrack shifted_str.xyz -G%s > %s" % (grd_str,slab_str_sampled)
    print(cmd)
    os.system(cmd)

    #print 'trench_age_sampled',trench_age_sampled
    #print 'slab_str_sampled',slab_str_sampled
    #print 'grd_str',grd_str
    #print 'age_grd ',age_grid
    AT=open(trench_age_sampled)
    SS=open(slab_str_sampled)
    SA=open(ofile,"w")
    while 1:
        line1=AT.readline()
        line2=SS.readline()
        if(line1):
            s1,s2,s3,s4=line1.split()
            flon=float(s1)
            flat=float(s2)
            fage=float(s4)
            if fage >= slab_NAN_age:
                fage=slab_NAN_age
            s1,s2,s3,s4=line2.split()
            flon=float(s1)
            flat=float(s2)
            fazim=float(s4)+90.0
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
                else:
                    break
            TP.close()
        else:
            break
    AT.close()
    SS.close()
    SA.close()
 
    tension=0.25
    age_min=0.1
    age_max=200.0
    tmp_grd=GMT_Utilities.mk_grd(ofile, gmt_dict['R'], gmt_dict['dx'], tension, age_min, age_max) 
    slab_age_grd="slab_age.grd"
    cmd="gmt grdmath %s %s OR = %s" % (tmp_grd,grd_depth,slab_age_grd)
    print(cmd)
    os.system(cmd)

    return slab_age_grd, trench_age_sampled
#=====================================================================
def displace_from_slab_surface(AboveBelow,x,y,s_depth,s_dip,s_str,d_depth):
 
    #colatitude
    theta=90.0-y
    #distance is the distance normal to slab in map view
    distance=d_depth*math.tan( d2r*(90.-s_dip) )
    #distance=d_depth*math.tan( d2r*(s_dip) )
    ss=s_str-90.0
    if AboveBelow == 'B': #below the slab surface
        dx1=distance*math.sin(d2r*ss)
        dy1=distance*math.cos(d2r*ss)
        dlon=dx1*180.0/(math.sin(d2r*theta)*math.pi*earth_radius)
        dlat=dy1*180.0/(math.pi*earth_radius)
        new_x=x-dlon
        new_y=y-dlat
    if AboveBelow == 'A': #Above the slab surface
        dx1=distance*math.sin(d2r*ss)
        dy1=distance*math.cos(d2r*ss)
        dlon=dx1*180.0/(math.sin(d2r*theta)*math.pi*earth_radius)
        dlat=dy1*180.0/(math.pi*earth_radius)
        new_x=x+dlon
        new_y=y+dlat

    actual_distance=math.sqrt(d_depth*d_depth + distance*distance)
    return new_x,new_y,actual_distance
#=====================================================================
def new_point_const_depth(AboveBelow,x,y,s_str,distance):
 
    #colatitude
    theta=90.0-y
    ss=s_str-90.0
    if AboveBelow == 'B': #below the slab surface
        dx1=distance*math.sin(d2r*ss)
        dy1=distance*math.cos(d2r*ss)
        dlon=dx1*180.0/(math.sin(d2r*theta)*math.pi*earth_radius)
        dlat=dy1*180.0/(math.pi*earth_radius)
        new_x=x-dlon
        new_y=y-dlat
    if AboveBelow == 'A': #below the slab surface
        dx1=distance*math.sin(d2r*ss)
        dy1=distance*math.cos(d2r*ss)
        dlon=dx1*180.0/(math.sin(d2r*theta)*math.pi*earth_radius)
        dlat=dy1*180.0/(math.pi*earth_radius)
        new_x=x+dlon
        new_y=y+dlat

    return new_x,new_y
#=====================================================================
def out_point(x,y,file_handle,size):
    file_handle.write("%f  %f  %f\n" % (x,y,size))
    return
#=====================================================================
def generate_points_around_slab(sn,slab_Nan_age,grd_age,grd_depth,grd_dip,grd_str,gmt_dict,layer_depths,xyz_N_file_handles,xyz_H_file_handles):

    xyz_depth="depth.xyz"
    xyz_dip="dip.xyz"
    xyz_str="str.xyz"
    xyz_slab_age="slab_age.xyz"

    cmd="gmt grd2xyz %s -s > %s" % (grd_depth,xyz_depth)
    print(cmd)
    os.system(cmd)
    cmd="gmt grd2xyz %s -s > %s" % (grd_dip,xyz_dip)
    print(cmd)
    os.system(cmd)
    cmd="gmt grd2xyz %s -s > %s" % (grd_str,xyz_str)
    print(cmd)
    os.system(cmd)
    cmd="gmt grd2xyz %s -s > %s" % (grd_age,xyz_slab_age)
    print(cmd)
    os.system(cmd)

    I_DEPTH=open(xyz_depth)
    I_DIP=open(xyz_dip)
    I_STR=open(xyz_str)
    I_AGE=open(xyz_slab_age)

    out_point_file_handle=open("out_points.xy","w")

    #depth_range=1.25*resolution_in_km
    depth_range=0.5*resolution_in_km
    iii=0
    while 1:
        iii+=1
        depth_line=I_DEPTH.readline()
        dip_line=I_DIP.readline()
        str_line=I_STR.readline()
        age_line=I_AGE.readline()
        if(depth_line and dip_line and str_line and age_line):
            x1,y1,depth=depth_line.split()
            x2,y2,dip=dip_line.split()
            x3,y3,str=str_line.split()
            x4,y4,s4=age_line.split()
            x=float(x1)
            y=float(y1)
            if iii==10000 or iii==20000 or iii==30000 or iii==40000 or iii == 15000 or iii==50000 or iii==100000:
                out_point(x,y,out_point_file_handle,0.1)
            s_depth=-float(depth)
            if(T_use=="Slab2"):
                s_dip=-float(dip)
            else:
                s_dip=float(dip)
            s_str=float(str)
            s_age=float(s4)
            horizontal_pts=int(200.0/resolution_in_km)
            for i, layer in enumerate(layer_depths):
                #Descend into the layers below this point
                if(float(layer) > s_depth):
                    d_depth=layer-s_depth
                    if d_depth < 200:
                        xnew,ynew,actual_dist=displace_from_slab_surface('B',x,y,s_depth,s_dip,s_str,d_depth)
                        if actual_dist < 200:
                            non_dim_dist=actual_dist/layer_km
                            #a=100.0
                            #a=slab_Nan_age
                            a=s_age
                            etemp = Thermal_Utilities.expected_temp(non_dim_dist,a,scalet)
                            xyz_N_file_handles[i].write("%f  %f  %f\n" % (xnew,ynew,etemp))
                #Ascend into the layers above this point
                if(float(layer) <= s_depth):
                    d_depth=s_depth-layer
                    xnew,ynew,actual_dist=displace_from_slab_surface('A',x,y,s_depth,s_dip,s_str,d_depth)
                    if actual_dist < 200:
                        etemp = T_max
                        xyz_N_file_handles[i].write("%f  %f  %f\n" % (xnew,ynew,etemp))
                #Find the layers nearest this point
                if(s_depth > (float(layer)-depth_range) and s_depth < (float(layer)+depth_range) ):
                    # Project 'below' for these points
                    actual_dist=0.0
                    for kk in range(horizontal_pts):
                        actual_dist=actual_dist+resolution_in_km
                        xnew,ynew=new_point_const_depth('B',x,y,s_str,-actual_dist)
                        if iii==10000 or iii==20000 or iii==30000 or iii==40000 or iii == 15000 or iii==50000 or iii==100000:
                            out_point(xnew,ynew,out_point_file_handle,0.05)
                        non_dim_dist=actual_dist/layer_km
                        #a=100.0
                        #a=slab_Nan_age
                        a=s_age
                        etemp = Thermal_Utilities.expected_temp(non_dim_dist,a,scalet)
                        xyz_H_file_handles[i].write("%f  %f  %f\n" % (xnew,ynew,etemp))
                    # Project 'above' for these points
                    actual_dist=0.0
                    for kk in range(horizontal_pts):
                        actual_dist=actual_dist+resolution_in_km
                        xnew,ynew=new_point_const_depth('A',x,y,s_str,-actual_dist)
                        etemp = T_max
                        xyz_H_file_handles[i].write("%f  %f  %f\n" % (xnew,ynew,etemp))
        else:
            break
    I_DEPTH.close()
    I_DIP.close()
    I_STR.close()

    out_point_file_handle.close()

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
#from Slab_Dictionary_Slab1_RUM import slab_dict
gmt_dict = {}

#if len(sys.argv) != 2:
#    usage()
#
#mode=sys.argv[1]


# Get the top level keys and sort them
slab_keys = list(slab_dict.keys());
slab_keys.sort()


cmd="gmt gmtset PS_MEDIA letter PROJ_LENGTH_UNIT inch"
os.system(cmd)

cmd="mkdir GRD_IC"
os.system(cmd)
cmd="mkdir GRD_FINAL"
os.system(cmd)
cmd="mkdir PDF"
os.system(cmd)

for s in slab_keys:
    print(" ")
    print("SLAB: %s" % s)
    print(" ")
    # Get a local copy of the sub dictionary
    sub_dict = slab_dict[s]
    # Get the sub level keys and sort them
    sub_keys = list(sub_dict.keys())
    sub_keys.sort()

    # Previously called 'off' in Slab 1 dictionary, now called off_age
    trench_age_dist=sub_dict['off_age']
    Nan_age=sub_dict['Nan_age']
    RUM=sub_dict['RUM']
    T_use=sub_dict['T_use']
    W_use=sub_dict['W_use']
    print('T_use, W_use',T_use, W_use)
    slab_Nan_age=sub_dict['Nan_age']
    date=sub_dict['date']

    if T_use == 'Slab2':
        sn=s
        depth_grids_dir=Slab2_grids_dir
        age_grids_dir=Slab2_Age_Dir
        model="slab2.0"
    elif T_use == 'RUM': 
        if RUM == 'only':
            sn=s
        else:
            sn=RUM
        depth_grids_dir=RUM_grids_dir
        age_grids_dir=RUM_Age_Dir
        model="rum"
    #print('sn',sn)

    # All Arrays will need to be remade for each slab
    
    #grd_depth="%s%s_%s_clip.grd" % (depth_grids_dir,sn,model)
    #grd_depth="%s%s_%s_new_depth.grd" % (depth_grids_dir,sn,model)
    grd_depth="%s%s_slab2_dep_%s.grd" % (Slab2_grids_dir,sn,date)
    gmt_dict['grid']=grd_depth
    Core_GMT.grdinfo( gmt_dict )

#=====================================================================
    depth_trans_diff=100.00
    width_trans_diff=50.0
    #convergence_vel=1.0 # cm/yr
    #convergence_vel=2.5 # cm/yr
    convergence_vel=5.0 # cm/yr

    # read layers for Rhea run
    #layer_depths=get_layer_depths()
    #In rhea2 these values are now floats, before they were ints
    layer_depths=get_layer_depths_rhea2()

    # Uniform layers using diffusion model
    generate_arrays(depth_trans_diff,width_trans_diff,convergence_vel)

       

    ic_grd_file_names, proj, region = generate_thermal_ic(sn,slab_Nan_age,T_use,depth_grids_dir,age_grids_dir,model)
 
    print('ic_grd_file_names',ic_grd_file_names)

    xy_file_name = load_T_from_grd_2_3DArray(ic_grd_file_names)

    update_array_for_variable_descent(sn,xy_file_name,proj,region)
    

    make_section(0,ic_grd_file_names,sn,layer_depths,"IC",T_use,W_use)
    make_section(1,ic_grd_file_names,sn,layer_depths,"IC",T_use,W_use)

    #Temporary fix  for setting bound. values on Tf & Th by setting to 1
    Tf[:,:,:]=1.0
    Th[:,:,:]=1.0
    #Ta=T

    #diffuse()
    #final_grd_file_names = generate_thermal_final_grd_files(sn,region)
   
    final_grd_file_names=diffuse_with_filter(sn,layer_depths,ic_grd_file_names,convergence_vel)

    #Tb=T

    #Plot_two_times(Ta,Tb,nx,ny,nz,proj,region,sn)


    label="Full.FINAL_var_convergence"
    #label="Full.FINAL_%2.2fcm_per_yr" % (convergence_vel)
    #label="Full.FINAL"
    make_section(0,final_grd_file_names,sn,layer_depths,label,T_use,W_use)
    make_section(1,final_grd_file_names,sn,layer_depths,label,T_use,W_use)

clean_up_and_finish()

# EOF

