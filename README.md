# SMD-Model-PostImport
Blender scripts (not addons) to help clean up the skeletons and materials of imported SMD files

These scripts are meant to run in Blender after some preliminary configuration (described at the beginning of each file), such as going into edit mode on the skeleton, or changing IMAGE_PATH to the appropriate directory.

I reccommend reviewing the results of each script and making manual edits as neccesary :)

SMD_skeleton_fixer.py: Faces of models usually have the most tweaking work to be done, where unchanged bones are often not entirely symmetrical, but rather one side points in the opposite direction. I recommend using symmetrized editing and doing "0 moves" on all such bones (say, changing the bone length by one unit then changing it back: this will enforce symmetry if the bones are named the same)

SMD_material_setup.py: some inputs where a multi-image setup was not expected may be hooked up incorrectly. Also, all nodes are currently dropped at 0,0,0, so I reccomend using the Node Arranger addon to fix this quickly before editing. Currently, you will need to select some node in the material to make it "active" before the addon will work.
