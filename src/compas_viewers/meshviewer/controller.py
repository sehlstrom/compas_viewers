import os

from functools import partial

from PySide2 import QtCore
from PySide2 import QtWidgets

from OpenGL.GL import *    # noqa: F401 F403
from OpenGL.GLU import *   # noqa: F401 F403
from OpenGL.GLUT import *  # noqa: F401 F403

import compas

from compas.datastructures import Mesh
from compas.datastructures import mesh_flip_cycles
from compas.datastructures import mesh_subdivide

from compas.geometry import centroid_points
from compas.utilities import hex_to_rgb
from compas.utilities import flatten

from compas_viewers import core
from compas_viewers.meshviewer.model import MeshView


HERE = os.path.dirname(__file__)


__all__ = ['Controller']


get_obj_file = partial(
    QtWidgets.QFileDialog.getOpenFileName,
    caption='Select OBJ file',
    dir=compas.DATA,
    filter='OBJ files (*.obj)'
)

get_stl_file = partial(
    QtWidgets.QFileDialog.getOpenFileName,
    caption='Select STL file',
    dir=compas.DATA,
    filter='STL files (*.stl)'
)

get_json_file = partial(
    QtWidgets.QFileDialog.getOpenFileName,
    caption='Select JSON file',
    dir=compas.DATA,
    filter='JSON files (*.json)'
)

get_ply_file = partial(
    QtWidgets.QFileDialog.getOpenFileName,
    caption='Select PLY file',
    dir=compas.DATA,
    filter='PLY files (*.ply)'
)

hex_to_rgb = partial(hex_to_rgb, normalize=True)


def flist(items):
    return list(flatten(items))


