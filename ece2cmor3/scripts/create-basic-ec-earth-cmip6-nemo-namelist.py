#!/usr/bin/env python
# Thomas Reerink

# Call this script by:
#  ./create-basic-ec-earth-cmip6-nemo-namelist.py
#  ./create-basic-ec-earth-cmip6-nemo-namelist.py; diff -b basic-flat-cmip6-file_def_nemo.xml bup-basic-flat-cmip6-file_def_nemo.xml; diff -b basic-cmip6-file_def_nemo.xml bup-basic-cmip6-file_def_nemo.xml

# First, this script reads the shaconemo xml ping files (the files which relate NEMO code variable
# names with CMOR names. NEMO code names which are labeled by 'dummy_' have not been identified by
# the Shaconemo comunity.
#
# Second, this script reads the four NEMO xml field_def files (the files which contain the basic info
# about the fields required by XIOS. These field_def files can either be taken from the shaconemo
# repository or from the EC-Earth repository. The four field_def files contain nearly 1200 variables
# with an id (15 id's occur twice) and about 100 variables whithout an id but with a field_ref (most
# of the latter one have an name attribute, but not all of them).
#
# Third, the NEMO only excel xlsx CMIP6 data request file is read. This file has been created
# elsewhere by checking the non-dummy NEMO shaconemo ping file cmor variable list against the
# full CMIP6 data request for all CMIP6 MIPs in which EC-Earth participates, i.e. for tier 3
# and priority 3: about 320 unique cmor-table - cmor-variable-name combinations.
#
# Fourth, a few lists are created or or/and modified, some renaming or for instance selecting the
# output frequency per field from the cmor table label.
#
# Five, the exentensive basic flat ec-earth cmip6 nemo XIOS input file template (the namelist or the
# file_def file) is written by combining all the available data. In this file for each variable the
# enable attribute is set to false, this allows another smaller program in ece2cmor3 to set those
# variables on true which are asked for in the various data requests of each individual MIP
# experiment.
#
# Six, the basic flat file_def file is read again, now all gathered info is part of this single xml
# tree which allows a more convenient way of selecting.
#
# Seven, a basic file_def is created by selecting on model component, output frequency and grid. For
# each sub selection a file element is defined.

import xml.etree.ElementTree as xmltree
import os.path                                                # for checking file existence with: os.path.isfile
import numpy as np                                            # for the use of e.g. np.multiply
from os.path import expanduser

ping_file_directory            = expanduser("~")+"/cmorize/shaconemo/ORCA1_LIM3_PISCES/EXP00/"
field_def_file_directory       = expanduser("~")+"/cmorize/shaconemo/ORCA1_LIM3_PISCES/EXP00/"
nemo_only_dr_nodummy_file_xlsx = expanduser("~")+"/cmorize/ece2cmor3/ece2cmor3/scripts/create-nemo-only-list/nemo-only-list-cmpi6-requested-variables.xlsx"
nemo_only_dr_nodummy_file_txt  = expanduser("~")+"/cmorize/ece2cmor3/ece2cmor3/scripts/create-nemo-only-list/bup-nemo-only-list-cmpi6-requested-variables.txt"


message_occurence_identical_id = True
message_occurence_identical_id = False

include_root_field_group_attributes = True
#include_root_field_group_attributes = False

exclude_dummy_fields = True
#exclude_dummy_fields = False

include_grid_ref_from_field_def_files = True
#include_grid_ref_from_field_def_files = False



################################################################################
###################################    1     ###################################
################################################################################

# READING THE PING FILES:

treeOcean     = xmltree.parse(ping_file_directory + "ping_ocean.xml")
treeSeaIce    = xmltree.parse(ping_file_directory + "ping_seaIce.xml")
treeOcnBgChem = xmltree.parse(ping_file_directory + "ping_ocnBgChem.xml")

rootOcean     = treeOcean.getroot()            # This root has two indices: the 1st index refers to field_definition-element, the 2nd index refers to the field-elements
rootSeaIce    = treeSeaIce.getroot()           # This root has two indices: the 1st index refers to field_definition-element, the 2nd index refers to the field-elements
rootOcnBgChem = treeOcnBgChem.getroot()        # This root has two indices: the 1st index refers to field_definition-element, the 2nd index refers to the field-elements

field_elements_Ocean     = rootOcean    [0][:]
field_elements_SeaIce    = rootSeaIce   [0][:]
field_elements_OcnBgChem = rootOcnBgChem[0][:]

#field_elements_Ocean     = treeOcean.getroot()    [0][:]     # This root has two indices: the 1st index refers to field_definition-element, the 2nd index refers to the field-elements
#field_elements_SeaIce    = treeSeaIce.getroot()   [0][:]     # This root has two indices: the 1st index refers to field_definition-element, the 2nd index refers to the field-elements
#field_elements_OcnBgChem = treeOcnBgChem.getroot()[0][:]     # This root has two indices: the 1st index refers to field_definition-element, the 2nd index refers to the field-elements

#Exclude the dummy_ variables from the ping list and removes the CMIP6_ prefix.
pinglistOcean_id        = []
pinglistOcean_field_ref = []
pinglistOcean_text      = []
pinglistOcean_expr      = []
for child in field_elements_Ocean:
 if exclude_dummy_fields and child.attrib["field_ref"].startswith('dummy_'):
  continue
 else:
  pinglistOcean_id.append(child.attrib["id"][6:])
  pinglistOcean_field_ref.append(child.attrib["field_ref"])
  pinglistOcean_text.append(child.text)
  if "expr" in child.attrib: pinglistOcean_expr.append(child.attrib["expr"])
  else:                      pinglistOcean_expr.append("None")

pinglistSeaIce_id        = []
pinglistSeaIce_field_ref = []
pinglistSeaIce_text      = []
pinglistSeaIce_expr      = []
for child in field_elements_SeaIce:
 if exclude_dummy_fields and child.attrib["field_ref"].startswith('dummy_'):
  continue
 else:
  pinglistSeaIce_id.append(child.attrib["id"][6:])
  pinglistSeaIce_field_ref.append(child.attrib["field_ref"])
  pinglistSeaIce_text.append(child.text)
  if "expr" in child.attrib: pinglistSeaIce_expr.append(child.attrib["expr"])
  else:                      pinglistSeaIce_expr.append("None")

pinglistOcnBgChem_id        = []
pinglistOcnBgChem_field_ref = []
pinglistOcnBgChem_text      = []
pinglistOcnBgChem_expr      = []
for child in field_elements_OcnBgChem:
 if exclude_dummy_fields and child.attrib["field_ref"].startswith('dummy_'):
  continue
 else:
  pinglistOcnBgChem_id.append(child.attrib["id"][6:])
  pinglistOcnBgChem_field_ref.append(child.attrib["field_ref"])
  pinglistOcnBgChem_text.append(child.text)
  if "expr" in child.attrib: pinglistOcnBgChem_expr.append(child.attrib["expr"])
  else:                      pinglistOcnBgChem_expr.append("None")

