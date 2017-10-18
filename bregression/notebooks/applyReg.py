
# coding: utf-8

# In[9]:

import os
import sys; sys.path.append("~/HHbbgg_ETH_devel/bregression/python") # to load packages
import training_utils as utils
import numpy as np
reload(utils)
import preprocessing_utils as preprocessing
reload(preprocessing)
import plotting_utils as plotting
reload(plotting)
import optimization_utils as optimization
reload(optimization)
import postprocessing_utils as postprocessing
reload(postprocessing)


# In[10]:

ntuples = 'heppy_05_10_2017'
# "%" sign allows to interpret the rest as a system command
get_ipython().magic(u'env data=$utils.IO.ldata$ntuples')
files = get_ipython().getoutput(u'ls $data | sort -t_ -k 3 -n')

ttbar= [s for s in files if "forTesting" in s] #use different ntuple to test the result
#ttbar= [s for s in files if "ttbar_RegressionPerJet.root" in s] # only limited statistics


utils.IO.add_target(ntuples,ttbar,1)
utils.IO.add_features(ntuples,ttbar,1)

for i in range(len(utils.IO.targetName)):        
    print "using target file n."+str(i)+": "+utils.IO.targetName[i]
for i in range(len(utils.IO.featuresName)):        
    print "using features file n."+str(i)+": "+utils.IO.featuresName[i]


# In[11]:

import pandas as pd
import root_pandas as rpd

branch_names = 'Jet_pt,noexpand:Jet_mcPt/Jet_pt,Jet_pt_reg,Jet_eta,Jet_corr,Jet_mcPt,Jet_mcFlavour,dR,rho,Jet_mt,Jet_leadTrackPt,Jet_leptonPtRel,Jet_leptonPt,Jet_leptonDeltaR,Jet_neHEF,Jet_neEmEF,Jet_chMult,Jet_vtxPt,Jet_vtxMass,Jet_vtx3dL,Jet_vtxNtrk,Jet_vtx3deL'.split(",")

features = 'Jet_pt,Jet_eta,Jet_corr,rho,Jet_mt,Jet_leadTrackPt,Jet_leptonPtRel,Jet_leptonPt,Jet_leptonDeltaR,Jet_neHEF,Jet_neEmEF,Jet_vtxPt,Jet_vtxMass,Jet_vtx3dL,Jet_vtxNtrk,Jet_vtx3deL'.split(",")
target = 'Jet_mcPt/Jet_pt'.split(",")
cuts='(Jet_mcPt > 20) & (Jet_mcFlavour==5 | Jet_mcFlavour==-5) & (Jet_pt > 15) & (Jet_eta<2.4 & Jet_eta>-2.4) & (dR < 0.4)'


branch_names = [c.strip() for c in branch_names]
features = [c.strip() for c in features]
target = [c.strip() for c in target]

#X_features = preprocessing.set_features("tree",branch_names,features,cuts)
X_features = preprocessing.set_features("tree",branch_names,features,"Jet_pt_reg>0") #with no cuts

print len(X_features)


# In[12]:

from sklearn.externals import joblib
import pandas as pd
import root_pandas as rpd

loaded_model = joblib.load(os.path.expanduser('~/HHbbgg_ETH_devel/bregression/output_files/regression_heppy_mcPt_cuts.pkl'))
X_test_features = preprocessing.get_test_sample(pd.DataFrame(X_features),0.)
X_pred_data = loaded_model.predict(X_test_features).astype(np.float64)

#data_frame = (rpd.read_root(utils.IO.featuresName[0],"tree", columns = branch_names)).query(cuts)
data_frame = (rpd.read_root(utils.IO.featuresName[0],"tree", columns = branch_names)).query("Jet_pt_reg>0")
#data_frame = (rpd.read_root(utils.IO.featuresName[0],"tree", columns = branch_names)) # with no cuts 

print len(data_frame)

#nTot is a multidim vector with all additional variables, dictVar is a dictionary associating a name of the variable
#to a position in the vector
nTot,dictVar = postprocessing.stackFeaturesReg(data_frame,branch_names,5)

outTag = 'output_nocuts_'
processPath=os.path.expanduser('~/HHbbgg_ETH_devel/bregression/output_root/')+outTag+utils.IO.featuresName[0].split("/")[len(utils.IO.featuresName[0].split("/"))-1]
postprocessing.saveTreeReg(processPath,dictVar,nTot,X_pred_data)


# In[19]:

import matplotlib.pyplot as plt
import training_utils as utils
import ROOT
from ROOT import gROOT
reload(utils)
reload(plotting)

#plot mc_gen/regressed_reco (from me and from Caterina)

predictions_pt = X_pred_data*nTot[:,dictVar['Jet_pt']]
true_pt = nTot[:,dictVar['Jet_mcPt']]
predictions_pt_caterina = nTot[:,dictVar['Jet_pt_reg']]

#print predictions_pt,predictions_pt_caterina,true_pt

rel_diff_regressed = true_pt/predictions_pt
rel_diff_caterina = true_pt/predictions_pt_caterina
plotting.plot_rel_pt_diff(rel_diff_regressed,rel_diff_caterina,True,50,'CaterinaComparison')


    


# In[ ]:



