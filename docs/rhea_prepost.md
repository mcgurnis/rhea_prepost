# Pre and Post Processing of data for Rhea computations

### M. Gurnis Aug. 4, 2026

---

This is a set of Python scripts that create the thermal structure of the lithosphere and mantle, along with plate boundaries, and writes them out in formats that the code `Rhea` can read.

Down load the code from github

```sh
git clone https://github.com/mcgurnis/rhea_prepost/tree/main
```

You'll need to ensure that the directory dir that you place this code in is in (src) your `PYTHONPATH`. There is a subdirectory in this repository called `example' that contains an ini file which will hold the directories that you data is located in as well as some control parameters.

### First step

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
- `Orig_Slabs2_grids_dir`   This is the original grids (net cdf files) that can be obtained from the USGS (https://www.usgs.gov/data/slab2-a-comprehensive-subduction-zone-geometry-model). Called Slab2.0.
- `New_grids_dir` Reprocessed Slab2 depth grids. I beleive an output of this workflow
- `Contours_Slab_dir` the slab contrours from the USGS Slab2.0 model
- `XY_dir` these are the xy files that define the outline of the Slab2.0 and part of that release.
- `age_grid` Some modifications of the above age grids, if needed
- `topo_grid` You can use the etopo2, 2-minute Gridded Global Relief Data (https://www.ncei.noaa.gov/products/etopo-global-relief-model)
- `dir_old_margins` this is a directory which stores the trench and ridge other plate boundaries
- `rhea_depths` this is a file that records the depth in km of a one-dimensional rhea mesh
- `profile_dir` This a location that profile data will be stored. These are profiles generated from the end points encoded in the Slab Dictionary .py file.

### Slab Dictionary

This is a Python script that only contains the slab dictionary, `slab_dict={}`. By editing this file, one controls which slab data to reprocess, including the slab depths and which slabs to create regional thermal models for.



