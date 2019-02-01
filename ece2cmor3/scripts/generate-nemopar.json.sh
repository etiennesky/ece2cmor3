#!/bin/bash
# Thomas Reerink
#
# This scripts requires 1 argument:
#
# ${1} the first argument is the ouput file: the new nemopar.json file.
#
# Run example:
#  ./generate-nemopar.json.sh new-nemopar.json
#

# The default example list for this moment could be produced by running:
#  more nemopar.json |grep -e target | sed -e 's/.*://'
# And pasting the result here in the arr array.

# The current list is in the arr array is produced by running:
#  more ${HOME}/cmorize/shaconemo/ping-files/r270/cmor-varlist-based-on-ping-r270-without-dummy-lines.txt | sed -e 's/^/"/'  -e 's/$/"/' > tmp-nemopar-list.txt
# And pasting the result here.

# Declare an array variable with all the nemo cmor variable names:
declare -a arr=(
"agessc"
"areacello"
"basin"
"bigthetao"
"bigthetaoga"
"cfc11"
"cfc12"
"deptho"
"diftrblo2d"
"diftrelo2d"
"diftrxylo2d"
"difvho"
"difvmo"
"difvmto"
"difvso"
"difvtrto"
"dispkevfo"
"dispkexyfo2d"
"evs"
"fgcfc11"
"fgcfc12"
"fgsf6"
"ficeberg2d"
"flandice"
"friver"
"fsitherm"
"hcont300"
"hfbasin"
"hfbasinpmadv"
"hfcorr"
"hfds"
"hfevapds"
"hfgeou"
"hfibthermds2d"
"hflso"
"hfrainds"
"hfrunoffds2d"
"hfsnthermds2d"
"hfsso"
"hfx"
"hfy"
"htovgyre"
"htovovrt"
"masscello"
"masso"
"mfo"
"mlotst"
"mlotstmax"
"mlotstmin"
"mlotstsq"
"msftbarot"
"msftyz"
"obvfsq"
"ocontempdiff"
"ocontemppadvect"
"ocontemppmdiff"
"ocontemprmadvect"
"ocontemptend"
"omldamax"
"osaltdiff"
"osaltpadvect"
"osaltpmdiff"
"osaltrmadvect"
"osalttend"
"pbo"
"pso"
"rlntds"
"rsdo"
"rsntds"
"sf6"
"sfdsi"
"sftof"
"sltbasin"
"sltnortha"
"sltovgyre"
"sltovovrt"
"so"
"sob"
"soga"
"somint"
"sos"
"sosga"
"sossq"
"t20d"
"tauuo"
"tauvo"
"thetao"
"thetaoga"
"thetaot"
"thetaot2000"
"thetaot300"
"thetaot700"
"thkcello"
"tnkebto2d"
"tnpeo"
"tob"
"tos"
"tosga"
"tossq"
"umo"
"uo"
"vmo"
"vo"
"volo"
"wfcorr"
"wfo"
"wfonocorr"
"wmo"
"wo"
"zhalfo"
"zos"
"zossq"
"zostoga"
"bfe"
"bfeos"
"bsi"
"bsios"
"calc"
"calcos"
"chl"
"chldiat"
"chldiatos"
"chlmisc"
"chlmiscos"
"chlos"
"co3"
"co3os"
"co3satcalc"
"co3satcalcos"
"dcalc"
"detoc"
"detocos"
"dfe"
"dfeos"
"dissic"
"dissicnatos"
"dissicos"
"dissoc"
"dissocos"
"dpco2"
"dpo2"
"epc100"
"epcalc100"
"epfe100"
"epsi100"
"expc"
"expcalc"
"expfe"
"expn"
"expp"
"expsi"
"fbddtalk"
"fbddtdic"
"fbddtdife"
"fbddtdin"
"fbddtdip"
"fbddtdisi"
"fgco2"
"fgo2"
"fric"
"frn"
"froc"
"fsfe"
"fsn"
"graz"
"intdic"
"intdoc"
"intpbfe"
"intpbsi"
"intpcalcite"
"intpn2"
"intpp"
"intppcalc"
"intppdiat"
"intppmisc"
"intppnitrate"
"limfediat"
"limfemisc"
"limirrdiat"
"limirrmisc"
"limndiaz"
"limnmisc"
"nh4"
"nh4os"
"no3"
"no3os"
"o2"
"o2min"
"o2os"
"pbfe"
"pbsi"
"pcalc"
"ph"
"phos"
"phyc"
"phycos"
"phydiat"
"phydiatos"
"phyfe"
"phyfeos"
"phymisc"
"phymiscos"
"physi"
"physios"
"pnitrate"
"po4"
"po4os"
"pp"
"ppdiat"
"ppmisc"
"ppos"
"remoc"
"si"
"sios"
"spco2"
"talk"
"talknatos"
"talkos"
"zmeso"
"zmesoos"
"zmicro"
"zmicroos"
"zo2min"
"zooc"
"zoocos"
"siage"
"siareaacrossline"
"siarean"
"siareas"
"sicompstren"
"siconc"
"sidconcdyn"
"sidconcth"
"sidivvel"
"sidmassdyn"
"sidmassevapsubl"
"sidmassgrowthbot"
"sidmassgrowthwat"
"sidmassmeltbot"
"sidmassmelttop"
"sidmasssi"
"sidmassth"
"sidmasstranx"
"sidmasstrany"
"siextentn"
"siextents"
"sifb"
"siflcondbot"
"siflcondtop"
"siflfwbot"
"siflfwdrain"
"siflsensupbot"
"siflswdtop"
"siforcecoriolx"
"siforcecorioly"
"siforceintstrx"
"siforceintstry"
"siforcetiltx"
"siforcetilty"
"sihc"
"siitdconc"
"siitdsnthick"
"siitdthick"
"simass"
"simassacrossline"
"sisali"
"sisaltmass"
"sishevel"
"sisnhc"
"sisnmass"
"sisnthick"
"sispeed"
"sistremax"
"sistresave"
"sistrxdtop"
"sistrxubot"
"sistrydtop"
"sistryubot"
"sitempbot"
"sitempsnic"
"sitemptop"
"sithick"
"sitimefrac"
"siu"
"siv"
"sivol"
"sivoln"
"sivols"
"sndmassdyn"
"sndmassmelt"
"sndmasssi"
"sndmasssnf"
"sndmasssubl"
"snmassacrossline"
)


function add_item {
 echo '    {'                     >> ${output_file}
 echo '        "source": "'$1'",' >> ${output_file}
 echo '        "target": "'$1'"'  >> ${output_file}
 echo '    },'                    >> ${output_file}
}

function add_last_item {
 echo '    {'                     >> ${output_file}
 echo '        "source": "'$1'",' >> ${output_file}
 echo '        "target": "'$1'"'  >> ${output_file}
 echo '    }'                     >> ${output_file}
}


if [ "$#" -eq 1 ]; then
 output_file=$1


 echo '['                         > ${output_file}

 # Loop through the array with all the nemo cmor variable names:
 # (Note individual array elements can be accessed by using "${arr[0]}", "${arr[1]}")
 
 N=${#arr[@]} # array length
 last_item="${arr[N-1]}"
#echo ${N} ${last_item}
 for i in "${arr[@]}"
 do
    if [ "$i" == ${last_item} ]; then
     add_last_item "$i"
    else
     add_item "$i"
    fi
 done

 echo ']'                         >> ${output_file}


 echo ' The file ' ${output_file} ' is created.'

else
    echo '  '
    echo '  This scripts requires one argument, e.g.:'
    echo '  ' $0 new-nemopar.json
    echo '  '
fi
