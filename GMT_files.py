#!/usr/bin/env python
#=====================================================================
#               Python Scripts for CitComS, gplates, and Rhea
#          Preprocessing, Data Assimilation, and Postprocessing
#                  ---------------------------------
#                              Authors:
#                            Michael Gurnis
#                              
#          (c) California Institute of Technology 2003-2026
#               Free for non-commercial academic use ONLY.
#      This program is distributed WITHOUT ANY WARRANTY whatsoever.
#=====================================================================
#  Copyright May 2026, by the California Institute of Technology.
#  United States Government Sponsorship Acknowledged.
#  ALL RIGHTS RESERVED. 
#=====================================================================

"""
GMT_files.py reads in files in long, lat, data files 
from CitcomS.py after passing through the zslice code and
writes out several files in GMT format. data means a list
of values associated with the long, lat value


usage:

input:

outout:

"""
import sys, string, os, math
from datetime import datetime as dt

def Vfile(zfile,velfile,nc,nodex,nodey,nprocx,nprocy):

    gmtchar=">"
    nodes_per_proc=nodex*nodey
    lines=range(nodes_per_proc)
    #long=range(nodes_per_proc)
    #lat=range(nodes_per_proc)
    #vx=range(nodes_per_proc)
    #vy=range(nodes_per_proc)
    input=open(zfile)
    output=open(velfile,"w")

    #HACKED
    #therm_diff = parser.getfloat('thermdiff')
    therm_diff = 1e-6
    layer_km = 6371.0
    #mult by scalev to get velocities in cm/yr
    scalev=(therm_diff/(layer_km*1e3))*(100.0*3600.0*24.0*365.25)

    Pi=math.pi
    vector_incr = int(0.05*nodes_per_proc)

    for n in range(nodes_per_proc):
        line=input.readline()
        long=float(line.split(' ')[0])
        lat=float(line.split(' ')[1])
        vx=float(line.split(' ')[2])
        vy=float(line.split(' ')[3])
        
        if n % vector_incr == 0:
            if vy <= 0.0:
                if vx < 0.0:
                    a=math.degrees(math.atan(vy/vx))
                    azimuth=360.0-a
                elif vx > 0.0:
                    a=math.degrees(math.atan(-vy/vx))
                    azimuth=180.0+a
                else:
                    azimuth=270.0
            elif vy > 0.0:
                if vx < 0.0:
                    a=math.degrees(math.atan(-vy/vx))
                    azimuth=a
                elif vx > 0.0:
                    a=math.degrees(math.atan(vy/vx))
                    azimuth=180.0-a
                else:
                    azimuth=90.0

            #length=math.hypot(vx,vy)/50000.
            length=scalev*math.hypot(vx,vy)
            print(dt.now(), ' velocity =', length,' cm/yr')
            length=length/25.0
            output.write('%f %f %f %f\n' % (long,lat,azimuth,length))

    input.close()
    output.close()

    return

def Tfile(zfile,tempfile,nc,nodex,nodey,nprocx,nprocy):

    gmtchar=">"
    nodes_per_proc=nodex*nodey
    lines=range(nodes_per_proc)
    long=range(nodes_per_proc)
    lat=range(nodes_per_proc)
    temp=range(nodes_per_proc)
    input=open(zfile)
    output=open(tempfile,"w")

    for n in range(nodes_per_proc):
        line=input.readline()
        long[n]=float(line.split(' ')[0])
        lat[n]=float(line.split(' ')[1])
        temp[n]=float(line.split(' ')[5])
        output.write('%f %f %f\n' % (long[n],lat[n],temp[n]))

    input.close()
    output.close()

    return


def Vifile(zfile,viscfile,nc,nodex,nodey,nprocx,nprocy):

    import math
    log=math.log10

    gmtchar=">"
    nodes_per_proc=nodex*nodey
    lines=range(nodes_per_proc)
    long=range(nodes_per_proc)
    lat=range(nodes_per_proc)
    visc=range(nodes_per_proc)
    input=open(zfile)
    output=open(viscfile,"w")

    for n in range(nodes_per_proc):
        line=input.readline()
        long[n]=float(line.split(' ')[0])
        lat[n]=float(line.split(' ')[1])
        visc[n]=float(line.split(' ')[6])
        output.write('%f %f %f\n' % (long[n],lat[n],log(visc[n])))

    input.close()
    output.close()

    return


