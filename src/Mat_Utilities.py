#!/usr/bin/env python
#=====================================================================
#
#               Python Scripts for CitcomS Data Assimilation
#                  ---------------------------------
#
#                              Authors:
#                            Michael Gurnis
#             (c) California Institute of Technology 2006-2026
#
#      This program is distributed WITHOUT ANY WARRANTY whatsoever.
#
#=====================================================================
#
#  Copyright May 2026, by the California Institute of Technology.
#
#=====================================================================

import Thermal_Utilities
import sys, string, os, time
from datetime import datetime as dt
import GMT_Utilities
import math, random
from Core_Util import now
#=====================================================================
# Global variables
verbose = True
r2d = 180.0/math.pi # radians to degrees
d2r = math.pi/180.0 # degrees to radians
#=====================================================================
def xy2xyz(xy_file,zvalue,square,spacing,bounds,res,zback):

    XYF=open(xy_file)
    xyz_file="tmp.xyz"
    cmd="rm -f %s" % xyz_file
    os.system(cmd)
    XYZF=open(xyz_file,"w")

    N_slab_pts=13
    points = [-1.5,-1.25,-1.,-0.75,-0.5,-0.25,0.,0.25,0.5,0.75,1.0,1.25,1.5]
    d_p_degrees=[]
    g=[]
    for ii in range(N_slab_pts):
        value=square*points[ii]
        result = zvalue*math.exp(-(value*value)/(square*square))
        d_p_degrees.append(value)
        g.append(result)

    print('d_p_degrees=',d_p_degrees)
    print('g',g)

    while 1:
        line=XYF.readline()
        if(line):
            c1 = line[0]
            if c1 == '>':
                m=0
                over_riding = None
                if len(line) >= 3:
                    over_riding = line[2]
            if c1 != '#'  and c1 != '>':
                m+=1
                if m > 2:
                    flat2=flat1
                    flon2=flon1
                if m > 1:
                    flat1=flat
                    flon1=flon
                lon, lat, value =line.split()
                flat=float(lat)
                flon=float(lon)
                if flon < 0.0:
                    flon=flon+360.0
                if m > 2:
                    dx=flon-flon2
                    dy=flat-flat2
                    for ii in range(N_slab_pts):
                        dist2 = d_p_degrees[ii]
                        zvalue2=g[ii]
                        flon_new,flat_new = new_point(flon1,flat1,dx,dy,dist2,over_riding)
                        if flon_new < 0.0:
                            flon_new=flon_new+360.0
                        if flon_new < 360.0:
                            XYZF.write("%g   %g   %g\n" % (flon_new,flat_new,zvalue2) )
                    lon, lat, value =line.split()

        else:
            break             

    XYF.close()
    XYZF.close()

    # create a uniformly spaced background with zback
    if spacing > 0:
        xyz_file_2="tmp_2.xyz"
        cmd="rm -f %s" % xyz_file_2
        os.system(cmd)
        XYZF=open(xyz_file_2,"w")
        #XYZF.write(">\n")
        flon=0.
        while flon <=360.: 
            flat=-89.
            while flat <= 89.0:
                XYZF.write("%g  %g  %g\n" % (flon,flat,zback))
                flat+=spacing
            flon+=spacing
    XYZF.close()
    
    xyz_file_3="tmp_3.xyz"
    cmd="rm -f %s" % xyz_file_3
    os.system(cmd)
    cmd = "cat %s %s > %s" % (xyz_file,xyz_file_2,xyz_file_3)
    print('cmd = ', cmd)
    os.system(cmd)
    cmd = "rm -f %s" % (xyz_file_2)
    os.system(cmd)

    return xyz_file_3
#=====================================================================
def slab_xy2xyz(xy_file,factor,advection,spacing,T_mantle,age_min,scalet,layer_km):

    scalet2=(layer_km*1e3*layer_km*1e3)/scalet
    XYF=open(xy_file)
    xyz_file="tmp.xyz"
    cmd="rm -f %s" % xyz_file
    os.system(cmd)
    XYZF=open(xyz_file,"w")

    sq_x = [-1.,-0.5,0.,0.5,1.0]
    sq_y = [-1.,-0.5,0.,0.5,1.0]
    cooling=[]
    # create a lookup array with the error function
    ii=0
    while ii<5:
        jj=0
        while jj<5:
            dist=sq_x[ii]*sq_x[ii] + sq_y[jj]*sq_y[jj]
            dist=math.sqrt(dist)
            kk=ii*5+jj
            value=1.0-Thermal_Utilities.erf(dist)
            cooling.append(value)
            jj+=1
        ii+=1

    while 1:
        line=XYF.readline()
        if(line):
            c1 = line[0]
            #if c1 == '>':
                #XYZF.write(line)
            if c1 != '#' and c1 != '>':
                #s1=line.strip('\n')
                lon, lat, iage =line.split()
                flat=float(lat)
                flon=float(lon)
                age=float(iage)
                if age < age_min:
                    age=age_min
                # thickness is depth to 0.9 isotherm divided by 2
                thickness=2.32*math.sqrt(age*scalet2) #in m
                square=thickness/(2.*1000.*110.0) #degrees of latitude
                #thickness=thickness/(layer_km*1e3) # non-dimensional
                #slab_temp=Thermal_Utilities.expected_temp(thickness,age,scalet)
                slab_temp_max=T_mantle # by definition 1/2 of the 0.9 isotherm
                #factor is a slab broadening that conserves buoyancy
                slab_temp_max=T_mantle - (T_mantle-slab_temp_max)/factor
                square=advection*factor*square

                if flon < 0.0:
                    flon=flon+360.0

                ii=0
                while ii<5:
                    jj=0
                    while jj<5:
                        flat1=flat+square*sq_x[ii]
                        flon1=flon+square*sq_y[jj]/math.cos(d2r*flat)
                        kk=ii*5+jj
                        slab_temp=slab_temp_max*cooling[kk]
                        XYZF.write("%g  %g  %g\n" % (flon1,flat1,slab_temp))
                        jj+=1
                    ii+=1
        else:
            break             

    XYF.close()
    XYZF.close()

    # create a uniformly spaced background with zback
    if spacing > 0:
        xyz_file_2="tmp_2.xyz"
        cmd="rm -f %s" % xyz_file_2
        os.system(cmd)
        XYZF=open(xyz_file_2,"w")
        #XYZF.write(">\n")
        flon=0.
        while flon <=360.: 
            flat=-89.
            while flat <= 89.0:
                XYZF.write("%g  %g  %g\n" % (flon,flat,T_mantle))
                flat+=spacing
            flon+=spacing
    XYZF.close()
    
    cmd = "cat %s %s >> %s" % (xyz_file,xyz_file_2,xyz_file)
    os.system(cmd)
    cmd = "rm -f %s" % (xyz_file_2)
    os.system(cmd)

    return xyz_file
#=====================================================================
def replace_type_code(file_old,new_type_code):
    # replace type in a PLATES 4 file

    print("\n\n new_type_code=",new_type_code)
    OLD=open(file_old)
    file_new="rt_file.dat"
    cmd="rm -f %s" % file_new
    os.system(cmd)
    NEW=open(file_new,"w")

    zvalue=-999.
    gmt_char = '>'
    while 1:
        line=OLD.readline()
        if(line):
            c1 = line[0]
            if c1 == '>':
                m=0
                NEW.write(">%s%s" % (new_type_code,line[4:]))
            if c1 != '#' and c1 != '>':
                m+=1
                NEW.write("%s" % line)
        else:
            break             

    OLD.close()
    NEW.close()
 
    return file_new

#=====================================================================
def sz_slab_dip(sz_age,deep_dip,default_dip,current_age):
    
    if current_age >= 0 and sz_age=='unknown':
        subduction_duration = 200.0-float(current_age)
    else:
        subduction_duration = float(sz_age)-float(current_age)

    if current_age == 0:
        if deep_dip == 'unknown':
            dip = float(default_dip)
        else:
            dip=float(deep_dip)
    else:
        # Tape et al. Paper version June 18, 2007
        dip = 73.39 + 8.9*1.0 - 0.17*20.0 - 0.090*subduction_duration

    return dip
#=====================================================================
def sz_age2slab_depth(sz_age,known_depth,current_age):

    print('sz_age=',sz_age,type(sz_age))
    print('known_depth=',known_depth,type(known_depth))
    print('current_age=',current_age,type(current_age))
    
    #age in Myr
    slab_velocity_1=5.0 #cm/yr Above middle of TZ
    slab_velocity_1=slab_velocity_1*10.0 #km/Myr
    slab_velocity_2=2.0 #cm/yr Belwo middle of TZ
    slab_velocity_2=slab_velocity_2*10.0 #km/Myr
    if current_age >= 0 and sz_age=='unknown':
        subduction_duration = 200.0-float(current_age)
    else:
        subduction_duration = float(sz_age)-float(current_age)

    if subduction_duration <= 0.0:
        duration_1 = 0.0
        duration_2 = 0.0
    elif subduction_duration > 0.0 and subduction_duration < 5.0:
        duration_1 = subduction_duration
        duration_2 = 0.0
    elif subduction_duration >= 5.0:
        duration_1 = 5.0
        duration_2 = subduction_duration-5.0

    if current_age == 0:
        if known_depth == 'unknown':
            if sz_age == 'unknown':
                depth=0
            else:
                depth=slab_velocity_1*duration_1 + slab_velocity_2*duration_2
        else:
            depth=float(known_depth)
    else:
        depth=slab_velocity_1*duration_1 + slab_velocity_2*duration_2

    if depth > 3000.0:
        depth=3000.0

    return depth
