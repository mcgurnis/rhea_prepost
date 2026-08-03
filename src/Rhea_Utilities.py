#!/usr/bin/env python
#=====================================================================
#
#               Python Scripts for data assimulation
#                  ---------------------------------
#
#                              Authors:
#                            Michael Gurnis
#          (c) California Institute of Technology 2009-2026
#
#               Free for non-commercial academic use ONLY.
#      This program is distributed WITHOUT ANY WARRANTY whatsoever.
#



import sys, string, os
import numpy as np
import Mat_Utilities, GMT_Utilities
from math import *

#Some gmt parameters needed in various functions
#region="-180/180/-90/90"
#region="0/360/-60/60"
region="0/360/-90/90" ##
proj="-JH180.0/6.0" ##
#proj="-JM6.0"
grd_res=1.0
#stencil_grd_res=0.05
#stencil_grd_res=1.0 #for plotting plate model comparisons

#=====================================================================

#=====================================================================

r2d = 180.0/pi
d2r=1.0/r2d
earth_radius = 6371.0
earth_radius_meters = 6371000.
therm_diff=1e-06
layer_km=earth_radius
#==================================================================
#Plate_model_dir="/home/datalib/Plate_Kinematic_Models/NUVEL/"
#Plate_model_dir="/net/holmes/home4/gurnis/Rhea_runs/Plate_Kinematic_Models/"
# For plateness
#Plate_model_dir="/net/beno/raid2/alisic/Rhea_input/Plate_Kinematic_Models/"
# For plotting plate models
#Plate_model_dir="/net/beno/data1/alisic/raid2/Rhea_input/Plate_Kinematic_Models/plot_data/"
Plate_model_dir="/net/holmes/home4/gurnis/Rhea_runs/Plate_Kinematic_Models/"

#==================================================================
#Mapping between my 3 letter codes and the 4 letter Nuvel codes
# Removed IND since part of AUS

# For nnr_nuvel1, hs2_nuvel1:
#Code={"AFR":"AFRC", "ANT":"ANTA", "ARB":"ARAB", "AUS":"AUST", "CAR":"CARB", "COC":"COCO", "EUR":"EURA", "NAZ":"NAZC", "NAM":"NOAM", "PAC":"PCFC", "SAM":"SOAM", "JDF":"JUFU", "PSP":"PHIL", "IND":"INDI" }

# For nnr_nuvel1a:
#Code={"AFR":"AFRC", "ANT":"ANTA", "ARB":"ARAB", "AUS":"AUST", "CAR":"CARB", "COC":"COCO", "EUR":"EURA", "NAZ":"NAZC", "NAM":"NOAM", "PAC":"PCFC", "SAM":"SOAM", "JDF":"JUFU", "PSP":"PHIL", "IND":"INDI", "SCO":"SCOT", "RIV":"RIVR" }

# For nnr_nuvel1_micro:
#Code={"AFR":"AFRC", "ANT":"ANTA", "ARB":"ARAB", "AUS":"AUST", "CAR":"CARB", "COC":"COCO", "EUR":"EURA", "NAZ":"NAZC", "NAM":"NOAM", "PAC":"PCFC", "SAM":"SOAM", "JDF":"JUFU", "PSP":"PHIL", "IND":"INDI", "NHB":"NHEB", "TON":"TONG", "KER":"KERM", "SAN":"SAND", "SCO":"SCOT", "MAR":"MARI" }

# For nnr_nuvel1a_micro:
#Code={"AFR":"AFRC", "ANT":"ANTA", "ARB":"ARAB", "AUS":"AUST", "CAR":"CARB", "COC":"COCO", "EUR":"EURA", "NAZ":"NAZC", "NAM":"NOAM", "PAC":"PCFC", "SAM":"SOAM", "JDF":"JUFU", "PSP":"PHIL", "IND":"INDI", "NHB":"NHEB", "TON":"TONG", "KER":"KERM", "SAN":"SAND", "SCO":"SCOT", "MAR":"MARI", "RIV":"RIVR" }

