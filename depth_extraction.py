import blenderproc as bproc
import os
import math as m
import h5py
from PIL import Image
import numpy as np
import shutil

# blenderproc run .\pipeline.py

OUTPUTS_DIR = os.path.join(os.getcwd(), 'outputs')
RESOURCES_DIR = os.path.join(os.getcwd(), 'resources')
SCENES_DIR = os.path.join(RESOURCES_DIR, 'scenes')

def render(camera, scene, output):
    # initialize blenderproc
    bproc.init()

    # load the objects into the scene
    objs = bproc.loader.load_blend(scene)

    # define a light and set its location and energy level
    light = bproc.types.Light()
    light.set_type("POINT")
    light.set_location([5, -5, 5])
    light.set_energy(1000)

    # define the camera resolution
    bproc.camera.set_resolution(640, 480)

    # read camera positions from file and convert into homogeneous camera-world transformation
    with open(camera, 'r') as f:
        trajectory = []
        count = 0
        for line in f.readlines():
            # generate camera pose from file
            line = [float(x) for x in line.split()]
            position, euler_rotation = line[:3], line[3:6]

            matrix_world = bproc.math.build_transformation_mat(position, euler_rotation)
            bproc.camera.add_camera_pose(matrix_world)

            # add camera pose to trajectory log
            trajectory.append(f"{count} {count} " + str(count + 1))
            count += 1
            o3d_world = bproc.math.change_source_coordinate_frame_of_transformation_matrix(matrix_world, ["X", "-Y", "-Z"])
            # coord_change_mat = np.array([[1., 0., 0.], [0, -1., 0.], [0., 0., -1.]], dtype=np.float32)
            # pts3D = pts3D.dot(coord_change_mat.T)
            for array in o3d_world:
                trajectory.append(' '.join(str(x) for x in array))

        # my old way of creating the transformation matrix
            # if (euler_rotation[0] == 0) and (euler_rotation[2] == 0):
            #     rotation_matrix = convertToMatrix(euler_rotation[0], euler_rotation[1], euler_rotation[2])
            # else:
            #     rotation_matrix = convertToMatrix((1.1), (0), (euler_rotation[2]+3.1415926))
            # trajectory.append(f"{rotation_matrix[0][0]} {rotation_matrix[0][1]} {rotation_matrix[0][2]} {(position[0])}")
            # trajectory.append(f"{rotation_matrix[1][0]} {rotation_matrix[1][1]} {rotation_matrix[1][2]} {(position[1])}")
            # trajectory.append(f"{rotation_matrix[2][0]} {rotation_matrix[2][1]} {rotation_matrix[2][2]} {position[2]}")
            # trajectory.append('0 0 0 1')

        # write trajectory log to output directory    
        with open(os.path.join(output, 'trajectory.log'), 'w') as t:
            for entry in trajectory:
                t.write(entry)
                t.write('\n')

    # enable depth rendering
    bproc.renderer.enable_depth_output(activate_antialiasing=False)

    # render poses in scene
    data = bproc.renderer.render()

    # write data to .hdf5 files
    bproc.writer.write_hdf5(output, data)


def extract(scene):
    for file in os.listdir(scene):
        if file.endswith('.hdf5'):
            with h5py.File(os.path.join(scene, file)) as hf:
                # extract data from hdf5 files
                colors = hf.get('colors')
                depth = hf.get('depth')

                # convert colors to jpg
                color_array = np.array(colors)
                im = Image.fromarray(color_array, mode="RGB")
                im.save(os.path.join(scene, f'{os.path.splitext(file)[0]}.jpg'))

                # convert depth to png

                # affects the length
                depth_array = np.array(depth)
                for i in range(len(depth_array)):
                    for j in range(len(depth_array[i])):
                        depth_array[i][j] = depth_array[i][j] * 15
                dp = Image.fromarray(depth_array)
                if dp.mode != 'RGB':
                    dp = dp.convert('RGB')
                dp.save(os.path.join(scene, f'{os.path.splitext(file)[0]}.png'))


#my old way of creating the 3x3 rotation matrix
# def convertToMatrix(x, y, z):
#     r = [[m.cos(y) * m.cos(z), (m.sin(x) * m.sin(y) * m.cos(z)) - (m.cos(x) * m.sin(z)), (m.cos(x) * m.sin(z) * m.cos(z)) + (m.sin(x) * m.sin(z))],
#          [m.cos(y) * m.sin(z), (m.sin(x) * m.sin(y) * m.sin(z)) - (m.cos(x) * m.cos(z)), (m.cos(x) * m.sin(z) * m.sin(z)) + (m.sin(x) * m.cos(z))],
#          [-(m.sin(y)),          m.sin(x) * m.cos(y),                                      m.cos(x) * m.cos(y)                                    ]]
#     return r

def main():
    # clean output directory
    if os.path.exists(OUTPUTS_DIR):
        shutil.rmtree(OUTPUTS_DIR)
    os.mkdir(OUTPUTS_DIR)

    # set camera poses    
    camera = os.path.join(RESOURCES_DIR, 'camera_positions.txt')

    # render scenes
    for scene in os.listdir(SCENES_DIR):
        output = os.path.join(OUTPUTS_DIR, os.path.splitext(scene)[0])
        if not os.path.exists(output):
            os.mkdir(output)
        render(camera, os.path.join(SCENES_DIR, scene), output)

    # extract data
    for scene in next(os.walk(OUTPUTS_DIR))[1]:
        extract(os.path.join(OUTPUTS_DIR, scene))

if __name__ == "__main__":
    main()