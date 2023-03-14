#!/usr/bin/env python
import csv
import sys
import os
import subprocess
import math
import time
import argparse
def print(*args):
    __builtins__.print(*("%.3f" % a if isinstance(a, float) else a
                         for a in args))


parser= argparse.ArgumentParser(description="Generate a segmented coil based on given parameters. Example: ./dcoilgen.py -l segmented.list -f test")
parser.add_argument("-l", dest="par_list", action="store", required=False, help="Provide the list of parameters. This is different for each of the coil types.")
parser.add_argument("-f", dest="output_file", action="store", required=False, default="DSToroid.gdml", help="Provide the required output file location")

args=parser.parse_args()
output_file=os.path.realpath(args.output_file)


p={}    # dictionary of parameter values

with open(args.par_list) as csvfile:
     reader=csv.reader(csvfile, delimiter=',', quotechar='|')
     for row in reader:
         if "mat" in row[0]:
           p[row[0]]=row[1].strip()
         else:
           p[row[0]]=float(row[1].strip())

p["C_COM"]=abs(p["C_z1_up"]-p["C_z2_up"])/2 +p["C_z1_up"]
 
p["C_l_arm"]= p["C_z2_up"]-p["C_z1_up"]
p["C_rad_front"]= (p["C_x1_up"]-p["C_x1_low"])/2.0
p["C_rad_back"]= (p["C_x2_up"]-p["C_x2_low"])/2.0
p["C_rpos"]=p["C_x1_low"]+ p["C_rad_front"]
p["C_zpos"]=p["C_z1_up"]+p["C_l_arm"]/2-7000   ## The 7000 needs to be the center of the mother volume

lower_shield1=33
intermediate_shield1=p['side_shield_height']/2.0
higher_shield1=p['side_shield_height']
length_shield1=p['side_shield_length_segment1']
zpos_shield1=p['side_shield_zstart']+length_shield1/2.0
widthbot_shield1=p['side_shield_bot_width']
widthtop_shield1=p['side_shield_top_width']

lower_shield2=33
intermediate_shield2=p['side_shield_height']/2.0
higher_shield2=p['side_shield_height']
length_shield2=p['side_shield_length_segment2']
zpos_shield2=zpos_shield1+(length_shield1+length_shield2)/2.0
widthbot_shield2=p['side_shield_bot_width']
widthtop_shield2=p['side_shield_top_width']

lower_shield3=33
intermediate_shield3=p['side_shield_height']/2.0
higher_shield3=p['side_shield_height']
length_shield3=p['side_shield_length_segment3']
zpos_shield3=zpos_shield2+(length_shield2+length_shield3)/2.0
widthbot_shield3=p['side_shield_bot_width']
widthtop_shield3=p['side_shield_top_width']


lower_shield4=33
intermediate_shield4=p['side_shield_height']/2.0
higher_shield4=p['side_shield_height']
length_shield4=p['side_shield_length_segment4']
zpos_shield4=zpos_shield3+(length_shield3+length_shield4)/2.0
widthbot_shield4=p['side_shield_bot_width']
widthtop_shield4=p['side_shield_top_width']

twobounce_groove_rmax=36
twobounce_groove_angdim= 28.0  # degrees
twobounce_groove_angpos= (360.0-twobounce_groove_angdim*7.0)/7.0  # degrees
twobounce_groove_beginz= 5936.5+12.7
twobounce_groove_endz = 5936.5+2152.65-12.7
twobounce_groove_zpos= 5000+2000

twobounce_beginz= [p['2_bounce_startz'], 5936.5+12.7, 5936.5+2152.65-12.7]
twobounce_endz=[5936.5+12.7, 5936.5+2152.65-12.7, 5936.5+2152.65]
twobounce_rmin=[25, 25, 25]
twobounce_rmax=[30.875, 32, 30.875]
twobounce_zpos=twobounce_beginz[0]+(twobounce_endz[-1]-twobounce_beginz[0])/2.0 # Just has to be a point between start and end

shield_clearance=0.7

r_inner_mother=0     
r_outer_mother=p["support_bar_minrad"]+2*p["support_bar_thickness"]+1
l_mother=2*( p["C_COM"] - p["C_z1_up"])+p["C_rad_front"]+p["C_rad_back"]+48

