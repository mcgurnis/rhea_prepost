#!/usr/bin/env python2.7
#=====================================================================
#
#               Python Scripts for CitcomS Version 2.0.2
#                  ---------------------------------
#
#                              Authors:
#                            Michael Gurnis
#          (c) California Institute of Technology 2006-2026
#               Free for non-commercial academic use ONLY.
#      This program is distributed WITHOUT ANY WARRANTY whatsoever.
#
#=====================================================================
#
#  Copyright Aug. 2006, by the California Institute of Technology.
#  ALL RIGHTS RESERVED. United States Government Sponsorship Acknowledged.
#
#=====================================================================

import sys, string, os, math
import CitcomParser
#=====================================================================
def expected_temp(distance,age,scalet):

    if age <= 0: age = 0.01
    age = age / scalet
    arg = 0.5 * distance/math.sqrt(age)
    temperature = erf(arg)
    return temperature

#=====================================================================
def expected_temp_barc(distance,age,scalet):
   # This is a trick so that for backarc basins
   # (which are the only values in the age files that are 
   # set to 0 when barc=1) the temperature is set to 1 throughout the 
   # lithosphere. I could also make this only for depth==0 but I need there
   # to be a disconnect between the slab and the surface so I make this througout
   # the lithosphere.   
    if age == 0:
        distance=2800
        age=0.01
        age=age/scalet
        arg = 0.5*distance/math.sqrt(age)
        temperature = erf(arg)
    else:
        if age < 0:
            age=0.01
        else:
            age=age
        age=age/scalet
        arg = 0.5*distance/math.sqrt(age)
        temperature = erf(arg)
    return temperature

#=====================================================================
def erf(x):
    # from formula 7.1.28 in Abramowitz and Stegun
    #implicit double precision (a-h,o-z)
    a1=0.0705230784
    a2=0.0422820123
    a3=0.0092705272
    a4=0.0001520143
    a5=0.0002765672
    a6=0.0000430638
    one=1.0
    x2=x*x
    x3=x*x2
    temp=one+a1*x+a2*x2+a3*x3+a4*x2*x2+a5*x2*x3+a6*x3*x3
    temp2=temp*temp
    temp4=temp2*temp2
    temp8=temp4*temp4
    temp16=temp8*temp8
    erf=one-one/temp16
    return erf
#=====================================================================

def erf_array(n):
   
    #predefine the array with length n 
    profile=range(0,n)
    #Define the central value to be zero
    if(n%2):
        profile[(n-1)/2]=0.0
    else:
        profile[n/2-1]=0.0	 
        profile[n/2]=0.0 
 
    xmax=2.0 # Maximum xscale (normalized)
    i=1
    while 1:
        print(i,n/2)
        loc=2*i*xmax/n
        if(n%2):
            profile[(n-1)/2-i]=erf(loc)
            profile[(n-1)/2+i]=profile[(n-1)/2-i]
        else:
            profile[n/2-i-1]=erf(loc)
            profile[n/2+i]=profile[n/2-i-1]
        i+=1
        if(i>=n/2): break
        if(n%2):
	        loc=2*(i+1)*xmax/n
	        profile[0]=erf(loc)
	        profile[n-1]=profile[0]

    return(profile)

#====================================================================
#====================================================================
#====================================================================
def mk_lith_temp_file( depth, nd_depth, afile, dict ):
    '''create a BLENDING function ALWAYS from 0 to 1 based on the 
    half-space cooling model that is used to create the thermal 
    lithosphere'''

    # NOTE: in Temp_history_gen.py this grid is multiplied by the
    # slab temperature grid (which varies from temperature_min to
    # temperature_mantle).  Since temperature_mantle is encoded
    # within the slab grid, we do not need to include temperature_mantle
    # in this lithosphere function.  Hence the temperatures are NOT 
    # scaled by the temperature drop and therefore this is a blending
    # function rather than the actual lith temperature - 05/07/12 DJB

    scalet = float(dict['scalet'])
    age_min = float(dict['lith_age_min'])
    grd_res = float(dict['grd_res'])
    age_max = float(dict['thermal_age_max'])

    lith_blend = 'lith_blend_%d.grd' % ( depth )

    cmd = 'grdsample %s -Gtmp0.grd -I%g' % (afile, grd_res)
    print(cmd)
    os.system(cmd)

    # maximum and minimum ages
    cmd = 'grdclip tmp0.grd -Gage.grd -Sa%f/%f -Sb%f/%f' % (age_max, age_max, age_min, age_min)
    print(cmd)
    os.system(cmd)

    cmd = 'grdmath age.grd %g DIV SQRT = tmp1.grd' % (scalet)
    print(cmd)
    os.system(cmd)

    cmd = 'grdmath %g 0.5 MUL tmp1.grd DIV ERF = %s' % (nd_depth, lith_blend)
    print(cmd)
    os.system(cmd)

    return lith_blend

