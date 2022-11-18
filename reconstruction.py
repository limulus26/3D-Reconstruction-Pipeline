import open3d as o3d
import numpy as np
import os

class CameraPose:

    def __init__(self, meta, mat):
        self.metadata = meta
        self.pose = mat

    def __str__(self):
        return 'Metadata : ' + ' '.join(map(str, self.metadata)) + '\n' + \
            "Pose : " + "\n" + np.array_str(self.pose)

def read_trajectory(filename):
    traj = []
    with open(filename, 'r') as f:
        metastr = f.readline()
        while metastr:
            metadata = list(map(int, metastr.split()))
            mat = np.zeros(shape=(4, 4))
            for i in range(4):
                matstr = f.readline()
                mat[i, :] = np.fromstring(matstr, dtype=float, sep=' \t')
            traj.append(CameraPose(metadata, mat))
            metastr = f.readline()
    return traj

def construct(scene):
    # read camera trajectory
    camera_poses = read_trajectory(os.path.join(scene, 'trajectory.log'))

    volume = o3d.pipelines.integration.ScalableTSDFVolume(
        voxel_length = 8.0 / 512.0,
        sdf_trunc = 0.4,
        color_type = o3d.pipelines.integration.TSDFVolumeColorType.RGB8
    )

    for i in range(len(camera_poses)):
        # print(f"Integrate {i}-th image into the volume.")
        color = o3d.io.read_image(os.path.join(scene, f"{i}.jpg"))
        depth = o3d.io.read_image(os.path.join(scene, f"{i}.png"))
        rgbd = o3d.geometry.RGBDImage.create_from_color_and_depth(
            color, depth, depth_trunc=10, convert_rgb_to_intensity=False, depth_scale=0.1
        )
        
        volume.integrate(
            rgbd,
            o3d.camera.PinholeCameraIntrinsic(
                o3d.camera.PinholeCameraIntrinsicParameters.PrimeSenseDefault
            ),
            np.linalg.inv(camera_poses[i].pose)
            # camera_poses[i].pose
        )
    
    # print("Extracting a triangle mesh from the volume and visualize it.")
    mesh = volume.extract_triangle_mesh()
    mesh.compute_vertex_normals()
    o3d.visualization.draw_geometries([mesh],
                                    #    front=[0.5297, -0.1873, -0.8272],
                                    #    lookat=[2.0712, 2.0312, 1.7251],
                                    #    up=[-0.0558, -0.9809, 0.1864],
                                    #    zoom=0.47
        )