# For hs3_nuvel1a:
#Code={"AFR":"AFRC", "ANT":"ANTA", "ARB":"ARAB", "AUS":"AUST", "CAR":"CARB", "COC":"COCO", "EUR":"EURA", "NAZ":"NAZC", "NAM":"NOAM", "PAC":"PCFC", "SAM":"SOAM", "JDF":"JUFU", "PSP":"PHIL", "IND":"INDI", "SCO":"SCOT" }

#NNR_MORVEL56 maps onto itself
Code={"pa":"pa","am":"am","an":"an","ar":"ar","au":"au","ca":"ca","co":"co","cp":"cp","eu":"eu","in":"in","jf":"jf","lw":"lw","na":"na","nb":"nb","mq":"mq","nz":"nz","ps":"ps","ri":"ri","sa":"sa","sc":"sc","sm":"sm","sr":"sr","su":"su","sw":"sw","yz":"yz","SL":"SL","BH":"BH","MO":"MO","SS":"SS","WL":"WL","CR":"CR","FT":"FT","KE":"KE","NI":"NI","TO":"TO","PM":"PM","AS":"AS","AT":"AT","GP":"GP","EA":"EA","JZ":"JZ","OK":"OK","NB":"NB","SB":"SB","MN":"MN","NH":"NH","BR":"BR","CL":"CL","MA":"MA","ND":"ND","AP":"AP","BU":"BU","MS":"MS","BS":"BS","TI":"TI","ON":"ON", "n1":"na"}

#=====================================================================



#=====================================================================
#    Open a rhea mesh for a single radius and write out a GMT.xy
#    file
#=====================================================================
def rheamesh2GMT(mesh_file_name):
    mesh = open(mesh_file_name,'r')
    name='nodes.xy'
    nodes = open(name,'w')
    #RHEAMESH=0  #For Rhea_mesh files created before Aug. 09
    #RHEAMESH=1  #For Rhea_mesh files created after Aug. 09
    RHEAMESH=2  #For Rhea2 mesh files created from Aug. '13

    while 1:
        line=mesh.readline()
        if(line):
            if(RHEAMESH==0):
                n, s_radius, phi, theta, visc =line.split() # 'theta' is colatitude
            if(RHEAMESH==1):
                n, s_radius, theta, phi, visc =line.split() # 'theta' is colatitude
            if(RHEAMESH==2):
                #n, s_radius, theta, phi =line.split() # 'theta' is colatitude
                n, s_radius, phi, theta =line.split() # 'theta' is colatitude
            #print line
            #print 'n',n
            #depth=1.0-float(s_radius)
            nint=int(float(n))
            #print 'nint',nint
            lon=180.0+float(phi)*r2d
            lat=90.0-float(theta)*r2d
            nodes.write("%f %f %d\n" % (lon,lat,nint) )
        else:
            break
    mesh.close()
    nodes.close()
    return name
#=====================================================================
# Depths at which rhea mesh occurs
#=====================================================================
def get_new_depths_for_rhea(level,depth_max):
    print('just before call to Rhea radii')
    radii = Rhea_radii(0.55,1.0,level)

    # GMT Contour file
    radii.reverse()
    contour_file = 'rhea_radii'
    cfile=open(contour_file,"w")
    for r in radii:
        #print 'r',r
        depth = int( round((1.0-r)*earth_radius) )
        if depth<depth_max:
            cfile.write("%f  C\n" % depth)
    cfile.close()

    # A List containing the radii and the dimensional depths (as integers)
    radii.reverse()
    radii_depths = []
    for r in radii:
        #print 'r',r
        depth = int( round((1.0-r)*earth_radius) )
        if depth<depth_max:
            radii_depths.append("%f  %d" % (r,depth) )
            #print radii_depths

    return contour_file, radii_depths
#=====================================================================
# Rhea Radial Mesh
#=====================================================================
def Rhea_radii(rin,rout,L):
    # L is the Rhea Level
    n=2**L + 1
    z=linspace(1,2,n) # Uniform spacing on reference
    r=[]
    for i in range(n):
       r.append( (rin**2/rout) * (rout/rin)**z[i] ) #Rhea radius
    return r
#=====================================================================
#    A Python compatible version of the MatLab function linspace
#=====================================================================
def linspace(xmin, xmax, N):
    if N==1: return xmax
    dx = (xmax-xmin)/float(N-1)
    x=[]
    for i in range(N):
        x.append(xmin + dx*float(i))
    return x
