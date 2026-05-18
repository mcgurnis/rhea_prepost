#!/usr/bin/env python
# If RUM==only, then slab grids are only RUM slab, else Slab1.0 slab
# If RUM!=only and != NONE, then used to map from Slab1.0 name to RUM name
# Use these
#slab_dict={'alu':{'RUM':'alu', 'off':0.75, 'Nan_age':50, 'C1':'210/55', 'E1':'200/64', 'C2':'190/50', 'E2':'188/55', 'Sub_type':'Ocean', 'T_use':'Slab1', 'W_use':'Slab1'}}
#slab_dict={'car':{'RUM':'only', 'off':0.1, 'Nan_age':250, 'C1':'292/20', 'E1':'292/17', 'C2':'300.0/12', 'E2':'297/12.5', 'Sub_type':'Ocean', 'T_use':'RUM', 'W_use':'RUM'}}
#slab_dict={'cas':{'RUM':'NONE', 'off':0.25, 'Nan_age':25, 'C1':'232/48', 'E1':'238/51', 'C2':'234/42', 'E2':'240/41.5', 'Sub_type':'Cont', 'T_use':'Slab1', 'W_use':'Slab1'}}
#slab_dict={'eph':{'RUM':'only', 'off':0.1, 'Nan_age':100, 'C1':'127/13', 'E1':'124/12', 'C2':'129.5/4', 'E2':'126.5/3', 'Sub_type':'Ocean', 'T_use':'RUM', 'W_use':'RUM'}}
#slab_dict={'hal':{'RUM':'only', 'off':0.1, 'Nan_age':100, 'C1':'126.5/3.0','E1':'128/1', 'C2':'126.5/-1.5', 'E2':'128/1', 'Sub_type':'Ocean', 'T_use':'RUM', 'W_use':'RUM'}}
#slab_dict={'hel':{'RUM':'only', 'off':0.1, 'Nan_age':100, 'C1':'26/34', 'E1':'26/37.5', 'C2':'29/35.5', 'E2':'30.5/37.2', 'Sub_type':'Cont', 'T_use':'RUM', 'W_use':'RUM'}}
#slab_dict={'ind':{'RUM':'only', 'off':0.1, 'Nan_age':250, 'C1':'120/-12', 'E1':'120/-5', 'C2':'131.5/-5', 'E2':'120.5/-6.5', 'Sub_type':'Ocean', 'T_use':'RUM', 'W_use':'RUM'}}
#slab_dict={'ita':{'RUM':'only', 'off':0.1, 'Nan_age':100, 'C1':'17.5/40.3', 'E1':'14.8/40', 'C2':'16/37.1', 'E2':'14.3/39.2', 'Sub_type':'Cont', 'T_use':'RUM', 'W_use':'RUM'}}
#slab_dict={'izu':{'RUM':'mar', 'off':0.25, 'Nan_age':150, 'C1':'145/30', 'E1':'136/27', 'C2':'150/15', 'E2':'142/17', 'Sub_type':'Ocean', 'T_use':'Slab1', 'W_use':'Slab1'}}
#slab_dict={'kur':{'RUM':'mar', 'off':0.25, 'Nan_age':125, 'C1':'157/47', 'E1':'147/54', 'C2':'146/37', 'E2':'128/42', 'Sub_type':'Cont', 'T_use':'Slab1', 'W_use':'Slab1'}}
#slab_dict={'luz':{'RUM':'only', 'off':0.1, 'Nan_age':250, 'C1':'123/17', 'E1':'121/17', 'C2':'122.3/15.3', 'E2':'121.5/16.5', 'Sub_type':'Ocean', 'T_use':'RUM', 'W_use':'RUM'}}
#slab_dict={'mex':{'RUM':'cam', 'off':0.25, 'Nan_age':25, 'C1':'258/14', 'E1':'262/20', 'C2':'267/12', 'E2':'270/18', 'Sub_type':'Cont', 'T_use':'Slab1', 'W_use':'Slab1'}}
#slab_dict={'min':{'RUM':'only', 'off':0.25, 'Nan_age':50, 'C1':'123.5/6.5', 'E1':'124.5/6.6', 'C2':'123.5/5.5', 'E2':'124.5/6', 'Sub_type':'Ocean', 'T_use':'RUM', 'W_use':'RUM'}}
#slab_dict={'mol':{'RUM':'only', 'off':0.1, 'Nan_age':250, 'C1':'126/8', 'E1': '122/8.5', 'C2':'126/0', 'E2':'120.5/3', 'Sub_type':'Ocean', 'T_use':'RUM', 'W_use':'RUM'}}
#slab_dict={'nhb':{'RUM':'only', 'off':0.1, 'Nan_age':25, 'C1':'163/-13', 'E1':'170/-11', 'C2':'167/-19', 'E2':'171/-17.5', 'Sub_type':'Ocean', 'T_use':'RUM', 'W_use':'RUM'}}
#slab_dict={'ryu':{'RUM':'ryu', 'off':1, 'Nan_age':50, 'C1':'135/31', 'E1':'132/36', 'C2':'129/23', 'E2':'125/29', 'Sub_type':'Ocean', 'T_use':'Slab1', 'W_use':'Slab1'}}
#slab_dict={'sam':{'RUM':'sam', 'off':0.75, 'Nan_age':50, 'C1':'277/-5', 'E1':'291/-4', 'C2':'285/-20', 'E2':'298/-14', 'Sub_type':'Cont', 'T_use':'Slab1','W_use':'Slab1'}}
#New profiles
#slab_dict={'sam':{'RUM':'NONE', 'off':0.75, 'Nan_age':50, 'C1':'284/-27', 'E1':'297/-30', 'C2':'284/-31', 'E2':'297/-34', 'Sub_type':'Cont', 'T_use':'Slab1','W_use':'Slab1'}}
#slab_dict={'sam':{'RUM':'only', 'off':0.75, 'Nan_age':50, 'C1':'277/-5', 'E1':'291/-4', 'C2':'285/-20', 'E2':'298/-14', 'Sub_type':'Cont', 'T_use':'Slab1','W_use':'Slab1'}}
#slab_dict={'sco':{'RUM':'ssa', 'off':0.1, 'Nan_age':25, 'C1':'335/-55', 'E1':'330/-57.25', 'C2':'335/-60.5', 'E2':'330.5/-59', 'Sub_type':'Ocean', 'T_use':'Slab1','W_use':'Slab1'}}
#slab_dict={'sol':{'RUM':'nbr', 'off':1, 'Nan_age':75, 'C1':'151/-8', 'E1':'150/-4','C2':'158.5/-11', 'E2':'161/-8', 'Sub_type':'Ocean', 'T_use':'Slab1','W_use':'Slab1'}}
#slab_dict={'sol':{'RUM':'NONE', 'off':1, 'Nan_age':75, 'C1':'151/-8', 'E1':'150/-4','C2':'158.5/-11', 'E2':'161/-8', 'Sub_type':'Ocean', 'T_use':'Slab1','W_use':'Slab1'}}
#slab_dict={'sul':{'RUM':'only', 'off':0.1, 'Nan_age':250, 'C1':'119.5/0.5', 'E1':'121/-1', 'C2':'123/1.5', 'E2':'122/-0.5', 'Sub_type':'Ocean',  'T_use':'RUM','W_use':'RUM'}}
#slab_dict={'ton':{'RUM':'only', 'off':0.25, 'Nan_age':100, 'C1':'182/-38','E1':'176/-36', 'C2':'178/-42.0', 'E2':'174/-39', 'Sub_type':'Ocean','T_use':'RUM','W_use':'RUM'}}
#slab_dict={'wph':{'RUM':'only','off':0.25, 'Nan_age':50, 'C1':'119/15', 'E1':'123/15', 'C2':'120/13', 'E2':'123/15', 'Sub_type':'Ocean', 'T_use':'RUM','W_use':'RUM'}}