total_pinglist_id        = pinglistOcean_id        + pinglistSeaIce_id        + pinglistOcnBgChem_id
total_pinglist_field_ref = pinglistOcean_field_ref + pinglistSeaIce_field_ref + pinglistOcnBgChem_field_ref
total_pinglist_text      = pinglistOcean_text      + pinglistSeaIce_text      + pinglistOcnBgChem_text
total_pinglist_expr      = pinglistOcean_expr      + pinglistSeaIce_expr      + pinglistOcnBgChem_expr

if exclude_dummy_fields:
 print '\n There are ', len(total_pinglist_id), 'non-dummy variables taken from the shaconemo ping files.\n'
else:
 print '\n There are ', len(total_pinglist_id), 'variables taken from the shaconemo ping files.\n'

#print pinglistOcean_id
#print pinglistOcean_field_ref
#print pinglistOcean_text

#print rootOcean    [0][:]
#print field_elements_Ocean

#print rootOcean    [0].attrib["test"]          # Get an attribute of the parent element
#print rootOcean    [0][0].attrib["field_ref"]
#print rootOcean    [0][1].attrib["id"]
#print rootOcean    [0][:].attrib["id"]         # does not work, needs an explicit for loop

field_example = "tomint"  # Specify a cmor field name
field_example = "cfc11"  # Specify a cmor field name
index_in_ping_list = pinglistOcean_id.index(field_example)
#print index_in_ping_list, pinglistOcean_id[index_in_ping_list], pinglistOcean_field_ref[index_in_ping_list], pinglistOcean_text[index_in_ping_list]

# Create an XML file, see http://stackabuse.com/reading-and-writing-xml-files-in-python/
# mydata = xmltree.tostring(rootOcean)
# myfile = open("bla.xml", "w")
# myfile.write(mydata)


#history

#print rootOcean.attrib["id"], rootSeaIce.attrib["id"], rootOcnBgChem.attrib["id"]

#print field_elements_Ocean    [1].__dict__  # Example print of the 1st Ocean     field-element
#print field_elements_SeaIce   [1].__dict__  # Example print of the 1st SeaIce    field-element
#print field_elements_OcnBgChem[1].__dict__  # Example print of the 1st OcnBgChem field-element

#print field_elements_Ocean    [1].tag,field_elements_Ocean    [1].attrib["id"],field_elements_Ocean    [1].attrib["field_ref"],field_elements_Ocean    [1].text  # Example print of the tag and some specified attributes of the 1st Ocean     field-element
#print field_elements_SeaIce   [1].tag,field_elements_SeaIce   [1].attrib["id"],field_elements_SeaIce   [1].attrib["field_ref"],field_elements_SeaIce   [1].text  # Example print of the tag and some specified attributes of the 1st SeaIce    field-element
#print field_elements_OcnBgChem[1].tag,field_elements_OcnBgChem[1].attrib["id"],field_elements_OcnBgChem[1].attrib["field_ref"],field_elements_OcnBgChem[1].text  # Example print of the tag and some specified attributes of the 1st OcnBgChem field-element

#for field_elements in [field_elements_Ocean, field_elements_SeaIce, field_elements_OcnBgChem]:
#    for child in field_elements:
#        print child.attrib["id"], child.attrib["field_ref"], child.text

#print rootOcean[0][0].attrib["field_ref"]
#print rootOcean[0][0].text
#print rootOcean[0][1].attrib["expr"]
#print rootOcean[0][1].text



################################################################################
###################################    2     ###################################
################################################################################

# READING THE FIELD_DEF FILES:

def create_element_lists(file_name, attribute_1, attribute_2):
    tree = xmltree.parse(file_name)
    roottree = tree.getroot()
    field_elements_attribute_1  = []   # The basic list in this routine containing the id attribute values
    field_elements_attribute_2  = []   # A list corresponding with the id list containing the grid_def attribute values
    fields_without_id_name      = []   # This seperate list is created for fields which don't have an id (most of them have a name attribute, but some only have a field_ref attribute)
    fields_without_id_field_ref = []   # A corresponding list with the field_ref attribute values is created. The other list contains the name attribute values if available, otherwise the name is assumed to be identical to the field_ref value.
    attribute_overview          = []

    text_elements               = []    # A list corresponding with the id list containing the text                  values (i.e. the arithmic expressions as defined in the field_def file)
    unit_elements               = []    # A list corresponding with the id list containing the unit        attribute values
    freq_offset_elements        = []    # A list corresponding with the id list containing the freq_offset attribute values
   #print ' Number of field elements across all levels: ', len(roottree.findall('.//field[@id]')), 'for file', file_name
   #for field in roottree.findall('.//field[@id]'): print field.attrib[attribute_1]
  ##eelements = roottree.findall('.//field[@id]')                                  # This root has two indices: the 1st index refers to field_definition-element, the 2nd index refers to the field-elements
  ##for i in range(0, len(eelements)):
    for group in range(0, len(roottree)):
       #print ' Group [', roottree[group].tag, ']', group, 'of', len(roottree) - 1, 'in file:', file_name
        elements = roottree[group][:]                                             # This root has two indices: the 1st index refers to field_definition-element, the 2nd index refers to the field-elements

        # If the field element is defined outside the field_group element, i.e. one level higher in the tree:
        if roottree[group].tag != "field_group":
         if "grid_ref" in roottree[group].attrib:
         #print ' A deviating tag ', roottree[group].tag, ' is detected, and has the id:', roottree[group].attrib[attribute_1], 'and has the grid_ref:', roottree[group].attrib[attribute_2]
          field_elements_attribute_1.append(roottree[group].attrib[attribute_1])
          field_elements_attribute_2.append('grid_ref="'+roottree[group].attrib[attribute_2]+'"')
          text_elements             .append(roottree[group].text)
          if "unit"        in roottree[group].attrib: unit_elements.append(roottree[group].attrib["unit"])
          else:                                       unit_elements.append("no unit definition")
          if "freq_offset" in roottree[group].attrib: freq_offset_elements.append(roottree[group].attrib["freq_offset"])
          else:                                       freq_offset_elements.append("no freq_offset")

         else:
          if "field_ref" in roottree[group].attrib:
          #print ' A deviating tag ', roottree[group].tag, ' is detected, and has the id:', roottree[group].attrib[attribute_1], 'and has no grid_ref attribute but it has an field_ref attribute:', roottree[group].attrib["field_ref"]
           detected_field_ref = roottree[group].attrib["field_ref"]
           for field in roottree.findall('.//field[@id="'+detected_field_ref+'"]'):
            detected_grid_ref = field.attrib["grid_ref"]
            if "unit"        in field.attrib: detected_unit = field.attrib["unit"]
            else:                             detected_unit = "no unit definition"
            if "freq_offset" in field.attrib: detected_freq_offset = field.attrib["freq_offset"]
            else:                             detected_freq_offset = "no freq_offset"
           #print ' A deviating tag ', roottree[group].tag, ' is detected, and has the id:', roottree[group].attrib[attribute_1], 'and has via the field_ref:', detected_field_ref, 'the grid_ref:', detected_grid_ref, 'with unit:', detected_unit
            field_elements_attribute_1.append(roottree[group].attrib[attribute_1])
            field_elements_attribute_2.append('grid_ref="'+detected_grid_ref+'"')
            text_elements             .append(roottree[group].text)
            if "unit"        in roottree[group].attrib: unit_elements.append(roottree[group].attrib["unit"])
            else:                                       unit_elements.append(detected_unit)
            if "freq_offset" in roottree[group].attrib: freq_offset_elements.append(roottree[group].attrib["freq_offset"])
            else:                                       freq_offset_elements.append(detected_freq_offset)
            
          else:
           print ' ERROR: No field_ref and no grid_ref attribute for this variable ', roottree[group].attrib[attribute_1], ' which has no field_group element level. This element has the attributes: ', roottree[group].attrib

        # If field_group element level exists:
        for child in elements:
         if child.tag != "field": print ' At expected "field" element level, a deviating tag ',  child.tag, ' is detected.', child.attrib.keys()
         attribute_overview = attribute_overview + child.attrib.keys()  # Merge each step the next list of attribute keys with the overview list

         # If id attribute exits:
         if attribute_1 in child.attrib:
          field_elements_attribute_1.append(child.attrib[attribute_1])
         #print ' ', attribute_1, ' = ', child.attrib[attribute_1]

          text_elements.append(child.text)
          if "unit"        in child.attrib: unit_elements.append(child.attrib["unit"])
          else:                             unit_elements.append("no unit definition")
          if "freq_offset" in child.attrib: freq_offset_elements.append(child.attrib["freq_offset"]); #print child.attrib["freq_offset"], child.attrib["id"], file_name
          else:                             freq_offset_elements.append("no freq_offset")

          if attribute_2 in child.attrib:
           field_elements_attribute_2.append('grid_ref="'+child.attrib[attribute_2]+'"')
          #print ' ', attribute_2, ' = ', child.attrib[attribute_2]
          else:
           if attribute_2 in roottree[group].attrib:
            # In case the attribute is not present in th element definition, it is taken from its parent element:
           #field_elements_attribute_2.append('GRID_REF="'+roottree[group].attrib[attribute_2]+'"');
            field_elements_attribute_2.append('grid_ref="'+roottree[group].attrib[attribute_2]+'"');
           #print ' WARNING: No ', attribute_2, ' attribute for this variable: ', child.attrib[attribute_1], ' This element has the attributes: ', child.attrib
           else:
           #print ' WARNING: No ', attribute_2, ' attribute for this variable: ', child.attrib[attribute_1], ' This element has the attributes: ', roottree[group].attrib
            if 'do include domain ref' == 'do include domain ref':
            #print 'do include domain ref'
             if "domain_ref" in roottree[group].attrib:
              field_elements_attribute_2.append('domain_ref="'+roottree[group].attrib["domain_ref"]+'"')
             else:
              print ' ERROR: No ', 'domain_ref', ' attribute either for this variable: ', child.attrib[attribute_1], ' This element has the attributes: ', roottree[group].attrib
              field_elements_attribute_2.append(None)
            else:
             field_elements_attribute_2.append(None)
         else:
          # If the element has no id it should have a field_ref attribute, so checking for that:
          if "field_ref" in child.attrib:
           if "name" in child.attrib:
            fields_without_id_name.append(child.attrib["name"])
            fields_without_id_field_ref.append(child.attrib["field_ref"])
           #print ' This variable {:15} has no id but it has a field_ref = {}'.format(child.attrib["name"], child.attrib["field_ref"])
           else:
            fields_without_id_name.append(child.attrib["field_ref"])      # ASSUMPTION about XIOS logic: in case no id and no name attribute are defined inside an element, it is assumed that the value of the field_ref attribute is taken as the value of the name attribute
            fields_without_id_field_ref.append(child.attrib["field_ref"])
           #print ' This variable {:15} has no id and no name, but it has a field_ref = {:15} Its full attribute list: {}'.format('', child.attrib["field_ref"], child.attrib)
          else:
           print ' ERROR: No ', attribute_1, 'and no field_ref attribute either for this variable. This element has the attributes: ', child.attrib

   #for item in range(0,len(fields_without_id_name)):
   # print ' This variable {:15} has no id but it has a field_ref = {}'.format(fields_without_id_name[item], fields_without_id_field_ref[item])
   #print ' The length of the list with fields without an id is: ', len(fields_without_id_name)
    attribute_overview = list(set(attribute_overview))
   #print '  ', attribute_overview
    if not len(field_elements_attribute_1) == len(field_elements_attribute_2 ): print ' ERROR: The id and grid_ref list are not of equal length\n'
    if not len(fields_without_id_name    ) == len(fields_without_id_field_ref): print ' ERROR: The name and field_ref list are not of equal length\n'
    return field_elements_attribute_1, field_elements_attribute_2, fields_without_id_name, fields_without_id_field_ref, attribute_overview, text_elements, unit_elements, freq_offset_elements


field_def_nemo_opa_id     , field_def_nemo_opa_grid_ref     , no_id_field_def_nemo_opa_name     , no_id_field_def_nemo_opa_field_ref     , attribute_overview_nemo_opa     , texts_opa     , units_opa     , freq_offsets_opa      = create_element_lists(ping_file_directory + "field_def_nemo-opa.xml"     , "id", "grid_ref")
field_def_nemo_lim_id     , field_def_nemo_lim_grid_ref     , no_id_field_def_nemo_lim_name     , no_id_field_def_nemo_lim_field_ref     , attribute_overview_nemo_lim     , texts_lim     , units_lim     , freq_offsets_lim      = create_element_lists(ping_file_directory + "field_def_nemo-lim.xml"     , "id", "grid_ref")
field_def_nemo_pisces_id  , field_def_nemo_pisces_grid_ref  , no_id_field_def_nemo_pisces_name  , no_id_field_def_nemo_pisces_field_ref  , attribute_overview_nemo_pisces  , texts_pisces  , units_pisces  , freq_offsets_pisces   = create_element_lists(ping_file_directory + "field_def_nemo-pisces.xml"  , "id", "grid_ref")
field_def_nemo_inerttrc_id, field_def_nemo_inerttrc_grid_ref, no_id_field_def_nemo_inerttrc_name, no_id_field_def_nemo_inerttrc_field_ref, attribute_overview_nemo_inerttrc, texts_inerttrc, units_inerttrc, freq_offsets_inerttrc = create_element_lists(ping_file_directory + "field_def_nemo-inerttrc.xml", "id", "grid_ref")