#=====================================================================
#
def velocity_scale():
    v=1.0 # In cm/yr
    eta0=1.0e+20
    # Pe = vR/kappa
    R=6.371e06
    kappa=1.0e-06
    sec_yr=3.1536e07
    Pe=(v*(0.01)/sec_yr)*R/kappa
    vscale=Pe

    edot_scale = kappa/(R**2)

    drho=2300.0 # water loaded topo
    g0=10.0
    topo_scale = eta0*edot_scale/(drho*g0)

    return vscale, edot_scale, topo_scale
#====================================================================
#
def gmt_vector(VL):
    #VL should be north, east, down
    vn=VL[0]
    ve=VL[1]
    azimuth=r2d*atan(ve/vn)
    if vn < 0.0 and ve >= 0.0:
        azimuth=180.0+azimuth
    if vn < 0.0 and ve < 0.0:
        azimuth=azimuth-180.0
    length = hypot(ve,vn)
    return azimuth, length
#====================================================================
#
def get_vectors_from_grd(ve_grd,vn_grd,scaling,sphere_pts,name,file_mode):

    if file_mode == 'print':
        velocity_vectors='%s_vel.xyV' % name
    if file_mode == 'process':
        velocity_vectors='%s_vel.V' % name

    VEL=open(velocity_vectors,"w")

    VL=np.zeros(3,dtype="float")
    cmd = "gmt grdtrack %s -G%s > vn.xyv" % (sphere_pts,vn_grd)
    print(cmd)
    os.system(cmd)
    cmd = "gmt grdtrack %s -G%s > ve.xyv" % (sphere_pts,ve_grd)
    print(cmd)
    os.system(cmd)
    NF=open("vn.xyv")
    EF=open("ve.xyv")
    while 1:
        line_n= NF.readline()
        line_e= EF.readline()
        if(line_n):
            n1,n2,n3 = line_n.split()
            if n3 != 'NaN':
                e1,e2,e3 = line_e.split()
                lon=float(n1)
                lat=float(n2)
                vn = float(n3)
                ve = float(e3)
                VL[0]=vn/scaling
                VL[1]=ve/scaling
                if file_mode == 'print':
                    azimuth, length = gmt_vector(VL)
                    #length=length/scaling
                    VEL.write("%f  %f  %f  %f\n" % (lon, lat,azimuth,length) )
                elif file_mode == 'process':
                    VEL.write("%g  %g  %g  %g\n" % (lon, lat,VL[0],VL[1]) )



        else:
            break

    NF.close()
    EF.close()

    return velocity_vectors
#====================================================================
#
def load_plate_model_into_dic(plate_model_file):

    PlateModel={}
    PlateModel_Index={}

    PM=open(plate_model_file)
    line=PM.readline()
    d9=1
    while 1:
        line=PM.readline()
        print(line)
        if(line):
            s1,s2,s3,s4,s5,s6,s7,s8=line.split()
            entry_for_s1="%s#%s#%s#%s#%s#%s#%s#%d" % (s2,s3,s4,s5,s6,s7,s8,d9)
            PlateModel[s1]=entry_for_s1
            d9+=1
        else:
            break

    PM.close()

    for nuvel_id in PlateModel:
        s2,s3,s4,s5,s6,s7,s8,s9=PlateModel[nuvel_id].split("#")
        num_code=int(s9)
        PlateModel_Index[num_code]=nuvel_id

    return PlateModel, PlateModel_Index
#====================================================================
#
def get_pole_from_nuvel(nuvel_id,PlateModel):
    s2,s3,s4,s5,s6,s7,s8,s9=PlateModel[nuvel_id].split("#")
    lat_pole_id=float(s2)
    lon_pole_id=float(s3)
    omega_id   =float(s4)
    num_code = float(s9)

    return lat_pole_id, lon_pole_id, omega_id, num_code