#=====================================================================
#
#=====================================================================
def Find_slab_data( dict, input_subduction_file ):

    '''Create a file containing the pertinent header details for slab
    assimilation along with the coordinates of the line features.
    Assume default values and override by GPML header data
    if specified in the input configuration file (GPML_HEADER).'''

    if verbose: print(dt.now(), 'Find_slab_data:')

    # parameters
    GPML_HEADER = dict['GPML_HEADER']
    default_slab_dip = dict['slab_dip']
    depth_max = dict['depth_max']
    age = dict['age']
    SZ_DURATION_OVERWRITE = dict['SZ_DURATION_OVERWRITE']
    default_slab_UM_descent_rate = dict['slab_UM_descent_rate']
    slab_LM_descent_rate = dict['slab_LM_descent_rate']

    # read and close input file
    infile = open(input_subduction_file,'r')
    lines = infile.readlines()
    infile.close()

    # remove file end mark (>)
    lines = lines[:-1]

    xy_file_new="sz_new%f.xy" % time.time()
    cmd="rm -f %s" % xy_file_new
    os.system(cmd)

    outfile = open(xy_file_new,'w')

    for line in lines:

        # shortcut to write out xy (coordinate) data
        if not line.startswith('>'):
            outfile.write("%s" % line)
            continue

        # report missing subduction zone polarities to user
        if line[1:3] not in ['sL','sR']:
            print('!!! Find_slab_data: Unknown subduction polarity')
            errorline = line.rstrip('\n')
            print('!!! Slab assimilation will FAIL for this line segment:')
            print('!!! %(errorline)s' % vars())

        # default parameters
        slab_depth = depth_max
        slab_dip = default_slab_dip
        sdepth = 0.0
        slab_UM_descent_rate = default_slab_UM_descent_rate

        # check for values in GPML header
        if GPML_HEADER:
            if verbose: print(dt.now(), 'reading GPML header data')
            header_data = {}
            header_data = get_header_GMT_xy_file_dictionary( line )
            s_depth = header_data.get('slabFlatLyingDepth', 'Unknown') 
            if s_depth != 'Unknown':
                sdepth = float(s_depth)
            sz_depth = header_data.get('subductionZoneDepth', 'Unknown') 
            if sz_depth != 'Unknown':
                slab_depth = float(sz_depth)
            sz_dip = header_data.get('subductionZoneDeepDip', 'Unknown') 
            if sz_dip != 'Unknown':
                slab_dip = float(sz_dip)
            sz_age = header_data.get('subductionZoneAge', 'Unknown') 
            TF_slab_flat = header_data.get('slabFlatLying', 'Unknown') 
            if sz_age != 'Unknown' and (SZ_DURATION_OVERWRITE) and TF_slab_flat == 'Unknown':
                # next check exists to deal with spurious GPlates data
                if age <= float(sz_age):

                    # use subductionZoneConvergence for upper mantle slab descent rate
                    test_slab_UM_descent_rate = header_data.get('subductionZoneConvergence', 'Unknown')
                    if test_slab_UM_descent_rate != 'Unknown':
                        slab_UM_descent_rate = float(test_slab_UM_descent_rate)

                    # duration of slab in UM if descending at slab_UM_descent_rate
                    # in Myr when slab_UM_descent_rate is in cm/yr
                    UM_duration = 660.0/(slab_UM_descent_rate*10.0)

                    #print 'slab_depth=',slab_depth, 'km'
                    print('age=',age,' sz_age=',sz_age)
                    print('slab_UM_descent_rate=', slab_UM_descent_rate, 'cm/yr')
                    print('UM_duration=',UM_duration, 'Myr')
                    s_duration = float(sz_age)-age

#                   Factor of 10 gives depth in km for slab_descent_rate in cm/yr
                    if s_duration < UM_duration:
                        slab_depth = slab_UM_descent_rate*s_duration*10.0
                    elif s_duration >= UM_duration:
                        slab_depth = 660.0 + slab_LM_descent_rate*(s_duration-UM_duration)*10.0
                    if slab_depth > depth_max:
                        slab_depth = depth_max
                    print('slab_depth=',slab_depth, 'km')

        # xy header line
        outline="%s DEPTH=%f DIP=%f START_DEPTH=%f\n" % (line[0:3],slab_depth,slab_dip,sdepth)
        outfile.write("%s" % outline)

    outfile.close()
 
    return xy_file_new

#=====================================================================
def Fill_xy(xy_file_old,min_deg):

    OLD=open(xy_file_old)
    xy_file_new="tmp_new%f.xy" % time.time()
    cmd="rm -f %s" % xy_file_new
    os.system(cmd)
    NEW=open(xy_file_new,"w")

    zvalue=-999.
    gmt_char = '>'
    tmp_file="insert.xy"
    while 1:
        line=OLD.readline()
        if(line):
            c1 = line[0]
            if c1 == '>':
                m=0
                #NEW.write("%s\n" % gmt_char)
                NEW.write("%s" % line)
            if c1 != '#' and c1 != '>':
                m+=1
                lon, lat =line.split()
                #lat, lon =line.split() #Tmp change made by MG
                flat=float(lat)
                flon=float(lon)
                if flon < 0.0:
                    flon=flon+360.0
                if flon > 360.0:
                    flon=flon-360.0
                #if m==1:
                #    NEW.write("%g   %g   %g\n" % (flon,flat,zvalue) )
                if m>1: 
                    dist=0.0
                    if (flon_1 > 20.0 and flon > 20.0) or (flon_1 < 340. and flon < 340.) : 
                        dist=math.sqrt((flat_1-flat)**2 + (flon_1-flon)**2)
                    if dist > min_deg:
                        num_new=int(dist/min_deg)
                        dlon=(flon-flon_1)/num_new
                        dlat=(flat-flat_1)/num_new
                        nn=0
                        flon_new=flon_1
                        flat_new=flat_1
                        while nn<num_new:
                            zdummy=float(nn)
                            NEW.write("%g   %g   %g\n" % (flon_new,flat_new,zdummy) )
                            flon_new=flon_new+dlon
                            flat_new=flat_new+dlat
                            nn+=1
                             
                        #flon_c=(flon_1+flon)/2.0
                        #flat_c=(flat_1+flat)/2.0
                        #cmd="gmt project -C%g/%g -E%g/%g -G%g > %s" % (flon_c,flat_c,flon,flat,min_deg,tmp_file) 
                        #os.system(cmd)
                        #TMP=open(tmp_file,"r")
                        #n=0
                        #while 1:
                        #    n+=1
                        #    tmp_line=TMP.readline()
                        #    if tmp_line:
                        #        if n>1:
                        #            NEW.write("%s" % tmp_line)
                        #    else:
                        #        break             
                        #TMP.close()
                flat_1=flat
                flon_1=flon
        else:
            break             

    OLD.close()
    NEW.close()
 
    return xy_file_new

#=====================================================================
def filter(grdfile,bounds,k,width,zmin,zmax):

    filtered_name="filtered.grd"

    clipped_name="mat%d.grd" % k

    if width != 'none':
        cmd="gmt grdfilter %s -D2 -Fg%g -V -G%s -R%s" % (grdfile,width,filtered_name,bounds)
        os.system(cmd)

        if zmin != 'none' or zmax != 'none':
            cmd="grdclip %s -G%s -Sa%g/%g -Sb%g/%g" % (filtered_name,clipped_name,zmax,zmax,zmin,zmin)
            os.system(cmd)
    else:
        cmd="cp %s %s" % (grdfile,clipped_name)
        os.system(cmd)

    return clipped_name

#=====================================================================
def mk_parallel_slab_base( dict, xy_tmp ):

    if verbose: print(dt.now(), 'mk_parallel_slab_base:')

    OLD = open(xy_tmp)
    lines = OLD.readlines()
    OLD.close()

    age = dict['age']
    pname = "parallel_slab_base_%d.xy" % age
    cmd = "rm -f %s" % pname
    os.system( cmd )
    NEW = open(pname,"w")

    dist = 1.0

    m = 0
    for line in lines:
        c1 = line[0]
        # header
        if c1 == dict['gmt_char']:
            m=0
            NEW.write("%s" % line)
            # over_riding plate in subduction zone
            over_riding = None
            if len(line) >= 3:
                over_riding = line[2]
            header_data = {}
            header_data = get_header_GMT_xy_file_dictionary( line )

            # extract data from header, otherwise 'Unknown'
            szd = header_data.get('subductionZoneDepth', 'Unknown')
            szdd = header_data.get('subductionZoneDeepDip', 'Unknown')

            if szd != 'Unknown':
                fszd = float(szd)
            else:
                fszd = dict['flat_slab_sub_depth']
            # maximum depth of flat slab at subduction zone
            if fszd > dict['flat_slab_sub_depth']:
                fszd = dict['flat_slab_sub_depth']
            if szdd != 'Unknown':
                fszdd = float(szdd)
            else:
                fszdd = dict['slab_dip']
            # dist in degrees
            dist = fszd/(math.tan(fszdd*d2r)*110.0)

            if verbose: print(dt.now(), 'fszd=',fszd,'fszdd=',fszdd,'dist=',dist)

        # line data
        elif c1 != dict['gmt_char']:
            m+=1
            if m > 2:
                flat2=flat1
                flon2=flon1
            if m > 1:
                flat1=flat
                flon1=flon
            lon, lat =line.split()
            flat=float(lat)
            flon=float(lon)
            if flon < 0.0:
                flon=flon+360.0
            if m > 2:
                dx=flon-flon2
                dy=flat-flat2
                flon_new,flat_new = new_point(flon1,flat1,dx,dy,dist,over_riding)
                if flon_new < 0.0:
                    flon_new=flon_new+360.0
                if flon_new < 360.0:
                    NEW.write("%g   %g\n" % (flon_new,flat_new) )

    NEW.close()
    return pname

