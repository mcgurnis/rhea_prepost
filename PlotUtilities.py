#!/usr/bin/env python
#=====================================================================
#                      Python Scripts for CitComS 
#          Preprocessing, Data Assimilation, and Postprocessing
#                  ---------------------------------
#                              Authors:
#                            Michael Gurnis
#                               Eh Tan
#                             Mark Turner
#          (c) California Institute of Technology 2003-2026
#               Free for non-commercial academic use ONLY.
#      This program is distributed WITHOUT ANY WARRANTY whatsoever.
#=====================================================================
#  Copyright July 2026, by the California Institute of Technology.
#  United States Government Sponsorship Acknowledged.
#  ALL RIGHTS RESERVED. 
#=====================================================================
import sys, string, os, math, glob
from datetime import datetime as dt
import CitcomParser, zslice, GMT_files
from Script_Utilities import now

# constants of nature 
r2d = 180.0/math.pi
earth_radius = 6371.0

# global control 
verbose = True
verbose = False
#=====================================================================
#=====================================================================
def cap_to_xySurfTopo(parameters_file, time):
    '''Read surface cap data files, write .xyz data'''

    # citcom model data
    parser = CitcomParser.Parser()
    parser.read(parameters_file)
    model = parser.getstr('datafile')
    nodex = parser.getint('nodex')
    nodey = parser.getint('nodey')
    nodez = parser.getint('nodez')
    nprocx = parser.getint('nprocx')
    nprocy = parser.getint('nprocy')
    nprocz = parser.getint('nprocz')
    nproc_surf = parser.getint('nproc_surf')

    # open output file 
    out = '%s.%s.surf.xyz' % (model, time)
    out_file = open(out, 'w')
    if verbose: print(dt.now(), 'cap_to_xySurfTopo: open,w ', out)

    # loop over caps
    for c in range (nproc_surf):

        # WARNING: surface files only have 1 digit for cap number
        c = '%d' % c

        # open the cap input file 
        inp = '%(model)s.surf%(c)s.%(time)s' % vars()
        inp_file = open(inp)
        if verbose: print(dt.now(), 'cap_to_xySurfTopo: open ', inp)

        # read the cap file into one big list of lines
        lines = inp_file.readlines()

        # pop the header line
        lines = lines[1:]

        # loop over the lines
        for line in lines:
                # separate into cols: 
                # lat lon topography heatflux vel_colat vel_lon
                cols = line.split(' ')

                # convert angles
                lat  = 90 - float(cols[0]) * r2d 
                lon  =      float(cols[1]) * r2d 
                # convert topo to km 
                topo =      float(cols[2]) / 1.0e+06

                # write data
                out_file.write( '%f %f %f\n' % (lon, lat, topo) )

          # end of i loop over x
        # end of j loop over y

    # end of loop over caps

    # close file 
    out_file.close()
    if verbose: print(dt.now(), 'cap_to_xySurfTopo: close: ', out)
    return out
#=====================================================================
#=====================================================================
#=====================================================================
#=====================================================================
def cap_to_xyComposition(parameters_file, time, level):
    '''read the combined capXX and optXX files into an xyz file.'''

    parser = CitcomParser.Parser()
    parser.read(parameters_file)
    model = parser.getstr('datafile')

    # Mesh data
    nproc_surf = parser.getint('nproc_surf')
    nodex = parser.getint('nodex')
    nodey = parser.getint('nodey')
    nodez = parser.getint('nodez')
    nprocx = parser.getint('nprocx')
    nprocy = parser.getint('nprocy')
    nprocz = parser.getint('nprocz')

    # Field spec
    output_optional = parser.getstr('output_optional')
    opts = output_optional.split()

    # open output file
    out = '%s.%s.z%03d.xyComposition' % (model, time, level)
    out_file = open(out, 'w')
    if verbose: print(dt.now(), 'cap_to_xyComposition: open,w ', out)

    # loop over caps
    for c in range (nproc_surf):
        c = '%02d' % c

        cap = '%(model)s.cap%(c)s.%(time)s' % vars()
        cap_file = open(cap)
        if verbose: print(dt.now(), 'cap_to_xyComposition: read ', cap)
        # read the regular cap file into one big list of lines
        cap_lines = cap_file.readlines()
        # pop the header line
        cap_lines = cap_lines[1:]

        # form file name from model parameters
        opt = '%(model)s.opt%(c)s.%(time)s' % vars()

        # open the file 
        opt_file = open(opt)
        if verbose: print(dt.now(), 'cap_to_xyComposition: read ', opt)

        # read the regular cap file into one big list of lines
        opt_lines = opt_file.readlines()

        # pop the header line
        opt_lines = opt_lines[1:]

        # loop over the node numbers, picking out the requested level
        for j in range(nodey):
          for i in range(nodex):
            for k in range(nodez):
              if k == level:
                n = k + i*nodez + j*nodez*nodex
                cap_line = cap_lines[n].rstrip()
                # separate into 3 cols: lat lon rest
                cap_cols = cap_line.split(' ', 3)
                # convert angles
                lat = 90 - float(cap_cols[0]) * r2d 
                lon =      float(cap_cols[1]) * r2d 

                opt_line = opt_lines[n].rstrip()

                # write data
                out_file.write( '%f %f %s\n' % (lon, lat, opt_line) )

              # end of f k == level
            # end of k loop over z
          # end of i loop over x
        # end of j loop over y

    # end of loop over caps

    # close file 
    out_file.close()
    if verbose: print(dt.now(), 'cap_to_xyComposition: close: ', out)
    return out

#=====================================================================
#=====================================================================
def cap_to_xy_file(out_name, type, parameters_file, field, time, cap_list, xlist, ylist, zlist):
    '''Read cap data files, write .xy data.'''

    # check extraction type
    # FIX : remove point and volume 

    types = ['point', 'xslice', 'yslice', 'zslize', 'volume']
    if type not in types:
        msg = 'type keyword', type, 'must be one of:', types
        raise IndexError(msg)

    # citcom model data
    parser = CitcomParser.Parser()
    parser.read(parameters_file)
    model = parser.getstr('datafile')
    nodex = parser.getint('nodex')
    nodey = parser.getint('nodey')
    nodez = parser.getint('nodez')
    nprocx = parser.getint('nprocx')
    nprocy = parser.getint('nprocy')
    nprocz = parser.getint('nprocz')
    nproc_surf = parser.getint('nproc_surf')

    # parse field value
    col_num = None
    if field.startswith('temp'):
        col_num = 6
    elif field.startswith('visc'):
        col_num = 7
    elif field.startswith('vx'):
        col_num = 3
    # ...
    else:
        msg = 'field "' + field + '" is not recognized.'
        raise IndexError(msg)

    # check cap input
    for c in cap_list:
        if not nproc_surf > c > -1:
          msg = 'cap_list element "' + str(c) + \
          '" is out of bounds: [0,', nproc_surf, ']'
          raise IndexError(msg)

    # check x,y,z input
    if xlist != None:
      for x in xlist:
        if not nodex > x > -1:
          msg = 'xlist element "' + str(x) + \
          '" is out of bounds: [0,' + str(nodex-1) + ']'
          raise IndexError(msg)

    if ylist != None:
      for y in ylist:
        if not nodey > y > -1:
          msg = 'ylist element "' + str(y) + \
          '" is out of bounds: [0,' + str(nodey-1) + ']'
          raise IndexError(msg)

    if zlist != None:
      for z in zlist:
        if not nodex > z > -1:
          msg = 'zlist element "' + str(z) + \
          '" is out of bounds: [0,' + str(nodex-1) + ']'
          raise IndexError(msg)

    # open output files
    out_file = open(out_name, 'w')
    if verbose: print(dt.now(), 'cap_to_xy_file: open,w ', out_file)


    # loop over caps
    for c in cap_list:
        c = '%02d' % c

        # open the cap input file 
        inp = '%(model)s.cap%(c)s.%(time)s' % vars()
        inp_file = open(inp)
        if verbose: print(dt.now(), 'cap_to_xy_file: open ', inp)

        # read the cap file into one big list of lines
        lines = inp_file.readlines()
        inp_file.close()
        if verbose: print(dt.now(), 'cap_to_xy_file: close ', inp)

        # pop the header line
        lines = lines[1:]

        # loop over the node numbers
        # NOTE loop order: Y , X , Z 
        # NOTE : indent change : 2 spaces
        for j in range(nodey):
            if ylist != None and j not in ylist: 
                continue # to next j 

            for i in range(nodex):
                if xlist != None and i not in xlist: 
                    continue # to next i 

                for k in range(nodez):
                    if zlist != None and k not in zlist:
                        continue # to next k 
               
                    # compute line number
                    n = k + i*nodez + j*nodez*nodex

                    line = lines[n].rstrip()
                    # separate into cols: lat lon vx vy vz temp visc 
                    cols = line.split(' ')

                    # convert angles
                    lat = 90 - float(cols[0]) * r2d 
                    lon =      float(cols[1]) * r2d 
                    rad =      float(cols[2]) 
                    field = float( cols[col_num] ) 

                    # write data
                    # determine how to write out data
                    if type == 'xslice':
                        out_file.write( '%f %f %f\n' % (lon, lat, field) )

                    # ... 

                    print('j i k n = %(j)d %(i)d %(k)d %(n)d -- lon lat rad value = %(lon)f %(lat)f %(rad)f %(field)f' % vars())

                # end of k loop over Z
            # end of i loop over X
        # end of j loop over Y
    # end of loop over caps

    # close file 
    #out_file.close()
    #if verbose: print now(), 'cap_to_xy_file: close: ', out
    #return out