#====================================================================
#
def velocity_from_pole(omega,euler_lat,euler_lon,lat_d,lon_d):
    #VL should be north, east, down
    VL=np.zeros(3,dtype='float')

    lat_e = d2r*euler_lat
    lon_e = d2r*euler_lon
    lat = d2r*lat_d
    lon = d2r*lon_d

    VL[0] = omega*cos(lat_e)*sin(lon-lon_e)
    VL[1] = omega*(sin(lat_e)*cos(lat) - cos(lat_e)*sin(lat)*cos(lon-lon_e))
    VL[2] = 0.0
    return VL
#====================================================================
#
def local_velocity_from_pole(lat_pt,lon_pt,lat_pole,lon_pole,omega):

    vn=cos(d2r*lat_pole)*sin(d2r*(lon_pt-lon_pole))
    ve=sin(d2r*lat_pole)*cos(d2r*lat_pt) - cos(d2r*lat_pole)*sin(d2r*lat_pt)*cos(d2r*(lon_pt-lon_pole))
    vn=omega*vn
    ve=omega*ve
    return vn,ve

#====================================================================
#
def get_velocity_vectors_for_plate_model(process_mode,plate_model,scale_factor,sphere_pts,PlateModel,PlateModel_Index,plates_grd,file_mode):
    #

    # process_mode
    # if 'D' sphere_pts is list of lon, lat, distance
    # if 'S' sphere_pts is list of lon, lat
    VL=np.zeros(3,dtype="float")

    cmd = "gmt grdtrack %s -G%s > pts.xyid" % (sphere_pts,plates_grd)
    os.system(cmd)

    SPPF=open("pts.xyid")

    if file_mode == 'print':
        actual_velocity_vectors="%s.xyV" % plate_model
    elif file_mode == 'process':
        actual_velocity_vectors="%s.V" % plate_model

    AVVF=open(actual_velocity_vectors,"w")

    while 1:
        line=SPPF.readline()
        if(line):
            if process_mode == 'S':
                n1,n2,n3 = line.split()
            if process_mode == 'D':
                n1,n2,sD, n3 = line.split()
            lon_pt=float(n1)
            lat_pt=float(n2)
            if n3 != 'NaN':
                num_code=int(float(n3))
                print('n3 num_code',n3,num_code)
            else:
                num_code = 0

            #is this a legit plate?
            isplate = 0
            if math.fabs(float(n3)-num_code) < 0.00001:
                isplate=1

            if n3 == 'NaN' or num_code <= 0:
                num_code=0
                VL[0]=0.0
                VL[1]=0.0
            elif isplate :
                print('num_code:', num_code, ', PlateModel_Index:', PlateModel_Index[num_code])
                nuvel_id=PlateModel_Index[num_code]
                print('nuvel_id=',nuvel_id)
                lat_pole_id, lon_pole_id, omega_id, ndummy = get_pole_from_nuvel(nuvel_id,PlateModel)
                vn,ve=local_velocity_from_pole(lat_pt,lon_pt,lat_pole_id,lon_pole_id,omega_id)
                VL[0]=vn
                VL[1]=ve

            if file_mode == 'print' and isplate:
                azimuth, length = gmt_vector(VL)
                length=scale_factor*length
                if process_mode == 'S':
                    AVVF.write("%g  %g  %g  %g %d\n" % (lon_pt,lat_pt,azimuth,length,num_code) )
                elif process_mode == 'D':
                    AVVF.write("%g  %g  %g  %g %d %s\n" % (lon_pt,lat_pt,azimuth,length,num_code,sD) )
            if file_mode == 'process':
                AVVF.write("%g  %g  %g  %g  %d\n" % (lon_pt,lat_pt,VL[0],VL[1],num_code) )
        else:
            break
    SPPF.close()
    AVVF.close()

    return actual_velocity_vectors

