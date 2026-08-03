#!/usr/bin/env python
#        #!/home/dli/epd/bin/python
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
# Last Update: Mike Gurnis, May 25, 2015
#
#=====================================================================

#import Core_GMT, GMT_Utilities, Mat_Utilities
import os, string, sys, math, time
#from obspy.fdsn import Client
#import urllib2

d2r=math.pi/180.0
earth_radius = 6371.0
#=====================================================================
#=====================================================================
#def get_IRIS_WebServices_Catalog(access_mode):

    #client = Client("IRIS")
    #print 'client=',client
#    response = urllib2.urlopen('http://service.iris.edu/fdsnws/event/1/query?starttime=2010-02-27T06:30:00&endtime=2011-04-01T06:30:00&catalog=GCMT&orderby=time&format=text&nodata=404')
    # Mark -- is it possible to have a command like this, created with the 
    # URL Builder and then have the reponse that I would normally see 
    # on the Web page?
#    print response
#    value=1
#    return value
#=====================================================================
def get_CMT_Catalog(cmtaccess_mode):
    if cmtaccess == 1:
        # Updated for Mac
        #CMT_Catalog="/net/holmes/scratch2/gurnis/Earthquake_Catelogs/CMT_Catalog/jan76_dec10.ndk"
        CMT_Catalog="/export/scratch1/gurnis/Earthquake_Catelogs/CMT_Catalog/jan76_dec10.ndk"
        cmt_simple="cmt_lon_lat_d_mb.xydm"

    CMT=open(CMT_Catalog)
    CMT_out=open(cmt_simple,"w")

    while 1:
        # Unravel the ndk format file
        line1=CMT.readline()
        line2=CMT.readline()
        line3=CMT.readline()
        line4=CMT.readline()
        line4=CMT.readline()
        if(line1):
            catalog=line1[0:3]
            date=line1[5:16]
            time=line1[16:25]
            lat=line1[27:33]
            lon=line1[34:42]
            depth=line1[42:47]
            mag=line1[48:55]
            location=line1[56:81]
            mb,ms=mag.split()
            CMT_out.write("%s %s %s %s\n" % (lon,lat,depth,mb))
        else:
            break

    CMT.close()
    CMT_out.close()

    return cmt_simple
#=====================================================================
def get_EHB_Catalog(access_mode):
    #updated for Mac
    #EHB_Catalog="/net/holmes/scratch2/gurnis/Earthquake_Catelogs/ISC_Catalogs/EHB_1960_2008.dat"
    EHB_Catalog="/Users/gurnis/Desktop/Gurnis_Files/Working/Data_Sets/Earthquake_Catelogs/ISC_Catalogs/EHB_1960_2008.dat"

    EHB=open(EHB_Catalog)
    ehb_simple="ehb_lon_lat_d_mb.xydm"
    EHB_out=open(ehb_simple,"w")

    while 1:
        # Unravel the ndk format file
        line=EHB.readline()
        if(line):
            event, author, date, time, lat, lon, depth, depfix, mag_author, type, mag = line.split(",")
            mb=float(mag)
            EHB_out.write("%s %s %s %g\n" % (lon,lat,depth,mb))
        else:
            break

    EHB.close()
    EHB_out.close()

    return ehb_simple
#=====================================================================