#=====================================================================
def mk_parallel_line(xy_tmp,k,dist):

    OLD=open(xy_tmp)
    pname = "parallel_%d.xy" % k
    cmd="rm -f %s" % pname
    os.system(cmd)
    NEW=open(pname,"w")

    zvalue=-999.
    gmt_char = '>'
    m=0
    while 1:
        line=OLD.readline()
        if(line):
            c1 = line[0]
            if c1 == '>':
                m=0
                NEW.write("%s" % line)
                #over_riding plate in subduction zone
                over_riding = None
                if len(line) >= 3:
                    over_riding = line[2]
            if c1 != '#'  and c1 != '>':
                m+=1
                if m > 2:
                    flat2=flat1 
                    flon2=flon1 
                    zvalue2=zvalue1 
                if m > 1:
                    flat1=flat 
                    flon1=flon 
                    zvalue1=zvalue 
                lon, lat, value =line.split()
                flat=float(lat)
                flon=float(lon)
                zvalue=float(value)
                if flon < 0.0:
                    flon=flon+360.0
                if m > 2:
                    dx=flon-flon2
                    dy=flat-flat2
                    flon_new,flat_new = new_point(flon1,flat1,dx,dy,dist,over_riding)
                    if flon_new < 0.0:
                        flon_new=flon_new+360.0
                    if flon_new < 360.0:
                        NEW.write("%g   %g   %g\n" % (flon_new,flat_new,zvalue1) )
        else:
            break             

    OLD.close()
    NEW.close()

    return pname
#=====================================================================
#  	MAKE A PARALLEL SURFACE BACKARC BASIN
#=====================================================================
def mk_backarc(sub,dmin,dmax,region,proj,age,grd_res,rotate):
    # Convert dmin and dmax to grd_res
    deld=(dmax-dmin)/111000.
    #Backarc basin is located in m behind the trench.
    xyfile=open(sub,'r')
    #region='-R0/360/-90/90'
    #proj='-JH/7'
    ticks='-B'
    backarcfile=open('backarc','w')
    line=xyfile.readlines()
    for m in range(len(line)-1): 
        if string.find(line[m],'>') >= 0:
            if line[m][0:3] == '>sL':
                left=1
                right=0
            if line[m][0:3] == '>sR':
                left=0
                right=1
        else:
                if (string.find(line[m+1],'>') < 0):
                    long1=line[m].split(' ')[0]
                    lat1=line[m].split(' ')[3]
                    long2=line[m+1].split(' ')[0]
                    lat2=line[m+1].split(' ')[3]
                    #print "finding backarc basin location points"
                    #1. Calculate bearing from long1lat1 to midpoint
                    #brng=find_bearing(long1,lat1,longm,latm)
                    (dist,brng)=rhumb_line(long1,lat1,long2,lat2)
                    #2. Decide which way I want to project outwards
                    if left == 1:
                        if brng > 270:
                            bearng_p=brng-270
                        else:
                            bearng_p=brng-90
                    if right == 1:
                        if brng > 90:
                            bearng_p=brng-270
                        else:
                            bearng_p=brng+90
                    #3. Find an end point given a distance and a bearing
                    (blon,blat)=find_end_point(lat1,long1,bearng_p,dmax)
                    backarcfile.write(str(blon)+' '+str(blat)+' 1 \n')
    xyfile.close()
    backarcfile.close()
    os.system("awk '{if ($1 < 0) print(360+$1, $2, $3); else print($0) } ' backarc > backarc2")
    os.system("makecpt -Crainbow -T0/1/0.1 -D > out.cpt")
    os.system("grdmask backarc2 -NNaN/NaN/1  -Gout.grd -I"+str(grd_res)+" "+region+" -S"+str(deld)+" -V")
    #os.system("grdimage out.grd -Cout.cpt "+region+" "+proj+" "+ticks+" -K > out.ps")
    #if rotate == 1:
    #    os.system("psxy /home/lydia/GPLATES/Model8_Output/LINES_EQ/Polygons.subduction_boundaries."+str(age)+".xy -: -R -J -O -M -N >> out.ps")
    #else:
    #    os.system("psxy /home/lydia/GPLATES/Model8_Output/LINES/Polygons.subduction_boundaries."+str(age)+".xy -: -R -J -O -M -N >> out.ps")
    return

#=====================================================================
#  	Find distance between 2 points
#=====================================================================
def find_barc(line,m):
    if (string.find(line[m],'>') < 0) and (string.find(line[m+1],'>') < 0):
        long1=line[m].split(' ')[0]
        lat1=line[m].split(' ')[3]
        long2=line[m+1].split(' ')[0]
        lat2=line[m+1].split(' ')[3]
        #print "finding backarc basin location points"
        #1. Calculate bearing from long1lat1 to midpoint
        #brng=find_bearing(long1,lat1,longm,latm)
        (dist,brng)=rhumb_line(long1,lat1,long2,lat2)
        return brng

#=====================================================================
#  	Find distance between 2 points
#=====================================================================

def get_distance(long1,lat1,long2,lat2):
    '''Returns the distance between two points on the earth.        
    Inputs used are:
        Longitude (in radians) of the first location,
        Latitude (in radians) of the first location,
        Longitude (in radians) of the second location, and
        Latitude (in radians) of the second location.
    Uses Haversines formula 
    Find information at http://www.movable-type.co.uk/scripts/latlong.html'''
    long_1 = math.radians(float(long1))
    lat_1  = math.radians(float(lat1))
    long_2 = math.radians(float(long2))
    lat_2  = math.radians(float(lat2))
    dlong = long_2 - long_1
    dlat = lat_2 - lat_1
    a = (math.sin(dlat / 2))**2 + math.cos(lat_1) * math.cos(lat_2) * (math.sin(dlong / 2))**2
    c = 2* math.atan2(math.sqrt(a), math.sqrt(1-a))
    dist = 6371.0e3 * c
    dist2= dist/2
    return dist

#=====================================================================
# Find the midpoint between two lat long coordinates
#=====================================================================

def find_mid_point(long1,lat1,long2,lat2):
    long_1 = math.radians(float(long1))
    if float(lat1) == -90:
        lat1=float(-89.99999)
    lat_1  = math.radians(float(lat1))
    long_2 = math.radians(float(long2))
    if float(lat2) == -90:
       lat2 = float(-89.9999)
    lat_2  = math.radians(float(lat2))
    dlong = long_2 - long_1
    dlat = lat_2 - lat_1
    Bx=math.cos(lat_2) * math.cos(dlong)
    By = math.cos(lat_2) * math.sin(dlong)
    latm=math.atan2(math.sin(lat_1)+math.sin(lat_2), math.sqrt((math.cos(lat_1)+Bx) * ( math.cos(lat_1)+Bx) + By*By))
    lonm = long_1 + math.atan2(By, (math.cos(lat_1) + Bx) )
    LatM=latm*180/math.pi
    LonM=lonm*180/math.pi
    return (LonM, LatM)

#=====================================================================
#  Calculate distance and bearing from start to stop point using rhumb
#  lines
# out=rhumb_line(4.0,50.0,71.0,42.0)
#=====================================================================

def rhumb_line(long1,lat1,long2,lat2):
    long_1 = math.radians(float(long1))
    if float(lat1) == -90:
        lat1=float(-89.99999)
    lat_1  = math.radians(float(lat1))
    long_2 = math.radians(float(long2))
    if float(lat2) == -90:
       lat2 = float(-89.9999)
    lat_2  = math.radians(float(lat2))
    dlong = long_2 - long_1
    dlat = lat_2 - lat_1
    R = 6371.0e3
    dPhi = math.log(math.tan(lat_2/2+math.pi/4.)/math.tan(lat_1/2+math.pi/4) )
    if abs(dlat)  > 1e-10:
        q=dlat/dPhi
    else:
        q=math.cos(lat_1)
    if abs(dlong) > math.pi:
        if dlong > 0:
            dlong=-1*(2*math.pi-dlong)
        else:
            dlong=2*math.pi+dlong
    d=math.sqrt(dlat*dlat+q*q*dlong*dlong)*R
    brng=math.atan2(dlong,dPhi)
    deg=brng*180/math.pi
    return (d,deg)
       


#=====================================================================
#  Calculate initial bearing from start to stop point
#=====================================================================
def find_bearing(long1,lat1,long2,lat2):
    # Bearing east from north 
    long_1 = math.radians(float(long1))
    lat_1  = math.radians(float(lat1))
    long_2 = math.radians(float(long2))
    lat_2  = math.radians(float(lat2))
    dlong = long_2 - long_1
    dlat = lat_2 - lat_1
    y=math.sin(dlong)*math.cos(lat_2)
    x=math.cos(lat_1)*math.sin(lat_2) - math.sin(lat_1)* math.cos(lat_2)*math.cos(dlong)
    b=math.atan2(y,x)
    deg=b*180/math.pi
    return (deg)

#=====================================================================
#  Calculate point location from bearing,distance and start point
#=====================================================================	

def find_end_point(lat1,long1,brng,d):
    long_1 = math.radians(float(long1))
    lat_1  = math.radians(float(lat1))
    brng_1=math.radians(float(brng))
    R = 6371.0e3
    a=math.sin(lat_1)*math.cos(d/R)
    b=math.cos(lat_1)*math.sin(d/R)*math.cos(brng_1)
    lat_2=math.asin(a+b)
    c=math.sin(brng_1)*math.sin(d/R)*math.cos(lat_1)
    d =math.cos(d/R)
    e = math.sin(lat_1)*math.sin(lat_2)
    lon_2=long_1+ math.atan2(c,d-e)
    LAT=lat_2*180./math.pi
    LON=lon_2*180./math.pi
    return (LON,LAT)

#=====================================================================
#  	Find backarc basin location behind trench
#=====================================================================