#=====================================================================
#=====================================================================
def cap_to_xyTemperature(parameters_file, time, level):
    '''Read cap data files, write .xyz data'''

    # citcom model data
    parser = CitcomParser.Parser()
    parser.read(parameters_file)
    model = parser.getstr('datafile')
    nodex = parser.getint('nodex')
    nodey = parser.getint('nodey')
    nodez = parser.getint('nodez')
    nprocx = parser.getint('nprocx')
    nprocy = parser.getint('nprocy')
    nprocz = parser.getint('nprocz')
    nproc_surf = parser.getint('nproc_surf')

    # open output file 
    out = '%s.%s.z%03d.temp.xyz' % (model, time, level)
    out_file = open(out, 'w')
    if verbose: print(dt.now(), 'cap_to_xyTemperature: open,w ', out)

    # loop over caps
    for c in range (nproc_surf):
        c = '%02d' % c

        # open the cap input file 
        inp = '%(model)s.cap%(c)s.%(time)s' % vars()
        inp_file = open(inp)
        if verbose: print(dt.now(), 'cap_to_xyTemperature: read ', inp)

        # read the cap file into one big list of lines
        lines = inp_file.readlines()
        # pop the header line
        lines = lines[1:]

        # loop over the node numbers, picking out the requested level
        # NOTE loop order: Y , X , Z 
        for j in range(nodey):
          for i in range(nodex):
            for k in range(nodez):

              if k == level:
                n = k + i*nodez + j*nodez*nodex
                line = lines[n].rstrip()
                # separate into cols: lat lon vx vy vz temp visc 
                cols = line.split(' ')

                # convert angles
                lat = 90 - float(cols[0]) * r2d 
                lon =      float(cols[1]) * r2d 
                rad =      float(cols[2]) 
                t   =      float(cols[6])

                # write data
                out_file.write( '%f %f %f\n' % (lon, lat, t) )

            # end of k loop over z
          # end of i loop over x
        # end of j loop over y

    # end of loop over caps

    # close file 
    out_file.close()
    if verbose: print(dt.now(), 'cap_to_xyTemperature: close: ', out)
    return out
#=====================================================================
#=====================================================================
def cap_to_xyViscosity(parameters_file, time, level):
    '''Read cap data files, write .xyViscosity data'''

    # citcom model data
    parser = CitcomParser.Parser()
    parser.read(parameters_file)
    model = parser.getstr('datafile')
    nodex = parser.getint('nodex')
    nodey = parser.getint('nodey')
    nodez = parser.getint('nodez')
    nprocx = parser.getint('nprocx')
    nprocy = parser.getint('nprocy')
    nprocz = parser.getint('nprocz')
    nproc_surf = parser.getint('nproc_surf')

    # open output file 
    out = '%s.%s.z%03d.visc.xyz' % (model, time, level)
    out_file = open(out, 'w')
    if verbose: print(dt.now(), 'cap_to_xyViscosity: open,w ', out)

    # loop over caps
    for c in range (nproc_surf):
        c = '%02d' % c

        # open the cap input file 
        inp = '%(model)s.cap%(c)s.%(time)s' % vars()
        inp_file = open(inp)
        if verbose: print(dt.now(), 'cap_to_xyViscosity: open ', inp)

        # read the cap file into one big list of lines
        lines = inp_file.readlines()

        # pop the header line
        lines = lines[1:]

        # loop over the node numbers, picking out the requested level
        # NOTE loop order: Y , X , Z 
        for j in range(nodey):
          for i in range(nodex):
            for k in range(nodez):

              if k == level:
                n = k + i*nodez + j*nodez*nodex
                line = lines[n].rstrip()
                # separate into cols: lat lon vx vy vz temp visc 
                cols = line.split(' ')

                # convert angles
                lat = 90 - float(cols[0]) * r2d 
                lon =      float(cols[1]) * r2d 
                rad =      float(cols[2]) 
                # vx  =      float(cols[3])
                # vy  =      float(cols[4])
                # vz  =      float(cols[5])
                # t   =      float(cols[6])
                vis =      float(cols[7])

                # write data
                out_file.write( '%f %f %f\n' % (lon, lat, vis) )

            # end of k loop over z
          # end of i loop over x
        # end of j loop over y

    # end of loop over caps

    # close file 
    out_file.close()
    if verbose: print(dt.now(), 'cap_to_xyViscosity: close: ', out)
    return out
#=====================================================================
#=====================================================================
def cap_to_xyVelocity(parameters_file, time, level, increment, scale):
    '''Read cap data files, write .xyz data'''

    # citcom model data
    parser = CitcomParser.Parser()
    parser.read(parameters_file)
    model = parser.getstr('datafile')
    nodex = parser.getint('nodex')
    nodey = parser.getint('nodey')
    nodez = parser.getint('nodez')
    nprocx = parser.getint('nprocx')
    nprocy = parser.getint('nprocy')
    nprocz = parser.getint('nprocz')
    nproc_surf = parser.getint('nproc_surf')

    # compute scalev velocities in cm/yr
    layer_km = 6371.0
    therm_diff = parser.getfloat('thermdiff')
    scalev=(therm_diff/(layer_km*1e3))*(100.0*3600.0*24.0*365.25)

    if verbose: print(dt.now(), 'cap_to_xyVelocity: parameters_file =', parameters_file)
    if verbose: print(dt.now(), 'cap_to_xyVelocity: time =', time)
    if verbose: print(dt.now(), 'cap_to_xyVelocity: level =', level)
    if verbose: print(dt.now(), 'cap_to_xyVelocity: increment =', increment)
    if verbose: print(dt.now(), 'cap_to_xyVelocity: 1/increment =', int(1/float(increment)))
    if verbose: print(dt.now(), 'cap_to_xyVelocity: scale =', scale)

    # open output file 
    out = '%s.%s.z%03d.velo_xy.xyz' % (model, time, level)
    out_file = open(out, 'w')
    if verbose: print(dt.now(), 'cap_to_xyVelocity: open,w ', out)

    # loop over caps
    for c in range (nproc_surf):
        c = '%02d' % c

        # open the cap input file 
        inp = '%(model)s.cap%(c)s.%(time)s' % vars()
        inp_file = open(inp)
        if verbose: print(dt.now(), 'cap_to_xyVelocity: read ', inp)

        # read the cap file into one big list of lines
        lines = inp_file.readlines()
        inp_file.close()
        if verbose: print(dt.now(), 'cap_to_xyVelocity: close ', inp)

        # pop the header line
        lines = lines[1:]

        # loop over the node numbers, picking out the requested level
        # NOTE loop order: Y , X , Z 
        if verbose: print(dt.now(), 'cap_to_xyVelocity: loop start ')
        p = 0
        q = 0

        for j in range(nodey):

          for i in range(nodex):

            for k in range(nodez):

              n = k + i*nodez + j*nodez*nodex

              if k == level:

                  # DEBUGING 
                  #if verbose: print now(), 'cap_to_xyVelocity: j=', j
                  #if verbose: print now(), 'cap_to_xyVelocity: i=', i
                  #if verbose: print now(), 'cap_to_xyVelocity: k=', k
                  #if verbose: print now(), 'cap_to_xyVelocity: inz=', i*nodez
                  #if verbose: print now(), 'cap_to_xyVelocity: jnznx=', j*nodez*nodex
                  #if verbose: print now(), 'cap_to_xyVelocity: n=', n

                  q = q + 1

                  # sub-sample data 
                  if q % int(1/float(increment)) == 0: 
                   p = p + 1
                   #if verbose: print now(), 'cap_to_xyVelocity: q=', q

                   line = lines[n].rstrip()
                   # separate into cols: lat lon vx vy vz temp visc 
                   cols = line.split(' ')

                   # convert angles
                   lat = 90 - float(cols[0]) * r2d 
                   lon =      float(cols[1]) * r2d 
                   rad =      float(cols[2]) 
                   vx  =      float(cols[3])
                   vy  =      float(cols[4])
                   #vz  =      float(cols[5])
                   #temp=      float(cols[6])
                   #visc=      float(cols[7])
       
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
                   # scale to get inches on page
                   length = (scalev * math.hypot(vx,vy)) / float(scale)

                   # write data
                   out_file.write( '%f %f %f %f\n' % (lon, lat, azimuth, length) )

                  # DEBUGING 
                  #else:
                  # if verbose: print now(), 'cap_to_xyVelocity: SKIP'

                # end of if q mod incre == 0 increment sub-sampling
              # end of if k == level
            # end of k loop over z
          # end of i loop over x
        # end of j loop over y
        if verbose: print(dt.now(), 'cap_to_xyVelocity: total =', q)
        if verbose: print(dt.now(), 'cap_to_xyVelocity: used =', p)

        if p == 0 :
         print(dt.now(), 'cap_to_xyVelocity: ERROR: no velocity values selected!')
         print(dt.now(), 'cap_to_xyVelocity: ERROR: increase "overlay_velocity_increment" control to a larger value.')

        if verbose: print(dt.now(), 'cap_to_xyVelocity: loop end ')

    # end of loop over caps

    # close file 
    out_file.close()
    if verbose: print(dt.now(), 'cap_to_xyVelocity: close: ', out)

    # FIX TEST
    #cmd = 'cp %(out)s %(out)s.%(increment)s.SAVE' % vars()
    #if verbose: print(dt.now(), 'cap_to_xyVelocity: cmd =', cmd)
    #os.system(cmd)

    return out