#Won't use these
#slab_dict={'sum':{'RUM':'ind', 'off':0.1, 'Nan_age':250, 'C1':'97/-3', 'E1':'102/2', 'C2':'108/-11', 'E2':'110/-5', 'Sub_type':'Cont', 'T_use':'Slab1', 'W_use':'Slab1'}}
#slab_dict={'van':{'RUM':'nhb', 'off':0.1, 'Nan_age':25, 'C1':'163/-13', 'E1':'170/-11', 'C2':'167/-19', 'E2':'171/-17.5', 'Sub_type':'Ocean', 'T_use':'Slab1', 'W_use':'Slab1'}}
#remove ryu from main data set -- something is wrong with data.  Maybe
#Outer boundary region which refines grd files is too large

#For combining all the regionals into the global
#For Rhea-2 Models 11/22/16
# The following have not been included:
#'luz':{'RUM':'only', 'off':0.1, 'Nan_age':250, 'C1':'123/17', 'E1':'121/17', 'C2':'122.3/15.3', 'E2':'121.5/16.5', 'Sub_type':'Ocean', 'T_use':'RUM', 'W_use':'RUM'}}
#'min':{'RUM':'only', 'off':0.25, 'Nan_age':50, 'C1':'123.5/6.5', 'E1':'124.5/6.6', 'C2':'123.5/5.5', 'E2':'124.5/6', 'Sub_type':'Ocean', 'T_use':'RUM', 'W_use':'RUM'}}
slab_dict={
'alu':{'RUM':'NONE', 'off':0.75, 'Nan_age':50, 'C1':'210/55', 'E1':'200/64', 'C2':'190/50', 'E2':'188/55', 'Sub_type':'Ocean', 'T_use':'Slab1', 'W_use':'Slab1'},
'car':{'RUM':'only', 'off':0.1, 'Nan_age':250, 'C1':'292/20', 'E1':'292/17', 'C2':'300.0/12', 'E2':'297/12.5', 'Sub_type':'Ocean', 'T_use':'RUM', 'W_use':'RUM'},
'cas':{'RUM':'NONE', 'off':0.25, 'Nan_age':25, 'C1':'232/48', 'E1':'238/51', 'C2':'234/42', 'E2':'240/41.5', 'Sub_type':'Cont', 'T_use':'Slab1', 'W_use':'Slab1'},
'eph':{'RUM':'only', 'off':0.1, 'Nan_age':100, 'C1':'127/13', 'E1':'124/12', 'C2':'129.5/4', 'E2':'126.5/3', 'Sub_type':'Ocean', 'T_use':'RUM', 'W_use':'RUM'},
'hal':{'RUM':'only', 'off':0.1, 'Nan_age':100, 'C1':'126.5/3.0','E1':'128/1', 'C2':'126.5/-1.5', 'E2':'128/1', 'Sub_type':'Ocean', 'T_use':'RUM', 'W_use':'RUM'},
'hel':{'RUM':'only', 'off':0.1, 'Nan_age':100, 'C1':'26/34', 'E1':'26/37.5', 'C2':'29/35.5', 'E2':'30.5/37.2', 'Sub_type':'Cont', 'T_use':'RUM', 'W_use':'RUM'},
'ita':{'RUM':'only', 'off':0.1, 'Nan_age':100, 'C1':'17.5/40.3', 'E1':'14.8/40', 'C2':'16/37.1', 'E2':'14.3/39.2', 'Sub_type':'Cont', 'T_use':'RUM', 'W_use':'RUM'},
'izu':{'RUM':'NONE', 'off':0.25, 'Nan_age':150, 'C1':'145/30', 'E1':'136/27', 'C2':'150/15', 'E2':'142/17', 'Sub_type':'Ocean', 'T_use':'Slab1', 'W_use':'Slab1'},
'kur':{'RUM':'NONE', 'off':0.25, 'Nan_age':125, 'C1':'157/47', 'E1':'147/54', 'C2':'146/37', 'E2':'128/42', 'Sub_type':'Cont', 'T_use':'Slab1', 'W_use':'Slab1'},
'mex':{'RUM':'NONE', 'off':0.25, 'Nan_age':25, 'C1':'258/14', 'E1':'262/20', 'C2':'267/12', 'E2':'270/18', 'Sub_type':'Cont', 'T_use':'Slab1', 'W_use':'Slab1'},
'mol':{'RUM':'only', 'off':0.1, 'Nan_age':250, 'C1':'126/8', 'E1': '122/8.5', 'C2':'126/0', 'E2':'120.5/3', 'Sub_type':'Ocean', 'T_use':'RUM', 'W_use':'RUM'},
'ryu':{'RUM':'NONE', 'off':1, 'Nan_age':50, 'C1':'135/31', 'E1':'132/36', 'C2':'129/23', 'E2':'125/29', 'Sub_type':'Ocean', 'T_use':'Slab1', 'W_use':'Slab1'},
'sam':{'RUM':'NONE', 'off':0.75, 'Nan_age':50, 'C1':'284/-27', 'E1':'297/-30', 'C2':'284/-31', 'E2':'297/-34', 'Sub_type':'Cont', 'T_use':'Slab1','W_use':'Slab1'},
'sco':{'RUM':'NONE', 'off':0.1, 'Nan_age':25, 'C1':'335/-55', 'E1':'330/-57.25', 'C2':'335/-60.5', 'E2':'330.5/-59', 'Sub_type':'Ocean', 'T_use':'Slab1','W_use':'Slab1'},
'sol':{'RUM':'NONE', 'off':1, 'Nan_age':75, 'C1':'151/-8', 'E1':'150/-4','C2':'158.5/-11', 'E2':'161/-8', 'Sub_type':'Ocean', 'T_use':'Slab1','W_use':'Slab1'},
'sum':{'RUM':'NONE', 'off':0.1, 'Nan_age':250, 'C1':'97/-3', 'E1':'102/2', 'C2':'108/-11', 'E2':'110/-5', 'Sub_type':'Cont', 'T_use':'Slab1', 'W_use':'Slab1'},
'sul':{'RUM':'only', 'off':0.1, 'Nan_age':250, 'C1':'119.5/0.5', 'E1':'121/-1', 'C2':'123/1.5', 'E2':'122/-0.5', 'Sub_type':'Ocean',  'T_use':'RUM','W_use':'RUM'},
'ton':{'RUM':'only', 'off':0.25, 'Nan_age':100, 'C1':'182/-38','E1':'176/-36', 'C2':'178/-42.0', 'E2':'174/-39', 'Sub_type':'Ocean','T_use':'RUM','W_use':'RUM'},
'van':{'RUM':'NONE', 'off':0.1, 'Nan_age':25, 'C1':'163/-13', 'E1':'170/-11', 'C2':'167/-19', 'E2':'171/-17.5', 'Sub_type':'Ocean', 'T_use':'Slab1', 'W_use':'Slab1'},
'wph':{'RUM':'only','off':0.25, 'Nan_age':50, 'C1':'119/15', 'E1':'123/15', 'C2':'120/13', 'E2':'123/15', 'Sub_type':'Ocean', 'T_use':'RUM','W_use':'RUM'}}



#slab_dict={'alu':{'RUM':'alu', 'off':0.75, 'Nan_age':50, 'C1':'210/55', 'E1':'200/64', 'C2':'190/50', 'E2':'188/55', 'Sub_type':'Ocean', 'T_use':'Slab1', 'W_use':'Slab1'},
#'car':{'RUM':'only', 'off':0.1, 'Nan_age':250, 'C1':'292/20', 'E1':'292/17', 'C2':'300.0/12', 'E2':'297/12.5', 'Sub_type':'Ocean', 'T_use':'RUM', 'W_use':'RUM'},
#'cas':{'RUM':'NONE', 'off':0.25, 'Nan_age':25, 'C1':'232/48', 'E1':'238/51', 'C2':'234/42', 'E2':'240/41.5', 'Sub_type':'Cont', 'T_use':'Slab1', 'W_use':'Slab1'},
#'eph':{'RUM':'only', 'off':0.1, 'Nan_age':100, 'C1':'127/13', 'E1':'124/12', 'C2':'129.5/4', 'E2':'126.5/3', 'Sub_type':'Ocean', 'T_use':'RUM', 'W_use':'RUM'},
#'hal':{'RUM':'only', 'off':0.1, 'Nan_age':100, 'C1':'126.5/3.0','E1':'128/1', 'C2':'126.5/-1.5', 'E2':'128/1', 'Sub_type':'Ocean', 'T_use':'RUM', 'W_use':'RUM'},
#'hel':{'RUM':'only', 'off':0.1, 'Nan_age':100, 'C1':'26/34', 'E1':'26/37.5', 'C2':'29/35.5', 'E2':'30.5/37.2', 'Sub_type':'Cont', 'T_use':'RUM', 'W_use':'RUM'},
#'ind':{'RUM':'only', 'off':0.1, 'Nan_age':250, 'C1':'120/-12', 'E1':'120/-5', 'C2':'131.5/-5', 'E2':'120.5/-6.5', 'Sub_type':'Ocean', 'T_use':'RUM', 'W_use':'RUM'},
#'ita':{'RUM':'only', 'off':0.1, 'Nan_age':100, 'C1':'17.5/40.3', 'E1':'14.8/40', 'C2':'16/37.1', 'E2':'14.3/39.2', 'Sub_type':'Cont', 'T_use':'RUM', 'W_use':'RUM'},
#'izu':{'RUM':'mar', 'off':0.25, 'Nan_age':150, 'C1':'145/30', 'E1':'136/27', 'C2':'150/15', 'E2':'142/17', 'Sub_type':'Ocean', 'T_use':'Slab1', 'W_use':'Slab1'},
#'kur':{'RUM':'mar', 'off':0.25, 'Nan_age':125, 'C1':'157/47', 'E1':'147/54', 'C2':'146/37', 'E2':'128/42', 'Sub_type':'Cont', 'T_use':'Slab1', 'W_use':'Slab1'},
#'luz':{'RUM':'only', 'off':0.1, 'Nan_age':250, 'C1':'123/17', 'E1':'121/17', 'C2':'122.3/15.3', 'E2':'121.5/16.5', 'Sub_type':'Ocean', 'T_use':'RUM', 'W_use':'RUM'},
#'mex':{'RUM':'cam', 'off':0.25, 'Nan_age':25, 'C1':'258/14', 'E1':'262/20', 'C2':'267/12', 'E2':'270/18', 'Sub_type':'Cont', 'T_use':'Slab1', 'W_use':'Slab1'},
#'mol':{'RUM':'only', 'off':0.1, 'Nan_age':250, 'C1':'126/8', 'E1': '122/8.5', 'C2':'126/0', 'E2':'120.5/3', 'Sub_type':'Ocean', 'T_use':'RUM', 'W_use':'RUM'},
#'nhb':{'RUM':'only', 'off':0.1, 'Nan_age':25, 'C1':'163/-13', 'E1':'170/-11', 'C2':'167/-19', 'E2':'171/-17.5', 'Sub_type':'Ocean', 'T_use':'RUM', 'W_use':'RUM'},
#'ryu':{'RUM':'ryu', 'off':1, 'Nan_age':50, 'C1':'135/31', 'E1':'132/36', 'C2':'129/23', 'E2':'125/29', 'Sub_type':'Ocean', 'T_use':'Slab1', 'W_use':'Slab1'},
#'sam':{'RUM':'sam', 'off':0.75, 'Nan_age':50, 'C1':'277/-5', 'E1':'291/-4', 'C2':'285/-20', 'E2':'298/-14', 'Sub_type':'Cont', 'T_use':'Slab1','W_use':'Slab1'},
#'sco':{'RUM':'ssa', 'off':0.1, 'Nan_age':25, 'C1':'335/-55', 'E1':'330/-57.25', 'C2':'335/-60.5', 'E2':'330.5/-59', 'Sub_type':'Ocean', 'T_use':'Slab1','W_use':'Slab1'},
#'sul':{'RUM':'only', 'off':0.1, 'Nan_age':250, 'C1':'119.5/0.5', 'E1':'121/-1', 'C2':'123/1.5', 'E2':'122/-0.5', 'Sub_type':'Ocean',  'T_use':'RUM','W_use':'RUM'},
#'ton':{'RUM':'only', 'off':0.25, 'Nan_age':100, 'C1':'182/-38','E1':'176/-36', 'C2':'178/-42.0', 'E2':'174/-39', 'Sub_type':'Ocean','T_use':'RUM','W_use':'RUM'},
#'wph':{'RUM':'only','off':0.25, 'Nan_age':50, 'C1':'119/15', 'E1':'123/15', 'C2':'120/13', 'E2':'123/15', 'Sub_type':'Ocean', 'T_use':'RUM','W_use':'RUM'}}