def get_backarc(longa,lata,longb,latb,dist,blength):
    R = 6371.0e3
    x0=math.radians(longa-longa)*R*math.cos(math.radians(lata))
    y0=math.radians(lata-lata)*R
    x1=math.radians(longb-longa)*R*math.cos(math.radians(latb))
    y1=math.radians(latb-lata)*R
    alpha=math.atan2(y1,x1)
    print(alpha)
    #alpha=math.atan(y1/x1)
    C=math.sqrt((dist**2)+(blength**2))
    beta=math.asin(blength/C)
    theta=alpha-beta
    x3=C*math.cos(theta)
    y3=C*math.sin(theta)
    # Convert back to lat long position
    ay=( ((180/math.pi)*y3)/R) +(lata)
    ax=((x3/(R*math.cos(math.radians(ay))) ) + math.radians(longa) )* (180/math.pi)
    return (ax, ay, x0, y0, x1, y1, x3, y3)

#=====================================================================
# 	MAKE A SLAB Stencil
#=====================================================================
def mk_slab_stencil( dict, xy_tmp, current_depth ):

    # parameters
    stencil_background = dict['stencil_background']
    stencil_radius = dict['stencil_radius']
    stencil_smooth = dict['stencil_smooth']
    layer_km = dict['layer_km']
    spacing_bkg_pts = dict['spacing_bkg_pts']
    spacing_slab_pts = dict['spacing_slab_pts']
    stencil_max = dict['stencil_max']
    stencil_shift = dict['stencil_shift_degs']
    FLAT_SLAB = dict['FLAT_SLAB']
    flat_slab_buoyancy = dict['flat_slab_buoyancy']
    fssd = dict['flat_slab_stencil_depth']
    N_slab_pts = dict['N_slab_pts']

    OLD = open( xy_tmp )
    lines = OLD.readlines()
    OLD.close()

    xyz_file = "tmp_stencil.xyz"
    cmd = "rm -f %s" % xyz_file
    os.system(cmd)
    XYZF = open( xyz_file, "w" )

    startval = -0.5*((N_slab_pts-1)*spacing_slab_pts)
    d_p_degrees = [startval+ii*spacing_slab_pts for ii in range(N_slab_pts)]
    d_p = [abs(ii*(110.0)) for ii in d_p_degrees] # abs value in km

    # since width of stencil symmetrical w.r.t. trench assume over_riding
    zvalue=-999.
    m=0

    for line in lines:
        c1 = line[0]
        if c1 == dict['gmt_char']:
            m=0
            #over_riding plate in subduction zone
            over_riding = None
            if len(line) >= 3:
                over_riding = line[2]
        if c1 != dict['gmt_char']:
            m+=1
            if m > 2:
                flat2=flat1 
                flon2=flon1 
                zvalue2=zvalue1 
            if m > 1:
                flat1=flat 
                flon1=flon 
                zvalue1=zvalue 
            lon, lat, value =line.split()
            flat=float(lat)
            flon=float(lon)

            if flon < 0.0:
                flon=flon+360.0
            if m > 2:
                dx=flon-flon2
                dy=flat-flat2
                for ii in range( N_slab_pts ):
                    # shift the stencil toward the over-riding plate
                    # compensates for position of the dipping shift slab
                    dist2 = stencil_shift + d_p_degrees[ii]
                    flon_new,flat_new = new_point(flon1,flat1,dx,dy,dist2,over_riding)
                    dist3 = math.sqrt( (d_p[ii]*d_p[ii]) + (current_depth*current_depth))
                    hd = current_depth/(d_p[ii]+0.00001)
                    cat = 1.0/math.sqrt(1.0+hd*hd) #cos(arctan(hd))
                    sat = math.sqrt(hd*hd)*cat #sin(arctan(hd))
                    a = 5.0*stencil_radius
                    b = stencil_radius
                    # ellipse in polar coordinates
                    gamma1 = a*b/math.sqrt( b*b*cat*cat + a*a*sat*sat )
                    a = 20*stencil_smooth
                    b = stencil_smooth
                    gamma2 = a*b/math.sqrt( b*b*cat*cat + a*a*sat*sat )
                    stencil_value = (1.0-math.tanh((dist3-gamma1)/gamma2))/2.00
                    if flon_new < 0.0:
                        flon_new=flon_new+360.0
                    if flon_new < 360.0:
                        XYZF.write("%g   %g   %g\n" % (flon_new,flat_new,stencil_value) )

    # additional stencil for flat slab (polygon)
    if FLAT_SLAB and flat_slab_buoyancy and current_depth < fssd:
        FLAT = open(dict['flat_slab_age_depth_file'])
        lines = FLAT.readlines()
        FLAT.close()
        for line in lines:
            lon, lat, value_a,value_d = line.split()
            XYZF.write("%s   %s   %g\n" % (lon,lat,stencil_max) )

    XYZF.close()

    # create a uniformly spaced background with zback
    if spacing_bkg_pts > 0:
        xyz_file_2="tmp_stencil_2.xyz"
        cmd="rm -f %s" % xyz_file_2
        os.system(cmd)
        XYZF=open(xyz_file_2,"w")
        flon=0.
        while flon <=360.:
            flat=-89.
            while flat <= 89.0:
                XYZF.write("%g  %g  %g\n" % (flon,flat,stencil_background))
                flat+= 2.0*spacing_bkg_pts*random.random()
            flon+= 2.0*spacing_bkg_pts*random.random()
    XYZF.close()

    xyz_file_3="tmp_stencil_3.xyz"
    cmd="rm -f %s" % xyz_file_3
    os.system(cmd)
    cmd = "cat %s %s > %s" % (xyz_file,xyz_file_2,xyz_file_3)
    os.system(cmd)
    cmd = "rm -f %s" % (xyz_file_2)
    os.system(cmd)

    return xyz_file_3

#=====================================================================
# 	MAKE A PARALLEL SLAB
#=====================================================================
def mk_parallel_slab(dict, xy_tmp, current_depth, advection):

    # parameters from dictionary
    radius_of_curvature = float(dict['radius_of_curvature'])
    T_mantle = float(dict['temperature_mantle'])
    T_min = float(dict['temperature_min'])
    age_min = float(dict['lith_age_min'])
    scalet = float(dict['scalet'])
    thermal_age_max = float(dict['thermal_age_max'])
    kappa = float(dict['thermdiff'])
    spacing_bkg_pts = dict['spacing_bkg_pts']
    spacing_slab_pts = dict['spacing_slab_pts']
    N_slab_pts = dict['N_slab_pts']

    Myr2s = (1.0e06)*(3.15e07) # Millions of years to seconds
    scaling = Myr2s*kappa

    OLD = open(xy_tmp)
    lines = OLD.readlines()
    OLD.close()

    xyz_file = "tmp.xyz"
    cmd = "rm -f %s" % xyz_file
    os.system(cmd)
    XYZF = open(xyz_file,"w")

    startval = -0.5*((N_slab_pts-1)*spacing_slab_pts)
    d_p_degrees = [startval+ii*spacing_slab_pts for ii in range(N_slab_pts)]
    d_p = [abs(ii*(110.0*1000.0)) for ii in d_p_degrees] # abs value in m

    if verbose: print(dt.now(), 'd_p_degrees',d_p_degrees)
    if verbose: print(dt.now(), 'advection',advection)
    if verbose: print(dt.now(), 'd_p',d_p)

    zvalue=-999.
    m=0

    for line in lines:
        c1 = line[0]
        if c1 == dict['gmt_char']:
            m=0
            line_segments = line.split(' ')
            slab_depth = float(line_segments[1].lstrip('DEPTH=') )
            slab_dip = float(line_segments[2].lstrip('DIP=') )
            start_depth = float(line_segments[3].lstrip('START_DEPTH=') )
            slab_dip = math.radians(slab_dip)
            corrected_depth = current_depth-start_depth
            dist = curving_slab(corrected_depth,radius_of_curvature,slab_dip)
            if current_depth > 660.0:  #make slabs vertical in the Lower mantle
                corrected_depth_1 = 660-start_depth
                dist = curving_slab(corrected_depth_1,radius_of_curvature,slab_dip)
            # Shift the position of the slab a fraction average thermal
            # thickness in direction of the subducting plate
            dist = (dist-60)/110.0

            #over_riding plate in subduction zone
            over_riding = None
            if len(line) >= 3:
                over_riding = line[2]
        if c1 != dict['gmt_char'] and current_depth <= slab_depth and current_depth >= start_depth:
            m+=1
            if m > 2:
                flat2 = flat1 
                flon2 = flon1 
                zvalue2 = zvalue1 
            if m > 1:
                flat1 = flat 
                flon1 = flon 
                zvalue1 = zvalue 
            lon, lat, value = line.split()
            flat = float(lat)
            flon = float(lon)
            zvalue = float(value)
            age = zvalue

            if age < age_min: age = age_min
            if age > thermal_age_max: age = thermal_age_max

            dd = 1.0/(2.0*math.sqrt(age*scaling))

            # 1/2 because a bl is created on each side of the slab
            # 1/sin(dip) to conserve down-dip buoyancy
            # (T-Mantle-T_min) for correct temperature drop (not necessarily 1)
            slab_temp_max = (T_mantle-T_min) / (2*math.sin(slab_dip))

            if flon < 0.0:
                flon = flon+360.0
            if m > 2:
                dx = flon-flon2
                dy = flat-flat2
                for ii in range(N_slab_pts):
                    slab_temp = T_mantle-slab_temp_max*(1.0-Thermal_Utilities.erf( dd*d_p[ii] ))

                    # prevent overprinting of pre-existing slabs by only exporting temperatures
                    # that are less than T_mantle by some small amount (hard-coded here as
                    # 0.05 non-dimensional temperature)
                    if slab_temp <= T_mantle-0.05:
                        dist2 = dist + advection*d_p_degrees[ii]
                        
                        flon_new,flat_new = new_point(flon1,flat1,dx,dy,dist2,over_riding)
                        if flon_new < 0.0:
                            flon_new = flon_new+360.0
                        if flon_new < 360.0:
                            XYZF.write("%g   %g   %g\n" % (flon_new,flat_new,slab_temp) )

    XYZF.close()

    # create a uniformly spaced background with zback
    if spacing_bkg_pts > 0:
        xyz_file_2 = "tmp_2.xyz"
        cmd = "rm -f %s" % xyz_file_2
        os.system(cmd)
        XYZF = open(xyz_file_2,"w")
        flon = 0.
        while flon <= 360.:
            flat = -89.
            while flat <= 89.0:
                XYZF.write("%g  %g  %g\n" % (flon,flat,T_mantle))
                flat += 2.0*spacing_bkg_pts*random.random()
            flon += 2.0*spacing_bkg_pts*random.random()
    XYZF.close()

    xyz_file_3 = "tmp_3.xyz"
    cmd = "rm -f %s" % xyz_file_3
    os.system(cmd)
    cmd = "cat %s %s > %s" % (xyz_file,xyz_file_2,xyz_file_3)
    os.system(cmd)
    cmd = "rm -f %s" % (xyz_file_2)
    os.system(cmd)

    return xyz_file_3

