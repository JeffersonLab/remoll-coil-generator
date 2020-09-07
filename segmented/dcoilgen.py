#!/usr/bin/env python
import csv
import sys
import os
import subprocess
import math
import time
import argparse



parser= argparse.ArgumentParser(description="Generate a segmented coil based on given parameters. Example: ./dcoilgen.py -l segmented.list -f test")
parser.add_argument("-l", dest="par_list", action="store", required=False, help="Provide the list of parameters. This is different for each of the coil types.")
parser.add_argument("-f", dest="output_file", action="store", required=False, default="DSToroid.gdml", help="Provide the required output file location")

args=parser.parse_args()
output_file=os.path.realpath(args.output_file)


p={}    # dictionary of parameter values

with open(args.par_list) as csvfile:
     reader=csv.reader(csvfile, delimiter=',', quotechar='|')
     for row in reader:
         p[row[0]]=float(row[1])

p["C_COM"]=abs(p["C1_z1_up"]-p["C4_mid_z2_up"])/2 +p["C1_z1_up"]
for i in range(1,4):
  p["C"+str(i)+"_l_arm"]= p["C"+str(i)+"_z2_up"]-p["C"+str(i)+"_z1_up"]
  p["C"+str(i)+"_rad_front"]= (p["C"+str(i)+"_x1_up"]-p["C"+str(i)+"_x1_low"])/2.0
  p["C"+str(i)+"_rad_back"]= (p["C"+str(i)+"_x2_up"]-p["C"+str(i)+"_x2_low"])/2.0
  p["C"+str(i)+"_rpos"]=p["C"+str(i)+"_x1_low"]+ p["C"+str(i)+"_rad_front"]
  p["C"+str(i)+"_zpos"]=p["C"+str(i)+"_z1_up"]+p["C"+str(i)+"_l_arm"]/2-p["C_COM"]   ## The 13000 needs to be the distance between the center of the daughter volume and the mother volume
  


for i in ["tb", "mid"]:
  p["C4_"+str(i)+"_l_arm"]= p["C4_"+str(i)+"_z2_up"]-p["C4_"+str(i)+"_z1_up"]
  p["C4_"+str(i)+"_rad_front"]= (p["C4_"+str(i)+"_x1_up"]-p["C4_"+str(i)+"_x1_low"])/2.0
  p["C4_"+str(i)+"_rad_back"]= (p["C4_"+str(i)+"_x2_up"]-p["C4_"+str(i)+"_x2_low"])/2.0
  p["C4_"+str(i)+"_rpos"]=p["C4_"+str(i)+"_x1_low"]+ p["C4_"+str(i)+"_rad_front"]
  p["C4_"+str(i)+"_zpos"]=p["C4_"+str(i)+"_z1_up"]+p["C4_"+str(i)+"_l_arm"]/2-p["C_COM"] 
print(p["C_COM"])
p["C4_rpos"]= p["C4_mid_rpos"]
p["C4_zpos"]= p["C4_mid_zpos"]
p["C4_l_arm"]=p["C4_mid_l_arm"]
r_inner_mother=0#p["C1_x1_low"]-2
r_outer_mother=p["C4_mid_x2_up"]+10
l_mother=2*( p["C_COM"] - p["C1_z1_up"])+p["C1_rad_front"]+p["C4_mid_rad_back"]+100


print("COM: "+str(p["C_COM"]))
print(r_inner_mother)
print(r_outer_mother)
print(l_mother)
print("Offset from center of mass: "+ str((-p["C1_rad_front"]+p["C4_mid_rad_back"])/2))



print("Upstream end of mother volume: "+ str((-l_mother/2+p["C_COM"])))

# photon collimator
r_inner_photon=74.22
r_outer_photon=180.22
r_extent_photon=r_outer_photon-r_inner_photon
h_inner_photon=2*17.25#2*18.25
h_outer_photon=2*54.15
r_inner_sub_photon=116.38
r_extent_sub_photon=r_outer_photon-r_inner_sub_photon
h_inner_sub_photon=2*12.75
h_outer_sub_photon=2*29.15
t_photon=70

# septapus shield
dx_septapus=6.0
dy_septapus=6.0  #18 24  Widening the septapus shield azimuthally
r_start_septapus= 35.0
r_end_septapus= 46.0  # 45 Lifting the shield up by a mm
z_start_septapus=p["C1_z1_low"]
dz_septapus= 3500.0



f=open(output_file+".gdml", "w+")