print(p["C_rad_back"]-p["C_rad_front"])
print("2bounce shield extends from "+str(twobounce_beginz)+" to "+str(twobounce_endz))
print("Mother volume extends from "+str(7000-l_mother/2)+" to "+str(7000+l_mother/2))
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
  theta=2*(i-1)*math.pi/7
  x1= math.cos(theta)*lower_shield1-math.sin(theta)*(-p["C_dy"]/2-p["E_dy"]-shield_clearance)
  y1= math.sin(theta)*lower_shield1+math.cos(theta)*(-p["C_dy"]/2-p["E_dy"]-shield_clearance)
  x2= math.cos(theta)*lower_shield1-math.sin(theta)*(-p["C_dy"]/2-p["E_dy"]-shield_clearance-widthbot_shield1)
  y2= math.sin(theta)*lower_shield1+math.cos(theta)*(-p["C_dy"]/2-p["E_dy"]-shield_clearance-widthbot_shield1)
  x3= math.cos(theta)*intermediate_shield1-math.sin(theta)*(-p["C_dy"]/2-p["E_dy"]-shield_clearance-widthtop_shield1)
  y3= math.sin(theta)*intermediate_shield1+math.cos(theta)*(-p["C_dy"]/2-p["E_dy"]-shield_clearance-widthtop_shield1)
  x4= math.cos(theta)*higher_shield1-math.sin(theta)*(-p["C_dy"]/2-p["E_dy"]-shield_clearance-widthtop_shield1)
  y4= math.sin(theta)*higher_shield1+math.cos(theta)*(-p["C_dy"]/2-p["E_dy"]-shield_clearance-widthtop_shield1)
  x5= math.cos(theta)*higher_shield1-math.sin(theta)*(-p["C_dy"]/2-p["E_dy"]-shield_clearance)
  y5= math.sin(theta)*higher_shield1+math.cos(theta)*(-p["C_dy"]/2-p["E_dy"]-shield_clearance)
  out+="\n\t<xtru name=\"solid_shield1_top_"+str(i)+"\"  lunit=\"mm\">"
  out+="\n\t\t<twoDimVertex x=\""+str(x1)+"\" y=\""+str(y1)+"\" />"
  out+="\n\t\t<twoDimVertex x=\""+str(x2)+"\" y=\""+str(y2)+"\" />"
  out+="\n\t\t<twoDimVertex x=\""+str(x3)+"\" y=\""+str(y3)+"\" />"
  out+="\n\t\t<twoDimVertex x=\""+str(x4)+"\" y=\""+str(y4)+"\" />"
  out+="\n\t\t<twoDimVertex x=\""+str(x5)+"\" y=\""+str(y5)+"\" />"

  out+="\n\t\t<section zOrder=\"1\" zPosition=\""+str(-length_shield1/2)+"\" xOffset=\"0\" yOffset=\"0\" scalingFactor=\"1\"/>"
  out+="\n\t\t<section zOrder=\"2\" zPosition=\""+str(length_shield1/2)+"\" xOffset=\"0\" yOffset=\"0\" scalingFactor=\"1\"/>"
  out+="\n\t</xtru>"

  x1= math.cos(theta)*lower_shield2-math.sin(theta)*(-p["C_dy"]/2-p["E_dy"]-shield_clearance)
  y1= math.sin(theta)*lower_shield2+math.cos(theta)*(-p["C_dy"]/2-p["E_dy"]-shield_clearance)
  x2= math.cos(theta)*lower_shield2-math.sin(theta)*(-p["C_dy"]/2-p["E_dy"]-shield_clearance-widthbot_shield2)
  y2= math.sin(theta)*lower_shield2+math.cos(theta)*(-p["C_dy"]/2-p["E_dy"]-shield_clearance-widthbot_shield2)
  x3= math.cos(theta)*intermediate_shield2-math.sin(theta)*(-p["C_dy"]/2-p["E_dy"]-shield_clearance-widthtop_shield2)
  y3= math.sin(theta)*intermediate_shield2+math.cos(theta)*(-p["C_dy"]/2-p["E_dy"]-shield_clearance-widthtop_shield2)
  x4= math.cos(theta)*higher_shield2-math.sin(theta)*(-p["C_dy"]/2-p["E_dy"]-shield_clearance-widthtop_shield2)
  y4= math.sin(theta)*higher_shield2+math.cos(theta)*(-p["C_dy"]/2-p["E_dy"]-shield_clearance-widthtop_shield2)  
  x5= math.cos(theta)*higher_shield2-math.sin(theta)*(-p["C_dy"]/2-p["E_dy"]-shield_clearance)
  y5= math.sin(theta)*higher_shield2+math.cos(theta)*(-p["C_dy"]/2-p["E_dy"]-shield_clearance)
  out+="\n\t<xtru name=\"solid_shield2_top_"+str(i)+"\"  lunit=\"mm\">"
  out+="\n\t\t<twoDimVertex x=\""+str(x1)+"\" y=\""+str(y1)+"\" />"
  out+="\n\t\t<twoDimVertex x=\""+str(x2)+"\" y=\""+str(y2)+"\" />"
  out+="\n\t\t<twoDimVertex x=\""+str(x3)+"\" y=\""+str(y3)+"\" />"
  out+="\n\t\t<twoDimVertex x=\""+str(x4)+"\" y=\""+str(y4)+"\" />"
  out+="\n\t\t<twoDimVertex x=\""+str(x5)+"\" y=\""+str(y5)+"\" />"
  out+="\n\t\t<section zOrder=\"1\" zPosition=\""+str(-length_shield2/2)+"\" xOffset=\"0\" yOffset=\"0\" scalingFactor=\"1\"/>"
  out+="\n\t\t<section zOrder=\"2\" zPosition=\""+str(length_shield2/2)+"\" xOffset=\"0\" yOffset=\"0\" scalingFactor=\"1\"/>"
  out+="\n\t</xtru>"

  x1= math.cos(theta)*lower_shield3-math.sin(theta)*(-p["C_dy"]/2-p["E_dy"]-shield_clearance)
  y1= math.sin(theta)*lower_shield3+math.cos(theta)*(-p["C_dy"]/2-p["E_dy"]-shield_clearance)
  x2= math.cos(theta)*lower_shield3-math.sin(theta)*(-p["C_dy"]/2-p["E_dy"]-shield_clearance-widthbot_shield3)
  y2= math.sin(theta)*lower_shield3+math.cos(theta)*(-p["C_dy"]/2-p["E_dy"]-shield_clearance-widthbot_shield3)
  x3= math.cos(theta)*intermediate_shield3-math.sin(theta)*(-p["C_dy"]/2-p["E_dy"]-shield_clearance-widthtop_shield3)
  y3= math.sin(theta)*intermediate_shield3+math.cos(theta)*(-p["C_dy"]/2-p["E_dy"]-shield_clearance-widthtop_shield3)
  x4= math.cos(theta)*higher_shield3-math.sin(theta)*(-p["C_dy"]/2-p["E_dy"]-shield_clearance-widthtop_shield3)
  y4= math.sin(theta)*higher_shield3+math.cos(theta)*(-p["C_dy"]/2-p["E_dy"]-shield_clearance-widthtop_shield3)
  x5= math.cos(theta)*higher_shield3-math.sin(theta)*(-p["C_dy"]/2-p["E_dy"]-shield_clearance)
  y5= math.sin(theta)*higher_shield3+math.cos(theta)*(-p["C_dy"]/2-p["E_dy"]-shield_clearance)
  out+="\n\t<xtru name=\"solid_shield3_top_"+str(i)+"\"  lunit=\"mm\">"
  out+="\n\t\t<twoDimVertex x=\""+str(x1)+"\" y=\""+str(y1)+"\" />"
  out+="\n\t\t<twoDimVertex x=\""+str(x2)+"\" y=\""+str(y2)+"\" />"
  out+="\n\t\t<twoDimVertex x=\""+str(x3)+"\" y=\""+str(y3)+"\" />"
  out+="\n\t\t<twoDimVertex x=\""+str(x4)+"\" y=\""+str(y4)+"\" />"
  out+="\n\t\t<twoDimVertex x=\""+str(x5)+"\" y=\""+str(y5)+"\" />"
  out+="\n\t\t<section zOrder=\"1\" zPosition=\""+str(-length_shield3/2)+"\" xOffset=\"0\" yOffset=\"0\" scalingFactor=\"1\"/>"
  out+="\n\t\t<section zOrder=\"2\" zPosition=\""+str(length_shield3/2)+"\" xOffset=\"0\" yOffset=\"0\" scalingFactor=\"1\"/>"
  out+="\n\t</xtru>"


  x1= math.cos(theta)*lower_shield4-math.sin(theta)*(-p["C_dy"]/2-p["E_dy"]-shield_clearance)
  y1= math.sin(theta)*lower_shield4+math.cos(theta)*(-p["C_dy"]/2-p["E_dy"]-shield_clearance)
  x2= math.cos(theta)*lower_shield4-math.sin(theta)*(-p["C_dy"]/2-p["E_dy"]-shield_clearance-widthbot_shield4)
  y2= math.sin(theta)*lower_shield4+math.cos(theta)*(-p["C_dy"]/2-p["E_dy"]-shield_clearance-widthbot_shield4)
  x3= math.cos(theta)*intermediate_shield4-math.sin(theta)*(-p["C_dy"]/2-p["E_dy"]-shield_clearance-widthtop_shield4)
  y3= math.sin(theta)*intermediate_shield4+math.cos(theta)*(-p["C_dy"]/2-p["E_dy"]-shield_clearance-widthtop_shield4)
  x4= math.cos(theta)*higher_shield4-math.sin(theta)*(-p["C_dy"]/2-p["E_dy"]-shield_clearance-widthtop_shield4)
  y4= math.sin(theta)*higher_shield4+math.cos(theta)*(-p["C_dy"]/2-p["E_dy"]-shield_clearance-widthtop_shield4)
  x5= math.cos(theta)*higher_shield4-math.sin(theta)*(-p["C_dy"]/2-p["E_dy"]-shield_clearance)
  y5= math.sin(theta)*higher_shield4+math.cos(theta)*(-p["C_dy"]/2-p["E_dy"]-shield_clearance)
  out+="\n\t<xtru name=\"solid_shield4_top_"+str(i)+"\"  lunit=\"mm\">"
  out+="\n\t\t<twoDimVertex x=\""+str(x1)+"\" y=\""+str(y1)+"\" />"
  out+="\n\t\t<twoDimVertex x=\""+str(x2)+"\" y=\""+str(y2)+"\" />"
  out+="\n\t\t<twoDimVertex x=\""+str(x3)+"\" y=\""+str(y3)+"\" />"
  out+="\n\t\t<twoDimVertex x=\""+str(x4)+"\" y=\""+str(y4)+"\" />"
  out+="\n\t\t<twoDimVertex x=\""+str(x5)+"\" y=\""+str(y5)+"\" />"
  out+="\n\t\t<section zOrder=\"1\" zPosition=\""+str(-length_shield4/2)+"\" xOffset=\"0\" yOffset=\"0\" scalingFactor=\"1\"/>"
  out+="\n\t\t<section zOrder=\"2\" zPosition=\""+str(length_shield4/2)+"\" xOffset=\"0\" yOffset=\"0\" scalingFactor=\"1\"/>"
  out+="\n\t</xtru>"



  x1= math.cos(theta)*lower_shield1-math.sin(theta)*(p["C_dy"]/2+p["E_dy"]+shield_clearance)
  y1= math.sin(theta)*lower_shield1+math.cos(theta)*(p["C_dy"]/2+p["E_dy"]+shield_clearance)
  x2= math.cos(theta)*lower_shield1-math.sin(theta)*(p["C_dy"]/2+p["E_dy"]+shield_clearance+widthbot_shield1)
  y2= math.sin(theta)*lower_shield1+math.cos(theta)*(p["C_dy"]/2+p["E_dy"]+shield_clearance+widthbot_shield1)
  x3= math.cos(theta)*intermediate_shield1-math.sin(theta)*(p["C_dy"]/2+p["E_dy"]+shield_clearance+widthtop_shield1)
  y3= math.sin(theta)*intermediate_shield1+math.cos(theta)*(p["C_dy"]/2+p["E_dy"]+shield_clearance+widthtop_shield1)
  x4= math.cos(theta)*higher_shield1-math.sin(theta)*(p["C_dy"]/2+p["E_dy"]+shield_clearance+widthtop_shield1)
  y4= math.sin(theta)*higher_shield1+math.cos(theta)*(p["C_dy"]/2+p["E_dy"]+shield_clearance+widthtop_shield1)
  x5= math.cos(theta)*higher_shield1-math.sin(theta)*(p["C_dy"]/2+p["E_dy"]+shield_clearance)
  y5= math.sin(theta)*higher_shield1+math.cos(theta)*(p["C_dy"]/2+p["E_dy"]+shield_clearance)
  out+="\n\t<xtru name=\"solid_shield1_bot_"+str(i)+"\"  lunit=\"mm\">"
  out+="\n\t\t<twoDimVertex x=\""+str(x5)+"\" y=\""+str(y5)+"\" />"
  out+="\n\t\t<twoDimVertex x=\""+str(x4)+"\" y=\""+str(y4)+"\" />"
  out+="\n\t\t<twoDimVertex x=\""+str(x3)+"\" y=\""+str(y3)+"\" />"
  out+="\n\t\t<twoDimVertex x=\""+str(x2)+"\" y=\""+str(y2)+"\" />"
  out+="\n\t\t<twoDimVertex x=\""+str(x1)+"\" y=\""+str(y1)+"\" />"
  out+="\n\t\t<section zOrder=\"1\" zPosition=\""+str(-length_shield1/2)+"\" xOffset=\"0\" yOffset=\"0\" scalingFactor=\"1\"/>"
  out+="\n\t\t<section zOrder=\"2\" zPosition=\""+str(length_shield1/2)+"\" xOffset=\"0\" yOffset=\"0\" scalingFactor=\"1\"/>"
  out+="\n\t</xtru>"

  x1= math.cos(theta)*lower_shield2-math.sin(theta)*(p["C_dy"]/2+p["E_dy"]+shield_clearance)
  y1= math.sin(theta)*lower_shield2+math.cos(theta)*(p["C_dy"]/2+p["E_dy"]+shield_clearance)
  x2= math.cos(theta)*lower_shield2-math.sin(theta)*(p["C_dy"]/2+p["E_dy"]+shield_clearance+widthbot_shield2)
  y2= math.sin(theta)*lower_shield2+math.cos(theta)*(p["C_dy"]/2+p["E_dy"]+shield_clearance+widthbot_shield2)
  x3= math.cos(theta)*intermediate_shield2-math.sin(theta)*(p["C_dy"]/2+p["E_dy"]+shield_clearance+widthtop_shield2)
  y3= math.sin(theta)*intermediate_shield2+math.cos(theta)*(p["C_dy"]/2+p["E_dy"]+shield_clearance+widthtop_shield2)
  x4= math.cos(theta)*higher_shield2-math.sin(theta)*(p["C_dy"]/2+p["E_dy"]+shield_clearance+widthtop_shield2)
  y4= math.sin(theta)*higher_shield2+math.cos(theta)*(p["C_dy"]/2+p["E_dy"]+shield_clearance+widthtop_shield2)
  x5= math.cos(theta)*higher_shield2-math.sin(theta)*(p["C_dy"]/2+p["E_dy"]+shield_clearance)
  y5= math.sin(theta)*higher_shield2+math.cos(theta)*(p["C_dy"]/2+p["E_dy"]+shield_clearance)
  out+="\n\t<xtru name=\"solid_shield2_bot_"+str(i)+"\"  lunit=\"mm\">"
  out+="\n\t\t<twoDimVertex x=\""+str(x5)+"\" y=\""+str(y5)+"\" />"
  out+="\n\t\t<twoDimVertex x=\""+str(x4)+"\" y=\""+str(y4)+"\" />"
  out+="\n\t\t<twoDimVertex x=\""+str(x3)+"\" y=\""+str(y3)+"\" />"
  out+="\n\t\t<twoDimVertex x=\""+str(x2)+"\" y=\""+str(y2)+"\" />"
  out+="\n\t\t<twoDimVertex x=\""+str(x1)+"\" y=\""+str(y1)+"\" />"
  out+="\n\t\t<section zOrder=\"1\" zPosition=\""+str(-length_shield2/2)+"\" xOffset=\"0\" yOffset=\"0\" scalingFactor=\"1\"/>"
  out+="\n\t\t<section zOrder=\"2\" zPosition=\""+str(length_shield2/2)+"\" xOffset=\"0\" yOffset=\"0\" scalingFactor=\"1\"/>"
  out+="\n\t</xtru>"

  x1= math.cos(theta)*lower_shield3-math.sin(theta)*(p["C_dy"]/2+p["E_dy"]+shield_clearance)
  y1= math.sin(theta)*lower_shield3+math.cos(theta)*(p["C_dy"]/2+p["E_dy"]+shield_clearance)
  x2= math.cos(theta)*lower_shield3-math.sin(theta)*(p["C_dy"]/2+p["E_dy"]+shield_clearance+widthbot_shield3)
  y2= math.sin(theta)*lower_shield3+math.cos(theta)*(p["C_dy"]/2+p["E_dy"]+shield_clearance+widthbot_shield3)
  x3= math.cos(theta)*intermediate_shield3-math.sin(theta)*(p["C_dy"]/2+p["E_dy"]+shield_clearance+widthtop_shield3)
  y3= math.sin(theta)*intermediate_shield3+math.cos(theta)*(p["C_dy"]/2+p["E_dy"]+shield_clearance+widthtop_shield3)
  x4= math.cos(theta)*higher_shield3-math.sin(theta)*(p["C_dy"]/2+p["E_dy"]+shield_clearance+widthtop_shield3)
  y4= math.sin(theta)*higher_shield3+math.cos(theta)*(p["C_dy"]/2+p["E_dy"]+shield_clearance+widthtop_shield3)
  x5= math.cos(theta)*higher_shield3-math.sin(theta)*(p["C_dy"]/2+p["E_dy"]+shield_clearance)
  y5= math.sin(theta)*higher_shield3+math.cos(theta)*(p["C_dy"]/2+p["E_dy"]+shield_clearance)
  out+="\n\t<xtru name=\"solid_shield3_bot_"+str(i)+"\"  lunit=\"mm\">"
  out+="\n\t\t<twoDimVertex x=\""+str(x5)+"\" y=\""+str(y5)+"\" />"
  out+="\n\t\t<twoDimVertex x=\""+str(x4)+"\" y=\""+str(y4)+"\" />"
  out+="\n\t\t<twoDimVertex x=\""+str(x3)+"\" y=\""+str(y3)+"\" />"
  out+="\n\t\t<twoDimVertex x=\""+str(x2)+"\" y=\""+str(y2)+"\" />"
  out+="\n\t\t<twoDimVertex x=\""+str(x1)+"\" y=\""+str(y1)+"\" />"
  out+="\n\t\t<section zOrder=\"1\" zPosition=\""+str(-length_shield3/2)+"\" xOffset=\"0\" yOffset=\"0\" scalingFactor=\"1\"/>"
  out+="\n\t\t<section zOrder=\"2\" zPosition=\""+str(length_shield3/2)+"\" xOffset=\"0\" yOffset=\"0\" scalingFactor=\"1\"/>"
  out+="\n\t</xtru>"
 
  x1= math.cos(theta)*lower_shield4-math.sin(theta)*(p["C_dy"]/2+p["E_dy"]+shield_clearance)
  y1= math.sin(theta)*lower_shield4+math.cos(theta)*(p["C_dy"]/2+p["E_dy"]+shield_clearance)
  x2= math.cos(theta)*lower_shield4-math.sin(theta)*(p["C_dy"]/2+p["E_dy"]+shield_clearance+widthbot_shield4)
  y2= math.sin(theta)*lower_shield4+math.cos(theta)*(p["C_dy"]/2+p["E_dy"]+shield_clearance+widthbot_shield4)
  x3= math.cos(theta)*intermediate_shield4-math.sin(theta)*(p["C_dy"]/2+p["E_dy"]+shield_clearance+widthtop_shield4)
  y3= math.sin(theta)*intermediate_shield4+math.cos(theta)*(p["C_dy"]/2+p["E_dy"]+shield_clearance+widthtop_shield4)
  x4= math.cos(theta)*higher_shield4-math.sin(theta)*(p["C_dy"]/2+p["E_dy"]+shield_clearance+widthtop_shield4)
  y4= math.sin(theta)*higher_shield4+math.cos(theta)*(p["C_dy"]/2+p["E_dy"]+shield_clearance+widthtop_shield4)
  x5= math.cos(theta)*higher_shield4-math.sin(theta)*(p["C_dy"]/2+p["E_dy"]+shield_clearance)
  y5= math.sin(theta)*higher_shield4+math.cos(theta)*(p["C_dy"]/2+p["E_dy"]+shield_clearance)
  out+="\n\t<xtru name=\"solid_shield4_bot_"+str(i)+"\"  lunit=\"mm\">"
  out+="\n\t\t<twoDimVertex x=\""+str(x5)+"\" y=\""+str(y5)+"\" />"
  out+="\n\t\t<twoDimVertex x=\""+str(x4)+"\" y=\""+str(y4)+"\" />"
  out+="\n\t\t<twoDimVertex x=\""+str(x3)+"\" y=\""+str(y3)+"\" />"
  out+="\n\t\t<twoDimVertex x=\""+str(x2)+"\" y=\""+str(y2)+"\" />"
  out+="\n\t\t<twoDimVertex x=\""+str(x1)+"\" y=\""+str(y1)+"\" />"
  out+="\n\t\t<section zOrder=\"1\" zPosition=\""+str(-length_shield4/2)+"\" xOffset=\"0\" yOffset=\"0\" scalingFactor=\"1\"/>"
  out+="\n\t\t<section zOrder=\"2\" zPosition=\""+str(length_shield4/2)+"\" xOffset=\"0\" yOffset=\"0\" scalingFactor=\"1\"/>"
  out+="\n\t</xtru>"

