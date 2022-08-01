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

for i in ["mid"]:
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
r_outer_mother=p["C4_mid_x4_up"]+10
l_mother=2*( p["C_COM"] - p["C1_z1_up"])+p["C1_rad_front"]+p["C4_mid_rad_back"]+100

print("COM: "+str(p["C_COM"]))
print(r_inner_mother)
print(r_outer_mother)
print(l_mother)
print("Offset from center of mass: "+ str((-p["C1_rad_front"]+p["C4_mid_rad_back"])/2))

print("Upstream end of mother volume: "+ str((-l_mother/2+p["C_COM"])))

# Epoxy protector
epoxy_protector_beginz = [10001.227, 11038.541, 12097.0, 12500.0, 13096.987]
epoxy_protector_endz = [10857.536, 11874.961, 12500.0, 12844.81]
epoxy_protector_rmin = [38, 40.5, 43, 44.2]
epoxy_protector_rmax = [41, 43.5, 46, 46]
epoxy_protector_dph= [p["C1_dy"]+2*p["E_dy"], p["C2_dy"]+2*p["E_dy"], p["C3_dy"]+2*p["E_dy"], p["C3_dy"]+2*p["E_dy"]]
epoxy_protector_zpos = [epoxy_protector_beginz[i] for i in range(0,5)]

epoxy_protector_subcoil4_rmin = 52.808
epoxy_protector_subcoil4_rmax = 55.808
epoxy_protector_subcoil4_dph = 2*(p["C4_mid_dy"]+p["E_dy"]+p["E_mid_dy"])
epoxy_protector_subcoil4_sectionr = [56.808, 78.652, 160.138, 129.02]
epoxy_protector_subcoil4_relsectionr = [epoxy_protector_subcoil4_sectionr[i]-epoxy_protector_subcoil4_sectionr[0] for i in range(0,4)]
epoxy_protector_subcoil4_sectionz = [13096.987, 14763.020, 16115.011, 16664.245]
epoxy_protector_subcoil4_relsectionz = [epoxy_protector_subcoil4_sectionz[i]-epoxy_protector_subcoil4_sectionz[0] for i in range(0,4)]
           
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
    out+="\n\t\t<section zOrder=\"1\" zPosition=\""+str(-yoff[i+str(j)]-p["C"+str(j)+"_dy"]/2)+"\" xOffset=\"0\" yOffset=\"0\" scalingFactor=\"1\"/>"
    out+="\n\t\t<section zOrder=\"2\" zPosition=\""+str(yoff[i+str(j)]+p["C"+str(j)+"_dy"]/2)+"\" xOffset=\"0\" yOffset=\"0\" scalingFactor=\"1\"/>"
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