#=====================================================================
#=====================================================================
#=====================================================================
def read_combine_opts(parameters_file, time, level, field):
    '''read the combined optXX files into ... '''

    parser = CitcomParser.Parser()
    parser.read(parameters_file)
    model = parser.getstr('datafile')

    # Mesh data
    nproc_surf = parser.getint('nproc_surf')
    nodex = parser.getint('nodex')
    nodey = parser.getint('nodey')
    nodez = parser.getint('nodez')
    nprocx = parser.getint('nprocx')
    nprocy = parser.getint('nprocy')
    nprocz = parser.getint('nprocz')

    # Field spec
    output_optional = parser.getstr('output_optional')
    opts = output_optional.split()

    # final combined file name
    combined_opt = '%s.%s.z%03d.combined.xyz' % (model, time, level)

    # loop over caps
    for c in range (nproc_surf):
        c = '%02d' % c

        inp = '%(model)s.cap%(c)s.%(time)s' % vars()
        opt = '%(model)s.opt%(c)s.%(time)s' % vars()
        cor = '%(model)s.coor%(c)s.%(time)s' % vars()
        tmp = '%(model)s.coor_opt%(c)s.%(time)s' % vars()

        # prepend the coordinates from cooresponding capXX file
        cmd = 'cut -d" " -f1,2,3 %(inp)s > %(cor)s' % vars()
        if verbose: 
            print(dt.now(), 'read_combine_opts: cmd =', cmd)
        os.system(cmd)

        cmd = 'paste -d" " %(cor)s %(opt)s > %(tmp)s' % vars()
        if verbose: 
            print(dt.now(), 'read_combine_opts: cmd =', cmd)
        os.system(cmd)

        # open the tmp file 
        tmp_file = open(tmp)
        if verbose: 
            print(dt.now(), 'read_combine_opts: open ', tmp)

        # read the tmp file into one big list of lines
        lines = tmp_file.readlines()
        # pop the bogus header line
        lines = lines[1:]

        # open up the output file
        out = '%s.coor_opt%s.%s.z%03d.xyCo' % (model, c, time, level)
        out_file = open(out, 'w')
        if verbose: 
            print(dt.now(), 'read_combine_opts: open,w ', out)

        # open temp
        # open opt
        # read coord
        # read composition 

        # loop over the node numbers, picking out the requested level
        for j in range(nodey):
          for i in range(nodex):
            for k in range(nodez):
              if k == level:
                n = k + i*nodez + j*nodez*nodex
                line = lines[n].rstrip()
                # separate into 3 cols: lat lon rest
                cols = line.split(' ', 3)

                # convert angles
                lat = 90 - float(cols[0]) * r2d 
                lon =      float(cols[1]) * r2d 

                # write data
                out_file.write( '%f %f %s\n' % (lon, lat, cols[3]) )

        # close out level 
        tmp_file.close()
        out_file.close()

        cmd = 'cat %(out)s >> %(combined_opt)s' % vars()
        if verbose: print(dt.now(), 'read_combine_opts: cmd=', cmd)
        os.system(cmd)

        cmd = 'wc -l %s'  % (combined_opt)
        if verbose: print(dt.now(), 'read_combine_opts: cmd=', cmd)
        os.system(cmd)

    # end of loop over caps

    # combine the caps
    #cmd = 'cat %s.coor_opt??.%s.z%03d.xyCo > %s'  % (model, time, level, combined_opt)
    #if verbose: print(dt.now(), 'read_combine_opts: cmd=', cmd)
    #os.system(cmd)

    # report
    cmd = 'wc -l %s'  % (combined_opt)
    if verbose: print(dt.now(), 'read_combine_opts: cmd=', cmd)
    os.system(cmd)

    # clean up
    rm_str  = '%(model)s.coor??.%(time)s ' % vars()
    # clean up
    rm_str  = '%(model)s.coor??.%(time)s ' % vars()
    rm_str += '%(model)s.coor_opt??.%(time)s ' % vars()
    rm_str += '%s.coor_opt??.%s.z%03d.xyCo ' % (model, time, level)
    cmd = 'rm -fv %(rm_str)s'  % vars()
    if verbose: print(dt.now(), 'read_combine_opts: cmd=', cmd)
    os.system(cmd)

    return combined_opt

#=====================================================================
def read_combine_caps(parameters_file, time, layer, field):

    parser = CitcomParser.Parser()
    parser.read(parameters_file)
    modelname = parser.getstr('datafile')

    # Mesh data
    nproc_surf = parser.getint('nproc_surf')
    nodex = parser.getint('nodex')
    nodey = parser.getint('nodey')
    nodez = parser.getint('nodez')
    nprocx = parser.getint('nprocx')
    nprocy = parser.getint('nprocy')
    nprocz = parser.getint('nprocz')

    # loop over caps
    nc=0
    while nc < nproc_surf:
        ifile = '%s.cap%02d.%d' % (modelname, nc, time)
        zfile = '%s.z%03d' % (ifile, layer)

        velfile = "%(zfile)s.xyVe" % vars()
        tempfile = "%(zfile)s.xyTe" % vars()
        viscfile = "%(zfile)s.xyVi" % vars()

        if verbose: print(dt.now(), 'read_combine_caps: ifile=', ifile)
        if verbose: print(dt.now(), 'read_combine_caps: zfile=', zfile)
        if verbose: print(dt.now(), 'read_combine_caps: velfile=', viscfile)
        if verbose: print(dt.now(), 'read_combine_caps: tempfile=', tempfile)
        if verbose: print(dt.now(), 'read_combine_caps: viscfile=', viscfile)

        # only extract if layer not found
        if not os.path.exists(zfile):
            if verbose: print(dt.now(), 'read_combine_caps: calling zslice')
            zslice.zslice(ifile, layer)

        if field.startswith('temp'): 
            if not os.path.exists(tempfile):
                if verbose: 
                    print(dt.now(), 'read_combine_caps: calling Tfile')
                GMT_files.Tfile(zfile,tempfile,nc,nodex,nodey,nprocx,nprocy)

        if field.startswith('visc'):
            if not os.path.exists(viscfile):
                if verbose: 
                    print(dt.now(), 'read_combine_caps: calling Vifile')
                GMT_files.Vifile(zfile,viscfile,nc,nodex,nodey,nprocx,nprocy)

        if field.startswith('velo'):
            if not os.path.exists(velfile):
                if verbose: 
                    print(dt.now(), 'read_combine_caps: calling Vfile')
                GMT_files.Vfile(zfile,velfile,nc,nodex,nodey,nprocx,nprocy)

        # clean up 
        cmd = "rm -vf %s" % (zfile)
        if verbose: print(dt.now(), 'read_combine_caps: cmd=', cmd)
        os.system(cmd)

        nc = nc+1

    # Combine the caps

    combined_name = "%s.%d.z%03d"      % (modelname, time, layer)
    combined_visc = '%s.%d.z%03d.xyVi' % (modelname, time, layer)
    combined_velo = '%s.%d.z%03d.xyVe'  % (modelname, time, layer)
    combined_temp = '%s.%d.z%03d.xyTe'  % (modelname, time, layer)

    # combine 
    if not os.path.exists(combined_name) \
    or not os.path.exists(combined_visc) \
    or not os.path.exists(combined_velo) \
    or not os.path.exists(combined_temp) :

        # NOTE: no other super processing programs use the .z??? files
        # but save this code for potential future use:
        #
        #cmd = "rm -f %s" % (combined_name)
        #if verbose: print now(), 'read_combine_caps: cmd=', cmd
        #os.system(cmd)
        #cmd = "cat %s.cap*.%d.z%03d > %s" % \
        #  (modelname,time,layer,combined_name)
        #if verbose: print now(), 'read_combine_caps: cmd=', cmd
        #os.system(cmd)
        #cmd = "rm -rfv %s.cap*.%d.z%03d" % (modelname,time,layer)
        #if verbose: print now(), 'read_combine_caps: cmd=', cmd
        #os.system(cmd)
        # 

        cmd = 'rm -f %s' % (combined_temp)
        if verbose: print(dt.now(), 'read_combine_caps: cmd=', cmd)
        os.system(cmd)
        cmd = 'cat %s.cap*.%d.z%03d.xyTe > %s' \
            % (modelname, time, layer, combined_temp)
        if verbose: print(dt.now(), 'read_combine_caps: cmd=', cmd)
        os.system(cmd)
        cmd = 'rm -rfv %s.cap*.%d.z%03d.xyTe' % (modelname, time, layer)
        if verbose: print(dt.now(), 'read_combine_caps: cmd=', cmd)
        os.system(cmd)

        cmd = 'rm -f %s' % (combined_visc)
        if verbose: print(dt.now(), 'read_combine_caps: cmd=', cmd)
        os.system(cmd)
        cmd = 'cat %s.cap*.%d.z%03d.xyVi > %s' \
            % (modelname, time, layer, combined_visc)
        if verbose: print(dt.now(), 'read_combine_caps: cmd=', cmd)
        os.system(cmd)
        cmd = 'rm -rfv %s.cap*.%d.z%03d.xyVi' % (modelname, time, layer)
        if verbose: print(dt.now(), 'read_combine_caps: cmd=', cmd)
        os.system(cmd)

        cmd = 'rm -f %s' % (combined_velo)
        if verbose: print(dt.now(), 'read_combine_caps: cmd=', cmd)
        os.system(cmd)
        cmd = 'cat %s.cap*.%d.z%03d.xyVe > %s' \
            % (modelname, time, layer, combined_velo)
        if verbose: print(dt.now(), 'read_combine_caps: cmd=', cmd)
        os.system(cmd)
        cmd = 'rm -rfv %s.cap*.%d.z%03d.xyVe' % (modelname, time, layer)
        if verbose: print(dt.now(), 'read_combine_caps: cmd=', cmd)
        os.system(cmd)

    return combined_temp, combined_visc, combined_velo