out="<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
out+="<gdml\n"
out+="\txmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\""
out+="\n\txsi:noNamespaceSchemaLocation=\"http://service-spi.web.cern.ch/service-spi/app/releases/GDML/schema/gdml.xsd\">\n"
out+="\n\n<define>"
out+="\n</define>"

out+="\n\n<materials>\n"
out+="\t<material name=\"G4_CW95\" state=\"solid\">\n"
out+="\t\t<D value=\"18.0\" unit=\"g/cm3\"/>\n"
out+="\t\t<fraction n=\"0.9500\" ref=\"G4_W\"/>\n"
out+="\t\t<fraction n=\"0.015\" ref=\"G4_Cu\"/>\n"
out+="\t\t<fraction n=\"0.035\" ref=\"G4_Ni\"/>\n"
out+="\t</material>\n"
out+="\t<material name=\"Epoxy\" state=\"solid\">\n"
out+="\t\t<D value=\"1.3\" unit=\"g/cm3\"/>\n"
out+="\t\t<fraction n=\"0.5354\" ref=\"C\"/>\n"
out+="\t\t<fraction n=\"0.1318\" ref=\"H\"/>\n"
out+="\t\t<fraction n=\"0.3328\" ref=\"O\"/>\n"
out+="\t</material>\n"
out+="\t<material name=\"G10\" state=\"solid\">\n"
out+="\t\t<D value=\"1.3\" unit=\"g/cm3\"/>\n"
out+="\t\t<fraction n=\"0.773\" ref=\"G4_SILICON_DIOXIDE\"/>\n"
out+="\t\t<fraction n=\"0.147\" ref=\"Epoxy\"/>\n"
out+="\t\t<fraction n=\"0.080\" ref=\"G4_Cl\"/>\n"
out+="\t</material>\n"
out+="</materials>\n"





out+="\n\n<solids>\n"


#photon collimator solid
out+="\n\t<xtru name=\"solid_photon_collimator\" lunit=\"mm\">"
out+="\n\t\t<twoDimVertex x=\""+str(-r_extent_photon/2)+"\" y=\""+str(h_inner_photon/2)+"\"/>"
out+="\n\t\t<twoDimVertex x=\""+str(-r_extent_photon/2)+"\" y=\""+str(-h_inner_photon/2)+"\"/>"
out+="\n\t\t<twoDimVertex x=\""+str(r_extent_photon/2)+"\" y=\""+str(-h_outer_photon/2)+"\"/>"
out+="\n\t\t<twoDimVertex x=\""+str(r_extent_photon/2)+"\" y=\""+str(-h_outer_sub_photon/2)+"\"/>"
out+="\n\t\t<twoDimVertex x=\""+str(r_extent_photon/2-r_extent_sub_photon)+"\" y=\""+str(-h_inner_sub_photon/2)+"\"/>"
out+="\n\t\t<twoDimVertex x=\""+str(r_extent_photon/2-r_extent_sub_photon)+"\" y=\""+str(h_inner_sub_photon/2)+"\"/>"
out+="\n\t\t<twoDimVertex x=\""+str(r_extent_photon/2)+"\" y=\""+str(h_outer_sub_photon/2)+"\"/>"
out+="\n\t\t<twoDimVertex x=\""+str(r_extent_photon/2)+"\" y=\""+str(h_outer_photon/2)+"\"/>"
out+="\n\t\t<section zOrder=\"1\" zPosition=\""+str(-t_photon/2)+"\" xOffset=\"0\" yOffset=\"0\" scalingFactor=\"1\"/>"
out+="\n\t\t<section zOrder=\"2\" zPosition=\""+str(t_photon/2)+"\" xOffset=\"0\" yOffset=\"0\" scalingFactor=\"1\"/>"
out+="\n\t</xtru>\n"


#septapus arm solid
out+="\n\t<xtru name=\"solid_septapus_arm\" lunit=\"mm\">"
out+="\n\t\t<twoDimVertex x=\""+str(-dx_septapus/2)+"\" y=\""+str(dy_septapus/2)+"\"/>"
out+="\n\t\t<twoDimVertex x=\""+str(-dx_septapus/2)+"\" y=\""+str(-dy_septapus/2)+"\"/>"
out+="\n\t\t<twoDimVertex x=\""+str(dx_septapus/2)+"\" y=\""+str(-dy_septapus/2)+"\"/>"
out+="\n\t\t<twoDimVertex x=\""+str(dx_septapus/2)+"\" y=\""+str(dy_septapus/2)+"\"/>"
out+="\n\t\t<section zOrder=\"1\" zPosition=\""+str(0)+"\" xOffset=\"0\" yOffset=\"0\" scalingFactor=\"1\"/>"
out+="\n\t\t<section zOrder=\"2\" zPosition=\""+str(dz_septapus)+"\" xOffset=\""+str(r_end_septapus-r_start_septapus)+"\" yOffset=\"0\" scalingFactor=\"1\"/>"
out+="\n\t</xtru>\n"

