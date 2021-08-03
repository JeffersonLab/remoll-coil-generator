#!/usr/bin/env python
import csv
import sys
import os
import subprocess
import math
import time
import argparse
import numpy as np


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

p["C_COM"]=abs(p["C_z1_up"]-p["C_z2_up"])/2 +p["C_z1_up"]
 
p["C_l_arm"]= p["C_z2_up"]-p["C_z1_up"]
p["C_rad_front"]= (p["C_x1_up"]-p["C_x1_low"])/2.0
p["C_rad_back"]= (p["C_x2_up"]-p["C_x2_low"])/2.0
p["C_rpos"]=p["C_x1_low"]+ p["C_rad_front"]
p["C_zpos"]=p["C_z1_up"]+p["C_l_arm"]/2-7000   ## The 7000 needs to be the center of the mother volume



x1=[33,33,33]
x2=[50,50,50]
x3=[100,100,100]
w1=[0.5, 0.5, 0.5]
w2=[3,3,3]
w3=[3,3,3]
zpos_shield=[5000+1001.5, 5000+1151.5, 5000+1650]
length_shield=[3, 297, 700]
y_off=4.5+1+0.7
zpos_shield1=zpos_shield[0]
zpos_shield2=zpos_shield[1]
zpos_shield3=zpos_shield[2]



lower_shield4=33
higher_shield4=60
length_shield4=750
zpos_shield4=5000+2375
widthbot_shield4=3
widthtop_shield4=3




r_inner_mother=p["C_x1_low"]-p["E_dy"]-0.01-0.01
r_outer_mother=p["C_x2_up"]+p["E_dy"]+1
l_mother=2*( p["C_COM"] - p["C_z1_up"])+p["C_rad_front"]+p["C_rad_back"]+48

print(p["C_rad_back"]-p["C_rad_front"])

print(r_inner_mother)
print(r_outer_mother)
print(l_mother)



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

xoff={}
yoff={}
xoff["C"]=0
xoff["outer_E"]= p["E_dy"]
xoff["inner_E"]= -p["C_dx"]
yoff["C"]=0
yoff["outer_E"]= p["E_dy"]
yoff["inner_E"]= 0
for i in ["C", "outer_E","inner_E"]: 
  out+="\n\t<xtru name=\"solid_"+i+"_mid\"  lunit=\"mm\">"
  out+="\n\t\t<twoDimVertex x=\""+str(xoff[i]+ p["C_x2_up"]-p["C_rpos"])+"\" y=\""+str(p["C_z2_up"]-p["C_z1_up"])+"\" />"
  out+="\n\t\t<twoDimVertex x=\""+str(xoff[i]+ p["C_x4_up"]-p["C_rpos"])+"\" y=\""+str(p["C_z4_up"]-p["C_z1_up"])+"\" />"
  out+="\n\t\t<twoDimVertex x=\""+str(xoff[i]+ p["C_x3_up"]-p["C_rpos"])+"\" y=\""+str(p["C_z3_up"]-p["C_z1_up"])+"\" />"
  out+="\n\t\t<twoDimVertex x=\""+str(xoff[i]+ p["C_x1_up"]-p["C_rpos"])+"\" y=\""+str(p["C_z1_up"]-p["C_z1_up"])+"\" />"
  out+="\n\t\t<twoDimVertex x=\""+str(-xoff[i]+ p["C_x1_low"]-p["C_rpos"])+"\" y=\""+str(p["C_z1_low"]-p["C_z1_up"])+"\" />"
  out+="\n\t\t<twoDimVertex x=\""+str(-xoff[i]+ p["C_x2_low"]-p["C_rpos"])+"\" y=\""+str(p["C_z2_low"]-p["C_z1_up"])+"\" />"
  out+="\n\t\t<section zOrder=\"1\" zPosition=\""+str(-yoff[i]-p["C_dy"]/2)+"\" xOffset=\"0\" yOffset=\"0\" scalingFactor=\"1\"/>"
  out+="\n\t\t<section zOrder=\"2\" zPosition=\""+str(yoff[i]+p["C_dy"]/2)+"\" xOffset=\"0\" yOffset=\"0\" scalingFactor=\"1\"/>"
  out+="\n\t</xtru>"
  out+="\n\t<tube name=\"solid_"+i+"_front\" rmin=\"0\" rmax=\""+str(xoff[i]+p["C_rad_front"])+"\" z=\""+str(2*yoff[i]+p["C_dy"])+"\" startphi=\"0\" deltaphi=\"pi\" aunit=\"rad\" lunit=\"mm\"/>\n"
  out+="\n\t<tube name=\"solid_"+i+"_back\" rmin=\"0\" rmax=\""+str(xoff[i]+p["C_rad_back"])+"\" z=\""+str(2*yoff[i]+p["C_dy"])+"\" startphi=\"0\" deltaphi=\"pi\" aunit=\"rad\" lunit=\"mm\"/>\n"
 
  ### Making unions
  out+="\n\t<union name=\"node_solid_"+i+"_frontmid\">"
  out+="\n\t\t<first ref=\"solid_"+i+"_front\"/>"
  out+="\n\t\t<second ref=\"solid_"+i+"_mid\"/>"
  out+="\n\t\t<position name=\"position_node_solid_"+i+"_frontmid\" y=\""+str(0)+"\"/>"
  out+="\n\t\t<rotation name=\"rotation_node_solid_"+i+"_frontmid\" x=\"pi\"/>"
  out+="\n\t</union>\n"

  out+="\n\t<union name=\"solid_"+i+"\">"
  out+="\n\t\t<first ref=\"node_solid_"+i+"_frontmid\"/>"
  out+="\n\t\t<second ref=\"solid_"+i+"_back\"/>"
  out+="\n\t\t<position name=\"position_node_solid_"+i+"\" x=\""+str( p["C_x2_up"]-p["C_rad_back"]-p["C_rpos"])+"\"  y=\""+str(-p["C_l_arm"])+"\"/>"
  out+="\n\t\t<rotation name=\"rotation_node_solid_"+i+"\" x=\"-pi\"/>"
  out+="\n\t</union>\n"