#=====================================================================

def age_in_MY(modelname,time_step,start_age,scalet):

    timefile="%s.time" % modelname
    tf=open(timefile)
    
    while 1:
        step, t, dt, CPUtime, CPUdt = tf.readline().split(' ')
        if(int(step) == time_step):
            elapsed_time=float(t)
            break
    age = start_age - elapsed_time*scalet
    tf.close() 
    return age

#=====================================================================
def get_depth(parameters_file, level):

    parser = CitcomParser.Parser()
    parser.read(parameters_file)

    coor = parser.getint('coor')

    if(coor):
        coor_file = parser.getstr('coor_file')
        cfile=open(coor_file,"r")
        line=cfile.readline()
        nz = int(line.split(' ')[1])
        n=1

        while n <= nz:
            line = cfile.readline()
            ni=int(line.split(' ')[0])
            zi=float(line.split(' ')[1])
            if( int(level) == ni ):
                depth = (1.0-zi)*6371.0 
                break
            n += 1
        else: 
            # level not found
            msg = 'level ' + str(level) + ' not found in coordinate file ' + '"' + coor_file + '"'
            raise IndexError(msg)

    else:
        print('ERROR -- could not open coor_file\:',coor_file,"\n")
        sys.exit(0)

    return depth

#=====================================================================
#=====================================================================
#=====================================================================
def read_citcoms_coord_0_file_into_zlist(parameters_file):
    '''read a global or regional case.coord.0 file; generate a list of tuples (level, z, depth); where: level ranges from 1 to nodez; z is the non-dimensional decimal fraction from model bottom (< 1.0) to surface (== 1.0); depth is in km.'''
 
    # identify file path
    parser = CitcomParser.Parser()
    parser.read(parameters_file)

    # SAVE for later ... might need it ... 
    # identify regional or global case type (also called 'zone')
    # set header prefix string 
    #if parser.getint('nproc_surf') == 1:
    #    # regional
    #elif parser.getint('nproc_surf') == 12:
    #    # global
    #else:
    #    raise IOError, 'Unknown run type. \
    #                    For Regional set nproc_surf=1 or \
    #                    Global set nproc_surf=12 in \
    #                    %(parameters_file)' %vars()

    # get an empty lists
    rlist = []
    zlist = []

    # read the files into a list of lines
    modelname = parser.getstr('datafile')
    file_name = '%(modelname)s.coord.0'  % vars()
    coord_file = open(file_name)
    try : 
        lines = coord_file.read().splitlines()
    finally:
        coord_file.close()

    # pop header line
    lines = lines[1:]

    level = 1
    for line in lines:

        # parse the line
        (theta, phi, r) = line.split()
        r = float(r)

        if rlist.count(r) == 0:
            rlist.append(r)

            # compute depth in km
            depth = (1.0 - r) * 6371.0 

            # fill the list
            tuple = (level, r, depth)
            zlist.append( tuple )
            level = level + 1
            if verbose: 
                print(dt.now(), 'read_citcoms_coord_files: level, z, depth:', tuple)

        else: 
           continue # to next line
        
    return zlist

#=====================================================================
def read_citcoms_coor_file_into_zlist(parameters_file):
    '''read a global or regional coor file; generate a list of tuples (level, z, depth); where: level ranges from 1 to nodez; z is the non-dimensional decimal fraction from model bottom (< 1.0) to surface (== 1.0); depth is in km.'''
 
    # identify file path
    parser = CitcomParser.Parser()
    parser.read(parameters_file)
    coor = parser.getint('coor')
    if not coor:
        # try reading the coord.0 file 
        return read_citcoms_coord_0_file_into_zlist(parameters_file)

    # identify regional or global case type (also called 'zone')
    # set header prefix string 
    if parser.getint('nproc_surf') == 1:
        # regional
        header_prefix = 'nsd= 3'
    elif parser.getint('nproc_surf') == 12:
        # global
        header_prefix = 'nodez='
    else:
        raise IOError('Unknown run type. \
                        For Regional set nproc_surf=1 or \
                        Global set nproc_surf=12 in \
                        %(parameters_file)' %vars())

    # read the file into a list of lines
    file_name = parser.getstr('coor_file')
    coor_file = open(file_name)
    try : 
        lines = coor_file.read().splitlines()
    finally:
        coor_file.close()

    # get an empty list of tuples (level, z, depth)
    zlist = []

    read = False

    for line in lines:

        # toggle read flag
        if line.lstrip().lstrip().startswith(header_prefix):
            read = not read 
            continue

        if read:

            # stop reading if another data block encountered 
            # delimited by lines starting with:
            #    ' nsd= N' where N is one of 1, 2, 3  
            # or 'nodeN' where N is one of 'x', 'y', 'z'
            if line.lstrip().lstrip().startswith('n'):
                read = not read 
                break;

            # parse the line
            (level, z) = line.split()
            level = int(level)
            z = float(z)
            
            # compute depth in km
            depth = (1.0 - z) * 6371.0 

            # fill the list
            tuple = (level, z, depth)
            zlist.append( tuple )

            # uncomment for really verbose
            #if verbose: 
            #    print now(), 'read_citcoms_coor_file: level, z, depth:', tuple

    return zlist


#=====================================================================
def get_depth_from_level(parameters_file, test_level):
    '''get depth in km from model level (1 .. nodez)'''

    print(dt.now(),'get_depth_from_level:')

    test_level = int(test_level)

    # get a list of tuples: (level, z, depth) from coor file
    list = read_citcoms_coor_file_into_zlist(parameters_file)
    # DEBUG 
    # print now(),'get_depth_from_level: list =', list

    # check bounds
    min = list[0][0]
    max = list[-1][0]
    print(dt.now(),'get_depth_from_level: level min =', min)
    print(dt.now(),'get_depth_from_level: level max =', max)
    if (test_level > max):
        msg = 'level %s > max level %s' % (test_level, max)
        raise IndexError(msg)
    if (test_level < min):
        msg = 'level %s < min level %s' % (test_level, min)
        raise IndexError(msg)

    # loop over tuples
    for (l,z,d) in list:
        if l == int(test_level):
            if verbose:
                print(dt.now(),'get_depth_from_level: (l,z,d) =', (l,z,d))
            return float(d)
    else:
        msg = 'level %s not found in coordinate file.' % test_level
        raise IndexError(msg)