#septapus tube
out+="\n\t<tube name=\"solid_septapus_tube\" rmin=\""+str(r_start_septapus-dx_septapus/2)+"\"  rmax=\""+str(r_start_septapus+dx_septapus/2)+"\" z=\""+str(l_mother/2+(z_start_septapus-p["C_COM"]))+"\" startphi=\"0\" deltaphi=\"360\" aunit=\"deg\" lunit=\"mm\"/>\n"



for j in range(1,4):
  xoff={}
  yoff={}
  xoff["C"+str(j)]=0
  xoff["outer_E"+str(j)]= p["E_dy"]
  xoff["inner_E"+str(j)]= -p["C"+str(j)+"_dx"]
  yoff["C"+str(j)]=0
  yoff["outer_E"+str(j)]= p["E_dy"]
  yoff["inner_E"+str(j)]= 0
  for i in ["C", "outer_E","inner_E"]: 
    out+="\n\t<xtru name=\"solid_"+i+str(j)+"_mid\"  lunit=\"mm\">"
    out+="\n\t\t<twoDimVertex x=\""+str(xoff[i+str(j)]+ p["C"+str(j)+"_x2_up"]-p["C"+str(j)+"_rpos"])+"\" y=\""+str(p["C"+str(j)+"_z2_up"]-p["C"+str(j)+"_z1_up"])+"\" />"
    out+="\n\t\t<twoDimVertex x=\""+str(xoff[i+str(j)]+ p["C"+str(j)+"_x1_up"]-p["C"+str(j)+"_rpos"])+"\" y=\""+str(p["C"+str(j)+"_z1_up"]-p["C"+str(j)+"_z1_up"])+"\" />"
    out+="\n\t\t<twoDimVertex x=\""+str(-xoff[i+str(j)]+ p["C"+str(j)+"_x1_low"]-p["C"+str(j)+"_rpos"])+"\" y=\""+str(p["C"+str(j)+"_z1_low"]-p["C"+str(j)+"_z1_up"])+"\" />"
    out+="\n\t\t<twoDimVertex x=\""+str(-xoff[i+str(j)]+ p["C"+str(j)+"_x2_low"]-p["C"+str(j)+"_rpos"])+"\" y=\""+str(p["C"+str(j)+"_z2_low"]-p["C"+str(j)+"_z1_up"])+"\" />"
    out+="\n\t\t<section zOrder=\"1\" zPosition=\""+str(-yoff[i+str(j)]-p["C"+str(j)+"_dy"]/2)+"\"/>"
    out+="\n\t\t<section zOrder=\"2\" zPosition=\""+str(yoff[i+str(j)]+p["C"+str(j)+"_dy"]/2)+"\"/>"
    out+="\n\t</xtru>"
    out+="\n\t<tube name=\"solid_"+i+str(j)+"_front\" rmin=\"0\" rmax=\""+str(xoff[i+str(j)]+p["C"+str(j)+"_rad_front"])+"\" z=\""+str(2*yoff[i+str(j)]+p["C"+str(j)+"_dy"])+"\" startphi=\"0\" deltaphi=\"pi\" aunit=\"rad\" lunit=\"mm\"/>\n"
    out+="\n\t<tube name=\"solid_"+i+str(j)+"_back\" rmin=\"0\" rmax=\""+str(xoff[i+str(j)]+p["C"+str(j)+"_rad_back"])+"\" z=\""+str(2*yoff[i+str(j)]+p["C"+str(j)+"_dy"])+"\" startphi=\"0\" deltaphi=\"pi\" aunit=\"rad\" lunit=\"mm\"/>\n"
 
  
    ### Making unions
    out+="\n\t<union name=\"node_solid_"+i+str(j)+"_frontmid\">"
    out+="\n\t\t<first ref=\"solid_"+i+str(j)+"_front\"/>"
    out+="\n\t\t<second ref=\"solid_"+i+str(j)+"_mid\"/>"
    out+="\n\t\t<position name=\"position_node_solid_"+i+str(j)+"_frontmid\" y=\"0\"/>"
    out+="\n\t\t<rotation name=\"rotation_node_solid_"+i+str(j)+"_frontmid\" x=\"pi\" />"
    out+="\n\t</union>\n"

    out+="\n\t\t<union name=\"solid_"+i+str(j)+"\">"
    out+="\n\t\t\t<first ref=\"node_solid_"+i+str(j)+"_frontmid\"/>"
    out+="\n\t\t\t<second ref=\"solid_"+i+str(j)+"_back\"/>"
    out+="\n\t\t\t<position name=\"position_node_solid_"+i+str(j)+"\" x=\""+str(p["C"+str(j)+"_x2_up"]-p["C"+str(j)+"_rad_back"]-p["C"+str(j)+"_rpos"])+"\" y=\""+str(-p["C"+str(j)+"_l_arm"])+"\"/>"
    out+="\n\t\t\t<rotation name=\"rotation_node_solid_"+i+str(j)+"_back\" x=\"-pi\" />"
    out+="\n\t\t</union>\n"