for i in range(1,8):
  theta_rot=2*(i-1)*math.pi/7

  for j in range(0,3):
        theta= np.arctan((w2[j]-w1[j])/(x2[j]-x1[j]))
        y3= (x3[j]-x2[j])*math.tan(theta)+w2[j]
	x5= x3[j]+ y3*math.tan(theta) 
	x_intermediate1= x5-(x5-x2[j])*(math.sin(theta))**2
	y_intermediate1= (x5-x2[j])*math.sin(theta)*math.cos(theta)

        x=[]
        y=[]
        yneg=[]


        x.append(x1[j])
        x.append(x2[j])
        x.append(x_intermediate1-w3[j]*math.cos(theta))
        x.append(x5-w3[j]/math.cos(theta))
        x.append(x5)
        x.append(x3[j])
        x.append(x2[j])
        x.append(x1[j])


        y.append(y_off)
        y.append(y_off)
        if not j==0:
           y.append(y_off+y_intermediate1-w3[j]*math.sin(theta))
        else: 
           y.append(y_off)
        y.append(y_off)
        y.append(y_off)
        y.append(y_off+y3)
        y.append(y_off+w2[j]/math.cos(theta))
        y.append(y_off+w1[j])
    
 
  	out+="\n\t<xtru name=\"solid_shield"+str(j+1)+"_top_"+str(i)+"\"  lunit=\"mm\">"
        for k in range(0, len(x)):
		out+="\n\t\t<twoDimVertex x=\""+str(x[k]*math.cos(theta_rot)-y[k]*math.sin(theta_rot))+"\" y=\""+str(x[k]*math.sin(theta_rot)+y[k]*math.cos(theta_rot))+"\" />"
  	out+="\n\t\t<section zOrder=\"1\" zPosition=\""+str(-length_shield[j]/2)+"\" xOffset=\"0\" yOffset=\"0\" scalingFactor=\"1\"/>"
        out+="\n\t\t<section zOrder=\"2\" zPosition=\""+str(length_shield[j]/2)+"\" xOffset=\"0\" yOffset=\"0\" scalingFactor=\"1\"/>"
  	out+="\n\t</xtru>"

        out+="\n\t<xtru name=\"solid_shield"+str(j+1)+"_bot_"+str(i)+"\"  lunit=\"mm\">"
        for k in range(0, len(x)):
                out+="\n\t\t<twoDimVertex x=\""+str(math.cos(theta_rot)*x[len(x)-k-1]+math.sin(theta_rot)*y[len(x)-k-1])+"\" y=\""+str(math.sin(theta_rot)*x[len(x)-k-1]-math.cos(theta_rot)*y[len(x)-k-1])+"\" />"
        out+="\n\t\t<section zOrder=\"1\" zPosition=\""+str(-length_shield[j]/2)+"\" xOffset=\"0\" yOffset=\"0\" scalingFactor=\"1\"/>"
        out+="\n\t\t<section zOrder=\"2\" zPosition=\""+str(length_shield[j]/2)+"\" xOffset=\"0\" yOffset=\"0\" scalingFactor=\"1\"/>"
        out+="\n\t</xtru>"

 
  x41= math.cos(theta_rot)*lower_shield4-math.sin(theta_rot)*(y_off)
  y41= math.sin(theta_rot)*lower_shield4+math.cos(theta_rot)*(y_off)
  x42= math.cos(theta_rot)*lower_shield4-math.sin(theta_rot)*(y_off+widthbot_shield4)
  y42= math.sin(theta_rot)*lower_shield4+math.cos(theta_rot)*(y_off+widthbot_shield4)
  x43= math.cos(theta_rot)*higher_shield4-math.sin(theta_rot)*(y_off+widthtop_shield4)
  y43= math.sin(theta_rot)*higher_shield4+math.cos(theta_rot)*(y_off+widthtop_shield4)
  x44= math.cos(theta_rot)*higher_shield4-math.sin(theta_rot)*(y_off)
  y44= math.sin(theta_rot)*higher_shield4+math.cos(theta_rot)*(y_off)
  out+="\n\t<xtru name=\"solid_shield4_bot_"+str(i)+"\"  lunit=\"mm\">"
  out+="\n\t\t<twoDimVertex x=\""+str(x44)+"\" y=\""+str(y44)+"\" />"
  out+="\n\t\t<twoDimVertex x=\""+str(x43)+"\" y=\""+str(y43)+"\" />"
  out+="\n\t\t<twoDimVertex x=\""+str(x42)+"\" y=\""+str(y42)+"\" />"
  out+="\n\t\t<twoDimVertex x=\""+str(x41)+"\" y=\""+str(y41)+"\" />"
  out+="\n\t\t<section zOrder=\"1\" zPosition=\""+str(-length_shield4/2)+"\" xOffset=\"0\" yOffset=\"0\" scalingFactor=\"1\"/>"
  out+="\n\t\t<section zOrder=\"2\" zPosition=\""+str(length_shield4/2)+"\" xOffset=\"0\" yOffset=\"0\" scalingFactor=\"1\"/>"
  out+="\n\t</xtru>"

  x41= math.cos(theta_rot)*lower_shield4-math.sin(theta_rot)*(-y_off)
  y41= math.sin(theta_rot)*lower_shield4+math.cos(theta_rot)*(-y_off)
  x42= math.cos(theta_rot)*lower_shield4-math.sin(theta_rot)*(-y_off-widthbot_shield4)
  y42= math.sin(theta_rot)*lower_shield4+math.cos(theta_rot)*(-y_off-widthbot_shield4)
  x43= math.cos(theta_rot)*higher_shield4-math.sin(theta_rot)*(-y_off-widthtop_shield4)
  y43= math.sin(theta_rot)*higher_shield4+math.cos(theta_rot)*(-y_off-widthtop_shield4)
  x44= math.cos(theta_rot)*higher_shield4-math.sin(theta_rot)*(-y_off)
  y44= math.sin(theta_rot)*higher_shield4+math.cos(theta_rot)*(-y_off)
  out+="\n\t<xtru name=\"solid_shield4_top_"+str(i)+"\"  lunit=\"mm\">"
  out+="\n\t\t<twoDimVertex x=\""+str(x41)+"\" y=\""+str(y41)+"\" />"
  out+="\n\t\t<twoDimVertex x=\""+str(x42)+"\" y=\""+str(y42)+"\" />"
  out+="\n\t\t<twoDimVertex x=\""+str(x43)+"\" y=\""+str(y43)+"\" />"
  out+="\n\t\t<twoDimVertex x=\""+str(x44)+"\" y=\""+str(y44)+"\" />"
  out+="\n\t\t<section zOrder=\"1\" zPosition=\""+str(-length_shield4/2)+"\" xOffset=\"0\" yOffset=\"0\" scalingFactor=\"1\"/>"
  out+="\n\t\t<section zOrder=\"2\" zPosition=\""+str(length_shield4/2)+"\" xOffset=\"0\" yOffset=\"0\" scalingFactor=\"1\"/>"
  out+="\n\t</xtru>"


 
### Upstream toroid mother







out+="\n\t<cone name=\"solid_US_toroidMother\" rmin1=\""+str(r_inner_mother)+"\"  rmax1=\""+str(r_outer_mother)+"\" rmin2=\""+str(r_inner_mother+(p["C_x2_low"]-p["C_x1_low"])/16)+"\" rmax2=\""+str(r_outer_mother)+"\" z=\""+str(l_mother)+"\" startphi=\"0\" deltaphi=\"360\" aunit=\"deg\" lunit=\"mm\"/>\n"




print(str(r_inner_mother+(p["C_x2_low"]-p["C_x1_low"])/12))

out+="\n</solids>\n"

out+="\n\n<structure>\n"


for i in range(1,8):
   ### Setting up coils
        out+="\n\t<volume name=\"logic_inner_E_"+str(i)+"\">"
        out+="\n\t\t<materialref ref=\"G10\"/>"
        out+="\n\t\t<solidref ref=\"solid_inner_E\"/>"
        out+="\n\t\t<auxiliary auxtype=\"Color\" auxvalue=\"orange\"/>"
        out+="\n\t\t<auxiliary auxtype=\"SensDet\" auxvalue=\"coilDet\"/>"
        out+="\n\t\t<auxiliary auxtype=\"DetNo\" auxvalue=\""+str(4007+i)+"\"/>"
        out+="\n\t</volume>\n"

        out+="\n\t<volume name=\"logic_C_"+str(i)+"\">"
        out+="\n\t\t<materialref ref=\"G4_Cu\"/>"
        out+="\n\t\t<solidref ref=\"solid_C\"/>"
        out+="\n\t\t\t<physvol name=\"inner_E_"+str(i)+"\">"
        out+="\n\t\t\t\t<volumeref ref=\"logic_inner_E_"+str(i)+"\"/>"
        out+="\n\t\t\t\t<rotation name=\"rot_inner_E_"+str(i)+"\" y=\"0\" aunit=\"rad\" />"
        out+="\n\t\t\t</physvol>\n"
        out+="\n\t\t<auxiliary auxtype=\"Color\" auxvalue=\"magenta\"/>"
        out+="\n\t\t<auxiliary auxtype=\"SensDet\" auxvalue=\"coilDet\"/>"
        out+="\n\t\t<auxiliary auxtype=\"DetNo\" auxvalue=\""+str(4000+i)+"\"/>"
        out+="\n\t</volume>\n"

        out+="\n\t<volume name=\"logic_outer_E_"+str(i)+"\">"
        out+="\n\t\t<materialref ref=\"G10\"/>"
        out+="\n\t\t<solidref ref=\"solid_outer_E\"/>"
        out+="\n\t\t\t<physvol name=\"C_"+str(i)+"\">"
        out+="\n\t\t\t\t<volumeref ref=\"logic_C_"+str(i)+"\"/>"
        out+="\n\t\t\t</physvol>\n"
        out+="\n\t\t<auxiliary auxtype=\"Color\" auxvalue=\"orange\"/>"
        out+="\n\t\t<auxiliary auxtype=\"SensDet\" auxvalue=\"coilDet\"/>"
        out+="\n\t\t<auxiliary auxtype=\"DetNo\" auxvalue=\""+str(4007+i)+"\"/>"
        out+="\n\t</volume>\n"

        out+="\n\t<volume name=\"logic_shield1_top_"+str(i)+"\">"
        out+="\n\t\t<materialref ref=\"G4_W\"/>"
        out+="\n\t\t<solidref ref=\"solid_shield1_top_"+str(i)+"\"/>"
        out+="\n\t\t<auxiliary auxtype=\"Color\" auxvalue=\"red\"/>"
        out+="\n\t\t<auxiliary auxtype=\"SensDet\" auxvalue=\"coilDet\"/>"
        out+="\n\t\t<auxiliary auxtype=\"DetNo\" auxvalue=\""+str(4014+i)+"\"/>"
        out+="\n\t</volume>\n"

        out+="\n\t<volume name=\"logic_shield2_top_"+str(i)+"\">"
        out+="\n\t\t<materialref ref=\"G4_W\"/>"
        out+="\n\t\t<solidref ref=\"solid_shield2_top_"+str(i)+"\"/>"
        out+="\n\t\t<auxiliary auxtype=\"Color\" auxvalue=\"red\"/>"
        out+="\n\t\t<auxiliary auxtype=\"SensDet\" auxvalue=\"coilDet\"/>"
        out+="\n\t\t<auxiliary auxtype=\"DetNo\" auxvalue=\""+str(4021+i)+"\"/>"
        out+="\n\t</volume>\n"

        out+="\n\t<volume name=\"logic_shield3_top_"+str(i)+"\">"
        out+="\n\t\t<materialref ref=\"G4_W\"/>"
        out+="\n\t\t<solidref ref=\"solid_shield3_top_"+str(i)+"\"/>"
        out+="\n\t\t<auxiliary auxtype=\"Color\" auxvalue=\"red\"/>"
        out+="\n\t\t<auxiliary auxtype=\"SensDet\" auxvalue=\"coilDet\"/>"
        out+="\n\t\t<auxiliary auxtype=\"DetNo\" auxvalue=\""+str(4028+i)+"\"/>"
        out+="\n\t</volume>\n"

        out+="\n\t<volume name=\"logic_shield4_top_"+str(i)+"\">"
        out+="\n\t\t<materialref ref=\"G4_W\"/>"
        out+="\n\t\t<solidref ref=\"solid_shield4_top_"+str(i)+"\"/>"
        out+="\n\t\t<auxiliary auxtype=\"Color\" auxvalue=\"red\"/>"
        out+="\n\t\t<auxiliary auxtype=\"SensDet\" auxvalue=\"coilDet\"/>"
        out+="\n\t\t<auxiliary auxtype=\"DetNo\" auxvalue=\""+str(4035+i)+"\"/>"
        out+="\n\t</volume>\n"



        out+="\n\t<volume name=\"logic_shield1_bot_"+str(i)+"\">"
        out+="\n\t\t<materialref ref=\"G4_W\"/>"
        out+="\n\t\t<solidref ref=\"solid_shield1_bot_"+str(i)+"\"/>"
        out+="\n\t\t<auxiliary auxtype=\"Color\" auxvalue=\"red\"/>"
        out+="\n\t\t<auxiliary auxtype=\"SensDet\" auxvalue=\"coilDet\"/>"
        out+="\n\t\t<auxiliary auxtype=\"DetNo\" auxvalue=\""+str(4014+i)+"\"/>"
        out+="\n\t</volume>\n"


        out+="\n\t<volume name=\"logic_shield2_bot_"+str(i)+"\">"
        out+="\n\t\t<materialref ref=\"G4_W\"/>"
        out+="\n\t\t<solidref ref=\"solid_shield2_bot_"+str(i)+"\"/>"
        out+="\n\t\t<auxiliary auxtype=\"Color\" auxvalue=\"red\"/>"
        out+="\n\t\t<auxiliary auxtype=\"SensDet\" auxvalue=\"coilDet\"/>"
        out+="\n\t\t<auxiliary auxtype=\"DetNo\" auxvalue=\""+str(4021+i)+"\"/>"
        out+="\n\t</volume>\n"

        out+="\n\t<volume name=\"logic_shield3_bot_"+str(i)+"\">"
        out+="\n\t\t<materialref ref=\"G4_W\"/>"
        out+="\n\t\t<solidref ref=\"solid_shield3_bot_"+str(i)+"\"/>"
        out+="\n\t\t<auxiliary auxtype=\"Color\" auxvalue=\"red\"/>"
        out+="\n\t\t<auxiliary auxtype=\"SensDet\" auxvalue=\"coilDet\"/>"
        out+="\n\t\t<auxiliary auxtype=\"DetNo\" auxvalue=\""+str(4028+i)+"\"/>"
        out+="\n\t</volume>\n"

        out+="\n\t<volume name=\"logic_shield4_bot_"+str(i)+"\">"
        out+="\n\t\t<materialref ref=\"G4_W\"/>"
        out+="\n\t\t<solidref ref=\"solid_shield4_bot_"+str(i)+"\"/>"
        out+="\n\t\t<auxiliary auxtype=\"Color\" auxvalue=\"red\"/>"
        out+="\n\t\t<auxiliary auxtype=\"SensDet\" auxvalue=\"coilDet\"/>"
        out+="\n\t\t<auxiliary auxtype=\"DetNo\" auxvalue=\""+str(4035+i)+"\"/>"
        out+="\n\t</volume>\n"

         

