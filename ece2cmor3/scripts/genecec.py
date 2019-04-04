#!/usr/bin/env python
# Thomas Reerink
#
# Run examples:
#  python genecec.py
#  mkdir -p log-genecec; ./genecec.py >& log-genecec/log-genecec-2019-v01 &
#  mkdir -p log-genecec; ./genecec.py 1> log-genecec/log-genecec-stdout-2019-v01 2> log-genecec/log-genecec-stderr-2019-v01 &
#
# Looping over all MIPs and within each MIP over all its MIP experiments.
# The experiment tier can be selected. For each selected experiment the
# namelists are created by calling the genecec-per-mip-experiment.sh script.
#
# With this script it is possible to generate the EC-Earth3 control output files, i.e.
# the IFS Fortran namelists (the ppt files), the NEMO xml files for XIOS (the
# file_def files for OPA, LIM and PISCES) and the instruction files for LPJ_GUESS (the
# *.ins files) for all MIP experiments in which EC-Earth3
# participates.
#
# This script is part of the subpackage genecec (GENerate EC-Eearth Control output files)
# which is part of ece2cmor3.

import sys
import os
from dreqPy import dreq
dq = dreq.loadDreq()

# Specify in the list below which tier experiments should be included. For
# instance [1,2] means tier 1 and tier 2 experiments are included:
experiment_tiers_included = [1]
ec_earth_mips  = ['CMIP', 'AerChemMIP', 'CDRMIP', 'C4MIP',                   'DCPP',                              'HighResMIP', 'ISMIP6', 'LS3MIP', 'LUMIP', 'OMIP', 'PAMIP', 'PMIP', 'RFMIP', 'ScenarioMIP', 'VolMIP', 'CORDEX', 'DynVar', 'SIMIP', 'VIACSAB'] # All 19 EC-Earth MIPs
#ec_earth_mips = ['CMIP', 'AerChemMIP', 'CDRMIP', 'C4MIP', 'CFMIP', 'DAMIP', 'DCPP', 'FAFMIP', 'GeoMIP', 'GMMIP', 'HighResMIP', 'ISMIP6', 'LS3MIP', 'LUMIP', 'OMIP', 'PAMIP', 'PMIP', 'RFMIP', 'ScenarioMIP', 'VolMIP', 'CORDEX', 'DynVar', 'SIMIP', 'VIACSAB'] # All 24 CMIP6 MIPs
#ec_earth_mips = ['CMIP']        # for a faster test
#ec_earth_mips = ['ScenarioMIP'] # for a faster test
experiment_counter = 0


# The list of MIPs for each of the eight EC-Earth3 model configurations which run CMIP in an iterable dictionary. This lists are needed to request the joint CMIP6 data requests
# for each of the EC-Earth3 model configurations:
cmip_ece_configurations = {
 'EC-EARTH-AOGCM'   : 'CMIP,DCPP,LS3MIP,PAMIP,RFMIP,ScenarioMIP,VolMIP,CORDEX,DynVar,SIMIP,VIACSAB',
 'EC-EARTH-HR'      : 'CMIP,DCPP,HighResMIP',
 'EC-EARTH-LR'      : 'CMIP,PMIP',
 'EC-EARTH-CC'      : 'C4MIP,CDRMIP,CMIP,LUMIP,OMIP',
 'EC-EARTH-GrisIS'  : 'CMIP,ISMIP6,PMIP',
 'EC-EARTH-AerChem' : 'AerChemMIP,CMIP',
 'EC-EARTH-Veg'     : 'CDRMIP,CMIP,LUMIP,LS3MIP,ScenarioMIP',
 'EC-EARTH-Veg-LR'  : 'CMIP,PMIP,ScenarioMIP'
}

# Some test cases:
##cmip_ece_configurations = {'EC-EARTH-AOGCM':'CMIP,DCPP,LS3MIP,PAMIP,RFMIP,ScenarioMIP,VolMIP,CORDEX,DynVar,SIMIP,VIACSAB'}
##cmip_ece_configurations = {'dummy':'dummy'}

# The list of MIPs for each of the four EC-Earth3 model configurations which run ScenarioMIP in an iterable dictionary. This lists are needed to request the joint CMIP6 data requests
# for each of the EC-Earth3 model configurations:
scenario_ece_configurations = {
 'EC-EARTH-AOGCM'   : 'CMIP,DCPP,LS3MIP,ScenarioMIP,CORDEX,DynVar,VIACSAB',
 'EC-EARTH-AerChem' : 'AerChemMIP,CMIP,ScenarioMIP',
 'EC-EARTH-Veg'     : 'CMIP,LUMIP,LS3MIP,ScenarioMIP',
 'EC-EARTH-Veg-LR'  : 'CMIP,PMIP,ScenarioMIP'
}

# Some test cases:
##scenario_ece_configurations = {'CMIP,DCPP,LS3MIP,ScenarioMIP,CORDEX,DynVar,VIACSAB'}
##scenario_ece_configurations = {'dummy':'dummy'}


# Define a dictionary which lists/maps for each MIP which EC-Earth3 model configurations are used to run the MIP:
ece_conf_mip_map = {
#'CMIP'        : ['EC-EARTH-AOGCM','EC-EARTH-HR','EC-EARTH-LR','EC-EARTH-CC','EC-EARTH-GrisIS','EC-EARTH-AerChem','EC-EARTH-Veg','EC-EARTH-Veg-LR'],
 'DCPP'        : ['EC-EARTH-AOGCM','EC-EARTH-HR'],
 'LS3MIP'      : ['EC-EARTH-AOGCM','EC-EARTH-Veg'],
 'PAMIP'       : ['EC-EARTH-AOGCM'],
 'RFMIP'       : ['EC-EARTH-AOGCM'],
 'ScenarioMIP' : ['EC-EARTH-AOGCM','EC-EARTH-Veg','EC-EARTH-Veg-LR'],
 'VolMIP'      : ['EC-EARTH-AOGCM'],
 'CORDEX'      : ['EC-EARTH-AOGCM'],
 'DynVar'      : ['EC-EARTH-AOGCM'],
 'SIMIP'       : ['EC-EARTH-AOGCM'],
 'VIACSAB'     : ['EC-EARTH-AOGCM'],
 'HighResMIP'  : ['EC-EARTH-HR'],
 'PMIP'        : ['EC-EARTH-LR','EC-EARTH-GrisIS','EC-EARTH-Veg-LR'],
 'C4MIP'       : ['EC-EARTH-CC'],
 'CDRMIP'      : ['EC-EARTH-CC','EC-EARTH-Veg'],
 'LUMIP'       : ['EC-EARTH-CC','EC-EARTH-Veg'],
 'OMIP'        : ['EC-EARTH-CC'],
 'ISMIP6'      : ['EC-EARTH-GrisIS'],
 'AerChemMIP'  : ['EC-EARTH-AerChem']
}


# Or instead of an (alphabetic) sorted dictionary an ordered dictionary could be used.
##for model_configuration in sorted(cmip_ece_configurations.keys()):
## print ' {:20}   {}'.format(model_configuration, cmip_ece_configurations[model_configuration])
##for model_configuration in sorted(scenario_ece_configurations.keys()):
## print ' {:20}   {}'.format(model_configuration, scenario_ece_configurations[model_configuration])
##sys.exit()


command_00 = 'rm -rf cmip6-output-control-files'
os.system(command_00)