out+="\n\t<polycone aunit=\"deg\" startphi=\"0\" deltaphi=\"360\" lunit=\"mm\" name=\"solid_twobounce_long\">"
for i in range(0,3):
     out+="\n\t\t <zplane rmin=\""+str(twobounce_rmin[i])+"\" rmax=\""+str(twobounce_rmax[i])+"\" z=\""+str(twobounce_beginz[i]-twobounce_zpos)+"\"/>"
     out+="\n\t\t <zplane rmin=\""+str(twobounce_rmin[i])+"\" rmax=\""+str(twobounce_rmax[i])+"\" z=\""+str(twobounce_endz[i]-twobounce_zpos)+"\"/>"
out+="\n\t</polycone>"

out+="\n\t<polycone aunit=\"deg\" startphi=\"0\" deltaphi=\""+str(twobounce_groove_angdim)+"\" lunit=\"mm\" name=\"solid_twobounce_groove\">"
out+="\n\t\t <zplane rmin=\""+str(twobounce_rmax[1])+"\" rmax=\""+str(twobounce_groove_rmax)+"\" z=\""+str(twobounce_groove_beginz-twobounce_groove_zpos)+"\"/>"
out+="\n\t\t <zplane rmin=\""+str(twobounce_rmax[1])+"\" rmax=\""+str(twobounce_groove_rmax)+"\" z=\""+str(twobounce_groove_endz-twobounce_groove_zpos)+"\"/>"
out+="\n\t</polycone>"