#=====================================================================
# 	MAKE A FLAT SLAB AGE FILE
#=====================================================================
def mk_flat_slab_age_depth_file( dict ):

    if verbose: print(dt.now(), 'mk_flat_slab_age_depth_file:')

    # parameters
    flat_slab_file = dict['flat_slab_file']
    sub_dir = dict['sub_dir']
    slab_dir = dict['slab_dir']
    sub_file = dict['sub_file']
    leading_edge_file = dict['slab_file']
    sub_base_file = dict['sub_base_file']
    age = dict['age']
    grd_res = dict['grd_res']
    bounds = dict['bounds']
    tension = dict['tension']
    flat_slab_region = dict['flat_slab_region']
    afile_1 = dict['afile_1']

    if verbose: print(dt.now(), 'sub_file=',sub_file)
    if verbose: print(dt.now(), 'leading_edge_file=',leading_edge_file)
    if verbose: print(dt.now(), 'sub_base_file=',sub_base_file)

    # clean up
    cmd = "rm -f flat_outline*.xy flat_slab_depth*.grd"
    os.system( cmd )

    slab_depth_file="slab_depth.xyz"
    OUT=open(slab_depth_file,"w")
    LEADING = open( leading_edge_file )

    # depths for the leading edge
    leading_edge_max=0.0
    while 1:
        line=LEADING.readline()
        if len(line)>1:
            c1 = line[0]
            if c1 == dict['gmt_char']:
                header_data = {}
                header_data = get_header_GMT_xy_file_dictionary( line )
                fld = header_data.get('slabFlatLyingDepth', 'Unknown') 
            else:
                lon, lat = line.split()
                flon=float(lon)
                if flon<0.0:
                    flon=360.0+flon
                if fld != 'Unknown':
                    ffld=float(fld)
                    if ffld > leading_edge_max:
                        leading_edge_max=ffld
                    lon, lat = line.split()
                    OUT.write("%g %s %s\n" % (flon,lat,fld) )
        else:
            break             
    LEADING.close()

    # not sure if this part does anything.  Technically it writes
    # zeros to OUT but this may not be necessary to compute
    # the flat slab depth correctly - DJB 01/21/13
    # depths (set to 0) for the subduction zone at trench
    SUB=open(sub_file)
    while 1:
        line=SUB.readline()
        if len(line)>1:
            c1 = line[0]
            if c1 == dict['gmt_char']:
                header_data = {}
                header_data = get_header_GMT_xy_file_dictionary( line )
                szd = header_data.get('subductionZoneDepth', 'Unknown') 
                if szd == 'Unknown':
                    fszd=0.0
                else:
                    fszd=float(szd)
                if fszd > leading_edge_max:
                    fszd=leading_edge_max
                #set to zero
                fszd=0.0
            else:
                lon, lat = line.split()
                flon=float(lon)
                if flon<0.0:
                    flon=360.0+flon
                OUT.write("%g %s %g\n" % (flon,lat,fszd) )
        else:
            break             
    SUB.close()

    # depths for the base of subduction zone i.e., where
    # the normal slab turns into the flat lying part
    BASE=open(sub_base_file)
    while 1:
        line=BASE.readline()
        if len(line)>1:
            c1 = line[0]
            if c1 == dict['gmt_char']:
                header_data = {}
                header_data = get_header_GMT_xy_file_dictionary( line )
                szd = header_data.get('subductionZoneDepth', 'Unknown') 
                if szd == 'Unknown':
                    fszd = dict['flat_slab_sub_depth']
                else:
                    fszd = float(szd)
            else:
                lon, lat = line.split()
                flon=float(lon)
                if flon<0.0:
                    flon=360.0+flon
                OUT.write("%g %s %g\n" % (flon,lat,fszd) )
        else:
            break             
    BASE.close()


    OUT.close()

    # grd file of slab depth
    grd_min = 0.0
    # this will cut off some of the deep slabs
    grd_max = leading_edge_max
    grd_res_tmp = 0.1
    grd_slab_depth = GMT_Utilities.mk_grd(slab_depth_file,bounds,grd_res_tmp,tension,grd_min,grd_max)

    flat_slab_new = GMT_Utilities.toggle_shift_xy( flat_slab_file, "S3" )

    # make mask of flat slab
    cmd="gmt grdmask %s -Gflat_slab_mask.grd -I0.1 -R%s -NNaN/0.0/1.0 -m -V" % (flat_slab_new,bounds)
    if verbose: print(dt.now(), cmd)
    os.system(cmd)

    cmd="gmt grdmath %s flat_slab_mask.grd MUL = flat_tmp.grd" % afile_1
    if verbose: print(dt.now(), cmd)
    os.system(cmd)

    cmd="gmt grdmath %s flat_slab_mask.grd MUL = flat_depth_tmp.grd" % grd_slab_depth
    if verbose: print(dt.now(), cmd)
    os.system(cmd)


    # these grdsample commands have a large impact on the overall runtime
    # of Temp_history_gen.py.  Reduced to 0.25 by DJB 07/05/12
    resample_res = 0.25*grd_res
    #resample_res=0.05*grd_res

    #Resample the grd files (both the age and the depth) on a mesh slightly higher res than grd_res
    cmd="gmt grdsample flat_tmp.grd -Gflat_slab_age.grd -I%g" % resample_res 
    if verbose: print(dt.now(), cmd) 
    os.system(cmd)
    cmd="gmt grdsample flat_depth_tmp.grd -Gflat_slab_depth.grd -I%g" % resample_res 
    if verbose: print(dt.now(), cmd) 
    os.system(cmd)


    #============================================================
    # For debugging
    proj_z = 'M2.5'
    bounds_z = flat_slab_region
    cmd="gmt makecpt -Crainbow -I -D -T50/150/10 > depth.cpt"
    os.system(cmd)
    cmd="gmt makecpt -Crainbow -I -D -T0/280/10 > age.cpt"
    os.system(cmd)
    fs_ps = "flat_slab_depth_age%d.ps" % age


    # First plot an image of the Depth of the flat slab portion
    cmd="gmt grdimage flat_slab_depth.grd -Cdepth.cpt -R%s -J%s -B10 -X1.0 -Y3.0 -P -K  > %s" % (bounds_z,proj_z,fs_ps)
    print(cmd)
    os.system(cmd)
    cmd="gmt psxy %s -B -R%s -W3/0 -J%s -O -K -m -V >> %s" % (flat_slab_new,bounds_z,proj_z,fs_ps)
    print(cmd)
    os.system(cmd)
    sub_sR="%s/topology_subduction_boundaries_sR_%0.2fMa.xy" % (sub_dir,age)
    cmd="gmt psxy %(sub_sR)s -R%(bounds_z)s -J%(proj_z)s -B -W6.0 -Sf0.2/0.07rt -G0 -X0.0 -Y0.0 -m -O -K >> %(fs_ps)s" % vars()
    print(cmd)
    os.system(cmd)
    sub_sL="%s/topology_subduction_boundaries_sL_%0.2fMa.xy" % (sub_dir,age)
    cmd="gmt psxy %(sub_sL)s -R%(bounds_z)s -J%(proj_z)s -B -W6.0 -Sf0.2/0.07lt -G0 -X0.0 -Y0.0 -m -O -K  >> %(fs_ps)s" % vars()
    print(cmd)
    os.system(cmd)
    slab_sL="%s/topology_slab_edges_leading_sL_%0.2fMa.xy" % (slab_dir,age)
    cmd="gmt psxy %(slab_sL)s -R%(bounds_z)s -J%(proj_z)s -B -W6.0 -Sf0.2/0.07lt -G0 -X0.0 -Y0.0 -m -O -K >> %(fs_ps)s" % vars()
    print(cmd)
    os.system(cmd)
    cmd="gmt psscale -D1.0/-0.5/2.0/0.25h -B25:'Depth (km)': -Cdepth.cpt -O -K  >> %(fs_ps)s" % vars()
    print(cmd)
    os.system(cmd)
    # MG doesn't know whythis was added:
    #cmd="gmt psxy %(sub_base_file)s -R%(bounds_z)s -J%(proj_z)s -B -W6.0/255/0/0 -X0.0 -Y0.0 -M -O -K >> %(fs_ps)s" % vars()
    #print cmd 
    #os.system(cmd)

    # Then plot an image of the age of the flat slab portion
    cmd="gmt grdimage flat_slab_age.grd -Cage.cpt -R%s -J%s -B10 -X3.5 -Y0.0 -P -O -K  >> %s" % (bounds_z,proj_z,fs_ps)
    print(cmd)
    os.system(cmd)
    cmd="gmt psxy %s -B -R%s -W3/0 -J%s -O -K -m -V >> %s" % (flat_slab_new,bounds_z,proj_z,fs_ps)
    print(cmd)
    os.system(cmd)
    sub_sR="%s/topology_subduction_boundaries_sR_%0.2fMa.xy" % (sub_dir,age)
    cmd="gmt psxy %(sub_sR)s -R%(bounds_z)s -J%(proj_z)s -B -W6.0 -Sf0.2/0.07rt -G0 -X0.0 -Y0.0 -m -O -K >> %(fs_ps)s" % vars()
    print(cmd)
    os.system(cmd)
    sub_sL="%s/topology_subduction_boundaries_sL_%0.2fMa.xy" % (sub_dir,age)
    cmd="gmt psxy %(sub_sL)s -R%(bounds_z)s -J%(proj_z)s -B -W6.0 -Sf0.2/0.07lt -G0 -X0.0 -Y0.0 -m -O -K  >> %(fs_ps)s" % vars()
    print(cmd)
    os.system(cmd)
    slab_sL="%s/topology_slab_edges_leading_sL_%0.2fMa.xy" % (slab_dir,age)
    cmd="gmt psxy %(slab_sL)s -R%(bounds_z)s -J%(proj_z)s -B -W6.0 -Sf0.2/0.07lt -G0 -X0.0 -Y0.0 -m -O -K >> %(fs_ps)s" % vars()
    print(cmd)
    os.system(cmd)
    cmd="gmt psscale -D1.0/-0.5/2.0/0.25h -B50:'Age (Ma)': -Cage.cpt -O >> %(fs_ps)s" % vars()
    print(cmd)
    os.system(cmd)

    # End debugging
    #============================================================

    flat_slab_age_file = "flat_slab_age.xyz"
    cmd="gmt grd2xyz flat_slab_age.grd -S > %s" % flat_slab_age_file
    if verbose: print(dt.now(), cmd)
    os.system(cmd)
    flat_slab_depth_file = "flat_slab_depth.xyz"
    cmd="gmt grd2xyz flat_slab_depth.grd -S > %s" % flat_slab_depth_file
    if verbose: print(dt.now(), cmd)
    os.system(cmd)
    AGE=open(flat_slab_age_file)
    DEPTH=open(flat_slab_depth_file)
    flat_slab_age_depth_file = "flat_slab_age_depth.xy"
    AD=open(flat_slab_age_depth_file,"w")
    while 1:
        line_a=AGE.readline()
        line_d=DEPTH.readline()
        if(line_a):
            lon_a, lat_a, value_a = line_a.split()
            lon_d, lat_d, value_d = line_d.split()
            if (lon_a != lon_d) or (lat_a != lat_d):
                print('ERROR -- mk_flat_slab_age_file')
                print('incompatible values in age and depth grd files')
                sys.exit(0)
            AD.write("%s %s %s %s\n" % (lon_a,lat_a,value_a,value_d))
        else:
            break

    AD.close()

    return flat_slab_age_depth_file

#=====================================================================
# 	MAKE A FLAT SLAB
#=====================================================================
def mk_flat_slab( dict, xyz_file_in, depth ):

    T_mantle = float(dict['temperature_mantle'])
    T_min = float(dict['temperature_min'])
    age_min = float(dict['lith_age_min'])
    scalet = float(dict['scalet'])
    thermal_age_max = float(dict['thermal_age_max'])
    kappa = float(dict['thermdiff'])
    layer_km = dict['layer_km']

    Myr2s = (1.0e06)*(3.15e07) # Millions of years to seconds
    scaling = Myr2s*kappa

    FSAF = open(dict['flat_slab_age_depth_file'])
    lines = FSAF.readlines()
    FSAF.close()
    xyz_file = 'flat%f.xyz' % depth
    cmd = 'rm -f %s' % xyz_file
    os.system(cmd)
    XYZF = open(xyz_file,"w")

    # same as expression for mk_parallel_slab, except no need to consider
    # dip of plate (since in this case it is flat)
    # divide by two because a boundary layer is created either side of the
    # center line.
    slab_temp_max = (T_mantle-T_min)/2

    for line in lines:
        c1 = line[0]
        if c1 != dict['gmt_char']:
            lon, lat, value_a, value_d = line.split()
            age = float(value_a)

            # minimum and maximum age
            if age < age_min: age = age_min
            if age > thermal_age_max: age = thermal_age_max
            dd = 1.0/(2.0*math.sqrt(age*scaling))
            slab_depth = float(value_d)
            # dist is (absolute) distance away from the center of the
            # flat slab in meters
            dist = abs(depth-slab_depth)*1000.0 # km to m

            # same as mk_parallel_slab
            slab_temp = T_mantle-slab_temp_max*(1.0-Thermal_Utilities.erf( dd*dist ))
            XYZF.write("%s   %s   %g\n" % (lon,lat,slab_temp) )

    XYZF.close()

    xyz_file_4="tmp_4.xyz"
    cmd="rm -f %s" % xyz_file_4
    os.system(cmd)
    cmd = "cat %s %s > %s" % (xyz_file_in,xyz_file,xyz_file_4)
    os.system(cmd)
    print(xyz_file_in,xyz_file,xyz_file_4)

    return xyz_file_4
#=====================================================================
def mk_parallel_region(xy_tmp,spacing,grd_res,width,region_value):

    OLD=open(xy_tmp)
    xyz_file="tmp.xyz"
    cmd="rm -f %s" % xyz_file
    os.system(cmd)
    XYZF=open(xyz_file,"w")

    d_p_degrees=[]
    print('width=',width)
    print('grd_res=',grd_res)
    N_region_pts = int(width/grd_res)
    print('N_region_pts=',N_region_pts)
    value=0.0
    ii=0
    while ii<N_region_pts:
        # spacing is degrees
        d_p_degrees.append(value)
        value+=grd_res
        ii+=1
   
    print('d_p_degrees',d_p_degrees)

    zvalue=-999.
    background_value=0.0

    gmt_char = '>'
    m=0
    while 1:
        line=OLD.readline()
        if(line):
            c1 = line[0]
            if c1 == '>':
                m=0
                #NEW.write("%s" % line)
                #over_riding plate in subduction zone
                over_riding = None
                if len(line) >= 3:
                    over_riding = line[2]
            if c1 != '#'  and c1 != '>':
                m+=1
                if m > 2:
                    flat2=flat1 
                    flon2=flon1 
                    zvalue2=zvalue1 
                if m > 1:
                    flat1=flat 
                    flon1=flon 
                    zvalue1=zvalue 
                lon, lat, value =line.split()
                flat=float(lat)
                flon=float(lon)
                zvalue=float(value)

                if flon < 0.0:
                    flon=flon+360.0
                if m > 2:
                    dx=flon-flon2
                    dy=flat-flat2
                    ii=0
                    while ii<N_region_pts:
                        dist2 = d_p_degrees[ii]
                        flon_new,flat_new = new_point(flon1,flat1,dx,dy,dist2,over_riding)
                        if flon_new < 0.0:
                            flon_new=flon_new+360.0
                        if flon_new < 360.0:
                            XYZF.write("%g   %g   %g\n" % (flon_new,flat_new,region_value) )
                        ii+=1
        else:
            break             

    OLD.close()

    XYZF.close()

    # create a uniformly spaced background with zback
    if spacing > 0:
        xyz_file_2="tmp_2.xyz"
        cmd="rm -f %s" % xyz_file_2
        os.system(cmd)
        XYZF=open(xyz_file_2,"w")
        #XYZF.write(">\n")
        flon=0.
        while flon <=360.:
            flat=-89.
            while flat <= 89.0:
                XYZF.write("%g  %g  %g\n" % (flon,flat,background_value))
                flat+=spacing
            flon+=spacing
    XYZF.close()

    cmd = "cat %s %s >> %s" % (xyz_file,xyz_file_2,xyz_file)
    os.system(cmd)
    cmd = "rm -f %s" % (xyz_file_2)
    os.system(cmd)

    return xyz_file

#=====================================================================
def exchange_coord(coord_file,z_file,prefix):

    CF=open(coord_file)
    ZF=open(z_file)
    new_name = "%s.xy" % prefix
    cmd="rm -f %s" % new_name
    os.system(cmd)
    NF=open(new_name,"w")

    while 1:
        cline=CF.readline()
        #print "cline:",cline
        zline=ZF.readline()
        #print "zline:",zline
        if(cline):
            c1 = cline[0]
            if c1 == '>':
                NF.write("%s" % cline)
            if c1 != '#'  and c1 != '>':
                clon, clat, cvalue =cline.split()
                zlon, zlat, zvalue =zline.split()
                NF.write("%s  %s  %s\n" % (clon,clat,zvalue) )
        else:
            break             

    CF.close()
    ZF.close()
    NF.close()

    return new_name
#=====================================================================
def mk_smooth_line(xy_tmp,k):

    OLD=open(xy_tmp)
    pname = "smooth_%d.xy" % k
    cmd="rm -f %s" % pname
    os.system(cmd)
    NEW=open(pname,"w")

    m=0
    while 1:
        line=OLD.readline()
        if(line):
            c1 = line[0]
            if c1 == '>':
                m=0
                NEW.write("%s" % line)
            if c1 != '#'  and c1 != '>':
                m+=1
                if m > 2:
                    flat2=flat1 
                    flon2=flon1 
                    zvalue2=zvalue1 
                if m > 1:
                    flat1=flat 
                    flon1=flon 
                    zvalue1=zvalue 
                lon, lat, value =line.split()
                flat=float(lat)
                flon=float(lon)
                zvalue=float(value)
                if flon < 0.0:
                    flon=flon+360.0
                if m > 2:
                    flat_new=0.25*flat + 0.5*flat1 + 0.25*flat2
                    flon_new=0.25*flon + 0.5*flon1 + 0.25*flon2
                    zvalue_new=0.25*zvalue + 0.5*zvalue1 + 0.25*zvalue2
                    if flon_new > 180.0:
                        flon_new=flon_new-360.0
                    NEW.write("%g   %g   %g\n" % (flon_new,flat_new,zvalue_new) )
        else:
            break             

    OLD.close()
    NEW.close()

    return pname
