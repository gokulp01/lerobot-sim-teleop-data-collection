# move from mujoco.viewer to viser!!
import numpy as np
import mujoco
import viser
import trimesh
import threading
import time
from typing import Optional
from scipy.spatial.transform import Rotation


class ViserViewer:
    
    def __init__(
        self, 
        model: mujoco.MjModel, 
        data: mujoco.MjData,
        host: str = "0.0.0.0",
        port: int = 8080
    ):
        self.model = model
        self.data = data
        
        self.server = viser.ViserServer(host=host, port=port)
        
        self.geom_handles = {}
        self.body_handles = {}
        
        self.cam = CameraSettings()
        
        self._setup_scene()
        
        print(f"Viser viewer started at http://{host}:{port}")
    
    def _setup_scene(self):
        """Setup the initial Viser scene with MuJoCo model geometry."""
        
        mujoco.mj_forward(self.model, self.data)
        
        for geom_id in range(self.model.ngeom):
            self._add_geom(geom_id)
    
    def _add_geom(self, geom_id: int):
        """Add a MuJoCo geometry to the Viser scene."""
        geom_type = self.model.geom_type[geom_id]
        geom_size = self.model.geom_size[geom_id]
        geom_rgba = self.model.geom_rgba[geom_id]
        
        geom_name = mujoco.mj_id2name(self.model, mujoco.mjtObj.mjOBJ_GEOM, geom_id)
        if geom_name is None:
            geom_name = f"geom_{geom_id}"
        
        pos = self.data.geom_xpos[geom_id].copy()
        mat = self.data.geom_xmat[geom_id].reshape(3, 3)
        
        rot = Rotation.from_matrix(mat)
        quat_xyzw = rot.as_quat()  # returns [x, y, z, w]
        quat = np.array([quat_xyzw[3], quat_xyzw[0], quat_xyzw[1], quat_xyzw[2]])  # wxyz format
        
        color = tuple(geom_rgba[:3])
        
        try:
            mesh = None
            
            if geom_type == mujoco.mjtGeom.mjGEOM_BOX:
                mesh = trimesh.creation.box(extents=geom_size * 2)
                
            elif geom_type == mujoco.mjtGeom.mjGEOM_SPHERE:
                mesh = trimesh.creation.icosphere(radius=geom_size[0], subdivisions=2)
                
            elif geom_type == mujoco.mjtGeom.mjGEOM_CAPSULE:
                mesh = trimesh.creation.capsule(radius=geom_size[0], height=geom_size[1] * 2)
                
            elif geom_type == mujoco.mjtGeom.mjGEOM_CYLINDER:
                mesh = trimesh.creation.cylinder(radius=geom_size[0], height=geom_size[1] * 2)
                
            elif geom_type == mujoco.mjtGeom.mjGEOM_MESH:
                mesh_id = self.model.geom_dataid[geom_id]
                if mesh_id >= 0:
                    mesh_start = self.model.mesh_vertadr[mesh_id]
                    mesh_nvert = self.model.mesh_vertnum[mesh_id]
                    mesh_vertices = self.model.mesh_vert[mesh_start:mesh_start + mesh_nvert].copy()
                    
                    mesh_face_start = self.model.mesh_faceadr[mesh_id]
                    mesh_nface = self.model.mesh_facenum[mesh_id]
                    mesh_faces = self.model.mesh_face[mesh_face_start:mesh_face_start + mesh_nface].copy()

                    mesh = trimesh.Trimesh(vertices=mesh_vertices, faces=mesh_faces)
            else:
                mesh = trimesh.creation.icosphere(radius=0.01, subdivisions=1)
            
            if mesh is not None:
                if hasattr(mesh, 'visual') and color is not None:
                    color_uint8 = (np.array(color) * 255).astype(np.uint8)
                    mesh.visual.vertex_colors = np.tile(color_uint8, (len(mesh.vertices), 1))
                
                handle = self.server.scene.add_mesh_trimesh(
                    name=f"/geom/{geom_name}",
                    mesh=mesh,
                    position=pos,
                    wxyz=quat
                )
                self.geom_handles[geom_id] = handle
                
        except Exception as e:
            print(f"Warning: Could not add geometry {geom_name}: {e}")
    
    def sync(self):
        for geom_id, handle in self.geom_handles.items():
            pos = self.data.geom_xpos[geom_id].copy()
            mat = self.data.geom_xmat[geom_id].reshape(3, 3)
            
            rot = Rotation.from_matrix(mat)
            quat_xyzw = rot.as_quat()  # returns [x, y, z, w]
            quat_wxyz = np.array([quat_xyzw[3], quat_xyzw[0], quat_xyzw[1], quat_xyzw[2]])
            
            try:
                handle.position = tuple(pos)
                handle.wxyz = tuple(quat_wxyz)
            except Exception as e:
                pass
    
    def close(self):
        pass
    
    def __del__(self):
        self.close()


class CameraSettings:
    
    def __init__(self):
        self.azimuth = 0.0
        self.distance = 1.0
        self.elevation = 0.0
        self.lookat = np.array([0.0, 0.0, 0.0])


def launch_passive(model: mujoco.MjModel, data: mujoco.MjData, **kwargs) -> ViserViewer:
    return ViserViewer(model, data, **kwargs)