### Upstream Support Bars

out+="\n\t<box aunit=\"deg\" startphi=\"0\" deltaphi=\"360\" lunit=\"mm\" name=\"solid_support_bar\" x=\""+str(2*p["support_bar_thickness"])+"\" y=\""+str(p["support_bar_thickness"])+"\" z=\""+str(p["support_bar_endz"]-p["support_bar_startz"])+"\"/>"

out+="\n\t<polycone aunit=\"deg\" startphi=\"0\" deltaphi=\"360\" lunit=\"mm\" name=\"solid_support_front_plate\">"
out+="\n\t\t <zplane rmin=\""+str(p["support_bar_minrad"])+"\" rmax=\""+str(r_outer_mother)+"\" z=\""+str(p["support_bar_startz"]-p["support_bar_thickness"]-7000)+"\"/>"
out+="\n\t\t <zplane rmin=\""+str(p["support_bar_minrad"])+"\" rmax=\""+str(r_outer_mother)+"\" z=\""+str(p["support_bar_startz"]-7000)+"\"/>"
out+="\n\t</polycone>"
                                           
out+="\n\t<polycone aunit=\"deg\" startphi=\"0\" deltaphi=\"360\" lunit=\"mm\" name=\"solid_support_end_plate\">"
out+="\n\t\t <zplane rmin=\""+str(p["support_bar_minrad"])+"\" rmax=\""+str(r_outer_mother)+"\" z=\""+str(p["support_bar_endz"]-7000)+"\"/>"
out+="\n\t\t <zplane rmin=\""+str(p["support_bar_minrad"])+"\" rmax=\""+str(r_outer_mother)+"\" z=\""+str(p["support_bar_endz"]+p["support_bar_thickness"]-7000)+"\"/>"
out+="\n\t</polycone>"
                                        