#
#=====================================================================
def find_value_on_line(xy_tmp,grdfile):

    OLD=open(xy_tmp)
    pname = "value%f.xy" % time.time()
    cmd="rm -f %s" % pname
    os.system(cmd)
    NEW=open(pname,"w")

    tmp_in_name = "in_track.xy"
    tmp_out_name = "out_track.xy"

    gmt_char = '>'
    n=0
    while 1:
        line=OLD.readline()
        if(line):
            c1 = line[0]
            if c1 == '>':
                if n > 0:
                   T_IN.close() 
                   cmd="gmt grdtrack %s -G%s > %s" % (tmp_in_name,grdfile,tmp_out_name)
                   os.system(cmd)
                   T_OUT=open(tmp_out_name)
                   while 1:
                       line2=T_OUT.readline()
                       if(line2):
                           lon, lat, value =line2.split()
                           flat=float(lat)
                           flon=float(lon)
                           zvalue=float(value)
                           if flon > 180.0:
                               flon=flon-360.0
                           NEW.write("%g   %g   %g\n" % (flon,flat,zvalue))
                       else:
                           break             
                   T_OUT.close() 
                NEW.write("%s" % line)
                T_IN=open(tmp_in_name,"w")
            if c1 != '#'  and c1 != '>':
                n+=1
                lon, lat, value =line.split()
                flat=float(lat)
                flon=float(lon)
                if flon < 0.0:
                    flon=flon+360.0
                T_IN.write("%g   %g\n" % (flon,flat) )
        else:
            break             

    OLD.close()

    # still need to read out last track:
    T_IN.close() 
    cmd="gmt grdtrack %s -G%s > %s" % (tmp_in_name,grdfile,tmp_out_name)
    os.system(cmd)
    T_OUT=open(tmp_out_name)
    while 1:
        line2=T_OUT.readline()
        if(line2):
            lon, lat, value =line2.split()
            flat=float(lat)
            flon=float(lon)
            zvalue=float(value)
            if flon > 180.0:
                flon=flon-360.0
            NEW.write("%g   %g   %g\n" % (flon,flat,zvalue))
        else:
            break             
    T_OUT.close() 

    NEW.close()

    return pname
#
#=====================================================================
# 
def new_point(x,y,dx,dy,h,over):
    import math


    if dx == 0.0:
        dx = 0.0001
    m=dy/dx
    if m == 0.0:
       m = 0.0001
    m2=-1.0/m
    #Q, trig quadrant
    if dx >= 0.0 and dy >= 0.0:
        Q='I'
    elif dx < 0.0 and dy > 0.0:
        Q='II'
    elif dx < 0.0 and dy <= 0.0:
        Q='III'
    else:
        Q='IV'
    polarity=0

    if over != None:
        if over == 'R':
            if Q == 'I' or Q == 'II':        
                polarity=1
            elif Q == 'III' or Q == 'IV':        
                polarity=-1
        elif over == 'L':
            if Q == 'I' or Q == 'II':        
                polarity=-1
            elif Q == 'III' or Q == 'IV':        
                polarity=1


    x2=x+polarity*h*math.cos(math.atan(m2))/math.cos(d2r*y)
    y2=y+polarity*h*math.sin(math.atan(m2)) 

    return x2, y2
#=====================================================================
# 
def curving_slab(d,radius,dip):
    #Dip is angle in radians
    d_c = radius*(1.0 - math.cos(dip))

    # Two possibilities, while shallow follows circle
    # if deeper, follows a line at a constant dip that
    # tangents the circle

    if d <= 0.0:
        dist=0.0

    if d > 0.0 and d <= d_c:
        y = radius - d
        dist = math.sqrt( radius*radius - y*y)

    elif d > d_c:
        x_c = radius*math.sin(dip)
        y_prime=d-d_c
        x_prime=y_prime/math.tan(dip)
        dist = x_c + x_prime

    return dist
#=====================================================================
# 	MAKE A SMOOTH SLAB
#=====================================================================
#-def mk_smooth_slab(xy_tmp,current_depth,radius_of_curvature,factor,advection,spacing,T_mantle,age_min,scalet,layer_km):
def mk_smooth_slab(xy_tmp,spacing,T_mantle,age_min,scalet,layer_km):

    print('inside mk_smooth_slab')

    scalet2=(layer_km*1e3*layer_km*1e3)/scalet
    OLD=open(xy_tmp)
    xyz_file="tmp.xyz"
    cmd="rm -f %s" % xyz_file
    os.system(cmd)
    XYZF=open(xyz_file,"w")

    Myr2s=(1.0e06)*(3.15e07) # Millions of years to seconds
    kappa=1.0e-06
    scaling=Myr2s*kappa
    print("scaling")
    print(scaling)
    N_slab_pts=31
    d_p_degrees=[]
    d_p=[]
    ii=0
    value=-1.5*spacing
    while ii<N_slab_pts:
        # spacing is degrees, convert to meters
        value = value + 0.1*spacing
        d_p_degrees.append(value)
        value2=abs(value*(110.*1000.0))     #absolute value in meters
        d_p.append(value2) 
        ii+=1
   
    #print 'd_p_degrees',d_p_degrees
    #print 'd_p',d_p

    zvalue=-999.
    gmt_char = '>'
    m=0
    while 1:
        line=OLD.readline()
        if(line):
            c1 = line[0]
            if c1 != '>':
                m+=1
                if m > 2:
                    flat2=flat1 
                    flon2=flon1 
                    zvalue2=zvalue1 
                if m > 1:
                    flat1=flat 
                    flon1=flon 
                    zvalue1=zvalue 
                lon, lat, value =line.split()
                flat=float(lat)
                flon=float(lon)
                zvalue=float(value)
                age=zvalue
                if age < age_min:
                    age=age_min
                #print "age"
                #print age
                dd=1.0/(2.0*math.sqrt(age*scaling))
                #slab_temp_max=0.5 # by definition 1/2, as a bl is created
                slab_temp_max=T_mantle # by definition 1/2, as a bl is created
                # on each side of the slab 
                #factor is a slab broadening that conserves buoyancy
                #slab_temp_max=T_mantle - (T_mantle-slab_temp_max)/factor
                #turned this part off because afvective thickening doesn't 
                #conserve buoyancy

                if flon < 0.0:
                    flon=flon+360.0
                if m > 2:
                    dx=flon-flon2
                    dy=flat-flat2
                    ii=0
                    while ii<N_slab_pts:
                        slab_temp=T_mantle-slab_temp_max*(1.0-Thermal_Utilities.erf( dd*d_p[ii] ))
                        #dist2 = dist + factor*advection*d_p_degrees[ii]
                        dist2 = d_p_degrees[ii]
                        #over_riding='none'
                        over_riding='R'
                        flon_new,flat_new = new_point(flon1,flat1,dx,dy,dist2,over_riding)
                        if flon_new < 0.0:
                            flon_new=flon_new+360.0
                        if flon_new < 360.0:
                            XYZF.write("%g   %g   %g\n" % (flon_new,flat_new,slab_temp) )
                            #XY.write("%g   %g\n" % (flon_new,flat_new) )
                        ii+=1
        else:
            break             

    OLD.close()

    XYZF.close()

    # create a uniformly spaced background with zback
    if spacing > 0:
        xyz_file_2="tmp_2.xyz"
        cmd="rm -f %s" % xyz_file_2
        os.system(cmd)
        XYZF=open(xyz_file_2,"w")
        #XYZF.write(">\n")
        flon=0.
        while flon <=360.:
            flat=-89.
            while flat <= 89.0:
                XYZF.write("%g  %g  %g\n" % (flon,flat,T_mantle))
                flat+= 2.0*spacing*random.random()
            flon+= 2.0*spacing*random.random()
    XYZF.close()
    #XY.close()

    xyz_file_3="tmp_3.xyz"
    cmd="rm -f %s" % xyz_file_3
    os.system(cmd)
    cmd = "cat %s %s > %s" % (xyz_file,xyz_file_2,xyz_file_3)
    os.system(cmd)
    cmd = "rm -f %s" % (xyz_file_2)
    os.system(cmd)

    return xyz_file_3
#=====================================================================
# 	RETURN A DIC FROM THE FIRST LINE OF A GMT FILE
#=====================================================================
#
def get_header_GMT_xy_file_dictionary( line ):
    '''Parse a gplates exported header line into a python dictionary.

    This function reads header lines of this type,
    ">sR # name: South America trench # ... # polygon: NAZ_003_000 # use_reverse: yes"
    and fills a dictionary with property/value pairs'''

    # dictionary to hold property value data
    dict = {}

    # list to hold property / value pairs from a split on '#' char
    pairs = []
    pairs = line.split('#')

    # check for missing data and just return the empty dictionary 
    if len(pairs) == 0:
        return dict

    # Specialized processing for first element from split 
    # (the first element lacks a ':' and only has a value )

    type = pairs.pop(0) # remove the first element from the list
    type = type.strip() # strip off trailing white space
    type = type.replace('>', '') # remove > char

    # add this prop/value pair to the dictionary using the key of 'type'
    dict['type'] = type

    # continue processing the rest of prop/value pairs

    for item in pairs:

        # split on the ':' character 
        list = item.split(':')

        prop = list[0]
        prop = prop.strip() # remove white space
        prop = prop.lstrip() # remove white space

        value = list[1]
        value = value.strip() # remove white space
        value = value.lstrip() # remove white space

        dict[prop] = value

    # now return the dictionary for the requested property,
    return dict