#=====================================================================
def get_z_from_level(parameters_file, test_level):
    '''get z value from model level (1 .. nodez)'''
   
    # get a list of tuples: (level, z, depth) from coor file
    list = read_citcoms_coor_file_into_zlist(parameters_file)

    # check bounds
    min = list[0][0]
    max = list[-1][0]
    if (test_level > max):
        msg = 'level %s > max level %s' % (test_level, max)
        raise IndexError(msg)
    if (test_level < min):
        msg = 'depth %s < min level %s' % (test_level, min)
        raise IndexError(msg)

    # loop over tuples
    for (l,z,d) in list:
        if l == int(test_level):
            if verbose:
                print(dt.now(),'get_z_from_level: (l,z,d) =', (l,z,d))
            return z
    else:
        msg = 'level %s not found in coordinate file.' % test_level
        raise IndexError(msg)
#=====================================================================
def get_level_from_depth(parameters_file, test_depth):
    '''locate and return closest level for given depth in km'''

    # get a list of tuples: (level, z, depth) from coor file
    zlist = read_citcoms_coor_file_into_zlist(parameters_file)

    # check bounds
    max = zlist[0][2]
    min = zlist[-1][2]
    if (test_depth > max):
        msg = 'depth %s km > max depth %s km' % (test_depth, max)
        raise IndexError(msg)
    if (test_depth < min):
        msg = 'depth %s km < min depth %s km' % (test_depth, min)
        raise IndexError(msg)

    # shortcut for exact values
    for (l,z,d) in zlist:
        if d == float(test_depth): 
            if verbose: 
                print(dt.now(),'get_level_from_depth: (l,z,d) =', (l,z,d))
            return l
        
    # list comprehension to compute the difference between
    # test_depth and model depths for all deltas in list
    # NOTE : the if clause > 
    delta_list = [ d - test_depth for (l,z,d) in zlist if d - test_depth > 0 ] 

    # get index of, and delta from depth value previous to test_depth
    prev_i = len(delta_list) - 1
    prev_delta = delta_list[-1]

    # get index of, and delta from depth value next to test_depth
    next_i = len(delta_list)
    next_delta = zlist[next_i][1] - test_depth

    # find smallest delta
    if abs(prev_delta) < abs(next_delta) :
        i = prev_i
    else:
        i = next_i

    level = zlist[i][0]
    if verbose: 
        print(dt.astimezonenow(),'get_level_from_depth:',\
        'prev=', zlist[prev_i],'delta=',prev_delta,'i=',prev_i)
        print(dt.now(),'get_level_from_depth:',\
        'test=', test_depth)
        print(dt.now(),'get_level_from_depth:',\
        'next=', zlist[next_i],'delta=',next_delta,'i=',next_i)
        print(dt.now(),'get_level_from_depth:',\
        'index=', i, 'level=', zlist[i][0])
    return level
#=====================================================================
def get_level_from_z(parameters_file, test_z):
    '''locate and return closest level for given z in non-dimensional coordinates (ex: 0.55 to 1.0)'''

    zlist = read_citcoms_coor_file_into_zlist(parameters_file)

    # check bounds
    max = zlist[-1][1]
    min = zlist[0][1]
    if (test_z > max):
        msg = 'z value %s > than max z %s' % (test_z, max)
        raise IndexError(msg)
    if (test_z < min):
        msg = 'z value %s < than min z %s' % (test_z, min)
        raise IndexError(msg)

    # shortcut for exact values
    for (l,z,d) in zlist:
        if float(z) == float(test_z): 
            if verbose: 
                print(dt.now(),'get_level_from_z: (l,z,d) = ', (l,z,d))
            return l
        
    # list comprehension to compute the difference between
    # test_z and model z for all deltas in list
    # NOTE : the if clause < 
    delta_list = [ z - test_z for (l,z,d) in zlist if z - test_z < 0 ] 

    # get index of, and delta from z value previous to test_z
    prev_i = len(delta_list) - 1
    prev_delta = delta_list[-1]

    # get index of, and delta from z value next to test_z
    next_i = len(delta_list)
    next_delta = zlist[next_i][1] - test_z

    # find smallest delta
    if abs(prev_delta) < abs(next_delta) :
        i = prev_i
    else:
        i = next_i

    level = zlist[i][0]
    if verbose: 
        print(dt.now(),'get_level_from_z:',\
        'prev=', zlist[prev_i],'delta=',prev_delta,'i=',prev_i)
        print(dt.now(),'get_level_from_z:',\
        'test=', test_z)
        print(dt.now(),'get_level_from_z:',\
        'next=', zlist[next_i],'delta=',next_delta,'i=',next_i)
        print(dt.now(),'get_level_from_z:',\
        'index=', i, 'level=', zlist[i][0])
    return level
#=====================================================================
def read_citcoms_time_file(parameters_file):
    '''read a citcoms .time file; generate a list of tuples (step, age, runtime); where: step is model steps; age is in Ma; runtime in Myr'''

    # establish a citcom parser
    parser = CitcomParser.Parser()
    parser.read(parameters_file)

    # get basic info about the case
    modelname = parser.getstr('datafile')
    start_age = parser.getfloat('start_age')
    therm_diff = parser.getfloat('thermdiff')
    output_format = parser.getstr('output_format')

    # compute temperature scale factor 
    # FIX where are these values from?
    layer_km = 6371.0
    scale_t = layer_km * 1e3 * layer_km * 1e3 / \
                  (therm_diff * 1.e6 * 365.25 * 24. * 3600.)
    
    # check for time file 
    # base name, local directory
    timefile = '%s.time' % modelname
    
    # check local dir first
    if not os.path.exists(timefile):

        # append sub dirs if local file not found:
        if output_format == 'hdf5':
            timefile = os.path.join('Data', timefile)

        if output_format == 'ascii':
            timefile = os.path.join('Data', '0', timefile)

        # re-check for file existance
        if not os.path.exists(timefile):
            raise IOError('File not found: %(timefile)s' % vars())

    # open the file 
    try:
        with open(timefile) as time_file:
            lines = time_file.read().splitlines()
    except IOError as e:
        print('I/O error(%s): %s' % (e.errno, e.strerror))
        return []
    except Exception:
        print('Unexpected error:', sys.exc_info()[0])
        raise

    # empty list
    tlist = []
    time_file.close()

    # loop over time file
    for line in lines:

        #step, t, dt, CPUtime, CPUdt = line.split() # FIX more general?
        step, t, dt, CPUtime, CPUdt = line.split(' ')
        step = int(step)

        # compute age in Ma
        age = start_age - ( float(t) * scale_t)
  
        # compute runtime in Myr
        runtime = float(t) * scale_t

        # fill the list
        tuple = (step, age, runtime)
        tlist.append(tuple)
        # if verbose:
        #     print now(), 'read_citcoms_time_file: s,a,r', tuple

    return tlist
#=====================================================================
def get_age_from_step(parameters_file, test_step):
    '''get age in Ma from model time step'''

    # get a list of tuples: (step, age, runtime) from the .time file
    list = read_citcoms_time_file(parameters_file)

    # check bounds
    min = list[0][0]
    max = list[-1][0]
    if (int(test_step) > max):
        msg = 'step %s > than max step %s' % (test_step, max)
        raise IndexError(msg)
    if (int(test_step) < min):
        msg = 'step %s < than min step %s' % (test_step, min)
        raise IndexError(msg)

    # loop over tuples
    for (s,a,r) in list:
        if s == int(test_step):
            if verbose: 
                print(dt.now(),'get_age_from_step: (s,a,r) =',(s,a,r))
            return a
    else:
        msg = 'step %s not found in .time file.' % test_step
        raise IndexError(msg)
#=====================================================================
def get_runtime_from_step(parameters_file, test_step):
    '''get runtime in Myr from model time step'''

    # get a list of tuples: (step, age, runtime) from the .time file
    list = read_citcoms_time_file(parameters_file)

    # check bounds
    min = list[0][0]
    max = list[-1][0]
    if (test_step > max):
        msg = 'step %s > than max step %s' % (test_step, max)
        raise IndexError(msg)
    if (test_step < min):
        msg = 'step %s < than min step %s' % (test_step, min)
        raise IndexError(msg)

    # loop over tuples
    for (s,a,r) in list:
        if s == int(test_step):
            if verbose:
                print(dt.now(),'get_runtime_from_step: (s,a,r) =',(s,a,r))
            return r
    else:
        msg = 'step %(test_step)i not found in .time file.' % vars()
        raise IndexError(msg)