#====================================================================
#
def get_velocity_vectors_for_pole(run_prefix,pole_file,scale_factor,sphere_pts,file_mode):
    #
    FN=open(pole_file)
    line=FN.readline()
    line=FN.readline()
    s1,s2,s3=line.split()
    lon_pole=float(s1); lat_pole=float(s2); omega=float(s3)
    FN.close()

    VL=np.zeros(3,dtype="float")

    SPF=open(sphere_pts)

    if file_mode == 'print':
        mean_velocity_vectors="%s_mean.xyV" % run_prefix
    elif file_mode == 'process':
        mean_velocity_vectors="%s_mean.V" % run_prefix

    MVVF=open(mean_velocity_vectors,"w")

    while 1:
        line=SPF.readline()
        if(line):
            n1,n2 = line.split()
            lon_pt=float(n1)
            lat_pt=float(n2)
            vn,ve=local_velocity_from_pole(lat_pt,lon_pt,lat_pole,lon_pole,omega)
            if file_mode == 'print':
                VL[0]=vn
                VL[1]=ve
                azimuth, length = gmt_vector(VL)
                length=scale_factor*length
                MVVF.write("%g  %g  %g  %g\n" % (lon_pt,lat_pt,azimuth,length) )
            elif file_mode == 'process':
                VL[0]=vn*scale_factor
                VL[1]=ve*scale_factor
                MVVF.write("%g  %g  %g  %g\n" % (lon_pt,lat_pt,VL[0],VL[1]) )
        else:
            break
    SPF.close()
    MVVF.close()

    return mean_velocity_vectors

#====================================================================
def get_polygon_grd(plate_id,mask_value,res):

    #polygon_xy = "/net/holmes/home4/gurnis/Rhea_runs/Plate_Margins/GPlates_polygons/%s.xy" % plate_id
    #polygon_xy = "/net/holmes/home4/gurnis/Rhea_runs/Plate_Margins/Bird_polygons/%s.xy" % plate_id
    polygon_xy = "/net/holmes/home4/gurnis/Rhea_runs/Plate_Margins/MORVEL56/%s.xy" % plate_id
    plate_grd = "%s.grd" % plate_id

    if plate_id == 'eu' or plate_id == 'nb' or plate_id == 'na' or plate_id == 'an':
        region_1="-180/180/-90/90"
        cmd="gmt grdmask %s -G%s -I%g -R%s -Nnan/%f/%f" % (polygon_xy,plate_grd,res,region_1,mask_value,mask_value)
        print(cmd)
        os.system(cmd)
        cmd="gmt grdedit %s -S -Rg" % plate_grd
        print(cmd)
        os.system(cmd)
    else:
        cmd="gmt grdmask %s -G%s -I%g -R%s -Nnan/%f/%f" % (polygon_xy,plate_grd,res,region,mask_value,mask_value)
        print(cmd)
        os.system(cmd)


    return polygon_xy, plate_grd
#====================================================================
def get_polygon_grd_with_background(plate_id,mask_value,mask_back,res):

    #polygon_xy = "/net/holmes/home4/gurnis/Rhea_runs/Plate_Margins/GPlates_polygons/%s.xy" % plate_id
    #polygon_xy = "/net/holmes/home4/gurnis/Rhea_runs/Plate_Margins/Bird_polygons/%s.xy" % plate_id
    polygon_xy = "/net/holmes/home4/gurnis/Rhea_runs/Plate_Margins/MORVEL56/%s.xy" % plate_id
    plate_grd = "%s.grd" % plate_id

    if plate_id == 'eu' or plate_id == 'nb' or plate_id == 'na' or plate_id == 'an':
        region_1="-180/180/-90/90"
        cmd="gmt grdmask %s -G%s -I%g -R%s -N%f/%f/%f" % (polygon_xy,plate_grd,res,region_1,mask_back,mask_value,mask_value)
        print(cmd)
        os.system(cmd)
        cmd="gmt grdedit %s -S -Rg" % plate_grd
        print(cmd)
        os.system(cmd)
    else:
        cmd="gmt grdmask %s -G%s -I%g -R%s -N%f/%f/%f" % (polygon_xy,plate_grd,res,region,mask_back,mask_value,mask_value)
        print(cmd)
        os.system(cmd)


    return polygon_xy, plate_grd