#=====================================================================
def ck_buoy(age,grd_file,age_grd_file,sub_dir,mantle_temp,layer_km,scalet,sbf):
    
    print('grd_file',grd_file)
    print('mantle_temp=',mantle_temp)

    CF=open(sbf)
    while 1:
        line=CF.readline()
        if(line):
            print('line',line)
            s1=line[0]
            print('s1',s1)
            if s1 == '>':    
                sa, snum=line.split(',')
                inage=int(sa.strip('>'))
                num=int(snum)
                if inage == age:
                    j=0
                    while j<num:
                        line=CF.readline()
                        print('inage',inage,' num=',num)
                        print('line',line)
                        start, middle,end,sdip =line.split(',')
                        print(start, middle,end,sdip)

                        slon0,slat0=middle.split('/')
                        lon1=float(slon0)-10.0
                        lon2=float(slon0)+10.0
                        lat1=float(slat0)-10.0
                        lat2=float(slat0)+10.0
                        # bounds for map
                        bounds="%f/%f/%f/%f" % (lon1,lon2,lat1,lat2)

                        slab_dip = float(sdip)
                        slab_dip = slab_dip*d2r
                        middle_loc="middle.xy"
                        middle_track="middle.xya"
                        ML=open(middle_loc,"w")
                        ML.write("%s  %s\n" % (slon0,slat0) )
                        ML.close()
                        cmd="gmt grdtrack %s -G%s > %s" % (middle_loc,age_grd_file,middle_track)
                        os.system(cmd)
                        ML=open(middle_track)
                        sd1,sd2,sage=ML.readline().split()
                        ML.close()
                        slab_age=float(sage)
                        print('slab_age',slab_age)

                        # sometimes the age grids have negative ages, and this causes the 
                        # code to crash.  Bug fix by Dan J. Bower.
                        if slab_age < 0: slab_age = 0.01

                        profile_file="profile1_%d.xyp" % j
                        track_file="track1_%d.xypT" % j
                        profile_file2="profile_%d.xy" % j
                        cmd="rm -f %s %s %s" % (profile_file,track_file,profile_file2)
                        os.system(cmd)

                        cmd="gmt project -C%s -E%s -Dg -G1 -Q > %s" % (start,end,profile_file)
                        print(cmd)
                        os.system(cmd)
                        cmd="gmt grdtrack %s -G%s > %s" % (profile_file,grd_file,track_file)
                        print(cmd)
                        os.system(cmd)
                        TF=open(track_file)
                        max_pts=0
                        while 1:
                            line=TF.readline()
                            if(line):
                                max_pts+=1
                            else:
                                break
                        TF.close()

                        xx1=range(max_pts)
                        temp1=range(max_pts)
                        TF=open(track_file)
                        OF=open(profile_file2,"w")
                        dist_max=0.0
                        n=0
                        while 1:
                            line=TF.readline()
                            if(line):
                                dum1,dum2, dist, stemp = line.split()
                                xx1[n]=float(dist)
                                temp1[n]=float(stemp)
                                if xx1[n] > dist_max:
                                    dist_max=xx1[n]
                                OF.write("%g  %g\n" % (xx1[n],temp1[n]) )
                                n+=1
                            else:
                                break

                        TF.close()
                        OF.close()

                        ET=open("etemp.xy","w")
                        f_int=0.0
                        e_int=0.0
                        i=0
                        for i in range(max_pts-1):
                            #Trapizoid rule
                            f1 = temp1[i]-mantle_temp 
                            f2 = temp1[i+1]-mantle_temp
                            # integral across temperature track
                            f_int = f_int + (xx1[i]-xx1[i+1])*(0.5*f1 + 0.5*f2)
                            edepth1 = xx1[i]/layer_km
                            edepth2 = xx1[i+1]/layer_km
                            e1 = Thermal_Utilities.expected_temp(edepth1,slab_age,scalet)
                            e1 *= mantle_temp
                            e2 = Thermal_Utilities.expected_temp(edepth2,slab_age,scalet)
                            e2 *= mantle_temp
                            ET.write("%g  %g\n" % (xx1[i],e1) )
                            e1 -= mantle_temp
                            e2 -= mantle_temp

                            # integral from age grid using half-space model
                            e_int = e_int + (xx1[i]-xx1[i+1])*(0.5*e1 + 0.5*e2)

                        ET.close()
                        abs_fint = math.fabs(f_int)
                        abs_eint = math.fabs(e_int)/math.sin(slab_dip)

                        expected_HS = 1.0*math.sqrt(slab_age/(math.pi*scalet) )*layer_km/math.sin(slab_dip)
                        error = int(round(abs_fint/expected_HS*100))
                        print('f_int=',abs_fint)
                        print('e_int=',abs_eint)
                        print('expected_HS=',expected_HS)
                        print('error=',error)

                        psfile_buoy = 'check_buoy_age%d_%d.ps' % (age,j)
                        cmd="gmt gmtset LABEL_FONT_SIZE 12"
                        map_info="-B5 -X1.0 -Y5.0"
                        proj="M2.5"
                        print(cmd)
                        os.system(cmd)

                        cmd="gmt grdimage %s -Ctemp.cpt -R%s -J%s %s -P -K > %s" % (grd_file,bounds,proj,map_info,psfile_buoy)
                        print(cmd)
                        os.system(cmd)
                        cmd="gmt psxy %s -R%s -J%s -W4/0 -X0.0 -Y0.0 -P -O -K >> %s" % (profile_file,bounds,proj,psfile_buoy)
                        print(cmd)
                        os.system(cmd)
                        cmd="gmt psxy %s -R%s -J%s -Sc0.1/0 -G0 -P -O -K >> %s" % (middle_loc,bounds,proj,psfile_buoy)
                        print(cmd)
                        os.system(cmd)
                        cmd="gmt grdimage %s -Cage.cpt -R -J -B -X4.0 -Y0.0 -P -O -K >> %s" % (age_grd_file,psfile_buoy)
                        print(cmd)
                        os.system(cmd)
#                        sub_sR="%s/Polygons.subduction_boundaries_sR.%d.xy" % (sub_dir,age)
                        sub_sR="%s/topology_subduction_boundaries_sR_%0.2fMa.xy" % (sub_dir,age)
                        cmd="gmt psxy %(sub_sR)s -R -J -W3.0/0 -Sf0.2/0.07rt -m -O -K >> %(psfile_buoy)s" % vars()
                        print(cmd)
                        os.system(cmd)
#                        sub_sL="%s/Polygons.subduction_boundaries_sL.%d.xy" % (sub_dir,age)
                        sub_sL="%s/topology_subduction_boundaries_sL_%0.2fMa.xy" % (sub_dir,age)
                        cmd="gmt psxy %(sub_sL)s -R -J -W3.0/0 -Sf0.2/0.07lt -m -O -K  >> %(psfile_buoy)s" % vars()
                        print(cmd)
                        os.system(cmd)
                        cmd="gmt psxy %s -R%s -J%s -Sc0.1 -G255 -P -O -K >> %s" % (middle_loc,bounds,proj,psfile_buoy)
                        print(cmd)
                        os.system(cmd)

                        ubound = mantle_temp+0.1
                        bounds_profile="0.0/%(dist_max)f/0.0/%(ubound)s" % vars()
                        #bounds_profile="0.0/2000/0.0/1.1"
                        cmd="gmt psxy %s -R%s -JX3.0/1.5 -B100f50:km:/a0.25f0.125:Temp:WeSn -W4/0 -P -X-3.5 -Y-2.5 -K -O >> %s" % (profile_file2,bounds_profile,psfile_buoy)
                        print(cmd)
                        os.system(cmd)
                        cmd="gmt psxy etemp.xy -R%s -J -W4/0/255/0 -P -X0.0 -Y0.0 -K -O >> %s" % (bounds_profile,psfile_buoy)
                        print(cmd)
                        os.system(cmd)

                        #label info
                        LAB = open('label.txt','w')
                        print("3.25 1.0 14 0 1 1 Slab Buoyancy = %.02f ND T-km" % (abs_fint), file=LAB)
                        print("3.25 0.75 14 0 1 1 HS Buoyancy = %.02f ND T-km" % (abs_eint), file=LAB)
                        print("3.25 0.5 14 0 1 1 HS Analytic = %.02f ND T-km" % (expected_HS), file=LAB)
                        print("3.25 0.25 14 0 1 1 Slab Buoyancy as percent = %d" % (error), file=LAB)
                        LAB.close()
                        # text label
                        cmd="gmt pstext label.txt -R0/8.5/0/11 -Jx1 -X0.0 -Y0.0 -O >> %(psfile_buoy)s" % vars()
                        os.system(cmd)

                        j+=1

        else:
            break

    CF.close()

    return
#=====================================================================

def get_strike(xyz_list,strike_list):

    m=0
    for coords in xyz_list:
        m+=1
        if m > 1:
            flat1=flat 
            flon1=flon 
        lon, lat, value =coords.split()
        flat=float(lat)
        flon=float(lon)
        if m > 1:
            dx=flon-flon1
            dy=flat-flat1
            if (dy == 0.0) and (dx > 0.0):
                strike = 90.0
            elif (dy == 0.0) and (dx <= 0.0):
                strike = 270.0
            else:
                strike = r2d*math.atan2(dx,dy)
                #if strike < 0.0:
                #    strike = 360.0+strike
            if m ==2:
                new_coord="%g %g %g\n" % (flon1,flat1,strike)
                strike_list.append(new_coord)
            new_coord="%s %s %g\n" % (lon,lat,strike)
            strike_list.append(new_coord)
    return