for j in ["mid","tb"]:
  xoff={}
  yoff={}
  xoff["C4_"+str(j)]=0
  xoff["outer_E4_"+str(j)]= p["E_dy"]
  xoff["inner_E4_"+str(j)]= -p["C4_"+str(j)+"_dx"]
  yoff["C4_"+str(j)]=0
  if j=="mid":
    yoff["outer_E4_"+str(j)]=( 2*p["E_tb_dy"]+2*p["E_mid_dy"]+p["C4_"+str(j)+"_dy"] )/2
    print( yoff["outer_E4_"+str(j)] )
  else:
    yoff["outer_E4_"+str(j)]= p["E_dy"]/2
  yoff["inner_E4_"+str(j)]= 0
  for i in ["C4_", "outer_E4_","inner_E4_"]:
    out+="\n\t<xtru name=\"solid_"+i+str(j)+"_mid\"  lunit=\"mm\">"
    out+="\n\t\t<twoDimVertex x=\""+str(xoff[i+str(j)]+ p["C4_"+str(j)+"_x2_up"]-p["C4_"+str(j)+"_rpos"])+"\" y=\""+str(p["C4_"+str(j)+"_z2_up"]-p["C4_"+str(j)+"_z1_up"])+"\" />"
    for k in reversed(range(3,23)):
      out+="\n\t\t<twoDimVertex x=\""+str(xoff[i+str(j)]+ p["C4_"+str(j)+"_x"+str(k)+"_up"]-p["C4_"+str(j)+"_rpos"])+"\" y=\""+str(p["C4_"+str(j)+"_z"+str(k)+"_up"]-p["C4_"+str(j)+"_z1_up"])+"\" />"

    out+="\n\t\t<twoDimVertex x=\""+str(xoff[i+str(j)]+ p["C4_"+str(j)+"_x1_up"]-p["C4_"+str(j)+"_rpos"])+"\" y=\""+str(p["C4_"+str(j)+"_z1_up"]-p["C4_"+str(j)+"_z1_up"])+"\" />"
    out+="\n\t\t<twoDimVertex x=\""+str(-xoff[i+str(j)]+ p["C4_"+str(j)+"_x1_low"]-p["C4_"+str(j)+"_rpos"])+"\" y=\""+str(p["C4_"+str(j)+"_z1_low"]-p["C4_"+str(j)+"_z1_up"])+"\" />"
    for k in range(3,5):
      out+="\n\t\t<twoDimVertex x=\""+str(-xoff[i+str(j)]+ p["C4_"+str(j)+"_x"+str(k)+"_low"]-p["C4_"+str(j)+"_rpos"])+"\" y=\""+str(p["C4_"+str(j)+"_z"+str(k)+"_low"]-p["C4_"+str(j)+"_z1_up"])+"\" />"
    out+="\n\t\t<twoDimVertex x=\""+str(-xoff[i+str(j)]+ p["C4_"+str(j)+"_x2_low"]-p["C4_"+str(j)+"_rpos"])+"\" y=\""+str(p["C4_"+str(j)+"_z2_low"]-p["C4_"+str(j)+"_z1_up"])+"\" />"
    out+="\n\t\t<section zOrder=\"1\" zPosition=\""+str(-yoff[i+str(j)]-p["C4_"+str(j)+"_dy"]/2)+"\"/>"
    out+="\n\t\t<section zOrder=\"2\" zPosition=\""+str(yoff[i+str(j)]+p["C4_"+str(j)+"_dy"]/2)+"\"/>"
    out+="\n\t</xtru>"
    out+="\n\t<tube name=\"solid_"+i+str(j)+"_front\" rmin=\"0\" rmax=\""+str(xoff[i+str(j)]+p["C4_"+str(j)+"_rad_front"])+"\" z=\""+str(2*yoff[i+str(j)]+p["C4_"+str(j)+"_dy"])+"\" startphi=\"0\" deltaphi=\"pi\" aunit=\"rad\" lunit=\"mm\"/>\n"
    out+="\n\t<tube name=\"solid_"+i+str(j)+"_back\" rmin=\"0\" rmax=\""+str(xoff[i+str(j)]+p["C4_"+str(j)+"_rad_back"])+"\" z=\""+str(2*yoff[i+str(j)]+p["C4_"+str(j)+"_dy"])+"\" startphi=\"0\" deltaphi=\"pi\" aunit=\"rad\" lunit=\"mm\"/>\n"
 
    ### Making unions
    out+="\n\t<union name=\"node_solid_"+i+str(j)+"_frontmid\">"
    out+="\n\t\t<first ref=\"solid_"+i+str(j)+"_front\"/>"
    out+="\n\t\t\t<second ref=\"solid_"+i+str(j)+"_mid\"/>"
    out+="\n\t\t\t<position name=\"position_node_solid_"+i+str(j)+"_frontmid\" x=\"0\" y=\"0\" z=\""+str(0)+"\"/>"
    out+="\n\t\t\t<rotation name=\"rotation_node_solid_"+i+str(j)+"_frontmid\" x=\"pi\" y=\"0\" z=\"0\"/>"
    out+="\n\t\t</union>\n"

    out+="\n\t\t<union name=\"solid_"+i+str(j)+"\">"
    out+="\n\t\t\t<first ref=\"node_solid_"+i+str(j)+"_frontmid\"/>"
    out+="\n\t\t\t<second ref=\"solid_"+i+str(j)+"_back\"/>"
    out+="\n\t\t\t<position name=\"position_node_solid_"+i+str(j)+"_back\" x=\""+str(p["C4_"+str(j)+"_x2_up"]-p["C4_"+str(j)+"_rad_back"]-p["C4_"+str(j)+"_rpos"])+"\" y=\""+str(-p["C4_"+str(j)+"_l_arm"])+"\"/>"
    out+="\n\t\t\t<rotation name=\"rotation_node_solid_"+i+str(j)+"_back\" x=\"-pi\" y=\"0\" z=\"0\"/>"
    out+="\n\t\t</union>\n"
    

pancake_solid={}
pancake_ypos={}
pancake_zpos={}
pancake_solid["top"]="tb"
pancake_solid["mid"]="mid"
pancake_solid["bot"]="tb"
pancake_zpos["top"]=p["C4_mid_dy"]+p["E_mid_dy"]+p["E_tb_dy"]+p["C4_tb_dy"]/2+p["E_dy"]/2
pancake_zpos["mid"]=0
pancake_zpos["bot"]=-pancake_zpos["top"]
pancake_ypos["mid"]=0
#pancake_ypos["top"]= abs(p["C4_tb_l_arm"]/2-p["C4_mid_l_arm"]/2)-abs(p["C4_mid_rad_front"]-p["C4_tb_rad_front"])



pancake_ypos["top"]= p["C4_mid_rad_front"]-p["C4_tb_rad_front"]
pancake_ypos["bot"]=pancake_ypos["top"]


##### Making the outer logical volume for coil 4
out+="\n\t<union name=\"solid_outer_E4_submodule\">"
out+="\n\t\t<first ref=\"solid_outer_E4_mid\"/>"
out+="\n\t\t<second ref=\"solid_outer_E4_tb\"/>"
out+="\n\t\t<position name=\"position\"  x=\""+str(0)+"\" y=\""+str(pancake_ypos["top"])+"\" z=\""+str(pancake_zpos["top"])+"\"/>"
out+="\n\t</union>"


out+="\n\t<union name=\"solid_outer_E4\">"
out+="\n\t\t<first ref=\"solid_outer_E4_submodule\"/>"
out+="\n\t\t<second ref=\"solid_outer_E4_tb\"/>"
out+="\n\t\t<position name=\"position\"  x=\""+str(0)+"\" y=\""+str(pancake_ypos["bot"])+"\" z=\""+str(pancake_zpos["bot"])+"\"/>"
out+="\n\t</union>"




print("offset:" +str(pancake_ypos["top"])+"\n")


### Downstream toroid mother
out+="\n\t<tube name=\"solid_DS_toroidMother\" rmin=\""+str(r_inner_mother)+"\"  rmax=\""+str(r_outer_mother)+"\" z=\""+str(l_mother)+"\" startphi=\"0\" deltaphi=\"360\" aunit=\"deg\" lunit=\"mm\"/>\n"


out+="\n</solids>\n"

out+="\n\n<structure>\n"


out+="\n\t<volume name=\"logic_septapus_tube\">"
out+="\n\t\t<materialref ref=\"G4_W\"/>"
out+="\n\t\t<solidref ref=\"solid_septapus_tube\"/>"
out+="\n\t\t<auxiliary auxtype=\"SensDet\" auxvalue=\"coilDet\"/>"
out+="\n\t\t<auxiliary auxtype=\"DetNo\" auxvalue=\""+str(56)+"\"/>"
out+="\n\t</volume>\n"

for i in range(1,8):
   #Setting up photon collimator
   out+="\n\t<volume name=\"logic_photon_collimator_"+str(i)+"\">"
   out+="\n\t\t<materialref ref=\"G4_CW95\"/>"
   out+="\n\t\t<solidref ref=\"solid_photon_collimator\"/>"
   out+="\n\t\t<auxiliary auxtype=\"SensDet\" auxvalue=\"coilDet\"/>"
   out+="\n\t\t<auxiliary auxtype=\"DetNo\" auxvalue=\""+str(2005)+"\"/>"
   out+="\n\t</volume>\n"

   out+="\n\t<volume name=\"logic_septapus_arm_"+str(i)+"\">"
   out+="\n\t\t<materialref ref=\"G4_W\"/>"
   out+="\n\t\t<solidref ref=\"solid_septapus_arm\"/>"
   out+="\n\t\t<auxiliary auxtype=\"SensDet\" auxvalue=\"coilDet\"/>"
   out+="\n\t\t<auxiliary auxtype=\"DetNo\" auxvalue=\""+str(56)+"\"/>"
   out+="\n\t</volume>\n"


   ### Setting up coils
   for j in range(1,4):
        out+="\n\t<volume name=\"logic_inner_E"+str(j)+"_"+str(i)+"\">"
        out+="\n\t\t<materialref ref=\"G10\"/>"
        out+="\n\t\t<solidref ref=\"solid_inner_E"+str(j)+"\"/>"
        out+="\n\t\t<auxiliary auxtype=\"Color\" auxvalue=\"orange\"/>"
        out+="\n\t\t<auxiliary auxtype=\"SensDet\" auxvalue=\"coilDet\"/>"
        out+="\n\t\t<auxiliary auxtype=\"DetNo\" auxvalue=\""+str(3007+i)+"\"/>"
        out+="\n\t</volume>\n"

        out+="\n\t<volume name=\"logic_C"+str(j)+"_"+str(i)+"\">"
        out+="\n\t\t<materialref ref=\"G4_Cu\"/>"
        out+="\n\t\t<solidref ref=\"solid_C"+str(j)+"\"/>"
        out+="\n\t\t<auxiliary auxtype=\"Color\" auxvalue=\"magenta\"/>"
        out+="\n\t\t<auxiliary auxtype=\"SensDet\" auxvalue=\"coilDet\"/>"
        out+="\n\t\t<auxiliary auxtype=\"DetNo\" auxvalue=\""+str(3000+i)+"\"/>"
        out+="\n\t\t\t<physvol name=\"inner_E"+str(j)+"\">"
        out+="\n\t\t\t\t<volumeref ref=\"logic_inner_E"+str(j)+"_"+str(i)+"\"/>"
        out+="\n\t\t\t\t<rotation name=\"rot_inner_E\" y=\"0\" aunit=\"rad\" />"
        out+="\n\t\t\t</physvol>\n"
        out+="\n\t</volume>\n"

        out+="\n\t<volume name=\"logic_outer_E"+str(j)+"_"+str(i)+"\">"
        out+="\n\t\t<materialref ref=\"G10\"/>"
        out+="\n\t\t<solidref ref=\"solid_outer_E"+str(j)+"\"/>"
        out+="\n\t\t<auxiliary auxtype=\"Color\" auxvalue=\"orange\"/>"
        out+="\n\t\t<auxiliary auxtype=\"SensDet\" auxvalue=\"coilDet\"/>"
        out+="\n\t\t<auxiliary auxtype=\"DetNo\" auxvalue=\""+str(3007+i)+"\"/>"
        out+="\n\t\t\t<physvol name=\"C"+str(j)+"\">"
        out+="\n\t\t\t\t<volumeref ref=\"logic_C"+str(j)+"_"+str(i)+"\"/>"
        out+="\n\t\t\t</physvol>\n"
        out+="\n\t</volume>\n"



   realsol={}
   realypos={}
   realzpos={}
   realsol["top"]="tb"
   realsol["topmid"]="mid"
   realsol["botmid"]="mid"
   realsol["bot"]="tb"
   realzpos["top"]=p["C4_mid_dy"]+p["E_mid_dy"]+p["E_tb_dy"]+p["C4_tb_dy"]/2
   realzpos["topmid"]=p["C4_mid_dy"]/2+p["E_mid_dy"]
   realzpos["botmid"]=-realzpos["topmid"]
   realzpos["bot"]= -realzpos["top"]
   realypos["topmid"]=0
   realypos["botmid"]=0
 #  realypos["top"]=   abs(p["C4_tb_l_arm"]/2-p["C4_mid_l_arm"]/2)-abs(p["C4_mid_rad_front"]-p["C4_tb_rad_front"])
   realypos["top"]= p["C4_mid_rad_front"]-p["C4_tb_rad_front"]

   realypos["bot"]=realypos["top"]


   for j in ["top", "topmid", "botmid", "bot"]:
        out+="\n\t<volume name=\"logic_inner_E4_"+str(j)+"_"+str(i)+"\">"
        out+="\n\t\t<materialref ref=\"G10\"/>"
        out+="\n\t\t<solidref ref=\"solid_inner_E4_"+str(realsol[j])+"\"/>"
        out+="\n\t\t<auxiliary auxtype=\"Color\" auxvalue=\"orange\"/>"
        out+="\n\t\t<auxiliary auxtype=\"SensDet\" auxvalue=\"coilDet\"/>"
        out+="\n\t\t<auxiliary auxtype=\"DetNo\" auxvalue=\""+str(3007+i)+"\"/>"
        out+="\n\t</volume>\n"

        out+="\n\t<volume name=\"logic_C4_"+str(j)+"_"+str(i)+"\">"
        out+="\n\t\t<materialref ref=\"G4_Cu\"/>"
        out+="\n\t\t<solidref ref=\"solid_C4_"+str(realsol[j])+"\"/>"
        out+="\n\t\t<auxiliary auxtype=\"Color\" auxvalue=\"magenta\"/>"
        out+="\n\t\t<auxiliary auxtype=\"SensDet\" auxvalue=\"coilDet\"/>"
        out+="\n\t\t<auxiliary auxtype=\"DetNo\" auxvalue=\""+str(3000+i)+"\"/>"
        out+="\n\t\t\t<physvol name=\"inner_E4_"+str(j)+"\">"
        out+="\n\t\t\t\t<volumeref ref=\"logic_inner_E4_"+str(j)+"_"+str(i)+"\"/>"
        out+="\n\t\t\t\t<rotation name=\"rot_inner_E4_\" y=\"0\" aunit=\"rad\" />"
        out+="\n\t\t\t</physvol>\n"
        out+="\n\t</volume>\n"


   out+="\n\t<volume name=\"logic_outer_E4_"+str(i)+"\">"
   out+="\n\t\t<materialref ref=\"G10\"/>"
   out+="\n\t\t<solidref ref=\"solid_outer_E4\"/>"
   out+="\n\t\t<auxiliary auxtype=\"Color\" auxvalue=\"orange\"/>"
   out+="\n\t\t<auxiliary auxtype=\"SensDet\" auxvalue=\"coilDet\"/>"
   out+="\n\t\t<auxiliary auxtype=\"DetNo\" auxvalue=\""+str(3007+i)+"\"/>"

   
   for j in ["top", "bot", "topmid","botmid"]:
      out+="\n\t\t\t<physvol name=\"C4_"+str(j)+"\">"
      out+="\n\t\t\t\t<volumeref ref=\"logic_C4_"+str(j)+"_"+str(i)+"\"/>"
      out+="\n\t\t\t\t<position name=\"pos_logic_C4_"+str(j)+"_"+str(i)+"\" y=\""+str(realypos[j])+"\" z=\""+str(realzpos[j])+"\"/>"
      out+="\n\t\t\t</physvol>\n"

   out+="\n\t</volume>\n"