#=====================================================================
def get_step_from_age(parameters_file, test_age):
    '''locate and return the closest step for given age in Ma'''

    # get a list of tuples: (step, age, runtime) from the .time file
    list = read_citcoms_time_file(parameters_file)

    # check bounds 
    max_age = list[0][1]
    min_age = list[-1][1]

    if (test_age > max_age):
        msg = 'age %f Ma > max age %f Ma' % (test_age, max_age)
        raise IndexError(msg)

    if (test_age < min_age):
        msg = 'age %f Ma < min age %f Ma' % (test_age, min_age)
        raise IndexError(msg)

    # shortcut for exact values
    for (s,a,r) in list:
        if a == test_age:
            if verbose: 
                print(dt.now(),'get_step_from_age: (s,a,r) =',(s,a,r))
            return s

    # list comprehension to compute the difference between 
    # test_age and model ages
    delta_list = [a-test_age for (s,a,r) in list if a-test_age > 0 ]

    # get index of, and delta from value to test for previous value
    prev_i = len(delta_list) - 1
    prev_delta = delta_list[-1]

    # get index of, and delta from value to test for next value
    next_i = len(delta_list)
    next_delta = list[next_i][1] - test_age

    # index smallest delta and index into list of tuples
    if abs(prev_delta) < abs(next_delta) :
        i = prev_i
    else: 
        i = next_i

    # FIX 
    i = prev_i

    step = list[i][0]

    if verbose:
        print(dt.now(), 'get_step_from_age:', 'prev=', list[prev_i], 'delta=', prev_delta, 'i=', prev_i)
        print(dt.now(), 'get_step_from_age:', 'test=', test_age)
        print(dt.now(), 'get_step_from_age:', 'next=', list[next_i], 'delta=', next_delta, 'i=', prev_i)

    return step
#=====================================================================
def get_step_from_runtime(parameters_file, test_runtime):
    '''locate and return the closest step for given runtime'''

    # get a list of tuples: (step, age, runtime) from the .time file
    list = read_citcoms_time_file(parameters_file)

    # check bounds : NOTE indices
    max_runtime = list[-1][2]
    min_runtime = list[0][2]
    if (test_runtime > max_runtime):
        msg = 'runtime %f Myr > max runtime %f Myr' % (test_runtime, max_runtime)
        raise IndexError(msg)
    if (test_runtime < min_runtime):
        msg = 'runtime %f Myr < min runtime %f Myr' % (test_runtime, min_runtime)
        raise IndexError(msg)

    # shortcut for exact values
    for (s,a,r) in list:
        if float(r) == float(test_runtime):
            if verbose: 
                print(dt.now(),'get_step_from_runtime: (s,a,r) =', (s,a,r))
            return s

    # list comprehension to compute the difference between 
    # test and values in list
    # NOTE : the if clause >
    delta_list = [r-test_runtime for (s,a,r) in list if r-test_runtime < 0 ]


    # get index of, and delta from value to test for previous value
    prev_i = len(delta_list) - 1
    prev_delta = delta_list[-1]

    # get index of, and delta from value to test for next value
    next_i = len(delta_list)
    next_delta = list[next_i][1] - test_runtime

    # index into main list of tuples
    i = 0
    if abs(prev_delta) < abs(next_delta) :
        i = prev_i
    else: 
        i = next_i

    step = list[i][0]
    if verbose:
        print(dt.now(), 'get_step_from_runtime:', \
        'prev=', list[prev_i],'delta=', prev_delta, 'i=', prev_i)
        print(dt.now(), 'get_step_from_runtime:', \
        'test=', test_runtime)
        print(dt.now(), 'get_step_from_runtime:', \
        'next=', list[next_i],'delta=', next_delta,'i=', prev_i)
    return step
#=====================================================================
def get_time(pfile,time):
    '''get time in steps (0 to ..) from time in any string form: t in steps, tMa in age, tMyr in runtime'''
    time = str( time ) 
    if time.endswith('Ma'):
        a = float(time[0:-2])
        t = get_step_from_age(pfile,a)
    elif time.endswith('Myr'):
        r = float(time[0:-3])
        t = get_step_from_runtime(pfile,r)
    else:
        t = int(time)
    return t
#=====================================================================
def get_level(pfile,level):
    '''get level number (1 to nodez) from level in any string form: l in level, lkm in depth (0.0 to ..), lz in non-dimensional units'''
    level = str(level)
    if level.endswith('km'):
        d = float(level[0:-2])
        l = get_level_from_depth(pfile,d)
    elif level.endswith('z'):
        z = float(level[0:-1])
        l = get_level_from_z(pfile,z)
    else:
        l = int(level)
    return l
#=====================================================================
#=====================================================================
#=====================================================================
def read_citcoms_tracers_into_dictionary(figure):
    '''read a set of citcom tracer files and generate a dictionary of lists.  Each list contains tuples of tracer coordinates.  The lists are accessed by the following keys:

    'llf' = list of tuples of (lat, lon, flavor) 

    etc. FIX 
    'tprf' = list of tuples of (theta, phi, radius, flavor;
    'llrf' = list of tuples of (theta, phi, depth, flavor) 
    etc. FIX 

    The units of the various tuple elements are: 
        theta: radians of colat, 
        phi: radians of lon, 
        lat, lon: degrees,
        r: non-dimensional radius (suface = 1.0, cmb usualy 0.5,
        depth: km,
        flavor: non-dimensional integer code,'''

    # get empty dictionary to fill and return
    dict = {}

    # parse figure and model data
    parameters = figure['parameters']
    parser = CitcomParser.Parser()
    parser.read(parameters)

    time = figure['time']
    field = figure['field']
    level = figure['level']

    # get number of flavors
    num_flavors = parser.getint('tracer_flavors')

    # correct for empty flavor runs
    if num_flavors == 0:
        num_flavors = 1

    # build sub-dictionaries, keyed by an integer index
    for i in range(num_flavors):
        dict[i] = {}
        # set the default flavor value for each flavor type
        dict[i]['flavor'] = None
        # set the default empty lists 
        dict[i]['latlon'] = []
        dict[i]['latlonrad'] = []
        dict[i]['latlondepth'] = []

    # get the level structure list of tuples of (level,radius,depth)
    zlist = read_citcoms_coor_file_into_zlist(parameters)
 
    # set filter bounds
    r_min = None
    r_max = None
    lon_min = None
    lon_max = None
    lat_min = None
    lat_max = None

    # compute spatial filter bounds for map processing
    if figure.get('overlay_tracers_level_spacing') : 

        delta = figure.get('overlay_tracers_level_spacing')

        for index, z in enumerate(zlist) :
            
            # test each level of model vs figure level
            if z[0] == figure['level'] :

                if str(delta).endswith('km'): 
                    r_mid = z[2] # (l,r,d)
                    r_min = z_mid + float(delta[:-2])
                    r_max = z_mid - float(delta[:-2])

                elif str(delta).endswith('z'):
                    z_mid = z[1] # (l,r,d)
                    # FIX 

                else:
                    d = int(delta) 

                    i_min = index - d
                    if ( i_min < 0 ): 
                        i_min = 0

                    i_max = index + d
                    if ( i_max > len(zlist)-1 ): 
                        i_max = len(zlist)-1

                    r_mid = z[1] # (l,r,d)
                    r_min = zlist[i_min][1]
                    r_max = zlist[i_max][1]

                    # correct special case levels
                    if index == ( len(zlist) - 1 ): 
                        r_max = r_mid # top
                    if index == 0: 
                        r_min = r_mid # bot 

    # compute spatial filter bounds for map processing
    if figure.get('overlay_tracers_lat_min'):
        lat_min = float( figure.get('overlay_tracers_lat_min') )

    if figure.get('overlay_tracers_lat_max'):
        lat_max = float( figure.get('overlay_tracers_lat_max') )

    if figure.get('overlay_tracers_lon_min'):
        lon_min = float( figure.get('overlay_tracers_lon_min') )

    if figure.get('overlay_tracers_lon_max'):
        lon_max = float( figure.get('overlay_tracers_lon_max') )


        if verbose:
            print(dt.now(), 'read_citcoms_tracers_into_dictionary: r_min =', r_min)
            print(dt.now(), 'read_citcoms_tracers_into_dictionary: r_max =', r_max)
            print(dt.now(), 'read_citcoms_tracers_into_dictionary: lon_min =', lon_min)
            print(dt.now(), 'read_citcoms_tracers_into_dictionary: lon_max =', lon_max)
            print(dt.now(), 'read_citcoms_tracers_into_dictionary: lat_min =', lat_min)
            print(dt.now(), 'read_citcoms_tracers_into_dictionary: lat_max =', lat_max)

    # FIX : etc
    # if figure.get('overlay_tracers_angle_spacing') :
 
    # read the tracer files one at a time
    modelname = parser.getstr('datafile')
    pattern = '%(modelname)s.tracer.*.%(time)s'  % vars()


    # FIX add a warning for files not found
    file_list = glob.glob(pattern)
    file_list.sort()

    for name in file_list:
        file = open(name)
        try : 
            # read into into a list of lines
            lines = file.read().splitlines()
        finally:
            file.close()

        if verbose:
            print(dt.now(), 'read_citcoms_tracers_into_dictionary: tracer file name =', name)

        # diagnostic output
        num_tracers_in_file = 0
        num_tracers_to_keep = 0

        # pop off header line
        lines = lines[1:]
        
        for line in lines:

            flavor = 1.0
            if parser.getint('tracer_flavors') == 0:
                # parse the line
                (theta, phi, r) = line.split()
            else:
                # parse the line
                (theta, phi, r, flavor) = line.split()

            theta = float(theta)
            phi = float(phi)
            r = float(r)

            # convert angles
            lat = 90 - ( r2d * theta )
            lon =      ( r2d * phi )

            # compute depth in km
            depth = ( 1.0 - r) * earth_radius

            # test spatial min/max filters 
            keep = True

            # test radius ... etc.
            if figure.get('overlay_tracers_level_spacing') :
                if r_min <= r <= r_max :
                    keep = True
                else: 
                    keep = False

            # test angles ... etc.
            if figure.get('overlay_tracers_lat_min') :
                if lat < lat_min:
                    keep = False

            if figure.get('overlay_tracers_lat_max') :
                if lat > lat_max:
                    keep = False

            if figure.get('overlay_tracers_lon_min') :
                if lon < lon_min:
                    keep = False

            if figure.get('overlay_tracers_lon_max') :
                if lon > lon_max:
                    keep = False

            if keep:
                # build the tuples t_*
                t_ll = (lat, lon)

                #if verbose: 
                #    print now(), 'read_citcoms_tracers_into_dictionary: t_ll =', t_ll, ', t,p,r', theta, phi, r, 'flav=', flavor

                # sort tracer by flavors into dictionaries
                for key in dict.keys():

                    # flavor not set: 
                    if dict[key]['flavor'] == None:
                        # set the flavor 
                        dict[key]['flavor'] = flavor
                        # append the tuples to the lists
                        dict[key]['latlon'].append(t_ll)
                        dict[key]['latlonrad'].append( (lat,lon,r) )
                        dict[key]['latlondepth'].append( (lat,lon,depth) )
                        break # out of loop over keys

                    # flavor has been set
                    else: 
                        if dict[key]['flavor'] == flavor:
                            dict[key]['latlon'].append(t_ll)
                            dict[key]['latlonrad'].append( (lat,lon,r) )
                            dict[key]['latlondepth'].append( (lat,lon,depth) )
                            break # out of loop over keys

                num_tracers_to_keep += 1

            # end of if keep:
            num_tracers_in_file += 1

        # end of look over lines
        print(dt.now(), 'read_citcoms_tracers_into_dictionary: num_tracers_in_file =', num_tracers_in_file)
        print(dt.now(), 'read_citcoms_tracers_into_dictionary: num_tracers_to_keep =', num_tracers_to_keep)

    # end of loop over filenames

    #if verbose: 
    #    print now(), 'read_citcoms_tracers_into_dictionary: ', dict

    return dict