total_field_def_nemo_id              = field_def_nemo_opa_id              + field_def_nemo_lim_id              + field_def_nemo_pisces_id              + field_def_nemo_inerttrc_id
total_field_def_nemo_grid_ref        = field_def_nemo_opa_grid_ref        + field_def_nemo_lim_grid_ref        + field_def_nemo_pisces_grid_ref        + field_def_nemo_inerttrc_grid_ref
# Note that the total name & field_ref ones are not used yet, because these cases did not occur in the set of CMIP6 data requested variables so far.
total_no_id_field_def_nemo_name      = no_id_field_def_nemo_opa_name      + no_id_field_def_nemo_lim_name      + no_id_field_def_nemo_pisces_name      + no_id_field_def_nemo_inerttrc_name
total_no_id_field_def_nemo_field_ref = no_id_field_def_nemo_opa_field_ref + no_id_field_def_nemo_lim_field_ref + no_id_field_def_nemo_pisces_field_ref + no_id_field_def_nemo_inerttrc_field_ref
total_attribute_overview_nemo_opa    = attribute_overview_nemo_opa        + attribute_overview_nemo_lim        + attribute_overview_nemo_pisces        + attribute_overview_nemo_inerttrc
# Take care the units are detected for field elements which have an id attribute:
total_texts                          = texts_opa        + texts_lim        + texts_pisces        + texts_inerttrc
total_units                          = units_opa        + units_lim        + units_pisces        + units_inerttrc
total_freq_offsets                   = freq_offsets_opa + freq_offsets_lim + freq_offsets_pisces + freq_offsets_inerttrc

#for item in range(0,len(total_no_id_field_def_nemo_name)):
# print ' This variable {:15} has no id but it has a field_ref = {}'.format(total_no_id_field_def_nemo_name[item], total_field_def_nemo_grid_ref[item])
print ' The length of the list with fields without an id is: ', len(total_no_id_field_def_nemo_name), '\n'

print ' In total there are', len(total_field_def_nemo_id), 'fields defined with an id in the field_def files,', len(total_field_def_nemo_id) - len(list(set(total_field_def_nemo_id))), 'of these id\'s occur twice.\n'

print ' The atribute overview of all field_def files:\n ', list(set(total_attribute_overview_nemo_opa)), '\n'

for text in total_texts:
 if text == None: total_texts[total_texts.index(text)] = "None"
#else:            print '{:6} {}'.format(total_texts.index(text), text)
 

#print field_def_nemo_opa_id

#print list(set(total_field_def_nemo_id))
#print list(set(total_field_def_nemo_grid_ref))
#print total_field_def_nemo_id
#print total_field_def_nemo_grid_ref


################################################################################
def check_all_list_elements_are_identical(iterator):
    iterator = iter(iterator)
    try:
        first = next(iterator)
    except StopIteration:
        return True
    return all(first == rest for rest in iterator)

get_indices = lambda x, xs: [i for (y, i) in zip(xs, range(len(xs))) if x == y]

def check_which_list_elements_are_identical(list_of_attribute_1, list_of_attribute_2):
    for child in list_of_attribute_1:
     indices_identical_ids = get_indices(child, list_of_attribute_1)
    #print len(indices_identical_ids), indices_identical_ids
     id_list       = []
     grid_ref_list = []
     for identical_child in range(0,len(indices_identical_ids)):
      id_list      .append(list_of_attribute_1[indices_identical_ids[identical_child]])
      grid_ref_list.append(list_of_attribute_2[indices_identical_ids[identical_child]])
     #print indices_identical_ids[identical_child], list_of_attribute_1[indices_identical_ids[identical_child]], list_of_attribute_2[indices_identical_ids[identical_child]]
     if not check_all_list_elements_are_identical(id_list)      : print ' WARNING: Different ids in sublist [should never occur] at positions:', indices_identical_ids, id_list
     if not check_all_list_elements_are_identical(grid_ref_list): print ' WARNING: The variable {:22} has different grid definitions, at positions: {:20} with grid: {}'.format(id_list[0] , indices_identical_ids, grid_ref_list)
     if message_occurence_identical_id and len(indices_identical_ids) > 1: print ' The variable {:22} occurs more than once, at positions: {:20} with grid: {}'.format(id_list[0] , indices_identical_ids, grid_ref_list)

#check_which_list_elements_are_identical(field_def_nemo_opa_id      , field_def_nemo_opa_grid_ref      )
#check_which_list_elements_are_identical(field_def_nemo_lim_id      , field_def_nemo_lim_grid_ref      )
#check_which_list_elements_are_identical(field_def_nemo_pisces_id   , field_def_nemo_pisces_grid_ref   )
#check_which_list_elements_are_identical(field_def_nemo_inerttrc_id , field_def_nemo_inerttrc_grid_ref )
check_which_list_elements_are_identical(total_field_def_nemo_id, total_field_def_nemo_grid_ref)

#x = [ 'w', 'e', 's', 's', 's', 'z','z', 's']
#print [i for i, n in enumerate(x) if n == 's']
################################################################################

#print tree.getroot().attrib["level"]              # example of getting an attribute value of the root  element: the field_definition element
#print tree.getroot()[0].attrib["id"]              # example of getting an attribute value of its child element: the field_group      element
#print tree.getroot()[0].attrib["grid_ref"]        # example of getting an attribute value of its child element: the field_group      element
#print field_def_nemo_opa[0].attrib["id"],         # example of getting an attribute value of its child element: the field            element
#print field_def_nemo_opa[0].attrib["grid_ref"]    # example of getting an attribute value of its child element: the field            element



################################################################################
###################################    3     ###################################
################################################################################

# READING THE NEMO DATA REQUEST FILES:

# This function can be used to read any excel file which has been produced by the checkvars.py script,
# in other words it can read the pre basic ignored, the pre basic identified missing, basic ignored,
# basic identified missing, available, ignored, identified-missing, and missing files.
def load_checkvars_excel(excel_file):
    import xlrd
    table_colname       = "Table"                                        # CMOR table name
    var_colname         = "variable"                                     # CMOR variable name
    prio_colname        = "prio"                                         # priority of variable
    dimension_colname   = "Dimension format of variable"                 # 
    longname_colname    = "variable long name"                           # 
    link_colname        = "link"                                         # 
    comment_colname     = "comment"                                      # for the purpose here: this is the model component
    author_colname      = "comment author"                               # 
    description_colname = "extensive variable description"               # 
    miplist_colname     = "list of MIPs which request this variable"     # 

    book = xlrd.open_workbook(excel_file)
    for sheetname in book.sheet_names():
        if sheetname.lower() in ["notes"]:
            continue
        sheet = book.sheet_by_name(sheetname)
        header = sheet.row_values(0)
        coldict = {}
        for colname in [table_colname, var_colname, prio_colname, dimension_colname, longname_colname, link_colname, comment_colname, description_colname, miplist_colname]:
            if colname not in header:
              print " Could not find the column: ", colname, " in the sheet", sheet, "\n in the file", excel_file, "\n"
              quit()
            coldict[colname] = header.index(colname)
        nr_of_header_lines = 2
        tablenames   = [c.value for c in sheet.col_slice(colx=coldict[table_colname      ], start_rowx = nr_of_header_lines)]
        varnames     = [c.value for c in sheet.col_slice(colx=coldict[var_colname        ], start_rowx = nr_of_header_lines)]
        varpriority  = [c.value for c in sheet.col_slice(colx=coldict[prio_colname       ], start_rowx = nr_of_header_lines)]
        vardimension = [c.value for c in sheet.col_slice(colx=coldict[dimension_colname  ], start_rowx = nr_of_header_lines)]
        varlongname  = [c.value for c in sheet.col_slice(colx=coldict[longname_colname   ], start_rowx = nr_of_header_lines)]
        weblink      = [c.value for c in sheet.col_slice(colx=coldict[link_colname       ], start_rowx = nr_of_header_lines)]
        comments     = [c.value for c in sheet.col_slice(colx=coldict[comment_colname    ], start_rowx = nr_of_header_lines)]
        description  = [c.value for c in sheet.col_slice(colx=coldict[description_colname], start_rowx = nr_of_header_lines)]
        miplist      = [c.value for c in sheet.col_slice(colx=coldict[miplist_colname    ], start_rowx = nr_of_header_lines)]
    return tablenames, varnames, varpriority, vardimension, varlongname, weblink, comments, description, miplist

# Read the excel file with the NEMO data request:
dr_table, dr_varname, dr_varprio, dr_vardim, dr_varlongname, dr_weblink, dr_ping_component, dr_description, dr_miplist = load_checkvars_excel(nemo_only_dr_nodummy_file_xlsx)

#print dr_miplist[0]



################################################################################
###################################    4     ###################################
################################################################################

# MANUPULATION, CREATION OF SOME LISTS:

################################################################################
# Convert the model component labeling in the ping file naming to the model component name in NEMO:
for element_counter in range(0,len(dr_ping_component)):
 if dr_ping_component[element_counter] == "ocean"    : dr_ping_component[element_counter] = "opa"
 if dr_ping_component[element_counter] == "seaIce"   : dr_ping_component[element_counter] = "lim"
 if dr_ping_component[element_counter] == "ocnBgChem": dr_ping_component[element_counter] = "pisces"
################################################################################


################################################################################
# Create the output_freq attribute from the table name:
table_list_of_dr = list(set(dr_table))
for table in range(0,len(table_list_of_dr)):
 if not table_list_of_dr[table] in set(["", "SImon", "Omon", "SIday", "Oyr", "Oday", "Oclim", "Ofx", "Odec"]): print "\n No rule defined for the encountered table: ", table_list_of_dr[table], "\n This probably needs an additon to the code of create-basic-ec-earth-cmip6-nemo-namelist.py.\n"

# Creating a list with the output_freq attribute and its value if a relevant value is known, otherwise omit attribute definiton:
dr_output_frequency = dr_table[:]  # Take care here: a slice copy is needed.
for table in range(0,len(dr_table)):
 if dr_table[table] == "SImon" or dr_table[table] == "Omon" : dr_output_frequency[table] = 'output_freq="mo"'  # mo stands in XIOS for monthly output
 if dr_table[table] == "SIday" or dr_table[table] == "Oday" : dr_output_frequency[table] = 'output_freq="d"'   # d  stands in XIOS for dayly   output
 if                               dr_table[table] == "Oyr"  : dr_output_frequency[table] = 'output_freq="y"'   # y  stands in XIOS for yearly  output
 if                               dr_table[table] == "Oclim": dr_output_frequency[table] = 'output_freq="mo"'  # Save "mo", then in post process average it over the climatology intervals (e.g. 30 year intervals). See: ece2cmor3/resources/tables/CMIP6_Oclim.json ece2cmor3/resources/tables/CMIP6_CV.json
 if                               dr_table[table] == "Ofx"  : dr_output_frequency[table] = 'output_freq="y"'   # fx fixed: time invariant: operation=once thus time unit might not matter
 if                               dr_table[table] == "Odec" : dr_output_frequency[table] = 'output_freq="y"'   # Save "y", then in post process average it over the decadal intervals
################################################################################


################################################################################
# Instead of pulling these attribute values from the root element, the field_group element, in the field_def files, we just define them here:
if include_root_field_group_attributes:
#root_field_group_attributes ='level="1" prec="4" operation="average" enabled=".TRUE." default_value="1.e20"'
 root_field_group_attributes ='level="1" prec="4" operation="average" default_value="1.e20"'
else:
 root_field_group_attributes =''
################################################################################



################################################################################
###################################    5     ###################################
################################################################################

# WRITING THE FLAT NEMO FILE_DEF FILE FOR CMIP6 FOR EC_EARTH:

# Below 'flat' means all fields are defined within one file element definition.
flat_nemo_file_def_xml_file = open('basic-flat-cmip6-file_def_nemo.xml','w')
flat_nemo_file_def_xml_file.write('<?xml version="1.0"?>\n\n  <file_defenition type="one_file" name="@expname@_@freq@_@startdate@_@enddate@" sync_freq="1d" min_digits="4">\n')
flat_nemo_file_def_xml_file.write('\n\n   <file_group>\n')
flat_nemo_file_def_xml_file.write('\n\n    <file>\n\n')

i = 0
number_of_field_element = 0
nr_of_missing_fields_in_field_def = 0
nr_of_available_fields_in_field_def = 0