### Upstream toroid mother

out+="\n\t<polycone aunit=\"deg\" startphi=\"0\" deltaphi=\"360\" lunit=\"mm\" name=\"solid_US_toroidMother\">"
out+="\n\t\t <zplane rmin=\""+str(r_inner_mother)+"\" rmax=\""+str(r_outer_mother)+"\" z=\""+str(5900-7000)+"\"/>"
out+="\n\t\t <zplane rmin=\""+str(r_inner_mother)+"\" rmax=\""+str(r_outer_mother)+"\" z=\""+str(twobounce_endz[-1]-7000)+"\"/>"
out+="\n\t</polycone>"

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
        out+="\n\t\t<materialref ref=\""+p["side_shield_mat"]+"\"/>"
        out+="\n\t\t<solidref ref=\"solid_shield1_top_"+str(i)+"\"/>"
        out+="\n\t\t<auxiliary auxtype=\"Color\" auxvalue=\"red\"/>"
        out+="\n\t\t<auxiliary auxtype=\"SensDet\" auxvalue=\"coilDet\"/>"
        out+="\n\t\t<auxiliary auxtype=\"DetNo\" auxvalue=\""+str(4014+i)+"\"/>"
        out+="\n\t</volume>\n"

        out+="\n\t<volume name=\"logic_shield2_top_"+str(i)+"\">"
        out+="\n\t\t<materialref ref=\""+p["side_shield_mat"]+"\"/>"
        out+="\n\t\t<solidref ref=\"solid_shield2_top_"+str(i)+"\"/>"
        out+="\n\t\t<auxiliary auxtype=\"Color\" auxvalue=\"red\"/>"
        out+="\n\t\t<auxiliary auxtype=\"SensDet\" auxvalue=\"coilDet\"/>"
        out+="\n\t\t<auxiliary auxtype=\"DetNo\" auxvalue=\""+str(4021+i)+"\"/>"
        out+="\n\t</volume>\n"

        out+="\n\t<volume name=\"logic_shield3_top_"+str(i)+"\">"
        out+="\n\t\t<materialref ref=\""+p["side_shield_mat"]+"\"/>"
        out+="\n\t\t<solidref ref=\"solid_shield3_top_"+str(i)+"\"/>"
        out+="\n\t\t<auxiliary auxtype=\"Color\" auxvalue=\"red\"/>"
        out+="\n\t\t<auxiliary auxtype=\"SensDet\" auxvalue=\"coilDet\"/>"
        out+="\n\t\t<auxiliary auxtype=\"DetNo\" auxvalue=\""+str(4028+i)+"\"/>"
        out+="\n\t</volume>\n"

        out+="\n\t<volume name=\"logic_shield4_top_"+str(i)+"\">"
        out+="\n\t\t<materialref ref=\""+p["side_shield_mat"]+"\"/>"
        out+="\n\t\t<solidref ref=\"solid_shield4_top_"+str(i)+"\"/>"
        out+="\n\t\t<auxiliary auxtype=\"Color\" auxvalue=\"red\"/>"
        out+="\n\t\t<auxiliary auxtype=\"SensDet\" auxvalue=\"coilDet\"/>"
        out+="\n\t\t<auxiliary auxtype=\"DetNo\" auxvalue=\""+str(4035+i)+"\"/>"
        out+="\n\t</volume>\n"



        out+="\n\t<volume name=\"logic_shield1_bot_"+str(i)+"\">"
        out+="\n\t\t<materialref ref=\""+p["side_shield_mat"]+"\"/>"
        out+="\n\t\t<solidref ref=\"solid_shield1_bot_"+str(i)+"\"/>"
        out+="\n\t\t<auxiliary auxtype=\"Color\" auxvalue=\"red\"/>"
        out+="\n\t\t<auxiliary auxtype=\"SensDet\" auxvalue=\"coilDet\"/>"
        out+="\n\t\t<auxiliary auxtype=\"DetNo\" auxvalue=\""+str(4014+i)+"\"/>"
        out+="\n\t</volume>\n"


        out+="\n\t<volume name=\"logic_shield2_bot_"+str(i)+"\">"
        out+="\n\t\t<materialref ref=\""+p["side_shield_mat"]+"\"/>"
        out+="\n\t\t<solidref ref=\"solid_shield2_bot_"+str(i)+"\"/>"
        out+="\n\t\t<auxiliary auxtype=\"Color\" auxvalue=\"red\"/>"
        out+="\n\t\t<auxiliary auxtype=\"SensDet\" auxvalue=\"coilDet\"/>"
        out+="\n\t\t<auxiliary auxtype=\"DetNo\" auxvalue=\""+str(4021+i)+"\"/>"
        out+="\n\t</volume>\n"

        out+="\n\t<volume name=\"logic_shield3_bot_"+str(i)+"\">"
        out+="\n\t\t<materialref ref=\""+p["side_shield_mat"]+"\"/>"
        out+="\n\t\t<solidref ref=\"solid_shield3_bot_"+str(i)+"\"/>"
        out+="\n\t\t<auxiliary auxtype=\"Color\" auxvalue=\"red\"/>"
        out+="\n\t\t<auxiliary auxtype=\"SensDet\" auxvalue=\"coilDet\"/>"
        out+="\n\t\t<auxiliary auxtype=\"DetNo\" auxvalue=\""+str(4028+i)+"\"/>"
        out+="\n\t</volume>\n"

        out+="\n\t<volume name=\"logic_shield4_bot_"+str(i)+"\">"
        out+="\n\t\t<materialref ref=\""+p["side_shield_mat"]+"\"/>"
        out+="\n\t\t<solidref ref=\"solid_shield4_bot_"+str(i)+"\"/>"
        out+="\n\t\t<auxiliary auxtype=\"Color\" auxvalue=\"red\"/>"
        out+="\n\t\t<auxiliary auxtype=\"SensDet\" auxvalue=\"coilDet\"/>"
        out+="\n\t\t<auxiliary auxtype=\"DetNo\" auxvalue=\""+str(4035+i)+"\"/>"
        out+="\n\t</volume>\n"

out+="\n\t<volume name=\"logic_twobounce_long\">"
out+="\n\t\t<materialref ref=\""+p["2_bounce_mat"]+"\"/>"
out+="\n\t\t<solidref ref=\"solid_twobounce_long\"/>"
out+="\n\t\t<auxiliary auxtype=\"Color\" auxvalue=\"red\"/>"
out+="\n\t\t<auxiliary auxtype=\"SensDet\" auxvalue=\"coilDet\"/>"
out+="\n\t\t<auxiliary auxtype=\"DetNo\" auxvalue=\""+str(95)+"\"/>"
out+="\n\t</volume>\n"

out+="\n\t<volume name=\"logic_twobounce_groove\">"
out+="\n\t\t<materialref ref=\""+p["2_bounce_mat"]+"\"/>"
out+="\n\t\t<solidref ref=\"solid_twobounce_groove\"/>"
out+="\n\t\t<auxiliary auxtype=\"Color\" auxvalue=\"red\"/>"
out+="\n\t\t<auxiliary auxtype=\"SensDet\" auxvalue=\"coilDet\"/>"
out+="\n\t\t<auxiliary auxtype=\"DetNo\" auxvalue=\""+str(96)+"\"/>"
out+="\n\t</volume>\n"
                                           
out+="\n\t<volume name=\"logic_support_front_plate\">"
out+="\n\t\t<materialref ref=\"G4_Al\"/>"
out+="\n\t\t<solidref ref=\"solid_support_front_plate\"/>"
out+="\n\t\t<auxiliary auxtype=\"Color\" auxvalue=\"G4_Al\"/>"
out+="\n\t\t<auxiliary auxtype=\"SensDet\" auxvalue=\"enclosureDet\"/>"
out+="\n\t\t<auxiliary auxtype=\"DetNo\" auxvalue=\""+str(92)+"\"/>"
out+="\n\t</volume>\n"
                             
out+="\n\t<volume name=\"logic_support_end_plate\">"
out+="\n\t\t<materialref ref=\"G4_Al\"/>"
out+="\n\t\t<solidref ref=\"solid_support_end_plate\"/>"
out+="\n\t\t<auxiliary auxtype=\"Color\" auxvalue=\"G4_Al\"/>"
out+="\n\t\t<auxiliary auxtype=\"SensDet\" auxvalue=\"enclosureDet\"/>"
out+="\n\t\t<auxiliary auxtype=\"DetNo\" auxvalue=\""+str(93)+"\"/>"
out+="\n\t</volume>\n"
                             
out+="\n\t<volume name=\"logic_support_bar\">"
out+="\n\t\t<materialref ref=\"G4_Al\"/>"
out+="\n\t\t<solidref ref=\"solid_support_bar\"/>"
out+="\n\t\t<auxiliary auxtype=\"Color\" auxvalue=\"G4_Al\"/>"
out+="\n\t\t<auxiliary auxtype=\"SensDet\" auxvalue=\"enclosureDet\"/>"
out+="\n\t\t<auxiliary auxtype=\"DetNo\" auxvalue=\""+str(94)+"\"/>"
out+="\n\t</volume>\n"

out+="\n\t<volume name=\"US_toroidMother\">"
out+="\n\t\t<materialref ref=\"G4_Galactic\"/>"
out+="\n\t\t<solidref ref=\"solid_US_toroidMother\"/>"