#=====================================================================
#=====================================================================
def clean_dir_of_z_data(figure):
    '''remove z data from case directory: '''

    model = figure['modelname']
    time = figure['time']

    # cap data
    cmd = 'rm -fv %(model)s.cap??.%(time)s.z???.xy??.grd' % vars()
    cmd += ' %(model)s.cap??.%(time)s.z???.xy??' % vars()
    cmd += ' %(model)s.cap??.%(time)s.z???' % vars()
    if verbose: 
        print(dt.now(), 'clean_dir_of_z_data: cmd =', cmd)
    os.system(cmd)

    # data for cross sections 
    cmd = 'rm -fv %(model)s.%(time)s.z???.xy??.grd' % vars()
    cmd += ' %(model)s.%(time)s.z???.xy??' % vars()
    cmd += ' %(model)s.%(time)s.z???' % vars()
    if verbose: 
        print(dt.now(), 'clean_dir_of_z_data: cmd =', cmd)
    os.system(cmd)

#=====================================================================
#=====================================================================
#=====================================================================
#=====================================================================
def xslice_regional(figure):
    '''slice out a section of data; set figure data''' 

    import math
    log = math.log10
    r2d = 180.0/math.pi

    # conversion factor
    layer_km = 6371.0

    parameters = figure['parameters']
    time_step = figure['time']
    field = figure['field']
    level = figure['level']
    xnode = int(figure['cross_section_xnode'])

    # max level to slice out
    level = figure['level']

    if verbose:
        print(dt.now(), 'xslice_regional: parameters = %(parameters)s ' % vars())
        print(dt.now(), 'xslice_regional: time_step = %(time_step)s ' % vars())
        print(dt.now(), 'xslice_regional: xnode = %(xnode)s ' % vars())

    parser = CitcomParser.Parser()
    parser.read(parameters)

    modelname = parser.getstr('datafile')

    nodex = parser.getint('nodex')
    nodey = parser.getint('nodey')
    nodez = parser.getint('nodez')

    # set mins and maxs in degrees
    lat_min = 90 - ( r2d * parser.getfloat('theta_min') )
    lat_max = 90 - ( r2d * parser.getfloat('theta_max') )

    lon_min = r2d * parser.getfloat('fi_min')
    lon_max = r2d * parser.getfloat('fi_max')

    figure['xslice_lat_min'] = lat_min
    figure['xslice_lat_max'] = lat_max
    figure['xslice_lon_min'] = lon_min
    figure['xslice_lon_max'] = lon_max
    if verbose: print(dt.now(), 'xslice_regional: lat_max = %(lat_max)s ' % vars())
    if verbose: print(dt.now(), 'xslice_regional: lat_min = %(lat_min)s ' % vars())
    if verbose: print(dt.now(), 'xslice_regional: lon_max = %(lon_max)s ' % vars())
    if verbose: print(dt.now(), 'xslice_regional: lon_min = %(lon_min)s ' % vars())

    # set mins and maxes in km
    xmax = parser.getfloat('theta_max') * layer_km
    xmin = 1.0e+6 # will be reset below

    ymax = parser.getfloat('fi_max') * layer_km
    ymin = 1.0e+6 # will be reset below

    zmax = -1.0e+6 # will be reset below
    zmin = 1.0e+6 # will be reset below

    rmax = -1.0e+6 # will be reset below
    rmin = 1.0e+6 # will be reset below

    # process cap files
    nc='00' # Only 1 cap for regional model
    ifile = '%(modelname)s.cap%(nc)s.%(time_step)s' % vars()
    if verbose: print(dt.now(), 'xslice_regional: open cap file: %(ifile)s' % vars())
    input = open(ifile)

    xytfile = '%(ifile)s.xsec.%(xnode)d.xyt' % vars() 
    xyvfile = '%(ifile)s.xsec.%(xnode)d.xyv' % vars()
    xypfile = '%(ifile)s.xsec.%(xnode)d.xyp' % vars()

    out_xyt= open(xytfile,"w")
    out_xyv= open(xyvfile,"w")
    out_xyp= open(xypfile,"w")

    if verbose: print(dt.now(), 'xslice_regional: open output xytfile = %(xytfile)s ' % vars())
    if verbose: print(dt.now(), 'xslice_regional: open output xyvfile = %(xyvfile)s ' % vars())
    if verbose: print(dt.now(), 'xslice_regional: open output xypfile = %(xypfile)s ' % vars())

    # read cap
    nodex, nodey, nodez = input.readline().split('x')
    nodex = int(nodex)
    nodey = int(nodey)
    nodez = int(nodez)

    if verbose: print(dt.now(), 'xslice_regional: nodex = %(nodex)s ' % vars())
    if verbose: print(dt.now(), 'xslice_regional: nodey = %(nodey)s ' % vars())
    if verbose: print(dt.now(), 'xslice_regional: nodez = %(nodez)s ' % vars())
    if verbose: print(dt.now(), 'xslice_regional: reading cap file: %(ifile)s' % vars())

    # read all the lines into a list
    lines = input.read().split('\n')

    # loop over nodes and lines
    for i in range(nodey):

        for j in range(nodex): 
            if j != int(xnode): continue # to next x plane

            for k in range(nodez):
                if k < int(level): continue # to next z level

                n = k + nodez*j + nodez*nodex*i

                theta = float(lines[n].split(' ')[0])
                fi = float(lines[n].split(' ')[1])
                rad = float(lines[n].split(' ')[2])
                v1 = float(lines[n].split(' ')[3])
                v2 = float(lines[n].split(' ')[4])
                v3 = float(lines[n].split(' ')[5])
                temp = float(lines[n].split(' ')[6])
                visc = float(lines[n].split(' ')[7])

                # convert radians to degrees
                lat = 90 - ( (180.0 / math.pi ) * theta )
                lon = (180.0 / math.pi ) * fi

                # convert radians and radius to km
                x = xmax - ( theta * layer_km )
                y = ymax - ( fi * layer_km )
                z = ( 1.0 - rad ) * layer_km

                # write out lon, rad, field files
                out_xyt.write("%g %g %g\n" % (lon, rad, temp) )
                out_xyv.write("%g %g %g\n" % (lon, rad, visc) )

                if field.startswith('phase') or figure.get('overlay_phase'):
                    phase = get_phase(figure, rad, temp)
                    out_xyp.write("%g %g %g\n" % (lon, rad, phase) )

                if (x < xmin): xmin = x # reset min 
                if (y < ymin): ymin = y # reset min 

                if (z < zmin): zmin = z # reset min
                if (z > zmax): zmax = z # reset max

                if (rad < rmin): rmin = rad # reset min
                if (rad > rmax): rmax = rad # reset max

                #print now(), 'xslice_regional: theta fi rad temp visc = %(theta)g %(fi)g %(rad)g / %(temp)g %(visc)g ' % vars()
                #print now(), 'xslice_regional: lat lon rad temp visc = %(lat)g %(lon)g %(rad)g / %(temp)g %(visc)g ' % vars()
                #print now(), 'xslice_regional: x y z temp visc = %(x)g %(y)g %(z)g / %(temp)g %(visc)g ' % vars()
            # end of loop over nodez
        # end of loop over nodex
    # end of loop over nodey
    input.close()
    out_xyt.close()
    out_xyv.close()
    out_xyp.close()
    figure['xslice_xyt'] = xytfile
    figure['xslice_xyv'] = xyvfile
    figure['xslice_xyp'] = xypfile

    if verbose: print(dt.now(), 'xslice_regional: ymin = %(ymin)s ' % vars())
    if verbose: print(dt.now(), 'xslice_regional: ymax = %(ymax)s ' % vars())
    if verbose: print(dt.now(), 'xslice_regional: zmin = %(zmin)s ' % vars())
    if verbose: print(dt.now(), 'xslice_regional: zmax = %(zmax)s ' % vars())
    if verbose: print(dt.now(), 'xslice_regional: rmin = %(rmin)s ' % vars())
    if verbose: print(dt.now(), 'xslice_regional: rmax = %(rmax)s ' % vars())

    figure['xslice_ymin'] = ymin
    figure['xslice_ymax'] = ymax
    figure['xslice_zmin'] = zmin
    figure['xslice_zmax'] = zmax
    figure['xslice_rmin'] = rmin
    figure['xslice_rmax'] = rmax