# Looping through the NEMO data request (which is currently based on the non-dummy ping file variables). The dr_varname list contains cmor variable names.
for i in range(0, len(dr_varname)):
#print dr_varname[i], dr_varname.index(dr_varname[i]), i, dr_table[i], dr_varname[i], dr_varprio[i], dr_vardim[i], dr_ping_component[i], dr_miplist[i]
 if not dr_varname[i] == "":
  number_of_field_element = number_of_field_element + 1
  index_in_ping_list = total_pinglist_id.index(dr_varname[i])
 #print ' {:20} {:20} {:20} '.format(dr_varname[i], total_pinglist_id[index_in_ping_list])
 #if not dr_varname[i] == total_pinglist_id[index_in_ping_list]: print ' WARNING: Different names [should not occur]:', dr_varname[i], total_pinglist_id[index_in_ping_list]

  # Creating a list with the grid_ref attribute and its value as abstracted from the field_def files, otherwise omit attribute definiton:
  if include_grid_ref_from_field_def_files:
   # Adding the grid_def attribute with value (or alternatively the domain_ref attribute with value):
   if not total_pinglist_field_ref[index_in_ping_list] in total_field_def_nemo_id:
    nr_of_missing_fields_in_field_def = nr_of_missing_fields_in_field_def + 1
    print 'missing:   ', nr_of_missing_fields_in_field_def, total_pinglist_field_ref[index_in_ping_list]
   else:
    nr_of_available_fields_in_field_def = nr_of_available_fields_in_field_def + 1
   #print 'available: ', nr_of_available_fields_in_field_def, total_pinglist_field_ref[index_in_ping_list]
    index_in_field_def_list = total_field_def_nemo_id.index(total_pinglist_field_ref[index_in_ping_list])
    grid_ref = total_field_def_nemo_grid_ref[index_in_field_def_list]
   #print index_in_field_def_list, total_field_def_nemo_grid_ref[index_in_field_def_list]

    texts        = 'fdf_expression="'+total_texts       [index_in_field_def_list]+'"'  # fdf expression: field_def file expression
    units        = 'unit="'          +total_units       [index_in_field_def_list]+'"'
    freq_offsets = 'freq_offset="'   +total_freq_offsets[index_in_field_def_list]+'"'
  else:
  #grid_ref = 'grid_ref="??"'
   grid_ref = ''

 #print i, number_of_field_element, " cmor table = ", dr_table[i], " cmor varname = ", dr_varname[i], " model component = ", dr_ping_component[i], "  nemo code name = ", total_pinglist_field_ref[index_in_ping_list], "  expression = ", total_pinglist_text[index_in_ping_list], " ping idex = ", index_in_ping_list
 #print index_in_ping_list, pinglistOcean_id[index_in_ping_list], pinglistOcean_field_ref[index_in_ping_list], pinglistOcean_text[index_in_ping_list]
  #                                                                                                                                                                                                                            40,                         25,                                                               40,       32,                      20,                 15,                          60,    25,           30,                                              17,                                50,                        15,                                      22,                              14,                            110,                                       125,                                          200,    80,                                                          80,     4,                                      60,          10,   {}))
 #flat_nemo_file_def_xml_file.write('{:40} {:25} {:40} {:32} {:20} {:15} {:60} {:25} {:30} {:17} {:50} {:15} {:22} {:14} {:110} {:125} {:200} {:80} {:80} {:4} {:60} {:10} {}'.format('     <field id="CMIP6_'+dr_varname[i]+'" ', 'name="'+dr_varname[i]+'"', '  field_ref="'+total_pinglist_field_ref[index_in_ping_list]+'"', grid_ref,  dr_output_frequency[i], '  enable="False"', root_field_group_attributes, units, freq_offsets, '  field_nr="'+str(number_of_field_element)+'"', '  grid_shape="'+dr_vardim[i]+'"', 'table="'+dr_table[i]+'"', ' component="'+dr_ping_component[i]+'"', ' priority="'+dr_varprio[i]+'"', ' miplist="'+dr_miplist[i]+'"', ' longname="'+dr_varlongname[i][:113]+'"', ' description="'+dr_description[i][:180]+'"', texts, '  ping_expr="'+total_pinglist_expr[index_in_ping_list]+'"', ' > ', total_pinglist_text[index_in_ping_list], ' </field>', '\n'))
  flat_nemo_file_def_xml_file.write('{:40} {:25} {:40} {:32} {:20} {:15} {:60} {:25} {:30} {:17} {:50} {:15} {:22} {:14} {:110} {:125} {:200} {:80} {:80} {:4} {:60} {:10} {}'.format('     <field id="CMIP6_'+dr_varname[i]+'" ', 'name="'+dr_varname[i]+'"', '  field_ref="'+total_pinglist_field_ref[index_in_ping_list]+'"', grid_ref,  dr_output_frequency[i], '  enable="False"', root_field_group_attributes, units, freq_offsets, '  field_nr="'+str(number_of_field_element)+'"', '  grid_shape="'+dr_vardim[i]+'"', 'table="'+dr_table[i]+'"', ' component="'+dr_ping_component[i]+'"', ' priority="'+dr_varprio[i]+'"', ' miplist="'+dr_miplist[i]+'"', ' longname="'+dr_varlongname[i][:113]+'"', ' description="'+     '??'              +'"', texts, '  ping_expr="'+total_pinglist_expr[index_in_ping_list]+'"', ' > ', total_pinglist_text[index_in_ping_list], ' </field>', '\n'))
#else:
# print i, " Empty line" # Filter the empty lines in the xlsx between the table blocks.


flat_nemo_file_def_xml_file.write('\n\n    </file>\n')
flat_nemo_file_def_xml_file.write('\n\n   </file_group>\n')
flat_nemo_file_def_xml_file.write('\n\n  </file_defenition>\n')

flat_nemo_file_def_xml_file.close()


################################################################################
###################################    6     ###################################
################################################################################

# READING THE BASIC FLAT FILE_DEF FILE:

tree_basic_file_def             = xmltree.parse("./basic-flat-cmip6-file_def_nemo.xml")
root_basic_file_def             = tree_basic_file_def.getroot()                        # This root has two indices: the 1st index refers to field_definition-element, the 2nd index refers to the field-elements
field_elements_basic_file_def   = root_basic_file_def[0][:]
#field_elements_basic_file_def  = tree_basic_file_def.getroot()[0][:]                  # This root has two indices: the 1st index refers to field_definition-element, the 2nd index refers to the field-elements

###print ' Number of field elements across all levels: ', len(roottree.findall('.//field[@id]')), 'for file', file_name
###for field in roottree.findall('.//field[@id]'): print field.attrib[attribute_1]
###for field in root_basic_file_def.findall('.//field[@id="'+detected_field_ref+'"]'):

