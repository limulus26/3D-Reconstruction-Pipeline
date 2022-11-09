# howdy

# for each object we can use the same camera poses and circle around the objects taking a photo
# at each point. then we can manually make a camera trajectory from the poses ez pz
# which we use in the tsdf module

# so the process will just look like

# for each object in list
#   make a new dir
#   circle the object taking snapshots at each point
#   save the snapshots in the new dir ()
#   start tsdf reconstruction within the new dir

# -- tsdf reconstruction --
# look at a dir
# use all the snapshots in the dir as input for the function
# run the function
# save the output