from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets

from compas_viewers.core import App

from compas_viewers.multimeshviewer.model import MeshObject
from compas_viewers.multimeshviewer.view import View
from compas_viewers.multimeshviewer.controller import Controller

from compas_viewers.multimeshviewer.settings import SETTINGS
from compas_viewers.multimeshviewer.ui import UI
from compas_viewers.multimeshviewer.style import STYLE


__all__ = ['MultiMeshViewer']


class ObjectTree(QtWidgets.QTreeWidget):

    def __init__(self):
        super().__init__()
        self.setColumnCount(2)
        self.setHeaderLabels(['Objects', 'Properties'])


class Manager(object):

    def __init__(self, parent, app):
        self._items = []
        self.app = app
        self.parent = parent
        self.widget = ObjectTree()
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.widget.setLayout(self.layout)
        self.parent.setWidget(self.widget)
        self.widget.itemSelectionChanged.connect(self.on_item_selection_changed)

    def set_items(self, items):
        self._items = items
        meshitems = []
        for item in items:
            meshitem = QtWidgets.QTreeWidgetItem()
            meshitem.setText(0, "Mesh")
            meshitems.append(meshitem)
            # vertices
            verticesitem = QtWidgets.QTreeWidgetItem(meshitem)
            verticesitem.setText(0, "Vertices")
            for key in item.data.vertices():
                vertexitem = QtWidgets.QTreeWidgetItem(verticesitem)
                vertexitem.setText(0, "{}".format(key))
            # edges
            edgesitem = QtWidgets.QTreeWidgetItem(meshitem)
            edgesitem.setText(0, "Edges")
        self.widget.addTopLevelItems(meshitems)

    def find_selected_item(self, item):
        index = self.widget.indexFromItem(item)
        trail = []
        while True:
            i = index.row()
            j = index.column()
            if i == -1 and j == -1:
                break
            trail.append((i, j))
            index = index.parent()
        return trail[::-1]

    def on_item_selection_changed(self):
        for item in self.widget.selectedItems():
            trail = self.find_selected_item(item)
            mid = trail[0][0]
            meshobject = self._items[mid]
            mesh = meshobject.data
            if len(trail) > 0:
                for m in self._items:
                    m.color = '#cccccc'
                meshobject.color = '#ff0000'
            if len(trail) > 1:
                pass
            if len(trail) > 2:
                if trail[1][0] == 0:
                    # vertex
                    key = int(item.text(0))
                    attr = {name: mesh.get_vertex_attribute(key, name) for name in mesh.default_vertex_attributes.keys()}
                    print("Mesh {}: Vertex {} => {}".format(mid, key, attr))
                else:
                    # edge
                    key = int(item.text(0))
                    attr = {name: mesh.get_edge_attribute(key, name) for name in mesh.default_edge_attributes.keys()}
                    print("Mesh {}: Edge {} => {}".format(mid, key, attr))
        self.app.view.make_buffers()
        self.app.view.updateGL()


class MultiMeshViewer(App):
    """"""

    def __init__(self):
        super().__init__(SETTINGS, UI, STYLE)
        self.controller = Controller(self)
        self.view = View(self.controller)
        self.view.camera.events.rotX.connect(self.controller.on_rotX)
        self.view.camera.events.rotZ.connect(self.controller.on_rotZ)
        self.view.camera.events.distance.connect(self.controller.on_distance)

        self.setup()
        self.init()
        self.init_sidebar2()

        self.manager = Manager(self.sidebar2, self)

        self.view.glInit()
        self.view.setup_grid()
        self.view.setup_axes()

    def init_sidebar2(self):
        self.sidebar2 = QtWidgets.QDockWidget()
        self.sidebar2.setObjectName('Sidebar')
        self.sidebar2.setAllowedAreas(QtCore.Qt.RightDockWidgetArea)
        self.sidebar2.setFeatures(QtWidgets.QDockWidget.NoDockWidgetFeatures)
        self.sidebar2.setMinimumWidth(180)
        self.sidebar2.setTitleBarWidget(QtWidgets.QWidget())
        self.sidebar2.setContentsMargins(0, 0, 0, 0)
        self.main.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.sidebar2)

    @property
    def meshes(self):
        return self.controller.meshes

    @meshes.setter
    def meshes(self, meshes):
        temp = []
        for mesh in meshes:
            if not isinstance(mesh, MeshObject):
                mesh = MeshObject(mesh)
            temp.append(mesh)
        self.controller.meshes = temp
        # self.controller.center()
        self.manager.set_items(self.meshes)
        self.view.glInit()
        self.view.make_buffers()
        self.view.updateGL()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import random

    from math import radians

    from compas.geometry import Box
    from compas.datastructures import Mesh
    from compas.datastructures import mesh_transform_numpy
    from compas.utilities import rgb_to_hex
    from compas.geometry import Translation
    from compas.geometry import Rotation

    meshes = []

    for i in range(10):
        vector = [random.randint(0, 10), random.randint(0, 10), random.randint(0, 5)]
        T = Translation(vector)
        axis = [0, 0, 1.0]
        angle = radians(random.randint(0, 180))
        R = Rotation.from_axis_and_angle(axis, angle)
        X = T * R
        w, h, d = random.randint(1, 3), random.randint(1, 3), random.randint(1, 3)
        box = Box.from_width_height_depth(w, h, d)
        mesh = Mesh.from_shape(box)
        mesh_transform_numpy(mesh, X)
        # rgb = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        rgb = (210, 210, 210)
        obj = MeshObject(mesh, color=rgb_to_hex(rgb))
        meshes.append(obj)

    viewer = MultiMeshViewer()
    viewer.meshes = meshes

    viewer.show()
