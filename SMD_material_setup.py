#Material setup script for SMD models, v1.5.1
#TYL!!!

"""
INSTRUCTIONS:
    This script is meant to set up blender materials for an imported SMD file, the 
    blend file being otherwise empty.
    
    NOTE: This script was designed based on experience, not on actual SMD material 
    research.
    
    1] Set MAT_PATH to the folder containing the images to be connected with the model. 
    Do not set IMAGES.
    
    2] Set NAME_SIZE to the number of underscore-separated elements at the beginning of 
    image and material names that confirm relationship. chr_thelabcat_body_dif as a 
    material with chr_thelabcat_body_nrm being a related image means that material 
    (and likely the rest of the model) would have a NAME_SIZE of 3.
    
    2B] If images and materials do not seem properly connected, 
    comment out the check_related() definition block and write your own code. The 
    function will be passed the name of the image without file prefixes or suffixes, 
    and the material name. Return True or False. One alternate definition is included.
    
    3] Run this script. NOTE: Material nodes are currently dropped at 0,0,0 with no 
    organizing. The Node Arranger addon is reccomended for manual use to clean this up.
    
    4] Enjoy!


CHANGELOG:
    version 1.5.1:
        -Improvements to doc
    version 1.5:
        -Added specular tint adjuster
    version 1.4:
        -Changed relation checking
    version 1.3x:
        -Used env to also indicate lum, NAMING ERROR SUSPECTED FOR STARDUST SPEEDWAY
    version 1.3:
        -Changed relation checking to work with portion of names being equal
        -Added handler for dif textures with lum
    version 1.2:
        -Changed spc and pow usage
        -Added alpha setup
    version 1.1:
        -Added changelog and instructions
        -Added case lower-izers
    version 1.0:
        -Initial working release
"""

try:
    import bpy
except ImportError:
    print("This script is meant to run in Blender.")

import glob

MAT_PATH="F:\\3D_models\\Jaywright\\images"
IMAGES=glob.glob(MAT_PATH+"\\*")
DISP_SCALE=0.00254

NAME_SIZE=2
def check_related(imgn, matn):
    try:
        if imgn.split("_")[:NAME_SIZE] == matn.split("_")[:NAME_SIZE]:
            return True
    except IndexError:
        pass
    return False

#def check_related(imgn, matn):
#    imgn=imgn.replace("_", "")
#    matn=matn.replace("_", "")
#    if len(imgn)>=len(matn):
#        for c in matn:
#            if c in imgn:
#                imgn=imgn[imgn.index(c)+1:]
#            else:
#                return False
#    else:
#        return False
#    return True