rpos=p["C_rpos"]
zpos= p["C_zpos"]-p["C_l_arm"]/2
for i in range(1,8):
        theta=2*(i-1)*math.pi/7
        xpos=rpos*(math.cos(theta))
        ypos=rpos*(math.sin(theta))
        out+="\n\t\t<physvol name=\"ucoil_"+str(i)+"\">"
        out+="\n\t\t\t<volumeref ref=\"logic_outer_E_"+str(i)+"\"/>"
        out+="\n\t\t\t<position name=\"pos_ucoil_"+str(i)+"\" x=\""+str(xpos)+"\" y=\""+str(ypos)+"\" z=\""+str(zpos)+"\"/>"
        out+="\n\t\t\t<rotation name=\"rot_ucoil_"+str(i)+"\" x=\"pi/2\" y=\""+str(theta)+"\" z=\"0\"/>"
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
        
        out+="\n\t\t<physvol name=\"twobounce_groove_"+str(i)+"\">"
        out+="\n\t\t\t<volumeref ref=\"logic_twobounce_groove\"/>"
        out+="\n\t\t\t<position name=\"pos_twobounce_groove_"+str(i)+"\" x=\""+str(0)+"\" y=\""+str(0)+"\" z=\""+str(-(-twobounce_groove_zpos+7000))+"\"/>"
        out+="\n\t\t\t<rotation name=\"rot_twobounce_groove_"+str(i)+"\" x=\"0\" y=\""+str(0)+"\" z=\""+str(theta-(twobounce_groove_angpos*math.pi/360))+"\"/>"
        out+="\n\t\t</physvol>\n"
                                           
        out+="\n\t\t<physvol name=\"support_bar_"+str(i)+"\">"
        out+="\n\t\t\t<volumeref ref=\"logic_support_bar\"/>"
        out+="\n\t\t\t<position name=\"pos_support_bar_"+str(i)+"\" x=\""+str((p["support_bar_minrad"]+p["support_bar_thickness"])*math.cos(twobounce_groove_angpos*math.pi/360))+"\" y=\""+str((p["support_bar_minrad"]+p["support_bar_thickness"])*math.sin(twobounce_groove_angpos*math.pi/360))+"\" z=\""+str((p["support_bar_startz"]+p["support_bar_endz"])/2.0-7000)+"\"/>"
        out+="\n\t\t\t<rotation name=\"rot_support_bar_"+str(i)+"\" x=\"0\" y=\""+str(0)+"\" z=\""+str(theta-(twobounce_groove_angpos*math.pi/360))+"\"/>"
        out+="\n\t\t</physvol>\n"

out+="\n\t\t<physvol name=\"twobounce_long\">"
out+="\n\t\t\t<volumeref ref=\"logic_twobounce_long\"/>"
out+="\n\t\t\t<position name=\"pos_twobounce_long\" x=\""+str(0)+"\" y=\""+str(0)+"\" z=\""+str(-(-twobounce_zpos+7000))+"\"/>"
out+="\n\t\t\t<rotation name=\"rot_twobounce_long\" x=\"0\" y=\""+str(0)+"\" z=\"0\"/>"
out+="\n\t\t</physvol>\n"
                                          
out+="\n\t\t<physvol name=\"support_front_plate\">"
out+="\n\t\t\t<volumeref ref=\"logic_support_front_plate\"/>"
out+="\n\t\t\t<position name=\"pos_support_front_plate\" x=\""+str(0)+"\" y=\""+str(0)+"\" z=\""+str(0)+"\"/>"
out+="\n\t\t\t<rotation name=\"rot_support_front_plate\" x=\"0\" y=\""+str(0)+"\" z=\"0\"/>"
out+="\n\t\t</physvol>\n"
                                           
out+="\n\t\t<physvol name=\"support_end_plate\">"
out+="\n\t\t\t<volumeref ref=\"logic_support_end_plate\"/>"
out+="\n\t\t\t<position name=\"pos_support_end_plate\" x=\""+str(0)+"\" y=\""+str(0)+"\" z=\""+str(0)+"\"/>"
out+="\n\t\t\t<rotation name=\"rot_support_end_plate\" x=\"0\" y=\""+str(0)+"\" z=\"0\"/>"
out+="\n\t\t</physvol>\n"



out+="\n\t\t<auxiliary auxtype=\"Alpha\" auxvalue=\"0.0\"/>"
out+="\n\t</volume>\n"
out+="\n</structure>\n"



out+="\n<setup name=\"US_toroidWorld\" version=\"1.0\">"
out+="\n\t<world ref=\"US_toroidMother\"/>"
out+="\n</setup>\n"

out+="\n</gdml>\n"

f.write(out)