component_collection   = []
output_freq_collection = []
grid_ref_collection    = []
for field in root_basic_file_def.findall('.//field[@component]'):   component_collection.append(field.attrib["component"])
for field in root_basic_file_def.findall('.//field[@output_freq]'): output_freq_collection.append(field.attrib["output_freq"])
for field in root_basic_file_def.findall('.//field[@grid_ref]'):    grid_ref_collection.append(field.attrib["grid_ref"])
component_overview   = list(set(component_collection))
output_freq_overview = list(set(output_freq_collection))
grid_ref_overview    = list(set(grid_ref_collection))

#print '\n There are', len(component_overview),   ' model components to loop over:\n ',   component_overview,   '\n'
#print   ' There are', len(output_freq_overview), ' output frequencies to loop over:\n ', output_freq_overview, '\n'
#print   ' There are', len(grid_ref_overview),    ' grids to loop over:\n ',              grid_ref_overview,    '\n'



################################################################################
###################################    7     ###################################
################################################################################

# WRITING THE BASIC NEMO FILE_DEF FILE FOR CMIP6 FOR EC_EARTH:

#for field in root_basic_file_def.findall('.//field[@component="opa"]'):
#for field in root_basic_file_def.findall('.//field[@component="opa"][@output_freq="mo"][@grid_ref="grid_T_2D"]'):

basic_nemo_file_def_xml_file = open('basic-cmip6-file_def_nemo.xml','w')
basic_nemo_file_def_xml_file.write('<?xml version="1.0"?>\n\n  <file_defenition type="one_file" name="@expname@_@freq@_@startdate@_@enddate@" sync_freq="1d" min_digits="4">\n')
basic_nemo_file_def_xml_file.write('\n\n   <file_group>\n')


field_counter = 0
file_counter  = 0

# Loop over the model components: ['lim', 'opa', 'pisces']
for component_value in component_overview:

 # Loop over the output frequencies: ['y', 'mo', 'd']
 for output_freq_value in output_freq_overview:

  # Loop over the grid references: ['grid_T_3D', 'grid_V_2D', 'grid_V_3D', 'grid_T_2D', 'grid_U_2D', 'grid_transect', 'grid_W_3D', 'grid_W_2D', 'grid_U_3D', 'grid_T_SFC', 'grid_1point', 'grid_ptr_T_3basin_2D', 'grid_T_3D_ncatice', 'grid_ptr_W_3basin_3D', 'grid_transect_lim']
  for grid_ref_value in grid_ref_overview:
   number_of_fields_per_file = 0

   # Internal loop of finding the selection based on the three selection criteria: model component, output_frequency and grid reference:
   for field in root_basic_file_def.findall('.//field[@component="'+component_value+'"][@output_freq="'+output_freq_value+'"][@grid_ref="'+grid_ref_value+'"]'):
    number_of_fields_per_file = number_of_fields_per_file + 1
    field_counter = field_counter + 1
   #print ' {:7} {:20} {:10} {}'.format(field.attrib["component"], field.attrib["name"], field.attrib["output_freq"], field.attrib["grid_ref"])
   if number_of_fields_per_file != 0:
    file_counter = file_counter + 1
   #print ' Number of fields per file is {:3} for the combination: {:7} {:4} {}'.format(number_of_fields_per_file, component_value, output_freq_value, grid_ref_value)

    # Writing the file elements for the file_def file:
    basic_nemo_file_def_xml_file.write('\n\n    <file id="file{}" label="{}-{}-{}">\n\n'.format(file_counter, component_value, output_freq_value, grid_ref_value))
    # Now we know in which case we have not an empty list of fields for a certain combination, we write a file element by repeating the same search loop:
    for written_field in root_basic_file_def.findall('.//field[@component="'+component_value+'"][@output_freq="'+output_freq_value+'"][@grid_ref="'+grid_ref_value+'"]'):
    #print 'tttt'+written_field.text+'tttt'  # To figure out the spaces in the string around None
     if written_field.text == "   None                                                          " : written_field.text = ''
     basic_nemo_file_def_xml_file.write(  '     <field id={:40} name={:25} field_ref={:40} grid_ref={:32} output_freq={:20} enable="False" > {:70} </field>\n'.format('"'+written_field.attrib["id"]+'"', '"'+written_field.attrib["name"]+'"', '"'+written_field.attrib["field_ref"]+'"', '"'+written_field.attrib["grid_ref"]+'"', '"'+written_field.attrib["output_freq"]+'"', written_field.text))
    basic_nemo_file_def_xml_file.write(  '\n    </file>\n')

  #else: print ' No fields for this combination: {:7} {:4} {}'.format(component_value, output_freq_value, grid_ref_value)


basic_nemo_file_def_xml_file.write('\n\n   </file_group>\n')
basic_nemo_file_def_xml_file.write('\n\n  </file_defenition>\n')

basic_nemo_file_def_xml_file.close()

print '\n There are', field_counter, 'fields distributed over', file_counter, 'files.\n'

#print tree_basic_file_def
#print root_basic_file_def.tag                     # Shows the root file_defenition element tag
#print root_basic_file_def.attrib                  # Shows the root file_defenition element attributes
#print root_basic_file_def[0].tag                  # Shows the      file_group      element tag
#print root_basic_file_def[0].attrib               # Shows the      file_group      element attributes
#print field_elements_basic_file_def[0].tag        # Shows the      file            element tag        of the first file  element
#print field_elements_basic_file_def[0].attrib     # Shows the      file            element attributes of the first file  element
#print field_elements_basic_file_def[0][0].tag     # Shows the      field           element tag        of the first field element
#print field_elements_basic_file_def[0][0].attrib  # Shows the      field           element attributes of the first field element

#for child in field_elements_basic_file_def[0]:
# print '{:25} {:28} {:5} {:25} {:10} {}'.format(child.attrib["id"], child.attrib["field_ref"], child.attrib["output_freq"], child.attrib["grid_ref"], child.attrib["component"], child.text)

################################################################################
###################################   End    ###################################
################################################################################





# TO DO:
#  Create a nemo only for all NEMO ping variables INCLUDING ping dummy vars. Are there variables not in ping but present in data request?
#  Check: Does the most general file contain all tier, prio = 3 and include all ping dummy variables?
#  Check for name attribute occurence in case the id attribute is available in element definition, if occuring: any action?
#  Add header to file_def containing: source of column data, instruction and idea of file
#  Actually the units of the data request should be added in the excel files, and then the dr_unit should also be included in the xml file.
#  Generate the dummy latest data request based ping files. And also the ones with the merged Shaconemo content.
#  Read also the ping comment, use np.genfromtxt for that.

