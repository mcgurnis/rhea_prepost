# Pre and Post Processing of data for Rhea computations

### M. Gurnis Aug. 10, 2026

---

This is a set of Python scripts that create the thermal structure of the lithosphere and mantle, along with plate boundaries, and writes them out in formats that the code `Rhea` can read.

Down load the code from github

```sh
git clone https://github.com/mcgurnis/rhea_prepost/tree/main
```

You'll need to ensure that the directory dir that you place this code in is in (src) your `PATH` and `PYTHONPATH`. There is a subdirectory in this repository called `example' that contains an ini file which will hold the directories where your data is located as well as some control parameters.

### I. Initial steps

---

The first step is to find a directory in which the many files of reprocessed data and pdf files will be stored.

```sh
mkdir My_Directory
cd My_Directory
cp ~/rhea_prepost/example/directories_files_for_rhea_structure.ini .
```

There will be a number of entries that will need to be changed in `directories_files_for_rhea_structure.ini` that will be indicated progressively in this document.

You will need local copies (or links) to the following files:


- `Slab2_Age_Dir` Age grids orginally from Earthbyte and reprocessed
- `Orig_Slabs2_grids_dir`   This is the original grids (net cdf files) that can be obtained from the USGS, [Slab2.0](https://www.usgs.gov/data/slab2-a-comprehensive-subduction-zone-geometry-model).
- `New_grids_dir` Reprocessed Slab2 depth grids. I beleive an output of this workflow
- `Contours_Slab_dir` the slab contrours from the USGS Slab2.0 model
- `XY_dir` these are the xy files that define the outline of the Slab2.0 and part of that release.
- `age_grid` Some modifications of the above age grids, if needed
- `topo_grid` You can use the 2-minute Gridded Global Relief Data, [etopo2](https://www.ncei.noaa.gov/products/etopo-global-relief-model).
- `dir_old_margins` this is a directory which stores the trench and ridge other plate boundaries
- `rhea_depths` this is a file that records the depth in km of a one-dimensional rhea mesh
- `profile_dir` This a location that profile data will be stored. These are profiles generated from the end points encoded in the Slab Dictionary .py file.

### II. The Slab Dictionary

This is a script that only contains the slab dictionary, `slab_dict={}`. By editing this file, one controls which slab data to reprocess, including the slab depths and which slabs to create regional thermal models for.

Each entry in `slab_dict` represents a subduction zone, keyed by a 3-letter abbreviation (e.g. `'alu'` = Aleutians, `'sum'` = Sumatra). The keys and their options are:

**Identification / provenance**
- `date` — (Slab2 file only) date the entry was last edited (MM.DD.YY)
- `RUM` — RUM (A regionalized upper mantle seismic model, https://doi.org/10.1029/97JB02488) is an older slab model. `'NONE'` means use only the Slab1/Slab2 geometry; `'only'` means use only the RUM geometry (no Slab1 equivalent); a name string (e.g. `'mar'`, `'ton'`) maps the Slab1 key to the corresponding RUM slab name
- The script currently only works in the `NONE` mode as the the RUM model from 1998 is out of date and the code works with only Slab2.0

**Plate Age parameters**
- `off_dep` / `off` — depth offset applied when reprocesses the slab surface (km or normalized units)
- `off_age` — position offset applied to the trench location in order to sample the plate age adjacent to the trench.
- `Nan_age` — age (Ma) assigned to NaN/missing values in the seafloor age grid, typically representing very old or continental crust

**Cross-section geometry** — pairs of `longitude/latitude` strings defining two cross-section profiles:
- `C1`, `C2` — center points of cross-sections 1 and 2
- `E1`, `E2` — end points of cross-sections 1 and 2

**Subduction type**
- `Sub_type` — lithology of the subducting plate: `'Ocean'` (oceanic) or `'Cont'` (continental)

**Data source selection**
- `T_use` — which slab model to use for the thermal structure (`'Slab1'`, `'Slab2'`, or `'RUM'`)
- `W_use` — which slab model to use for the wedge geometry (same options)


### III. Visualize the input data and reprocess the slab data

Start by running the script **Plot_Reprocess_Slab2.0.py** in your main directory as

``` sh
Plot_Reprocess_Slab2.0.py mode
```

where `mode` must be

- `S`  Summary Table of Slabs
- `C`  Contour files of slab depths
- `G`  Global plot
- `R`  A set of regional plots
- `P`  Process the data to create the regional Slab2
       files and associated individual plots
- `X`  Make summary cross section

The running with the `mode` set to `S`, `C`, `G`, and `R` to ensure that all of the data is being processed correctly and it will eiher make a summary table or PDF files which are all store in the directory PDF. 

Running with `mode` set to `P` is essential to process the data to create the regional Slab2 files and make associated individual plots. This must be done before building and creating individual thermals structures for each subduction zone.

If the goal is to create thermal structures for each of the subduction zones individually, then from the main directory `cd PDF`, and inspect three PDF files for each subduction zone (as a three letter prefix, like *alu* for the Aleutians). These three files, for example *alu_slab_depth80_width40_1.pdf*, *_2.pdf*, and *_3.pdf*. Pay close attention to the age  

### IV. Slab Thermal Models

By running the script **Generate_Regional_Thermal_Slab.py** a three-dimensional thermal model for slabs in the upper mantle is generated in spherical coordinates. The assumption is that the script **Plot_Reprocess_Slab2.0.py** has already been run with the `mode` set to `P`.

The thermal structure of each slab is determined in the following way. First, an initial thermal structure is formed from the modified `'Slab2'` depth surface. A downward normal from this surface is created and the distance along this line is used to create a thermal structure from a half-space cooling model. The *plate age* is based on the modified, local age grid. Second, one this thermal structure is formed it is diffused outward using a time-scale equal to the actual depth in the mantle and the local convergence velocity. In other words, slab which just entered the mantle remains mostly unchanged while slab near 670 km depth is diffused more. This diffusion is either solved by a Gaussian filter or solving the diffusion equation with the finite difference method.  In the file, *directories_files_for_rhea_structure.ini*, the parameter *Advance_in_time*  must be set to determine how the forward diffusion is computed (Gaussian filter or FD):

``` sh
Advance_in_time=SolveFilter
Advance_in_time=SolveDiffusion
```
If the *advance_in_time=SolveDiffusion* is set, then the geometry used by the FD method must be specified:

``` sh
full_or_horizontal=full
full_or_horizontal=horizontal
```
If the parameter is set to *full* then a spherical coordinate system is used within a cut-out of a sphere, while if it is set to *horizontal* then heat diffusses outward on the surface of a sphere at that depth.

The resulting thermal structure are placed in several directories, `GRD_IC` and `GRD_FINAL` with the meaning that *IC* refers to the initial condition before diffusion and *FINAL* to after the diffusion. Inside each directory, there is a subdirectory for each subduction zone, like `GRD_IC/alu`. In those subdirectories, the thermal structure are stored as *GMT grd* files (i.e. net-cdf files), for example *layer_029.grd* which is the file for 29 km depth. These depths are specific to a `Rhea` mesh in which the depths are found in the file `directories_files_for_rhea_structure.ini` by the file named `rhea_depths`. In addition, plots in map view and cross section are created. 

The results can be validated in several ways. First, under `PDF` in subdirectories for each subduction zone, such as `PDF/alu` there are visualizations. There, are files, for example, *temp_029.pdf* and *temp_final_029.pdf* for maps of the initial and final thermal structure. In the same subdirectory, there are cross sections, such as *alu_section_1.IC.pdf* and *alu_section_1.Full.FINAL_var_convergence.pdf* for cross sections through the initial and final thermal model. Second, the degree to which the filtering or FD solution conserves heat can be determined with **Diagnose_Regional_Slab_temp.py**.

``` sh
Diagnose_Regional_Slab_temp.py sn depth
```

where `sn` is the *slab name* (e.g. kur, sam, izu, van, ker) and `depth` is *depth in km* (this depth must be in the `rhea_depths`). This script integrates the temperature difference (in units of C x km) and should be a small value. It is found to be generally small, but not infinitesimal. The results are found in PDF directory for that slab in a file such as *temperature_diagnostic_alu_depth_125.pdf*.

If needed, the final step for the generation of the slab thermal models is to combine all of the regional thermal structures at each depth into a single global grid file at that same depth.

``` sh
Create_Global_from_Regional_Slabs.py
```


