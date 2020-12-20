#SMD mesh skeleton corrector v1.2b
#Solo Deo gloria et lauda, amen!

"""
INSTRUCTIONS:
    
    This script is designed to fix the bones in an imported SMD Scource file skeleton 
    so that they are formatted more like traditional blender armatures. This mainly 
    consists of connecting children to parents, but having the parents reach out to 
    the children before they connect so the children do not stretch the wrong way 
    (say, great bit of philosophy there, ;-D).
    
    WARNING: May not preserve stored animations.
    
    1] Make sure the deformed meshes are parented to the armature. 
    
    2] Scale armature to correct size in Blender. This is usually a factor of 2.54 or 
    other relations between metric and imperial. For Sonic Generations, the scale for 
    all models has appeared to be 1/0.0254 their correct size when imported into blender.
    
    2] Rotate and move the model as neccesary, then apply all transformations for the 
    armature AND the mesh.
    
    3] Go into edit mode on the armature, and select all bones.
    
    4] Run this script.
    
    5] Double-check bones on the ends of chains, such as fingers and quills.
    
    6] Enjoy, TYL!
    
CHANGELOG:
    
    version 1.2:
        -Further fix in elbow SA: main if statement used children[0] for both conditions :-P
        -Added changelog
        -Added instructions
        -Changed handling of elbow bones: lengthen for easy access
    version 1.1:
        -Fix in elbow setup analyzer: elbows are parented to the outer bone, not the inner
    version 1:
        -Initial working release
"""

import bpy
def distance(vec1, vec2):
    return ((vec2[0]-vec1[0])**2+(vec2[1]-vec1[1])**2+(vec2[2]-vec1[2])**2)**0.5

done_names=[]

for b in bpy.context.selected_bones:
    if not b.name in done_names: #if we havent somehow already messed with this bone
        
        if len(b.children)==1:
            #Bone has one child, stretch out and connect
            b.tail=b.children[0].head[:]
            b.children[0].use_connect=True
            
        elif len(b.children)==0 and b.parent:
            #bone has no children
            if len(b.parent.children)==1: #bone is an only child, base orientation on parent
                b.tail=b.head*2-b.parent.head
            else: #parent has multiple children, lengthen this bone
                #0.003696 m
                b.length=0.01
            
        elif len(b.children)==2 and (distance(b.children[0].head, b.head)<0.001 or distance(b.children[1].head, b.head)<0.001):
            #bone has two children, one at same head location as parent, this is an elbow setup.
            #connect the one, orient the elbow bone
            
            if len(b.children[0].children)==0 and len(b.children[1].children)>0:
                #child 0 is the elbow bone
                elbow=b.children[0]
                main=b.children[1]
                
            elif len(b.children[1].children)==0 and len(b.children[0].children)>0:
                #child 1 is the elbow bone
                elbow=b.children[1]
                main=b.children[0]
                
            else: #catchall
                done_names.append(b.name)
                print(b.name+" appeared to be part of elbow setup, but failed analysis.")
                continue
            
            elbow.head=b.head[:]
            b.tail=main.head[:]
            main.use_connect=True
            
            elbow.length=0.02 #Lengthen the elbow to make it visible
            
#            if len(main.children)==1: #main has one child, go halfway with elbow
#                elbow.tail=(main.children[0].head-elbow.head)/2+elbow.head
#            else: #main has multiple children, base elbow on parent
#                elbow.tail=elbow.head+(elbow.head-b.head)/2
            done_names.append(elbow.name)
            
        done_names.append(b.name)