#Iterate through all blender materials
for mat in bpy.data.materials:
    
    #Configure basic settings for the material
    mat.blend_method="HASHED"
    mat.shadow_method="CLIP"
    mat.use_nodes=True
    
    #Set up basic Principled BSDF
    mat.node_tree.nodes.clear()
    shader=mat.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
    output=mat.node_tree.nodes.new("ShaderNodeOutputMaterial")
    mat.node_tree.links.new(shader.outputs["BSDF"], output.inputs["Surface"])
    
    #Variables for nodes which may or may not already exist on the encountering of new images
    normal_node=None
    nrm_color_comb=None
    
    #Iterate through all images in the specified path (This does not guarantee an image will be used only once)
    for img_fn in IMAGES:
        
        #Clean the image filename, then check if it is related to our material
        img_tname=img_fn.lower().split("\\")[-1][:-4]
        if not check_related(img_tname, mat.name.lower()):
            continue
        
        #Prepare image name for suffix searching
        img_name=img_tname.split("_")
        
        #Load the image
        img_node=mat.node_tree.nodes.new('ShaderNodeTexImage')
        img_node.image=bpy.data.images.load(img_fn)
        
        
        #Search for suffixes and attatch the image properly
        if "dif" in img_name:
            #Base color
            mat.node_tree.links.new(img_node.outputs["Color"], shader.inputs["Base Color"])
            mat.node_tree.links.new(img_node.outputs["Alpha"], shader.inputs["Alpha"])
            
            if "lum" in img_name:
                #material also glows
                mat.node_tree.links.new(img_node.outputs["Color"], shader.inputs["Emission"])
        #elif "env" in img_name: #Suspected naming error!
        #    mat.node_tree.links.new(img_node.outputs["Color"], shader.inputs["Emission"])
        
        elif "nrm" in img_name:
            #Normal map
            if not normal_node:
                normal_node=mat.node_tree.nodes.new('ShaderNodeNormalMap')
            mat.node_tree.links.new(normal_node.outputs["Normal"], shader.inputs["Normal"])
            img_node.image.colorspace_settings.name="Non-Color"
            
            if "RG" in img_name or "BA" in img_name:
                #Halves of the normal map
                if not nrm_color_comb:
                    nrm_color_comb=mat.node_tree.nodes.new('ShaderNodeCombineRGB')
                    mat.node_tree.links.new(nrm_color_comb.outputs["Image"], normal_node.inputs["Color"])
                RG_sep_node=mat.node_tree.nodes.new("ShaderNodeSeparateRGB")
                mat.node_tree.links.new(img_node.outputs["Color"], RG_sep_node.inputs["Image"])
                
                if "RG" in img_name:
                    #link the red and green channels to the red and green channels
                    mat.node_tree.links.new(RG_sep_node.outputs["R"], nrm_color_comb.inputs["R"])
                    mat.node_tree.links.new(RG_sep_node.outputs["G"], nrm_color_comb.inputs["G"])
                elif "BA" in img_name:
                    #link the red channel to the blue channel, green/alpha is not used
                    mat.node_tree.links.new(RG_sep_node.outputs["R"], nrm_color_comb.inputs["B"])
            
            else:
                #Standard, unsplit normal map
                mat.node_tree.links.new(img_node.outputs["Color"], normal_node.inputs["Color"])
        
        elif "spc" in img_name:
            #Specular
            img_node.image.colorspace_settings.name="Non-Color"
            mat.node_tree.links.new(img_node.outputs["Color"], shader.inputs["Specular"])
            
            #Specular tint. How colorful is the specular image? Assume the dif is similarly colored
            
            #Convert specular color to BW
            spc_bw_node=mat.node_tree.nodes.new("ShaderNodeRGBToBW")
            
            #Find difference between specular color and BW
            spc_comp_node=mat.node_tree.nodes.new("ShaderNodeMixRGB")
            spc_comp_node.blend_type="DIFFERENCE"
            
            #Split difference into three channels
            spc_split_node=mat.node_tree.nodes.new("ShaderNodeSeparateRGB")
            
            #Find largest channel, and control specular tint with it
            spc_max1_node=mat.node_tree.nodes.new("ShaderNodeMath")
            spc_max1_node.operation="MAXIMUM"
            
            spc_max2_node=mat.node_tree.nodes.new("ShaderNodeMath")
            spc_max2_node.operation="MAXIMUM"
            
            #Specular tint calculation links setup
            mat.node_tree.links.new(img_node.outputs["Color"], spc_bw_node.inputs["Color"])
            mat.node_tree.links.new(spc_bw_node.outputs["Val"], spc_comp_node.inputs["Color1"])
            mat.node_tree.links.new(img_node.outputs["Color"], spc_comp_node.inputs["Color2"])
            mat.node_tree.links.new(spc_comp_node.outputs["Color"], spc_split_node.inputs["Image"])
            mat.node_tree.links.new(spc_max1_node.outputs["Value"], spc_max2_node.inputs[0])
            mat.node_tree.links.new(spc_split_node.outputs["R"], spc_max1_node.inputs[0])
            mat.node_tree.links.new(spc_split_node.outputs["G"], spc_max1_node.inputs[1])
            mat.node_tree.links.new(spc_split_node.outputs["B"], spc_max2_node.inputs[1])
            mat.node_tree.links.new(spc_max2_node.outputs["Value"], shader.inputs["Specular Tint"])
        
        elif "fal" in img_name:
            #Displacement
            img_node.image.colorspace_settings.name="Non-Color"
            disp_node=mat.node_tree.nodes.new('ShaderNodeDisplacement')
            disp_node.inputs["Scale"].default_value=DISP_SCALE
            mat.node_tree.links.new(img_node.outputs["Color"], disp_node.inputs["Height"])
        
        elif "pow" in img_name:
            #Inverted roughness
            img_node.image.colorspace_settings.name="Non-Color"
            pow_inv_node=mat.node_tree.nodes.new('ShaderNodeInvert')
            mat.node_tree.links.new(img_node.outputs["Color"], pow_inv_node.inputs["Color"])
            mat.node_tree.links.new(pow_inv_node.outputs["Color"], shader.inputs["Roughness"])

