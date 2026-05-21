#### Wrapper Script
# Wrapper script for the multi-layer sphere model.
#
# DD 5/2026
import numpy as np
clear('all')
close_('all')
start_time = tic
## 0. Set Engine Paths
addpath(genpath(fullfile('..','..','MatlabEngines')))
## 1. Setup Model
# -- Define EM constants
eps0 = 8.85418782e-12

mu0 = 1.25663706e-06

# -- Load model
bem01_load_model
## 2. Set up dipoles
# Dipole positions are incorporated throught the primary field.
plot_tissue = 1

viewax = np.array([- 120,20])
bem01_setup_dipoles