def Sfile(zfile,surffile,nc,nodex,nodey,nprocx,nprocy,scale_s):

    r2d = 180.0/math.pi

    gmtchar=">"
    nodes_per_proc=nodex*nodey
    lines=range(nodes_per_proc)
    long=range(nodes_per_proc)
    lat=range(nodes_per_proc)
    surf=range(nodes_per_proc)
    input=open(zfile)
    output=open(surffile,"w")

    #Get header
    line=input.readline()
    for n in range(nodes_per_proc):
        line=input.readline()
        long[n]=float(line.split(' ')[1])
        long[n]=long[n]*r2d
        lat[n]=float(line.split(' ')[0])
        lat[n] = 90 - lat[n]*r2d
        surf[n]=float(line.split(' ')[2])
        surf[n]=scale_s*surf[n]
        output.write('%f %f %f\n' % (long[n],lat[n],surf[n]))

    input.close()
    output.close()

    return


def Efile(zfile,meshfile,procfile,nc,nodex,nodey,nprocx,nprocy):

    gmtchar=">"
    nodes_per_proc=nodex*nodey
    long=range(nodes_per_proc)
    lat=range(nodes_per_proc)
    input=open(zfile)
    output=open(meshfile,"w")
    proc_poly=open(procfile,"w")

    for n in range(nodes_per_proc):
        line=input.readline()
        long[n]=float(line.split(' ')[0])
        lat[n]=float(line.split(' ')[1])

    
    for i in range(nodex):
        output.write('%s\n' % gmtchar)
        for j in range(nodey):
            n = i*nodey + j
            output.write('%f %f\n' % (long[n],lat[n]))

    for j in range(nodey):
        output.write('%s\n' % gmtchar)
        for i in range(nodex):
            n = i*nodey + j
            output.write('%f %f\n' % (long[n],lat[n]))

    red   = [250,   0, 150, 200, 250, 250, 150, 250, 250, 150, 150, 250]
    green = [150, 250, 150, 200, 150, 250, 150, 250, 150, 250, 150, 250]
    blue  = [150, 250, 250, 150, 150,   0, 250, 150, 150, 150, 250,   0]


    nox=(nodex-1)/nprocx + 1
    noy=(nodey-1)/nprocy + 1
    for nx in range(nprocx):
        for ny in range(nprocy):
            intensity=0.3 + 0.7*(nx+1)*(ny+2)/(nprocx*(nprocy+1))
            r=int(intensity*red[nc])
            g=int(intensity*green[nc])
            b=int(intensity*blue[nc])
            color = '-G%d/%d/%d' % (r,g,b)
            proc_poly.write('%s %s\n' % (gmtchar,color) )
            for ii in range(nox):
                i=nx*(nox-1)+ii
                jj=0
                j=ny*(noy-1)+jj
                n = i*nodey + j
                proc_poly.write('%f %f\n' % (long[n],lat[n]))
            for jj in range(noy):
                ii=nox-1
                i=nx*(nox-1)+ii
                j=ny*(noy-1)+jj
                n = i*nodey + j
                proc_poly.write('%f %f\n' % (long[n],lat[n]))
            for ii in range(nox):
                i=nx*(nox-1)-ii
                jj=noy-1
                j=ny*(noy-1)+jj
                n = i*nodey + j
                proc_poly.write('%f %f\n' % (long[n],lat[n]))
            for jj in range(noy):
                ii=0
                i=nx*(nox-1)+ii
                j=ny*(noy-1)+noy-1-jj
                n = i*nodey + j
                proc_poly.write('%f %f\n' % (long[n],lat[n]))

    input.close()
    output.close()
    proc_poly.close()

    return 

