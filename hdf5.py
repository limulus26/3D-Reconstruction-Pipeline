import h5py
from PIL import Image
import numpy as np


with h5py.File('../output/1.hdf5') as hf:

    # Extract exr files from hdf5
    colors = hf.get('colors')
    depth = hf.get('depth')
    normals = hf.get('normals')

    # Convert colors to jpg
    color_array = np.array(colors)
    im = Image.fromarray(color_array)
    im.save("colors.jpg")

    # Convert depth to jpg
    depth_array = np.array(depth)
    np.save('depth.npy', depth_array)
    # im = Image.fromarray(depth_array)
    # im.save("depth.png")

    # Convert normals to jpg
    # normals_array = np.array(normals)
    # im = Image.fromarray(normals_array, mode="F")
    # im.save("normals.jpg")