#====================================================================
def process_data_from_plate_model(plate_id,plate_model,stencil_grd_res):

    #Mapping between my 3 letter codes and the 4 letter Nuvel codes
    nuvel_id=Code[plate_id]
    plate_model_file = "%s%s.dat" % (Plate_model_dir,plate_model)

    PlateModel, PlateModel_Index =load_plate_model_into_dic(plate_model_file)
    lat_pole_id, lon_pole_id, omega_id, num_code = get_pole_from_nuvel(nuvel_id,PlateModel)
    plate_model_pole_file='%s_pole.xyz' % plate_id
    PMPF=open(plate_model_pole_file,"w")
    PMPF.write(">%s %s pole\n" % (plate_id,plate_model) )
    PMPF.write("%g %g %g\n" % (lon_pole_id,lat_pole_id,omega_id) )
    PMPF.close()

    plates_stencil_grd = "plates_stencil_%s_%s.grd" % (plate_model,stencil_grd_res)

    print('plates_stencil_grd',plates_stencil_grd)
    if not ( os.path.exists(plates_stencil_grd) ):

        i=0
        for id in Code:
            print('id',id)
            nuvel_id=Code[id]
            lat_pole_id, lon_pole_id, omega_id, num_code = get_pole_from_nuvel(nuvel_id,PlateModel)
            polygon_xy, plate_grd =get_polygon_grd(id,num_code,stencil_grd_res)
            if i == 0:
                cmd="cp %s %s" % (plate_grd,plates_stencil_grd)
                os.system(cmd)
            else:
                cmd="gmt grdmath %s %s AND = tmp.grd" % (plates_stencil_grd,plate_grd)
                os.system(cmd)
                cmd="mv tmp.grd %s" % (plates_stencil_grd)
                os.system(cmd)
            i+=1


    return plate_model_pole_file, PlateModel, PlateModel_Index, plates_stencil_grd

#====================================================================

def substract_vectors(run_prefix,rhea_velocity_vectors,mean_velocity_vectors,file_mode):

    rhea_vel=open(rhea_velocity_vectors,"r")
    mean_vel=open(mean_velocity_vectors,"r")

    if file_mode == 'print':
        rhea_velocity_substractmean="%s_substractmean.xyV" % run_prefix
    elif file_mode == 'process':
        rhea_velocity_substractmean="%s_substractmean.V" % run_prefix

    outfile=open(rhea_velocity_substractmean,"w")

    while 1:
        lineR=rhea_vel.readline()
        lineM=mean_vel.readline()
        if(lineR):
            if file_mode == 'print':
                lon,lat,azR,lenR = lineR.split()
                lon,lat,azM,lenM = lineM.split()

                # Use inverse version of gmt_vector to convert to ve and vn for both vectors
                vnR = sqrt(float(lenR)**2 / (tan(float(azR)*d2r)**2 + 1.))
                veR = vnR * tan(float(azR)*d2r)
                if (fabs(float(azR)) > 90.):
                    vnR = -fabs(vnR)
                else:
                    vnR = fabs(vnR)
                if (float(azR) < 0.):
                    veR = -fabs(veR)
                else:
                    veR = fabs(veR)

                vnM = sqrt(float(lenM)**2 / (tan(float(azM)*d2r)**2 + 1.))
                veM = vnM * tan(float(azM)*d2r)
                if (fabs(float(azM)) > 90.):
                    vnM = -fabs(vnM)
                else:
                    vnM = fabs(vnM)
                if (float(azM) < 0.):
                    veM = -fabs(veM)
                else:
                    veM = fabs(veM)

            elif file_mode == 'process':
                lon,lat,vn1,ve1 = lineR.split()
                lon,lat,vn2,ve2 = lineM.split()
                vnR = float(vn1)
                veR = float(ve1)
                vnM = float(vn2)
                veM = float(ve2)

            # Substract ve and vn components
            vnS = vnR - vnM
            veS = veR - veM
            vrS = 0.

            if file_mode == 'print':
                # Use gmt_vector to convert substracted vector back to azimuth and length
                vectorS = [vnS, veS, vrS]
                azS, lenS = gmt_vector(vectorS)
                outfile.write("%g  %g  %g  %g\n" % (float(lon),float(lat),azS,lenS) )
            elif file_mode == 'process':
                outfile.write("%g  %g  %g  %g\n" % (float(lon),float(lat),vnS,veS) )
        else:
            break

    rhea_vel.close()
    mean_vel.close()
    outfile.close()

    return rhea_velocity_substractmean

# EOF