for j in ["mid"]:
  xoff={}
  yoff={}
  xoff["C4_"+str(j)]=0
  xoff["outer_E4_"+str(j)]= p["E_dy"]
  xoff["inner_E4_"+str(j)]= -p["C4_"+str(j)+"_dx"]
  yoff["C4_"+str(j)]=0
  if j=="mid":
    yoff["outer_E4_"+str(j)]=(2*p["E_mid_dy"]+2*p["E_dy"]+p["C4_"+str(j)+"_dy"] )/2
    print(yoff["outer_E4_"+str(j)])
  yoff["inner_E4_"+str(j)]= 0
  for i in ["C4_", "outer_E4_","inner_E4_"]:
    out+="\n\t<xtru name=\"solid_"+i+str(j)+"_mid\"  lunit=\"mm\">"
    out+="\n\t\t<twoDimVertex x=\""+str(xoff[i+str(j)]+ p["C4_"+str(j)+"_x2_up"]-p["C4_"+str(j)+"_rpos"])+"\" y=\""+str(p["C4_"+str(j)+"_z2_up"]-p["C4_"+str(j)+"_z1_up"])+"\" />"
    for k in reversed(range(3,24)):
      out+="\n\t\t<twoDimVertex x=\""+str(xoff[i+str(j)]+ p["C4_"+str(j)+"_x"+str(k)+"_up"]-p["C4_"+str(j)+"_rpos"])+"\" y=\""+str(p["C4_"+str(j)+"_z"+str(k)+"_up"]-p["C4_"+str(j)+"_z1_up"])+"\" />"

    out+="\n\t\t<twoDimVertex x=\""+str(xoff[i+str(j)]+ p["C4_"+str(j)+"_x1_up"]-p["C4_"+str(j)+"_rpos"])+"\" y=\""+str(p["C4_"+str(j)+"_z1_up"]-p["C4_"+str(j)+"_z1_up"])+"\" />"
    out+="\n\t\t<twoDimVertex x=\""+str(-xoff[i+str(j)]+ p["C4_"+str(j)+"_x1_low"]-p["C4_"+str(j)+"_rpos"])+"\" y=\""+str(p["C4_"+str(j)+"_z1_low"]-p["C4_"+str(j)+"_z1_up"])+"\" />"
    for k in range(3,5):
      out+="\n\t\t<twoDimVertex x=\""+str(-xoff[i+str(j)]+ p["C4_"+str(j)+"_x"+str(k)+"_low"]-p["C4_"+str(j)+"_rpos"])+"\" y=\""+str(p["C4_"+str(j)+"_z"+str(k)+"_low"]-p["C4_"+str(j)+"_z1_up"])+"\" />"
    out+="\n\t\t<twoDimVertex x=\""+str(-xoff[i+str(j)]+ p["C4_"+str(j)+"_x2_low"]-p["C4_"+str(j)+"_rpos"])+"\" y=\""+str(p["C4_"+str(j)+"_z2_low"]-p["C4_"+str(j)+"_z1_up"])+"\" />"
    out+="\n\t\t<section zOrder=\"1\" zPosition=\""+str(-yoff[i+str(j)]-p["C4_"+str(j)+"_dy"]/2)+"\" xOffset=\"0\" yOffset=\"0\" scalingFactor=\"1\"/>"
    out+="\n\t\t<section zOrder=\"2\" zPosition=\""+str(yoff[i+str(j)]+p["C4_"+str(j)+"_dy"]/2)+"\" xOffset=\"0\" yOffset=\"0\" scalingFactor=\"1\"/>"
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
 
for i in range(0,4):
   x1= epoxy_protector_rmin[i]
   y1=-epoxy_protector_dph[i]/2.0
   x2= epoxy_protector_rmax[i]
   y2=-epoxy_protector_dph[i]/2.0
   x3= epoxy_protector_rmax[i]
   y3= epoxy_protector_dph[i]/2.0
   x4= epoxy_protector_rmin[i]
   y4= epoxy_protector_dph[i]/2.0
   out+="\n\t<xtru name=\"solid_epoxy_protector_"+str(i+1)+"\"  lunit=\"mm\">"
   out+="\n\t\t<twoDimVertex x=\""+str(x1)+"\" y=\""+str(y1)+"\" />"
   out+="\n\t\t<twoDimVertex x=\""+str(x2)+"\" y=\""+str(y2)+"\" />"
   out+="\n\t\t<twoDimVertex x=\""+str(x3)+"\" y=\""+str(y3)+"\" />"
   out+="\n\t\t<twoDimVertex x=\""+str(x4)+"\" y=\""+str(y4)+"\" />"
   out+="\n\t\t<section zOrder=\"1\" zPosition=\""+str(0)+"\" xOffset=\"0\" yOffset=\"0\" scalingFactor=\"1\"/>"
   out+="\n\t\t<section zOrder=\"2\" zPosition=\""+str(epoxy_protector_endz[i]-epoxy_protector_beginz[i])+"\" xOffset=\"0\" yOffset=\"0\" scalingFactor=\"1\"/>"
   out+="\n\t</xtru>"

x1= epoxy_protector_subcoil4_rmin
y1=-epoxy_protector_subcoil4_dph/2.0
x2= epoxy_protector_subcoil4_rmax
y2=-epoxy_protector_subcoil4_dph/2.0
x3= epoxy_protector_subcoil4_rmax
y3= epoxy_protector_subcoil4_dph/2.0
x4= epoxy_protector_subcoil4_rmin
y4= epoxy_protector_subcoil4_dph/2.0
out+="\n\t<xtru name=\"solid_epoxy_protector_5\"  lunit=\"mm\">"
out+="\n\t\t<twoDimVertex x=\""+str(x1)+"\" y=\""+str(y1)+"\" />"
out+="\n\t\t<twoDimVertex x=\""+str(x2)+"\" y=\""+str(y2)+"\" />"
out+="\n\t\t<twoDimVertex x=\""+str(x3)+"\" y=\""+str(y3)+"\" />"
out+="\n\t\t<twoDimVertex x=\""+str(x4)+"\" y=\""+str(y4)+"\" />"
for j in  range(1,5):
  out+="\n\t\t<section zOrder=\""+str(j)+"\" zPosition=\""+str(epoxy_protector_subcoil4_relsectionz[j-1])+"\" xOffset=\""+str(epoxy_protector_subcoil4_relsectionr[j-1])+"\" yOffset=\"0\" scalingFactor=\"1\"/>"