# DONE:
#  Read the basic-flat-cmip6-file_def_nemo.xml so all data is inside one xml tree. DONE
#  Therafter: Select on three criteria: model component (i.e. opa, lim, pisces), output frequency and (staggered) grid: create for each
#   sub group a file element in the file_def file. DONE.
#  Is it possible to read the field_def files and pull the grid_ref for each field element from the parent element? DONE
#  Add script which reads ping file xml files and write the nemo only pre basic xmls file. DONE (within this script)
#  Does the added field_def_nemo-inerttrc.xml for pisces need any additional action? DONE (not realy, just include it)
#  Add link from dr TRIED (rejected, too much effort due to string conversion.)
#  Check whether the xml field_def text, which contains the arithmetic expression, is consistent with the expression given in the ping files. DONE, i.e. this data is added in fdf_expression attribute
# 'standard_name' in the field_def files can be ignored, right? Yes, omit.
# 'long_name'     in the field_def files can be ignored because it is taken from the cmor tables, right? Yes, omit.
# 'unit'          in the field_def files can be ignored because it is taken from the cmor tables, right? Add for consistency check. DONE: quite some variables miss a unit attribute

# The <!-- Transects --> block in field_def_nemo-opa.xml has field element definitions which are defined without a file_group element,
# that means they have one element layer less. DONE: this case is now covered


# The atribute overview of all field_def files:
#  ['name', 'grid_ref', 'freq_offset', 'axis_ref', 'standard_name', 'read_access', 'long_name', 'detect_missing_value', 'field_ref', 'freq_op', 'operation', 'id', 'unit']
#  [                    'freq_offset', 'axis_ref',                  'read_access',              'detect_missing_value',              'freq_op', 'operation',     , 'unit']

# The freq_offset attribute is always inside the field element definition in the field_def files (with value: _reset_ or 1mo-2ts ):
# One occurence of the attribute in the set of Transects fields:
#  grep -iHn freq_offset field_def_nemo-* | grep -v '<field '
#  grep -iHn freq_offset field_def_nemo-* | sed -e 's/.*freq_offset="//' -e 's/".*//'
# This data has been added to the basic flat xml in the freq_offset attribute.

# The freq_op attribute is always inside the field element definition in the field_def files (always with the value: 1mo):
#  grep -iHn freq_op field_def_nemo-* | grep -v '<field '
#  grep -iHn freq_offset field_def_nemo-* | sed -e 's/.*freq_op="//' -e 's/".*//'
# This data has NOT (YET) been added to the basic flat xml.

# The detect_missing_value attribute is always inside the field element definition in the field_def files (and only present if set to true):
#  grep -iHn detect_missing_value field_def_nemo-* | grep -v '<field '
#  grep -iHn detect_missing_value field_def_nemo-* | grep -v 'detect_missing_value="true"'
# This data has NOT (YET) been added to the basic flat xml.

# The operation attribute is inside the field_definition, field_group, or field element definition in the field_def files (with
# different values: average, maximum, minimum, once, instant):
#  grep -iHn operation field_def_nemo-*
#  grep -iHn operation field_def_nemo-* | grep -v '<field_'
#  grep -iHn operation field_def_nemo-* | grep -v '<field '
#  grep -iHn operation field_def_nemo-* | sed -e 's/.*operation="//' -e 's/".*//'
# This data has NOT (YET) been added to the basic flat xml.


# One variables has the read_access attribute in the field element, but so far is not part of CMIP6 data request:
#  field_def_nemo-opa.xml:351:         <field id="uoce_e3u_vsum_e2u_op"  long_name="ocean current along i-axis * e3u * e2u summed on the vertical"  read_access="true"  freq_op="1mo"    field_ref="e2u"       unit="m3/s"> @uoce_e3u_vsum_e2u </field>
# grep -iHn read_access field_def_nemo-*

# Two variables have an additional axis_ref attribute in field element definition beside their domain_ref attribute in
# their parent group definition, but so far are not part of CMIP6 data request:
#  field_def_nemo-opa.xml:595:        <field id="berg_real_calving"  long_name="icb calving into iceberg class"                  unit="kg/s"     axis_ref="icbcla" />
#  field_def_nemo-opa.xml:596:        <field id="berg_stored_ice"    long_name="icb accumulated ice mass by class"               unit="kg"       axis_ref="icbcla" />




# # Create the xml file structure with xmltree:
# file_definition_element = xmltree.Element('file_definition')                   # Defines the root element
# file_element            = xmltree.SubElement(file_definition_element, 'file')
# field_element_1         = xmltree.SubElement(file_element, 'field')
# field_element_2         = xmltree.SubElement(file_element, 'field')
# field_element_3         = xmltree.SubElement(file_element, 'field')
# field_element_1.set('name','field 1')
# field_element_2.set('name','field 2')
# field_element_3.set('name','field 3')
# field_element_1.set('id','id field 1')
# field_element_2.set('id','id field 2')
# field_element_3.set('id','id field 3')

# # Write the xml file with xmltree:
# general_nemo_file_def_file = open("general_xios_file_def.xml", "w")
# general_nemo_file_def_file.write(xmltree.tostring(file_definition_element))

##tree = xmltree.parse('general_xios_file_def.xml')
##tree.write('newgeneral_xios_file_def.xml')

## create the file structure
#data = ET.Element('data')
#items = ET.SubElement(data, 'items')
#item1 = ET.SubElement(items, 'item')
#item2 = ET.SubElement(items, 'item')
#item1.set('name','item1')
#item2.set('name','item2')
#item1.text = 'item1abc'
#item2.text = 'item2abc'



# Below a block with an alternative way of reading the data request, i.e. instead of the excel xlsx file an ascii file is read:

# # Checking if the file exist:
# if os.path.isfile(nemo_only_dr_nodummy_file_txt) == False: print(' The  ', nemo_only_dr_nodummy_file_txt, '  does not exist.'); sys.exit(' stop')

# #data_entire_file    = np.loadtxt(nemo_only_dr_nodummy_file_txt, skiprows=2)
# # https://docs.scipy.org/doc/numpy-1.14.0/reference/generated/numpy.genfromtxt.html#numpy.genfromtxt
# data_entire_file    = np.genfromtxt(nemo_only_dr_nodummy_file_txt, dtype=None, comments='#', delimiter=None, skip_header=2, skip_footer=0, converters=None, missing_values=None, filling_values=None, usecols=None, names=None, excludelist=None, deletechars=None, replace_space='_', autostrip=False, case_sensitive=True, defaultfmt='f%i', unpack=None, usemask=False, loose=True, invalid_raise=True, max_rows=None)
# number_of_data_rows    = data_entire_file.shape[0]
# number_of_data_columns = data_entire_file.shape[1]
# #print data_entire_file[5][1] # print the element at the 6th line, 2nd column
# ##print data_entire_file[:][1] # This does not work as expected
# #print number_of_data_rows, number_of_data_columns
