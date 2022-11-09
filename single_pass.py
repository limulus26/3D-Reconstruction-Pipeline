import blenderproc as bproc
import argparse
import math as m

# blenderproc run ..\scripts\single_pass.py examples/resources/camera_positions examples/resources/scene.obj examples/basics/basic/output

def convertToMatrix(z, y, x):
    r = [[m.cos(y) * m.cos(z), (m.sin(x) * m.sin(y) * m.cos(z)) - (m.cos(x) * m.sin(z)), (m.cos(x) * m.sin(z) * m.cos(z)) + (m.sin(x) * m.sin(z))],
         [m.cos(y) * m.sin(z), (m.sin(x) * m.sin(y) * m.sin(z)) - (m.cos(x) * m.cos(z)), (m.cos(x) * m.sin(z) * m.sin(z)) + (m.sin(x) * m.cos(z))],
         [-(m.sin(y)),          m.sin(x) * m.cos(y),                                      m.cos(x) * m.cos(y)                                    ]]
    return r

parser = argparse.ArgumentParser()
parser.add_argument('camera', help="Path to the camera file, should be examples/resources/camera_positions")
parser.add_argument('scene', help="Path to the scene.obj file, should be examples/resources/scene.obj")
parser.add_argument('output_dir', help="Path to where the final files, will be saved, could be examples/basics/basic/output")
args = parser.parse_args()

bproc.init()

# load the objects into the scene
objs = bproc.loader.load_obj(args.scene)

# define a light and set its location and energy level
light = bproc.types.Light()
light.set_type("POINT")
light.set_location([5, -5, 5])
light.set_energy(1000)

# define the camera resolution
bproc.camera.set_resolution(640, 480)

# read the camera positions file and convert into homogeneous camera-world transformation
with open(args.camera, "r") as f:
    trajLines = []
    count = 0
    for line in f.readlines():
        line = [float(x) for x in line.split()]
        position, euler_rotation = line[:3], line[3:6]
        matrix_world = bproc.math.build_transformation_mat(position, euler_rotation)
        bproc.camera.add_camera_pose(matrix_world)
        # Create odometry log file
        trajLines.append(str(count) + " " + str(count) + " " + str(count + 1))
        count += 1
        er = convertToMatrix(euler_rotation[0], euler_rotation[1], euler_rotation[2])
        strEr = []
        for row in er:
            strEr.append([str(i) for i in row])
        trajLines.append(strEr[0][0] + " " + strEr[0][1] + " " + strEr[0][2] + " " + str(position[0]))
        trajLines.append(strEr[1][0] + " " + strEr[1][1] + " " + strEr[1][2] + " " + str(position[1]))
        trajLines.append(strEr[2][0] + " " + strEr[2][1] + " " + strEr[2][2] + " " + str(position[2]))
        trajLines.append('0 0 0 1')

    with open('trajectory.log', 'w') as t:
        for entry in trajLines:
            t.write(entry)
            t.write('\n')

# activate normal and depth rendering
bproc.renderer.enable_normals_output()
bproc.renderer.enable_depth_output(activate_antialiasing=False)

# render the whole pipeline
data = bproc.renderer.render()

# write the data to a .hdf5 container
bproc.writer.write_hdf5(args.output_dir, data)