out+="\n\t</xtru>"

### Downstream toroid mother
out+="\n\t<tube name=\"solid_DS_toroidMother\" rmin=\""+str(r_inner_mother)+"\"  rmax=\""+str(r_outer_mother)+"\" z=\""+str(l_mother)+"\" startphi=\"0\" deltaphi=\"360\" aunit=\"deg\" lunit=\"mm\"/>\n"

out+="\n</solids>\n"

out+="\n\n<structure>\n"

for i in range(1,8):
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
        out+="\n\t\t\t\t<rotation name=\"rot_inner_E\" y=\"0\" unit=\"rad\" />"
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
   realsol["topmid"]="mid"
   realsol["botmid"]="mid"
   realzpos["topmid"]=p["C4_mid_dy"]/2+p["E_mid_dy"]
   realzpos["botmid"]=-realzpos["topmid"]
   realypos["topmid"]=0
   realypos["botmid"]=0

   for j in ["topmid", "botmid"]:
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
        out+="\n\t\t\t\t<rotation name=\"rot_inner_E4_\" y=\"0\" unit=\"rad\" />"
        out+="\n\t\t\t</physvol>\n"
        out+="\n\t</volume>\n"

   out+="\n\t<volume name=\"logic_outer_E4_"+str(i)+"\">"
   out+="\n\t\t<materialref ref=\"G10\"/>"
   out+="\n\t\t<solidref ref=\"solid_outer_E4_mid\"/>"
   out+="\n\t\t<auxiliary auxtype=\"Color\" auxvalue=\"orange\"/>"
   out+="\n\t\t<auxiliary auxtype=\"SensDet\" auxvalue=\"coilDet\"/>"
   out+="\n\t\t<auxiliary auxtype=\"DetNo\" auxvalue=\""+str(3007+i)+"\"/>"
   
   for j in ["topmid","botmid"]:
      out+="\n\t\t\t<physvol name=\"C4_"+str(j)+"\">"
      out+="\n\t\t\t\t<volumeref ref=\"logic_C4_"+str(j)+"_"+str(i)+"\"/>"
      out+="\n\t\t\t\t<position name=\"pos_logic_C4_"+str(j)+"_"+str(i)+"\" y=\""+str(realypos[j])+"\" z=\""+str(realzpos[j])+"\"/>"
      out+="\n\t\t\t</physvol>\n"

   out+="\n\t</volume>\n"

for i in range(0,5):
  out+="\n\t<volume name=\"logic_epoxy_protector_"+str(i+1)+"\">"
  out+="\n\t\t<materialref ref=\"G4_W\"/>"
  out+="\n\t\t<solidref ref=\"solid_epoxy_protector_"+str(i+1)+"\"/>"
  out+="\n\t\t<auxiliary auxtype=\"Color\" auxvalue=\"blue\"/>"
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
        
   for j in range(1,6):     
        out+="\n\t\t<physvol name=\"epoxy_protector_"+str(j)+"_"+str(i)+"\">"
        out+="\n\t\t\t<volumeref ref=\"logic_epoxy_protector_"+str(j)+"\"/>"
        out+="\n\t\t\t<position name=\"pos_epoxy_protector_"+str(i)+"\" x=\""+str(0)+"\" y=\""+str(0)+"\" z=\""+str(-(-epoxy_protector_zpos[j-1]+p["C_COM"]))+"\"/>"
        out+="\n\t\t\t<rotation name=\"rot_epoxy_protector_"+str(i)+"\" x=\"0\" y=\""+str(0)+"\" z=\""+str(theta)+"\"/>"
        out+="\n\t\t</physvol>\n"

out+="\n\t</volume>\n"
out+="\n</structure>\n"



out+="\n<setup name=\"DS_toroidWorld\" version=\"1.0\">"
out+="\n\t<world ref=\"DS_toroidMother\"/>"
out+="\n</setup>\n"

out+="\n</gdml>"

f.write(out)

