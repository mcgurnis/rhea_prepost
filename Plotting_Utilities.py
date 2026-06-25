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
"""
Plotting_Utilities.py

Shared plotting utility functions used by Plot_Reprocess_Slab2.0.py
and Generate_Regional_Thermal_Slab.py.
"""
#=====================================================================

import os, sys, math

#=====================================================================
# Constants

d2r          = math.pi / 180.0
earth_radius = 6371.0

# Plate boundary files
dir_old_margins = "/net/holmes/home4/gurnis/Rhea_runs/Plate_Margins/NewDataSet"
trenches  = "%s/Trench-1-12-10.xy"    % dir_old_margins
ridges    = "%s/Ridges-5-26-10.xy"    % dir_old_margins
fractures = "%s/Fractures-1-12-10.xy" % dir_old_margins
interface = "%s/Interface-1-12-10.xy" % dir_old_margins

#=====================================================================
def make_pdf(psfile, slab=None):
    """Convert a PostScript file to PDF and move it to the PDF directory.

    Args:
        psfile: path to the .ps file to convert.
        slab:   optional slab name; when provided PDFs are placed in
                PDF/<slab>/ (creating the subdirectory as needed).
                When omitted PDFs are moved to the flat PDF/ directory.
    """
    print("\n    Converting file to pdf ...")
    cmd = "gmt psconvert %s -A -Tf -E200" % psfile
    os.system(cmd)

    cmd = 'rm -f *.ps'
    os.system(cmd)

    if slab is not None:
        cmd = "mkdir PDF/" + slab
        os.system(cmd)
        cmd = 'mv *.pdf PDF/%s/' % slab
    else:
        cmd = 'mv *.pdf PDF'
    os.system(cmd)

    return
#=====================================================================
def shift_profile(profile, shift_dir, xs, zs):
    PR = open(profile)
    if shift_dir == "Z":
        while 1:
            line = PR.readline()
            if(line):
                sx1, sz1 = line.split()
                fx1 = float(sx1)
                if(fx1 >= xs):
                    zoff = float(sz1)
                    break
            else:
                break
    elif shift_dir == "P":
        print("P")
        line = PR.readline()
        sx1, sz1 = line.split()
        poff = float(sx1)
    PR.close()
    shifted_profile = 'tmp_%s.pz' % shift_dir
    PR = open(profile)
    PS = open(shifted_profile, "w")
    while 1:
        line = PR.readline()
        if(line):
            sx1, sz1 = line.split()
            fx1 = float(sx1)
            fz1 = float(sz1)
            if shift_dir == "Z":
                PS.write("%s  %g\n" % (sx1, fz1 - zoff + zs))
            elif shift_dir == "P":
                PS.write("%g  %s\n" % (fx1 - poff, sz1))
        else:
            break
    PR.close()
    PS.close()
    return shifted_profile
#=====================================================================
def overlay_plate_boundaries(psfile, RIDGES, CLOSEGMT=False):
    """Overlay plate boundary features on an open PostScript file.

    Args:
        psfile:   path to the PostScript file being built.
        RIDGES:   if truthy, draw mid-ocean ridges.
        CLOSEGMT: if True the final GMT call omits -K, closing the PS
                  file.  Default False keeps the file open for further
                  overlay commands.
    """
    teeth = "0.1/0.035lt"

    # Trenches — always followed by at least fractures, so always -K
    cmd = "gmt psxy %s -J -R -B -W1,100/100/255 -Sf%s -G100/100/255 -P -O -K >> %s" % (trenches, teeth, psfile)
    print(cmd)
    os.system(cmd)

    # Ridges
    if RIDGES:
        cmd = "gmt psxy %s -J -R -B -W1,255/0/0 -V -P -O -K >> %s" % (ridges, psfile)
        print(cmd)
        os.system(cmd)
        cmd = "gmt psxy %s -J -R -B -W0.5,255/255/255 -V -P -O -K >> %s" % (ridges, psfile)
        print(cmd)
        os.system(cmd)

    # Fractures — still -K because interface follows
    cmd = "gmt psxy %s -J -R -B -W1,128/128/128 -V -P -O -K >> %s" % (fractures, psfile)
    print(cmd)
    os.system(cmd)

    # Interface — last element; honour CLOSEGMT
    ok = "" if CLOSEGMT else " -K"
    cmd = "gmt psxy %s -J -R -B -W1,0/255/0 -Sf0.1/0.035lt -G0/255/0 -V -P -O%s >> %s" % (interface, ok, psfile)
    print(cmd)
    os.system(cmd)

    return
#=====================================================================
def new_point(x1, y1, depth, dip, str, slab_width):
    """Compute a point displaced to the centre of the thermal slab.

    Given a point on the slab surface (x1, y1, depth) and the local
    dip, strike, and half-thickness (slab_width), returns the
    coordinates of the corresponding point at the slab centre.

    Returns:
        new_x, new_y, new_depth
    """
    old_x     = float(x1)
    old_y     = float(y1)
    old_depth = float(depth)
    old_dip   = float(dip)
    old_str   = float(str)

    # colatitude
    theta     = 90.0 - old_y
    new_depth = old_depth - slab_width * math.sin(d2r * (90. - old_dip))
    # horizontal distance in map view
    distance  = slab_width * math.cos(d2r * (90. - old_dip))
    ss        = old_str - 90.0
    dx        = distance * math.sin(d2r * ss)
    dy        = distance * math.cos(d2r * ss)
    dlon      = dx * 180.0 / (math.sin(d2r * theta) * math.pi * earth_radius)
    dlat      = dy * 180.0 / (math.pi * earth_radius)
    new_x     = old_x + dlon
    new_y     = old_y + dlat
    return new_x, new_y, new_depth
#=====================================================================