out+="\n\t<volume name=\"US_toroidMother\">"
out+="\n\t\t<materialref ref=\"G4_Galactic\"/>"
out+="\n\t\t<solidref ref=\"solid_US_toroidMother\"/>"


for i in range(1,8):
        rpos=p["C_rpos"]
        theta_rot=2*(i-1)*math.pi/7
        xpos=rpos*(math.cos(theta_rot))
        ypos=rpos*(math.sin(theta_rot))
        zpos= p["C_zpos"]-p["C_l_arm"]/2
        out+="\n\t\t<physvol name=\"ucoil_"+str(i)+"\">"
        out+="\n\t\t\t<volumeref ref=\"logic_outer_E_"+str(i)+"\"/>"
        out+="\n\t\t\t<position name=\"pos_ucoil_"+str(i)+"\" x=\""+str(xpos)+"\" y=\""+str(ypos)+"\" z=\""+str(zpos)+"\"/>"
        out+="\n\t\t\t<rotation name=\"rot_ucoil_"+str(i)+"\" x=\"pi/2\" y=\""+str(theta_rot)+"\" z=\"0\"/>"
        out+="\n\t\t</physvol>\n"

        out+="\n\t\t<physvol name=\"shield1_top_"+str(i)+"\">"
        out+="\n\t\t\t<volumeref ref=\"logic_shield1_top_"+str(i)+"\"/>"
        out+="\n\t\t\t<position name=\"pos_shield1_top_"+str(i)+"\" x=\""+str(0)+"\" y=\""+str(0)+"\" z=\""+str(p["C_zpos"]-(-zpos_shield1+7000))+"\"/>"
        out+="\n\t\t\t<rotation name=\"rot_shield1_top_"+str(i)+"\" x=\"0\" y=\""+str(0)+"\" z=\"0\"/>"
        out+="\n\t\t</physvol>\n"
 
        out+="\n\t\t<physvol name=\"shield2_top_"+str(i)+"\">"
        out+="\n\t\t\t<volumeref ref=\"logic_shield2_top_"+str(i)+"\"/>"
        out+="\n\t\t\t<position name=\"pos_shield2_top_"+str(i)+"\" x=\""+str(0)+"\" y=\""+str(0)+"\" z=\""+str(p["C_zpos"]-(-zpos_shield2+7000))+"\"/>"
        out+="\n\t\t\t<rotation name=\"rot_shield2_top_"+str(i)+"\" x=\"0\" y=\""+str(0)+"\" z=\"0\"/>"
        out+="\n\t\t</physvol>\n"

        out+="\n\t\t<physvol name=\"shield3_top_"+str(i)+"\">"
        out+="\n\t\t\t<volumeref ref=\"logic_shield3_top_"+str(i)+"\"/>"
        out+="\n\t\t\t<position name=\"pos_shield3_top_"+str(i)+"\" x=\""+str(0)+"\" y=\""+str(0)+"\" z=\""+str(p["C_zpos"]-(-zpos_shield3+7000))+"\"/>"
        out+="\n\t\t\t<rotation name=\"rot_shield3_top_"+str(i)+"\" x=\"0\" y=\""+str(0)+"\" z=\"0\"/>"
        out+="\n\t\t</physvol>\n"

        out+="\n\t\t<physvol name=\"shield4_top_"+str(i)+"\">"
        out+="\n\t\t\t<volumeref ref=\"logic_shield4_top_"+str(i)+"\"/>"
        out+="\n\t\t\t<position name=\"pos_shield4_top_"+str(i)+"\" x=\""+str(0)+"\" y=\""+str(0)+"\" z=\""+str(p["C_zpos"]-(-zpos_shield4+7000))+"\"/>"
        out+="\n\t\t\t<rotation name=\"rot_shield4_top_"+str(i)+"\" x=\"0\" y=\""+str(0)+"\" z=\"0\"/>"
        out+="\n\t\t</physvol>\n"


        out+="\n\t\t<physvol name=\"shield1_bot_"+str(i)+"\">"
        out+="\n\t\t\t<volumeref ref=\"logic_shield1_bot_"+str(i)+"\"/>"
        out+="\n\t\t\t<position name=\"pos_shield1_bot_"+str(i)+"\" x=\""+str(0)+"\" y=\""+str(0)+"\" z=\""+str(p["C_zpos"]-(-zpos_shield1+7000))+"\"/>"
        out+="\n\t\t\t<rotation name=\"rot_shield1_bot_"+str(i)+"\" x=\"0\" y=\""+str(0)+"\" z=\"0\"/>"
        out+="\n\t\t</physvol>\n"

        out+="\n\t\t<physvol name=\"shield2_bot_"+str(i)+"\">"
        out+="\n\t\t\t<volumeref ref=\"logic_shield2_bot_"+str(i)+"\"/>"
        out+="\n\t\t\t<position name=\"pos_shield2_bot_"+str(i)+"\" x=\""+str(0)+"\" y=\""+str(0)+"\" z=\""+str(p["C_zpos"]-(-zpos_shield2+7000))+"\"/>"
        out+="\n\t\t\t<rotation name=\"rot_shield2_bot_"+str(i)+"\" x=\"0\" y=\""+str(0)+"\" z=\"0\"/>"
        out+="\n\t\t</physvol>\n"

        out+="\n\t\t<physvol name=\"shield3_bot_"+str(i)+"\">"
        out+="\n\t\t\t<volumeref ref=\"logic_shield3_bot_"+str(i)+"\"/>"
        out+="\n\t\t\t<position name=\"pos_shield3_bot_"+str(i)+"\" x=\""+str(0)+"\" y=\""+str(0)+"\" z=\""+str(p["C_zpos"]-(-zpos_shield3+7000))+"\"/>"
        out+="\n\t\t\t<rotation name=\"rot_shield3_bot_"+str(i)+"\" x=\"0\" y=\""+str(0)+"\" z=\"0\"/>"
        out+="\n\t\t</physvol>\n"

        out+="\n\t\t<physvol name=\"shield4_bot_"+str(i)+"\">"
        out+="\n\t\t\t<volumeref ref=\"logic_shield4_bot_"+str(i)+"\"/>"
        out+="\n\t\t\t<position name=\"pos_shield4_bot_"+str(i)+"\" x=\""+str(0)+"\" y=\""+str(0)+"\" z=\""+str(p["C_zpos"]-(-zpos_shield4+7000))+"\"/>"
        out+="\n\t\t\t<rotation name=\"rot_shield4_bot_"+str(i)+"\" x=\"0\" y=\""+str(0)+"\" z=\"0\"/>"
        out+="\n\t\t</physvol>\n"
        
out+="\n\t\t<auxiliary auxtype=\"Alpha\" auxvalue=\"0.0\"/>"
out+="\n\t</volume>\n"
out+="\n</structure>\n"



out+="\n<setup name=\"US_toroidWorld\" version=\"1.0\">"
out+="\n\t<world ref=\"US_toroidMother\"/>"
out+="\n</setup>\n"

out+="\n</gdml>\n"

f.write(out)