# Loop over MIPs:
for mip in dq.coll['mip'].items:
  mip_name  = mip.label
  print '\n Starting to work on: ', mip_name, '\n'

 #if mip_name == 'CMIP' or mip_name == 'ScenarioMIP':
  if mip_name == 'CMIP':
   if mip_name == 'CMIP':
    ece_configurations = cmip_ece_configurations
   elif mip_name == 'ScenarioMIP':
    ece_configurations = scenario_ece_configurations
   else:
    print '\n Aborting genecec: programmer error: no case for: ', mip_name, ' in joined MIP treatment.\n'
    sys.exit()

   for model_configuration in sorted(ece_configurations.keys()):
     mip_list         = ece_configurations[model_configuration]
     mip_label        = mip_list.replace(",", ".")      # Convert the comma separated list into a dot separated list because this is what comes out from genecec-per-mip-experiment.sh
     multiplemips     = "." in mip_label
     select_substring = mip_label[0:2].lower()

    #print ' mip = '             , mip
    #print ' mip_name = '        , mip_name
    #print ' mip_list = '        , mip_list
    #print ' mip_label = '       , mip_label
    #print ' multiplemips = '    , multiplemips
    #print ' select_substring = ', select_substring
    #sys.exit()

     # Loop over experiments:
     for u in dq.inx.iref_by_sect[mip.uid].a['experiment']:
       if experiment_counter == 0:
         omit_setup_argument = ''
       else:
         omit_setup_argument = ' omit-setup'
       ex = dq.inx.uid[u]

      #command_x1 = "sed -i -e 's/True\" field_ref=\"toce_pot\"/False\" field_ref=\"toce_pot\"/' cmip6-output-control-files/" + mip_label + '/cmip6-experiment-' + mip_label + '-' + ex.label + '/file_def_nemo-opa.xml'
      #command_x2 = "sed -i -e '/sfdsi_2/d' cmip6-output-control-files/" + mip_label + '/cmip6-experiment-' + mip_label + '-' + ex.label + '/file_def_nemo-opa.xml'
       command_01 = './genecec-per-mip-experiment.sh ' + mip_list + ' ' + ex.label + ' ' + str(ex.tier[0]) + ' 1 ' + omit_setup_argument
       command_02 = 'rm -rf cmip6-output-control-files/' + mip_label + '/cmip6-experiment-*/file_def-compact'
       command_03 = 'rm -f  cmip6-output-control-files/' + mip_label + '/cmip6-experiment-*/cmip6-file_def_nemo.xml'
       command_04 = "sed -i -e 's/uoce_e3u_vsum_e2u_cumul. freq_op=.1ts/uoce_e3u_vsum_e2u_cumul/' cmip6-output-control-files/" + mip_label + '/cmip6-experiment-' + mip_label + '-' + ex.label + '/file_def_nemo-opa.xml'
       command_05 = "sed -i -e '/deptho/d' cmip6-output-control-files/" + mip_label + '/cmip6-experiment-' + mip_label + '-' + ex.label + '/file_def_nemo-opa.xml'
       command_c  = "sed -i 's/enabled=\"True\" field_ref=\"transport/enabled=\"False\" field_ref=\"transport/' cmip6-output-control-files/" + mip_name + '/cmip6-experiment-' + mip_name + '-' + ex.label + '/file_def_nemo*'
       command_07 = '      mv cmip6-output-control-files/' + mip_name + '/cmip6-experiment-' + mip_name + '-' + ex.label + '/volume-estimate-* cmip6-output-control-files/' + mip_name + '/' + model_configuration + '/cmip6-experiment-' + mip_name + '-' + ex.label + '/volume-estimate-'  + mip_name + '-' + ex.label + '-' + model_configuration + '.txt'
       command_08 = './drq2varlist.py --drq cmip6-data-request/cmip6-data-request-m=' + mip_label + '-e=' + ex.label + '-t=' + str(ex.tier[0]) + '-p=' + '1' + '/cmvme_' + select_substring + '*_' + ex.label + '_' + str(ex.tier[0]) + '_1.xlsx --ececonf ' + model_configuration + ' --varlist cmip6-output-control-files/' + mip_name + '/' + model_configuration + '/cmip6-experiment-' + mip_name + '-' + ex.label + '/cmip6-data-request-varlist-' + mip_name + '-' + ex.label + '-' + model_configuration + '.json'
       command_09 = 'mkdir -p cmip6-output-control-files/' + mip_name + '/' + model_configuration + '/cmip6-experiment-' + mip_name + '-' + ex.label + '; mv cmip6-output-control-files/' + mip_label + '/cmip6-experiment-' + mip_label + '-' + ex.label + '/*' + ' cmip6-output-control-files/' + mip_name + '/' + model_configuration + '/cmip6-experiment-' + mip_name + '-' + ex.label + '; rm -rf ' + ' cmip6-output-control-files/' + mip_label
      #print '{}'.format(command_01)
       if mip_name in ec_earth_mips:
         #if ex.tier[0] in experiment_tiers_included and ex.label == 'piControl':   # for a faster test
         #if ex.tier[0] in experiment_tiers_included and ex.label == 'historical':  # for a faster test
          if ex.tier[0] in experiment_tiers_included:
            #os.system(command_x1)  # Just set the toce fields false again because we still face troubles with them
            #os.system(command_x2)  # Delete the line with sfdsi_2 from the file_def_nemo-opa.xml files
             os.system(command_01)
             os.system(command_02)  # Remove the file_def-compact subdirectory with the compact file_def files
             os.system(command_03)  # Remove the cmip6-file_def_nemo.xml file
             os.system(command_04)  # Remove the freq_op attribute for the variable msftbarot (uoce_e3u_vsum_e2u_cumul) from the file_def_nemo.xml file
             os.system(command_05)  # Remove deptho from the file_def_nemo-opa.xml #249
             os.system(command_c)   # Switching the 'transect' variables off (the transect grid definition seems to depend on the XIOS 2.5 upgrade)
             os.system(command_07)  # Rename volume-estimate file for joint MIPs
             os.system(command_08)  # Produce the json data request variant, the so called varlist.json
             os.system(command_09)  # Rename directory names for joint MIPs
             experiment_counter = experiment_counter + 1
          else:
             print ' Tier {} experiments are not included: Skipping: {}'.format(ex.tier[0], command_01)
       else:
          print ' EC-Earth3 does not participate in {:11}: Skipping: {}'.format(mip_name, command_01)

  else:
    #print '\n Model configuration is: ', model_configuration, 'for', mip_name, ex.label, '\n'
     print '\n Reporting that ', mip_name, ' concerns a usual single MIP case'
     mip_list  = mip_name
     mip_label = mip_name
     if mip_name in ec_earth_mips:
      model_configuration = ece_conf_mip_map[mip_name]
     else:
      model_configuration = ['no-match']

     # Loop over experiments:
     for u in dq.inx.iref_by_sect[mip.uid].a['experiment']:
       if experiment_counter == 0:
         omit_setup_argument = ''
       else:
         omit_setup_argument = ' omit-setup'
       ex = dq.inx.uid[u]

      #command_x1 = "sed -i -e 's/True\" field_ref=\"toce_pot\"/False\" field_ref=\"toce_pot\"/' cmip6-output-control-files/" + mip_label + '/cmip6-experiment-' + mip_label + '-' + ex.label + '/file_def_nemo-opa.xml'
      #command_x2 = "sed -i -e '/sfdsi_2/d' cmip6-output-control-files/" + mip_label + '/cmip6-experiment-' + mip_label + '-' + ex.label + '/file_def_nemo-opa.xml'
       command_01 = './genecec-per-mip-experiment.sh ' + mip_list + ' ' + ex.label + ' ' + str(ex.tier[0]) + ' 1 ' + omit_setup_argument
       command_02 = 'rm -rf cmip6-output-control-files/' + mip_label + '/cmip6-experiment-*/file_def-compact'
       command_03 = 'rm -f  cmip6-output-control-files/' + mip_label + '/cmip6-experiment-*/cmip6-file_def_nemo.xml'
       command_04 = "sed -i -e 's/uoce_e3u_vsum_e2u_cumul. freq_op=.1ts/uoce_e3u_vsum_e2u_cumul/' cmip6-output-control-files/" + mip_label + '/cmip6-experiment-' + mip_label + '-' + ex.label + '/file_def_nemo-opa.xml'
       command_05 = "sed -i -e '/deptho/d' cmip6-output-control-files/" + mip_label + '/cmip6-experiment-' + mip_label + '-' + ex.label + '/file_def_nemo-opa.xml'
       command_c  = "sed -i 's/enabled=\"True\" field_ref=\"transport/enabled=\"False\" field_ref=\"transport/' cmip6-output-control-files/" + mip_name + '/cmip6-experiment-' + mip_name + '-' + ex.label + '/file_def_nemo*'
      #print '{}'.format(command_01)
       if mip_name in ec_earth_mips:
         #if ex.tier[0] in experiment_tiers_included and ex.label == 'ssp585':      # for a faster test
          if ex.tier[0] in experiment_tiers_included:
            #os.system(command_x1)  # Just set the toce fields false again because we still face troubles with them
            #os.system(command_x2)  # Delete the line with sfdsi_2 from the file_def_nemo-opa.xml files
             os.system(command_01)
             os.system(command_02)  # Remove the file_def-compact subdirectory with the compact file_def files
             os.system(command_03)  # Remove the cmip6-file_def_nemo.xml file
             os.system(command_04)  # Remove the freq_op attribute for the variable msftbarot (uoce_e3u_vsum_e2u_cumul) from the file_def_nemo.xml file
             os.system(command_05)  # Remove deptho from the file_def_nemo-opa.xml #249
             os.system(command_c)   # Switching the 'transect' variables off (the transect grid definition seems to depend on the XIOS 2.5 upgrade)

             # Looping over the various EC-Earth3 model configurations in order to generate for each of them the json cmip6 data request file:
             for conf in model_configuration:
              command_10 = './drq2varlist.py --drq cmip6-data-request/cmip6-data-request-m=' + mip_label + '-e=' + ex.label + '-t=' + str(ex.tier[0]) + '-p=' + '1' + '/cmvme_' + mip_name + '_' + ex.label + '_' + str(ex.tier[0]) + '_1.xlsx --ececonf ' + conf + ' --varlist cmip6-output-control-files/' + mip_name + '/cmip6-experiment-' + mip_name + '-' + ex.label + '/cmip6-data-request-varlist-' + mip_name + '-' + ex.label + '-' + conf + '.json'
              os.system(command_10) # Produce the json data request variant, the so called varlist.json

             experiment_counter = experiment_counter + 1
          else:
             print ' Tier {} experiments are not included: Skipping: {}'.format(ex.tier[0], command_01)
       else:
          print ' EC-Earth3 does not participate in {:11}: Skipping: {}'.format(mip_name, command_01)