class Controller(core.controller.Controller):

    def __init__(self, app):
        super(Controller, self).__init__(app)
        self._mesh = None
        self._meshview = None

    @property
    def settings(self):
        return self.app.settings

    @property
    def view(self):
        return self.app.view

    @property
    def mesh(self):
        return self._mesh

    @property
    def meshview(self):
        return self._meshview

    @mesh.setter
    def mesh(self, mesh):
        self._mesh = mesh
        self._meshview = MeshView(mesh)

    def center_mesh(self):
        xyz = [self.mesh.vertex_coordinates(key) for key in self.mesh.vertices()]
        cx, cy, cz = centroid_points(xyz)
        for key, attr in self.mesh.vertices(True):
            attr['x'] -= cx
            attr['y'] -= cy
            attr['z'] -= cz

    def adjust_camera(self):
        pass

    # ==========================================================================
    # Slots
    # ==========================================================================

    def on_rotX(self, rx):
        slider = self.controls['elevation']
        slider.update(rx)

    def on_rotZ(self, rz):
        slider = self.controls['azimuth']
        slider.update(rz)

    def on_distance(self, d):
        slider = self.controls['distance']
        slider.update(d)

    # ==========================================================================
    # commands
    # ==========================================================================

    def select_command(self):
        pass

    # ==========================================================================
    # constructors
    # ==========================================================================

    def from_obj(self):
        filename, _ = get_obj_file()
        if filename:
            self.mesh = Mesh.from_obj(filename)
            # self.center_mesh()
            self.view.make_buffers()
            self.view.updateGL()

    def to_obj(self):
        self.message('Export to OBJ is under construction...')

    def from_json(self):
        filename, _ = get_json_file()
        if filename:
            self.mesh = Mesh.from_json(filename)
            self.view.make_buffers()
            self.view.updateGL()

    def to_json(self):
        self.message('Export to JSON is under construction...')

    def from_stl(self):
        filename, _ = get_stl_file()
        if filename:
            self.mesh = Mesh.from_stl(filename)
            self.view.make_buffers()
            self.view.updateGL()

    def to_stl(self):
        self.message('Export to STL is under construction...')

    def from_ply(self):
        filename, _ = get_ply_file()
        if filename:
            self.mesh = Mesh.from_ply(filename)
            self.view.make_buffers()
            self.view.updateGL()

    def to_ply(self):
        self.message('Export to STL is under construction...')

    def from_polyhedron(self, f):
        self.mesh = Mesh.from_polyhedron(f)
        self.view.make_buffers()
        self.view.updateGL()

    # ==========================================================================
    # view
    # ==========================================================================

    def zoom_extents(self):
        self.message('Zoom Extents is under construction...')

    def zoom_in(self):
        self.view.camera.zoom_in()
        self.view.updateGL()

    def zoom_out(self):
        self.view.camera.zoom_out()
        self.view.updateGL()

    def set_view(self, view):
        self.view.current = view
        self.view.updateGL()

    def update_camera_settings(self):
        self.log('Updating the camera settings.')

    def capture_image(self):
        result = QtWidgets.QFileDialog.getSaveFileName(caption="File name", dir=HERE)
        if not result:
            return
        filepath = result[0]
        root, ext = os.path.splitext(filepath)
        if not ext:
            return
        self.view.capture(filepath, ext[1:])

    def capture_video(self):
        self.message('Capture Video is under construction...')

    # ==========================================================================
    # appearance
    # ==========================================================================

    def slide_size_vertices(self, value):
        self.settings['vertices.size:value'] = value
        self.view.updateGL()

    def edit_size_vertices(self, value):
        self.settings['vertices.size:value'] = value
        self.view.updateGL()

    def slide_width_edges(self, value):
        self.settings['edges.width:value'] = value
        self.view.updateGL()

    def edit_width_edges(self, value):
        self.settings['edges.width:value'] = value
        self.view.updateGL()

    def slide_scale_normals(self, value):
        self.settings['normals.scale:value'] = value
        self.view.updateGL()

    def edit_scale_normals(self, value):
        self.settings['normals.scale:value'] = value
        self.view.updateGL()

    # ==========================================================================
    # visibility
    # ==========================================================================

    def toggle_faces(self, state):
        self.settings['faces.on'] = state == QtCore.Qt.Checked
        self.view.updateGL()

    def toggle_edges(self, state):
        self.settings['edges.on'] = state == QtCore.Qt.Checked
        self.view.updateGL()

    def toggle_vertices(self, state):
        self.settings['vertices.on'] = state == QtCore.Qt.Checked
        self.view.updateGL()

    def toggle_normals(self, state):
        self.message('Display of face and vertex normals is still under construction...')
        self.settings['normals.on'] = state == QtCore.Qt.Checked
        self.view.updateGL()

    # ==========================================================================
    # color
    # ==========================================================================

    def change_vertices_color(self, color):
        self.settings['vertices.color'] = color
        self.view.update_vertex_buffer('vertices.color', self.view.array_vertices_color)
        self.view.updateGL()
        self.app.main.activateWindow()

    def change_edges_color(self, color):
        self.settings['edges.color'] = color
        self.view.update_vertex_buffer('edges.color', self.view.array_edges_color)
        self.view.updateGL()
        self.app.main.activateWindow()

    def change_faces_color_front(self, color):
        self.settings['faces.color:front'] = color
        self.view.update_vertex_buffer('faces.color:front', self.view.array_faces_color_front)
        self.view.updateGL()
        self.app.main.activateWindow()

    def change_faces_color_back(self, color):
        self.settings['faces.color:back'] = color
        self.view.update_vertex_buffer('faces.color:back', self.view.array_faces_color_back)
        self.view.updateGL()
        self.app.main.activateWindow()

    def change_normals_color(self, color):
        self.settings['normals.color'] = color
        self.view.update_vertex_buffer('normals.color', self.view.array_normals_color)
        self.view.updateGL()
        self.app.main.activateWindow()

    # ==========================================================================
    # camera
    # ==========================================================================

    def slide_azimuth(self, value):
        self.view.camera.rz = float(value)
        self.view.updateGL()

    def edit_azimuth(self, value):
        pass

    def slide_elevation(self, value):
        self.view.camera.rx = float(value)
        self.view.updateGL()

    def edit_elevation(self, value):
        pass

    def slide_distance(self, value):
        self.view.camera.distance = float(value)
        self.view.updateGL()

    def edit_distance(self, value):
        pass

    def slide_fov(self, value):
        self.view.camera.fov = float(value)
        self.view.updateGL()

    def edit_fov(self, value):
        pass

    # ==========================================================================
    # tools
    # ==========================================================================

    # open dialog or panel for additional options
    # set options and apply

    def flip_normals(self):
        mesh_flip_cycles(self.mesh)
        # this is a bit of a hack
        # faces of the viewmesh only get calculated at the time when the mesh
        # is assigned to the viewmesh
        self.meshview.mesh = self.mesh
        self.view.update_index_buffer('faces:front', self.view.array_faces_front)
        self.view.update_index_buffer('faces:back', self.view.array_faces_back)
        self.view.updateGL()

    # implement as toggle?
    # if 'on' the orginal is shown as control mesh (edges only)
    # and the subdivision surface up to the specified level
    def subdivide(self, scheme, k):
        self.mesh = mesh_subdivide(self.mesh, scheme=scheme, k=k)
        self.view.make_buffers()
        self.view.updateGL()

    def smooth_wo_shrinking(self):
        pass

    def smooth_area(self):
        pass

    def smooth_laplacian(self):
        pass


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    pass