#All
#slab_dict={'alu':{'RUM':'alu', 'off':0.75, 'Nan_age':50, 'C1':'210/55', 'E1':'200/64', 'C2':'190/50', 'E2':'188/55', 'Sub_type':'Ocean'},'ass':{'RUM':'only', 'off':0.1, 'Nan_age':50, 'C1':'93.5/26', 'E1':'95.5/24', 'C2':'93.0/18', 'E2':'96.5/21', 'Sub_type':'Cont'}, 'car':{'RUM':'only', 'off':0.1, 'Nan_age':250, 'C1':'292/20', 'E1':'292/17', 'C2':'300.0/12', 'E2':'297/12.5', 'Sub_type':'Ocean'}, 'cas':{'RUM':'NONE', 'off':0.25, 'Nan_age':25, 'C1':'232/48', 'E1':'238/51', 'C2':'234/42', 'E2':'240/41.5', 'Sub_type':'Cont'}, 'eph':{'RUM':'only', 'off':0.1, 'Nan_age':100, 'C1':'127/13', 'E1':'124/12', 'C2':'129.5/4', 'E2':'126.5/3', 'Sub_type':'Ocean'}, 'hal':{'RUM':'only', 'off':0.1, 'Nan_age':100, 'C1':'126.5/3.0','E1':'128/1', 'C2':'126.5/-1.5', 'E2':'128/1', 'Sub_type':'Ocean'}, 'hel':{'RUM':'only', 'off':0.1, 'Nan_age':100, 'C1':'26/34', 'E1':'26/37.5', 'C2':'29/35.5', 'E2':'30.5/37.2', 'Sub_type':'Cont'}, 'nhb':{'RUM':'only', 'off':0.1, 'Nan_age':25, 'C1':'163/-13', 'E1':'170/-11', 'C2':'167/-19', 'E2':'171/-17.5', 'Sub_type':'Ocean'}, 'ind':{'RUM':'only', 'off':0.1, 'Nan_age':250, 'C1':'120/-12', 'E1':'120/-5', 'C2':'131.5/-5', 'E2':'120.5/-6.5', 'Sub_type':'Ocean'}, 'ita':{'RUM':'only', 'off':0.1, 'Nan_age':100, 'C1':'17.5/40.3', 'E1':'14.8/40', 'C2':'16/37.1', 'E2':'14.3/39.2', 'Sub_type':'Cont'}, 'izu':{'RUM':'mar', 'off':0.25, 'Nan_age':150, 'C1':'145/30', 'E1':'136/27', 'C2':'150/15', 'E2':'142/17', 'Sub_type':'Ocean'},'ker':{'RUM':'ton', 'off':0.25, 'Nan_age':100, 'C1':'190/-18', 'E1':'178/-19.5', 'C2':'187/-26', 'E2':'177/-23', 'Sub_type':'Ocean'},'kur':{'RUM':'mar', 'off':0.25, 'Nan_age':125, 'C1':'157/47', 'E1':'147/54', 'C2':'146/37', 'E2':'128/42', 'Sub_type':'Cont'}, 'luz':{'RUM':'only', 'off':0.1, 'Nan_age':250, 'C1':'123/17', 'E1':'121/17', 'C2':'122.3/15.3', 'E2':'121.5/16.5', 'Sub_type':'Ocean'}, 'mex':{'RUM':'cam', 'off':0.25, 'Nan_age':25, 'C1':'258/14', 'E1':'262/20', 'C2':'267/12', 'E2':'270/18', 'Sub_type':'Cont'},'min':{'RUM':'only', 'off':0.25, 'Nan_age':50, 'C1':'123.5/6.5', 'E1':'124.5/6.6', 'C2':'123.5/5.5', 'E2':'124.5/6', 'Sub_type':'Ocean'}, 'mol':{'RUM':'only', 'off':0.1, 'Nan_age':250, 'C1':'126/8', 'E1': '122/8.5', 'C2':'126/0', 'E2':'120.5/3', 'Sub_type':'Ocean'}, 'phi':{'RUM':'eph', 'off':0.5, 'Nan_age':50, 'C1':'127/13', 'E1':'124/12', 'C2':'128/9', 'E2':'125/8', 'Sub_type':'Ocean'},'ryu':{'RUM':'ryu', 'off':1, 'Nan_age':50, 'C1':'135/31', 'E1':'132/36', 'C2':'129/23', 'E2':'125/29', 'Sub_type':'Ocean'}, 'sam':{'RUM':'sam', 'off':0.75, 'Nan_age':50, 'C1':'277/-5', 'E1':'291/-4', 'C2':'285/-20', 'E2':'298/-14', 'Sub_type':'Cont'},'sco':{'RUM':'ssa', 'off':0.1, 'Nan_age':25, 'C1':'335/-55', 'E1':'330/-57.25', 'C2':'335/-60.5', 'E2':'330.5/-59', 'Sub_type':'Ocean'},'sol':{'RUM':'nbr', 'off':1, 'Nan_age':75, 'C1':'151/-8', 'E1':'150/-4','C2':'158.5/-11', 'E2':'161/-8', 'Sub_type':'Ocean'},'sul':{'RUM':'only', 'off':0.1, 'Nan_age':250, 'C1':'119.5/0.5', 'E1':'121/-1', 'C2':'123/1.5', 'E2':'122/-0.5', 'Sub_type':'Ocean'}, 'sum':{'RUM':'ind', 'off':0.1, 'Nan_age':250, 'C1':'97/-3', 'E1':'102/2', 'C2':'108/-11', 'E2':'110/-5', 'Sub_type':'Cont'},'ton':{'RUM':'only', 'off':0.25, 'Nan_age':100, 'C1':'182/-38','E1':'176/-36', 'C2':'178/-42.0', 'E2':'174/-39', 'Sub_type':'Ocean'}, 'van':{'RUM':'nhb', 'off':0.1, 'Nan_age':25, 'C1':'163/-13', 'E1':'170/-11', 'C2':'167/-19', 'E2':'171/-17.5', 'Sub_type':'Ocean'}, 'wph':{'RUM':'only', 'off':0.25, 'Nan_age':50, 'C1':'119/15', 'E1':'123/15', 'C2':'120/13', 'E2':'123/15', 'Sub_type':'Ocean'}}

