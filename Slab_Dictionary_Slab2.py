#!/usr/bin/env python
#All Slab2 except hin and pam
#small edits to x-section pts, needs to be put into whole set
slab_dict={
'alu':{'date':'02.23.18', 'RUM':'NONE', 'off_dep':0.2, 'off_age':0.75, 'Nan_age':50, 'C1':'210/55', 'E1':'200/64', 'C2':'190/50', 'E2':'188/55', 'Sub_type':'Ocean', 'T_use':'Slab2', 'W_use':'Slab2'},
'cal':{'date':'02.24.18', 'RUM':'NONE', 'off_dep':0.01, 'off_age':1.0, 'Nan_age':240, 'C1':'17.4/36.2', 'E1':'12/39', 'C2':'18.5/38.4', 'E2':'12/39.3', 'Sub_type':'Cont', 'T_use':'Slab2', 'W_use':'Slab2'},
'cam':{'date':'02.24.18', 'RUM':'NONE', 'off_dep':0.25, 'off_age':0.25, 'Nan_age':25, 'C1':'258/14', 'E1':'262/20', 'C2':'267/12', 'E2':'270/18', 'Sub_type':'Cont', 'T_use':'Slab2', 'W_use':'Slab2'},
'car':{'date':'02.24.18', 'RUM':'NONE', 'off_dep':0.01, 'off_age':0.1, 'Nan_age':250, 'C1':'292/20', 'E1':'292/17', 'C2':'304.0/12', 'E2':'297/12.5', 'Sub_type':'Ocean', 'T_use':'Slab2', 'W_use':'Slab2'},
'cas':{'date':'02.24.18', 'RUM':'NONE', 'off_dep':0.10, 'off_age':0.25, 'Nan_age':25, 'C1':'232/48', 'E1':'238/51', 'C2':'234/42', 'E2':'240/41.5', 'Sub_type':'Cont', 'T_use':'Slab2', 'W_use':'Slab2'},
'cot':{'date':'02.24.18', 'RUM':'NONE', 'off_dep':0.01, 'off_age':0.25, 'Nan_age':40, 'C1':'123/6.5', 'E1':'124.9/6.9', 'C2':'123.8/5.5', 'E2':'125.3/6.9', 'Sub_type':'Cont', 'T_use':'Slab2', 'W_use':'Slab2'},
'hal':{'date':'02.23.18', 'RUM':'NONE', 'off_dep':0.01, 'off_age':0.25, 'Nan_age':100, 'C1':'130/3.0','E1':'120/4.5', 'C2':'129/0.0', 'E2':'119/1.5', 'Sub_type':'Ocean', 'T_use':'Slab2', 'W_use':'Slab2'},
'hel':{'date':'02.24.18', 'RUM':'NONE', 'off_dep':0.01, 'off_age':-0.40, 'Nan_age':100, 'C1':'26/32', 'E1':'26/39.5', 'C2':'30.5/33', 'E2':'30.5/40.2', 'Sub_type':'Cont', 'T_use':'Slab2', 'W_use':'Slab2'},
'him':{'date':'02.24.18', 'RUM':'NONE', 'off_dep':0.01, 'off_age':0.1, 'Nan_age':100, 'C1':'76.6/30', 'E1':'79/33', 'C2':'83.5/27', 'E2':'85/30', 'Sub_type':'Cont', 'T_use':'Slab2', 'W_use':'Slab2'},
'izu':{'date':'02.24.18', 'RUM':'NONE', 'off_dep':0.25, 'off_age':0.25, 'Nan_age':150, 'C1':'145/30', 'E1':'136/27', 'C2':'150/15', 'E2':'142/17', 'Sub_type':'Ocean', 'T_use':'Slab2', 'W_use':'Slab2'},
'ker':{'date':'02.24.18', 'RUM':'NONE', 'off_dep':0.25, 'off_age':0.25, 'Nan_age':100, 'C1':'190/-18', 'E1':'178/-19.5', 'C2':'187/-26', 'E2':'177/-23', 'Sub_type':'Ocean', 'T_use':'Slab2', 'W_use':'Slab2'},
'kur':{'date':'02.24.18', 'RUM':'NONE', 'off_dep':0.25, 'off_age':0.25, 'Nan_age':125, 'C1':'157/47', 'E1':'147/54', 'C2':'146/37', 'E2':'128/42', 'Sub_type':'Cont', 'T_use':'Slab2', 'W_use':'Slab2'},
'mak':{'date':'02.24.18', 'RUM':'NONE', 'off_dep':0.05, 'off_age':3.75, 'Nan_age':80, 'C1':'58/24', 'E1':'58.5/30', 'C2':'63.6/24', 'E2':'62.5/30', 'Sub_type':'Cont', 'T_use':'Slab2', 'W_use':'Slab2'},
'man':{'date':'02.24.18', 'RUM':'NONE', 'off_dep':0.05, 'off_age':0.25, 'Nan_age':20, 'C1':'120/21.5', 'E1':'123/21.3', 'C2':'119/16.2', 'E2':'122/16', 'Sub_type':'Cont', 'T_use':'Slab2', 'W_use':'Slab2'},
'mue':{'date':'02.24.18', 'RUM':'NONE', 'off_dep':0.05, 'off_age':0.25, 'Nan_age':190, 'C1':'-69/17', 'E1':'-69/18.5', 'C2':'-66/17', 'E2':'-66/18.5', 'Sub_type':'Cont', 'T_use':'Slab2', 'W_use':'Slab2'},
'phi':{'date':'02.26.18', 'RUM':'NONE', 'off_dep':0.25, 'off_age':0.1, 'Nan_age':100, 'C1':'127/13', 'E1':'124/12', 'C2':'129/4', 'E2':'126.5/3', 'Sub_type':'Ocean', 'T_use':'Slab2', 'W_use':'Slab2'},
'png':{'date':'02.26.18', 'RUM':'NONE', 'off_dep':0.05, 'off_age':4.0, 'Nan_age':40, 'C1':'136/0.7', 'E1':'134.5/-4.7', 'C2':'141/-0.3', 'E2':'138.9/-5.6', 'Sub_type':'Cont', 'T_use':'Slab2', 'W_use':'Slab2'},
'puy':{'date':'02.26.18', 'RUM':'NONE', 'off_dep':0.1, 'off_age':0.35, 'Nan_age':80, 'C1':'164/-45', 'E1':'168/-45.8', 'C2':'164/-48', 'E2':'166/-48.4', 'Sub_type':'Cont', 'T_use':'Slab2', 'W_use':'Slab2'},
'ryu':{'date':'02.26.18', 'RUM':'NONE', 'off_dep':0.15, 'off_age':1, 'Nan_age':50, 'C1':'135/31', 'E1':'132/36', 'C2':'129/23', 'E2':'125/29', 'Sub_type':'Ocean', 'T_use':'Slab2', 'W_use':'Slab2'},
'sam':{'date':'02.23.18', 'RUM':'NONE', 'off_dep':0.15, 'off_age':0.75, 'Nan_age':50, 'C1':'275/-4', 'E1':'290/0', 'C2':'284/-31', 'E2':'301/-34', 'Sub_type':'Cont', 'T_use':'Slab2','W_use':'Slab2'},
'sco':{'date':'02.23.18', 'RUM':'NONE', 'off_dep':0.30, 'off_age':0.1, 'Nan_age':25, 'C1':'335/-55', 'E1':'330/-57.25', 'C2':'335/-60.5', 'E2':'330.5/-59', 'Sub_type':'Ocean', 'T_use':'Slab2','W_use':'Slab2'},
'sol':{'date':'02.23.18', 'RUM':'NONE', 'off_dep':0.10, 'off_age':1, 'Nan_age':75, 'C1':'151/-8', 'E1':'150/-2','C2':'158.5/-11', 'E2':'161/-8', 'Sub_type':'Ocean', 'T_use':'Slab2','W_use':'Slab2'},
'sul':{'date':'02.23.18', 'RUM':'NONE', 'off_dep':0.10, 'off_age':0.1, 'Nan_age':100, 'C1':'120/2.5', 'E1':'121/-1', 'C2':'123/2.6', 'E2':'122.0/-1', 'Sub_type':'Cont', 'T_use':'Slab2', 'W_use':'Slab2'},
'sum':{'date':'02.23.18', 'RUM':'NONE', 'off_dep':0.25, 'off_age':0.1, 'Nan_age':250, 'C1':'97/-3', 'E1':'102/2', 'C2':'108/-11', 'E2':'110/-2', 'Sub_type':'Cont', 'T_use':'Slab2', 'W_use':'Slab2'},
'van':{'date':'02.23.18', 'RUM':'NONE', 'off_dep':0.25, 'off_age':0.1, 'Nan_age':25, 'C1':'163/-13', 'E1':'170/-11', 'C2':'167/-19', 'E2':'171/-17.5', 'Sub_type':'Ocean', 'T_use':'Slab2', 'W_use':'Slab2'}
}
#slab_dict={
#'alu':{'date':'02.23.18', 'RUM':'NONE', 'off_dep':0.2, 'off_age':0.75, 'Nan_age':50, 'C1':'210/55', 'E1':'200/64', 'C2':'190/50', 'E2':'188/55', 'Sub_type':'Ocean', 'T_use':'Slab2', 'W_use':'Slab2'},
#'cal':{'date':'02.24.18', 'RUM':'NONE', 'off_dep':0.01, 'off_age':1.0, 'Nan_age':240, 'C1':'17.4/36.2', 'E1':'14/39', 'C2':'18.5/38.4', 'E2':'14.3/39.3', 'Sub_type':'Cont', 'T_use':'Slab2', 'W_use':'Slab2'},
#'cam':{'date':'02.24.18', 'RUM':'NONE', 'off_dep':0.25, 'off_age':0.25, 'Nan_age':25, 'C1':'258/14', 'E1':'262/20', 'C2':'267/12', 'E2':'270/18', 'Sub_type':'Cont', 'T_use':'Slab2', 'W_use':'Slab2'},
#'car':{'date':'02.24.18', 'RUM':'NONE', 'off_dep':0.01, 'off_age':0.1, 'Nan_age':250, 'C1':'292/20', 'E1':'292/17', 'C2':'304.0/12', 'E2':'297/12.5', 'Sub_type':'Ocean', 'T_use':'Slab2', 'W_use':'Slab2'},
#'cas':{'date':'02.24.18', 'RUM':'NONE', 'off_dep':0.10, 'off_age':0.25, 'Nan_age':25, 'C1':'232/48', 'E1':'238/51', 'C2':'234/42', 'E2':'240/41.5', 'Sub_type':'Cont', 'T_use':'Slab1', 'W_use':'Slab1'},
#'cot':{'date':'02.24.18', 'RUM':'NONE', 'off_dep':0.01, 'off_age':0.25, 'Nan_age':40, 'C1':'123/6.5', 'E1':'124.9/6.9', 'C2':'123.8/5.5', 'E2':'125.3/6.9', 'Sub_type':'Cont', 'T_use':'Slab2', 'W_use':'Slab2'},
#'hal':{'date':'02.23.18', 'RUM':'NONE', 'off_dep':0.01, 'off_age':0.25, 'Nan_age':100, 'C1':'130/2','E1':'125/4', 'C2':'129/0', 'E2':'122/1', 'Sub_type':'Ocean', 'T_use':'Slab2', 'W_use':'Slab2'},
#'hel':{'date':'02.24.18', 'RUM':'NONE', 'off_dep':0.01, 'off_age':-0.40, 'Nan_age':100, 'C1':'26/32', 'E1':'26/37.5', 'C2':'30.5/33', 'E2':'30.5/37.2', 'Sub_type':'Cont', 'T_use':'Slab2', 'W_use':'Slab2'},
#'him':{'date':'02.24.18', 'RUM':'NONE', 'off_dep':0.01, 'off_age':0.1, 'Nan_age':100, 'C1':'76.6/30', 'E1':'79/33', 'C2':'83.5/27', 'E2':'85/30', 'Sub_type':'Cont', 'T_use':'Slab2', 'W_use':'Slab2'},
#'hin':{'date':'02.24.18', 'RUM':'NONE', 'off_dep':0.01, 'off_age':0.1, 'Nan_age':100, 'C1':'69.9/35.5', 'E1':'69.4/37', 'C2':'71.2/35.8', 'E2':'70.6/37.3', 'Sub_type':'Cont', 'T_use':'Slab2', 'W_use':'Slab2'},
#'izu':{'date':'02.24.18', 'RUM':'NONE', 'off_dep':0.25, 'off_age':0.25, 'Nan_age':150, 'C1':'145/30', 'E1':'136/27', 'C2':'150/15', 'E2':'142/17', 'Sub_type':'Ocean', 'T_use':'Slab2', 'W_use':'Slab2'},
#'ker':{'date':'02.24.18', 'RUM':'NONE', 'off_dep':0.25, 'off_age':0.25, 'Nan_age':100, 'C1':'190/-18', 'E1':'178/-19.5', 'C2':'187/-26', 'E2':'177/-23', 'Sub_type':'Ocean', 'T_use':'Slab2', 'W_use':'Slab2'},
#'kur':{'date':'02.24.18', 'RUM':'NONE', 'off_dep':0.25, 'off_age':0.25, 'Nan_age':125, 'C1':'157/47', 'E1':'147/54', 'C2':'146/37', 'E2':'128/42', 'Sub_type':'Cont', 'T_use':'Slab2', 'W_use':'Slab2'},
#'mak':{'date':'02.24.18', 'RUM':'NONE', 'off_dep':0.05, 'off_age':3.75, 'Nan_age':80, 'C1':'58/25', 'E1':'58.5/29.5', 'C2':'63.6/25', 'E2':'62.5/29', 'Sub_type':'Cont', 'T_use':'Slab2', 'W_use':'Slab2'},
#'man':{'date':'02.24.18', 'RUM':'NONE', 'off_dep':0.05, 'off_age':0.25, 'Nan_age':20, 'C1':'120/21.5', 'E1':'122/21.3', 'C2':'119/16.2', 'E2':'121/16', 'Sub_type':'Cont', 'T_use':'Slab2', 'W_use':'Slab2'},
#'mue':{'date':'02.24.18', 'RUM':'NONE', 'off_dep':0.05, 'off_age':0.25, 'Nan_age':190, 'C1':'-69/17', 'E1':'-69/18.5', 'C2':'-66/17', 'E2':'-66/18.5', 'Sub_type':'Cont', 'T_use':'Slab2', 'W_use':'Slab2'},
#'pam':{'date':'02.26.18', 'RUM':'NONE', 'off_dep':0.05, 'off_age':0.1, 'Nan_age':100, 'C1':'71.5/38.9', 'E1':'72.6/36.7', 'C2':'74.5/39.9', 'E2':'74.5/37', 'Sub_type':'Cont', 'T_use':'Slab2', 'W_use':'Slab2'},
#'phi':{'date':'02.26.18', 'RUM':'NONE', 'off_dep':0.25, 'off_age':0.1, 'Nan_age':100, 'C1':'127/13', 'E1':'124/12', 'C2':'129/4', 'E2':'126.5/3', 'Sub_type':'Ocean', 'T_use':'Slab2', 'W_use':'Slab2'},
#'png':{'date':'02.26.18', 'RUM':'NONE', 'off_dep':0.05, 'off_age':4.0, 'Nan_age':40, 'C1':'136/0.7', 'E1':'134.5/-4.7', 'C2':'141/-0.3', 'E2':'138.9/-5.6', 'Sub_type':'Cont', 'T_use':'Slab2', 'W_use':'Slab2'},
#'puy':{'date':'02.26.18', 'RUM':'NONE', 'off_dep':0.1, 'off_age':0.35, 'Nan_age':80, 'C1':'15.86/45', 'E1':'168/-45.8', 'C2':'164/-48', 'E2':'166/-48.4', 'Sub_type':'Cont', 'T_use':'Slab2', 'W_use':'Slab2'},
#'ryu':{'date':'02.26.18', 'RUM':'NONE', 'off_dep':0.15, 'off_age':1, 'Nan_age':50, 'C1':'135/31', 'E1':'132/36', 'C2':'129/23', 'E2':'125/29', 'Sub_type':'Ocean', 'T_use':'Slab1', 'W_use':'Slab1'},
#'sam':{'date':'02.23.18', 'RUM':'NONE', 'off_dep':0.15, 'off_age':0.75, 'Nan_age':50, 'C1':'284/-27', 'E1':'297/-30', 'C2':'284/-31', 'E2':'297/-34', 'Sub_type':'Cont', 'T_use':'Slab1','W_use':'Slab1'},
#'sco':{'date':'02.23.18', 'RUM':'NONE', 'off_dep':0.30, 'off_age':0.1, 'Nan_age':25, 'C1':'335/-55', 'E1':'330/-57.25', 'C2':'335/-60.5', 'E2':'330.5/-59', 'Sub_type':'Ocean', 'T_use':'Slab1','W_use':'Slab1'},
#'sol':{'date':'02.23.18', 'RUM':'NONE', 'off_dep':0.10, 'off_age':1, 'Nan_age':75, 'C1':'151/-8', 'E1':'150/-4','C2':'158.5/-11', 'E2':'161/-8', 'Sub_type':'Ocean', 'T_use':'Slab1','W_use':'Slab1'},
#'sul':{'date':'02.23.18', 'RUM':'NONE', 'off_dep':0.10, 'off_age':0.1, 'Nan_age':100, 'C1':'120/2.5', 'E1':'121/-0.6', 'C2':'123/2.6', 'E2':'122.6/0.7', 'Sub_type':'Cont', 'T_use':'Slab2', 'W_use':'Slab2'},
#'sum':{'date':'02.23.18', 'RUM':'NONE', 'off_dep':0.25, 'off_age':0.1, 'Nan_age':250, 'C1':'97/-3', 'E1':'102/2', 'C2':'108/-11', 'E2':'110/-5', 'Sub_type':'Cont', 'T_use':'Slab1', 'W_use':'Slab1'},
#'van':{'date':'02.23.18', 'RUM':'NONE', 'off_dep':0.25, 'off_age':0.1, 'Nan_age':25, 'C1':'163/-13', 'E1':'170/-11', 'C2':'167/-19', 'E2':'171/-17.5', 'Sub_type':'Ocean', 'T_use':'Slab1', 'W_use':'Slab1'}
#}

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