out+="\n\t<volume name=\"DS_toroidMother\">"
out+="\n\t\t<materialref ref=\"G4_Galactic\"/>"
out+="\n\t\t<solidref ref=\"solid_DS_toroidMother\"/>"
out+="\n\t\t<auxiliary auxtype=\"Alpha\" auxvalue=\"0.0\"/>"


for i in range(1,8):
   for j in range(1,5):
        rpos=p["C"+str(j)+"_rpos"]
        theta=2*(i-1)*math.pi/7
        xpos=rpos*(math.cos(theta))
        ypos=rpos*(math.sin(theta))
        zpos= p["C"+str(j)+"_zpos"]- p["C"+str(j)+"_l_arm"]/2

        out+="\n\t\t<physvol name=\"dcoil"+str(j)+"_"+str(i)+"\">"
        out+="\n\t\t\t<volumeref ref=\"logic_outer_E"+str(j)+"_"+str(i)+"\"/>"
        out+="\n\t\t\t<position name=\"pos_dcoil"+str(j)+"_"+str(i)+"\" x=\""+str(xpos)+"\" y=\""+str(ypos)+"\" z=\""+str(zpos)+"\"/>"
        out+="\n\t\t\t<rotation name=\"rot_dcoil"+str(j)+"_"+str(i)+"\" x=\"pi/2\" y=\""+str(theta)+"\" z=\""+str(0)+"\"/>"
        out+="\n\t\t</physvol>\n"


   rpos=r_inner_photon+r_extent_photon/2
   theta=2*i*math.pi/7+2*math.pi/14
   xpos=rpos*(math.cos(theta))
   ypos=rpos*(math.sin(theta))
   zpos=12835-p["C_COM"]
   print(rpos)
   out+="\n\t\t<physvol name=\"photon_collimator_"+str(i)+"\">"
   out+="\n\t\t\t<volumeref ref=\"logic_photon_collimator_"+str(i)+"\"/>"
   out+="\n\t\t\t<position name=\"pos_photon_collimator_"+str(i)+"\" x=\""+str(xpos)+"\" y=\""+str(ypos)+"\" z=\""+str(zpos)+"\"/>"
   out+="\n\t\t\t<rotation name=\"rot_photon_collimator_"+str(i)+"\" x=\""+str(0)+"\" y=\"0\" z=\""+str(-theta)+"\"/>"
   out+="\n\t\t</physvol>\n"

   rpos=r_start_septapus
   theta=2*i*math.pi/7
   xpos=rpos*(math.cos(theta))
   ypos=rpos*(math.sin(theta))
   zpos=z_start_septapus-p["C_COM"]
   print(rpos)
   out+="\n\t\t<physvol name=\"septapus_arm_"+str(i)+"\">"
   out+="\n\t\t\t<volumeref ref=\"logic_septapus_arm_"+str(i)+"\"/>"
   out+="\n\t\t\t<position name=\"pos_septapus_arm_"+str(i)+"\" x=\""+str(xpos)+"\" y=\""+str(ypos)+"\" z=\""+str(zpos)+"\"/>"
   out+="\n\t\t\t<rotation name=\"rot_septapus_arm_"+str(i)+"\" x=\""+str(0)+"\" y=\"0\" z=\""+str(-theta)+"\"/>"
   out+="\n\t\t</physvol>\n"


out+="\n\t\t<physvol name=\"septapus_tube\">"
out+="\n\t\t\t<volumeref ref=\"logic_septapus_tube\"/>"
out+="\n\t\t\t<position name=\"pos_septapus_tube\" x=\""+str(0)+"\" y=\""+str(0)+"\" z=\""+str(z_start_septapus-p["C_COM"]-((z_start_septapus-p["C_COM"])+l_mother/2)/2)+"\"/>"
out+="\n\t\t</physvol>\n"




out+="\n\t</volume>\n"
out+="\n</structure>\n"



out+="\n<setup name=\"DS_toroidWorld\" version=\"1.0\">"
out+="\n\t<world ref=\"DS_toroidMother\"/>"
out+="\n</setup>\n"

out+="\n</gdml>"

f.write(out)