#=====================================================================
#=====================================================================
def get_phase(figure, radius, t):
    '''From the CitcomS model parameters, a radius and a temperature, compute total phase.'''

    # access the citcoms meta-data
    parser = CitcomParser.Parser()
    parameters = figure['parameters']
    parser.read( parameters )

    # outer radius of the model, in non-dimensional units
    radius_outer = parser.getfloat('radius_outer')

    #if verbose: print now(), "get_phase: radius_outer =", radius_outer
    #if verbose: print now(), "get_phase: radius =", radius
    #if verbose: print now(), "get_phase: t =", t

    # initial total phase value
    total_phase = 0.0

    # loop over phase ids
    for id in ['410', '670', 'cmb']:

        # get the phase parameters for this id
        width = parser.getfloat('width' + id)
        transT = parser.getfloat('transT' + id)
        clapeyron = parser.getfloat('clapeyron' + id)
        Ra_phase = parser.getfloat('Ra_' + id)

        #if verbose: print now(), "get_phase: Ra_phase = ", Ra_phase

        # skip ids with Ra_phase == zero
        if int(Ra_phase) == 0:
            #if verbose: print now(), "get_phase: skip this id = ", id
            continue # to next id

        # NOTE name change.
        if id == '670':  
            z_level = parser.getfloat('z_' + 'lmantle')
        else:
            z_level = parser.getfloat('z_' + id)


        # compute pressure differential and phase
        #
        # 
        pressure = (radius_outer - radius) - z_level - \
                       clapeyron * (t - transT)

        phase = 0.5 * ( 1.0 + math.tanh( pressure / width ) )

        total_phase += phase

        #if verbose: print now(), "get_phase: z_level =", z_level
        #if verbose: print now(), "get_phase: clapeyron =", clapeyron
        #if verbose: print now(), "get_phase: transT =", transT
        #if verbose: print now(), "get_phase: width =", width
        #if verbose: print now(), 'get_phase: pressure =', pressure
        #if verbose: print now(), 'get_phase: phase =', phase
        # end of loop over ids

    #if verbose: print now(), 'get_phase: total_phase =', total_phase

    return total_phase

#=====================================================================
#=====================================================================
def splice_multisegment_xy_file(file_name, pattern):
    '''split a multisegment xy file by searching for pattern in the header lines'''

    # create an empty list to hold the sub set of the xy data
    splice = []

    # read the file into a list of lines
    file = open(file_name)
    try :   
        lines = file.read().splitlines()
    finally:
        file.close()

    # read flag
    read = False

    for line in lines:

        # toggle read flag
        if line.startswith('>'):
            ## parse line
            #(name,feature_id) = line.split(';')
            if line.find(pattern) != -1:
                read = not read
                splice.append(line)
                break;
            else:
                # stop reading if a non-matching header line detected
                read = not read

        if read:
            splice.append(line)


    return splice
#=====================================================================
#=====================================================================
# SAVE:
#    190                 std::ostringstream oss;
#    191                 oss << "gplates_";
#    192                 oss << _region_id << "_";
#    193                 oss << _ref_number << "_";
#    194                 oss << _string_number << "_";
#    195                 oss << _feature_name << "_";
#    196                 oss << _rotation_group_id << "_";
#    197                 oss << _time_window.GetTimeString() << "_";
#    198                 oss << _type_code << "_";
#    199                 oss << _type_code_number << "_";
##    200                 oss << _conj_plate_id << "_";
#=====================================================================
#=====================================================================
# FIX save
# FIX save
# FIX save
#    # identify regional or global case type (also called 'zone')
#    # set header prefix string 
#    if parser.getint('nproc_surf') == 1:
#        # regional
#        header_prefix = 'nsd= 3'
#    elif parser.getint('nproc_surf') == 12:
#        # global
#        header_prefix = 'nodez='
#    else:
#        raise IOError, 'Unknown run type. \
#                        For Regional set nproc_surf=1 or \
#                        Global set nproc_surf=12 in \
#                        %(parameters_file)' %vars()
# FIX save
# FIX save
# FIX save
#=====================================================================
#=====================================================================
#=====================================================================
def test_time_functions():
    '''test of time functions '''

    # parse cmd line
    file = sys.argv[1]
    test_step = int( sys.argv[2] )
    test_age = float( sys.argv[3] )
    test_runtime = float( sys.argv[4] )
    
    age = get_age_from_step( file, test_step )
    print(dt.now(), 'test_time_functions: test_step = %(test_step)i --> age = %(age)f' % vars())

    runtime = get_runtime_from_step( file, test_step )
    print(dt.now(), 'test_time_functions: test_step = %(test_step)i --> runtime = %(runtime)f' % vars())

    step = get_step_from_age( file, test_age )
    print(dt.now(), 'test_time_functions: test_age = %(test_age)f --> step = %(step)i' % vars())

    step = get_step_from_runtime( file, test_runtime )
    print(dt.now(), 'test_time_functions: test_runtime = %(test_runtime)f --> step = %(step)i' % vars())

#=====================================================================
def test_cap_reader():
    '''simple function to test various calls to cap_to_xy_file()'''

    #cap_to_xy_file('test.xy', 'pid7038.cfg', 'temp', 300, [0], [1,5], None, [0,65])
    # single value , from a single cap
    #cap_to_xy_file('test.xy', 'pid7038.cfg', 'vx', 300, [0], [0], [0], [0])

    # line data, drill down all 65 levels
    #cap_to_xy_file('test.xy', 'pid7038.cfg', 'vx', 300, [0], [0], [0], range(65) )

    # horizontal slice of surface, z = 64
    #cap_to_xy_file('test.xy', 'pid7038.cfg', 'vx', 300, [0], range(129), range(129), [64])

    # vertical slice, X vs. Z(0 to 9), at Y = 0
    cap_to_xy_file('TEST.xy', 'xslice', 'pid18523.cfg', 'vx', 300, [0], None, [0], range(0,10))
# def cap_to_xy_file(out_name, type, parameters_file, field, time, cap_list, xlist, ylist, zlist):
#=====================================================================
if __name__ == '__main__':

    verbose = True

    # test_time_functions()

    test_cap_reader()
#=====================================================================