print ' There are {} experiments included. '.format(experiment_counter)


# Add a test case with which all available variables over all EC-Earth MIP experiments are switched on,
# i.e. are enabled in the file_def files:
if os.path.isdir("cmip6-output-control-files/CMIP/EC-EARTH-AOGCM/cmip6-experiment-CMIP-piControl/"):
 command_a = "cp -r cmip6-output-control-files/CMIP/EC-EARTH-AOGCM/cmip6-experiment-CMIP-piControl/ cmip6-output-control-files/test-all-nemo-mip-variables/"
else:
 command_a = "cp -r cmip6-output-control-files/CMIP/cmip6-experiment-CMIP-piControl/ cmip6-output-control-files/test-all-nemo-mip-variables/"
command_b  = "sed -i 's/enabled=\"False\"/enabled=\"True\"/' cmip6-output-control-files/test-all-nemo-mip-variables/file_def_nemo-*"
command_c  = "sed -i 's/enabled=\"True\" field_ref=\"transport/enabled=\"False\" field_ref=\"transport/' cmip6-output-control-files/test-all-nemo-mip-variables/file_def_nemo-*"
command_d  = "echo 'This directory is intended for the maintainers only. In order to be able to test all NEMO OPA & LIM output by running one experiment, all those fields are enabled in the OPA & LIM file_def files in this directory. For the rest the control output files in this directory equal the CMIP piControl experiment.' > cmip6-output-control-files/test-all-nemo-mip-variables/README"
os.system(command_a) # Create a new subdirectory for testing all available variables in the file_def files
os.system(command_b) # Switch on all available variables in the file_def files
os.system(command_c) # Switching the 'transect' variables off (the transect grid definition seems to depend on the XIOS 2.5 upgrade)
os.system(command_d) # Add a README to the test-all-nemo-mip-variables directory