#All without izu
#slab_dict={'alu':{'RUM':'alu', 'off':0.75, 'Nan_age':50, 'C1':'210/55', 'E1':'200/64', 'C2':'190/50', 'E2':'188/55', 'Sub_type':'Ocean'},'ass':{'RUM':'only', 'off':0.1, 'Nan_age':50, 'C1':'93.5/26', 'E1':'95.5/24', 'C2':'93.0/18', 'E2':'96.5/21', 'Sub_type':'Cont'}, 'car':{'RUM':'only', 'off':0.1, 'Nan_age':250, 'C1':'292/20', 'E1':'292/17', 'C2':'300.0/12', 'E2':'297/12.5', 'Sub_type':'Ocean'}, 'cas':{'RUM':'NONE', 'off':0.25, 'Nan_age':25, 'C1':'232/48', 'E1':'238/51', 'C2':'234/42', 'E2':'240/41.5', 'Sub_type':'Cont'}, 'eph':{'RUM':'only', 'off':0.1, 'Nan_age':100, 'C1':'127/13', 'E1':'124/12', 'C2':'129.5/4', 'E2':'126.5/3', 'Sub_type':'Ocean'}, 'hal':{'RUM':'only', 'off':0.1, 'Nan_age':100, 'C1':'126.5/3.0','E1':'128/1', 'C2':'126.5/-1.5', 'E2':'128/1', 'Sub_type':'Ocean'}, 'hel':{'RUM':'only', 'off':0.1, 'Nan_age':100, 'C1':'26/34', 'E1':'26/37.5', 'C2':'29/35.5', 'E2':'30.5/37.2', 'Sub_type':'Cont'}, 'nhb':{'RUM':'only', 'off':0.1, 'Nan_age':25, 'C1':'163/-13', 'E1':'170/-11', 'C2':'167/-19', 'E2':'171/-17.5', 'Sub_type':'Ocean'}, 'ind':{'RUM':'only', 'off':0.1, 'Nan_age':250, 'C1':'120/-12', 'E1':'120/-5', 'C2':'131.5/-5', 'E2':'120.5/-6.5', 'Sub_type':'Ocean'}, 'ita':{'RUM':'only', 'off':0.1, 'Nan_age':100, 'C1':'17.5/40.3', 'E1':'14.8/40', 'C2':'16/37.1', 'E2':'14.3/39.2', 'Sub_type':'Cont'}, 'ker':{'RUM':'ton', 'off':0.25, 'Nan_age':100, 'C1':'190/-18', 'E1':'178/-19.5', 'C2':'187/-26', 'E2':'177/-23', 'Sub_type':'Ocean'},'kur':{'RUM':'mar', 'off':0.25, 'Nan_age':125, 'C1':'157/47', 'E1':'147/54', 'C2':'146/37', 'E2':'128/42', 'Sub_type':'Cont'}, 'luz':{'RUM':'only', 'off':0.1, 'Nan_age':250, 'C1':'123/17', 'E1':'121/17', 'C2':'122.3/15.3', 'E2':'121.5/16.5', 'Sub_type':'Ocean'}, 'mex':{'RUM':'cam', 'off':0.25, 'Nan_age':25, 'C1':'258/14', 'E1':'262/20', 'C2':'267/12', 'E2':'270/18', 'Sub_type':'Cont'},'min':{'RUM':'only', 'off':0.25, 'Nan_age':50, 'C1':'123.5/6.5', 'E1':'124.5/6.6', 'C2':'123.5/5.5', 'E2':'124.5/6', 'Sub_type':'Ocean'}, 'mol':{'RUM':'only', 'off':0.1, 'Nan_age':250, 'C1':'126/8', 'E1': '122/8.5', 'C2':'126/0', 'E2':'120.5/3', 'Sub_type':'Ocean'}, 'phi':{'RUM':'eph', 'off':0.5, 'Nan_age':50, 'C1':'127/13', 'E1':'124/12', 'C2':'128/9', 'E2':'125/8', 'Sub_type':'Ocean'},'ryu':{'RUM':'ryu', 'off':1, 'Nan_age':50, 'C1':'135/31', 'E1':'132/36', 'C2':'129/23', 'E2':'125/29', 'Sub_type':'Ocean'}, 'sam':{'RUM':'sam', 'off':0.75, 'Nan_age':50, 'C1':'277/-5', 'E1':'291/-4', 'C2':'285/-20', 'E2':'298/-14', 'Sub_type':'Cont'},'sco':{'RUM':'ssa', 'off':0.1, 'Nan_age':25, 'C1':'335/-55', 'E1':'330/-57.25', 'C2':'335/-60.5', 'E2':'330.5/-59', 'Sub_type':'Ocean'},'sol':{'RUM':'nbr', 'off':1, 'Nan_age':75, 'C1':'151/-8', 'E1':'150/-4','C2':'158.5/-11', 'E2':'161/-8', 'Sub_type':'Ocean'},'sul':{'RUM':'only', 'off':0.1, 'Nan_age':250, 'C1':'119.5/0.5', 'E1':'121/-1', 'C2':'123/1.5', 'E2':'122/-0.5', 'Sub_type':'Ocean'}, 'sum':{'RUM':'ind', 'off':0.1, 'Nan_age':250, 'C1':'97/-3', 'E1':'102/2', 'C2':'108/-11', 'E2':'110/-5', 'Sub_type':'Cont'},'ton':{'RUM':'only', 'off':0.25, 'Nan_age':100, 'C1':'182/-38','E1':'176/-36', 'C2':'178/-42.0', 'E2':'174/-39', 'Sub_type':'Ocean'}, 'van':{'RUM':'nhb', 'off':0.1, 'Nan_age':25, 'C1':'163/-13', 'E1':'170/-11', 'C2':'167/-19', 'E2':'171/-17.5', 'Sub_type':'Ocean'}, 'wph':{'RUM':'only', 'off':0.25, 'Nan_age':50, 'C1':'119/15', 'E1':'123/15', 'C2':'120/13', 'E2':'123/15', 'Sub_type':'Ocean'}}


#Below, save alternative cross-sections
#profiles in the middle and northern part of Tonga showing deep complexity
#slab_dict={'ker':{'RUM':'ton', 'off':0.25, 'Nan_age':100, 'C1':'190/-18', 'E1':'178/-19.5', 'C2':'187/-26', 'E2':'177/-23', 'Sub_type':'Ocean'}}

#profiles at the southern area just north of Hikurangi 
#slab_dict={'ker':{'RUM':'ton', 'off':0.25, 'Nan_age':100, 'C1':'184/-34', 'E1':'176/-31', 'C2':'182/-38.0', 'E2':'176/-36'}, 'Sub_type':'Ocean'}}

#Note on ind for indonesia, a key for RUM slabs. This is coded above as
#        RUM=only, because the RUM slabs extend further to the east 
#        of ~124E compared to sum (Slab 1.0)
#Note on ton for tonga, a key for RUM slabs. This is coded above as
#        RUM=only, because the RUM slabs extend further to the south
#        (especially) in the Hikurangi SZ. Also slight to the north
#        compared to ker (Slab 1.0)
#Note on nhb for new hebrides, a key for RUM slabs (vanuatu). 
#        This is coded above as
#        RUM=only, because the RUM slabs extend further afield
#        compared to van (Slab 1.0)


