from common import Orientation
import numpy as np
from display.slice_view_widget import SliceWidget

class Coordinate_mapper(object):
    """Map coordinates between views and volumes
    """
    def __init__(self, views: dict, saved_flip_info: dict):
        self.views = views  # Get a reference to the views dict that contains the slice view widgets
        self.flip_info = saved_flip_info


    def view_to_volume(self, x: int, y: int, idx: int, src_view: SliceWidget) -> tuple:
        """
        Given coordinates from a slice view, convert to actual coordinates in the correct volume space
        This is required as we do some inversion of the order of slices as they come off the volumes to show
        a view that the IMPC annotators like.

        Currently not working if there are no Slice views that are in axial view

        Parameters
        ----------
        x: int
        y: int
        idx: int
        src_view: SliceWidget
        reverse: bool
            True: map from volume space to image space
            False: map from image space to volume sapce

        Returns
        -------
        (x, y, z)

        Notes
        -----

        This maps the view coordinates from any view to the noral axial view. Then adds correction for the inverted
        slice ordering

        Problem: If the impc_vie is active the view_to_view() inverts x when mapping between
        axial and the other views so that cross hairs work. this breaks the mouse
        position labels

        """
        # This will break if there are no axial views present

        src_dims = src_view.main_volume.shape_xyz()

        # first map to axial space. the new order of the pint at that position

        flip_to_axial_order = {
            Orientation.axial: [0, 1, 2],
            Orientation.coronal: [0, 2, 1],
            Orientation.sagittal: [1, 2, 0]
        }

        # # Pyqtgraph indexes the x dimension in the opposite direction to Slicer, so flip it
        # dims = self.main_volume.shape_xyz()
        if src_view.orientation in (Orientation.axial, Orientation.coronal):
            x = src_dims[0] - x
        elif src_view.orientation == Orientation.sagittal:
            x = src_dims[1] - x

        order = flip_to_axial_order[src_view.orientation]
        axial_space_points = [j for _, j in sorted(zip(order, [x, y, idx]), key=lambda pair: pair[0])]

        if self.flip_info['impc_view']:
            if src_view.orientation == Orientation.axial:
                axial_space_points[2] = src_dims[2] - axial_space_points[2]
                axial_space_points[1] = src_dims[1] - axial_space_points[1]

            if src_view.orientation == Orientation.coronal:
                axial_space_points[1] = src_dims[1] - axial_space_points[1]

        return axial_space_points

    def view_to_view(self, x, y, z, src_view, dest_view, rev=False):
        """
        Given a coordinate on one view with a given orientation as well as horizontal flip and slice ordering status,
        map to another view with a given orientation , flip and ordering.
        Parameters
        ----------
        x: int
            the x position in the view
        y: int
            the y position in the view
        z: int
            the slice index
        src_view: [SliceWidget, None]
            The slice view widget that the corrdinate is mapped from. If none assum nornal volume space (z == axial)
        dest_view: SliceWidget
            The slice view widget to map the coordinates to
        rev: bool
            whether to return the inverted point (len(dimension) - point)
        Returns
        -------
        tuple
            (x,y,idx)

        """

        if src_view is None:
            src_orientation = Orientation.axial
        else:
            src_orientation = src_view.orientation

        dest_orientation = dest_view.orientation
        dest_dims = dest_view.main_volume.shape_xyz()

        # first map to axial space. the new order of the pint at that position

        flip_to_axial_order = {
            Orientation.axial:    [0, 1, 2],
            Orientation.coronal:  [0, 2, 1],
            Orientation.sagittal: [1, 2, 0]
        }

        order = flip_to_axial_order[src_orientation]
        axial_space_points = [j for _, j in sorted(zip(order, [x, y, z]), key=lambda pair: pair[0])]

        if rev:  # CROSS HAIRS
            axial_space_points = [d - p for p, d in zip(axial_space_points, dest_dims)]

        flip_from_axial_order = {
            Orientation.axial:    [0, 1, 2],
            Orientation.coronal:  [0, 2, 1],
            Orientation.sagittal: [2, 0, 1]
        }

        order = flip_from_axial_order[dest_orientation]
        dest_points = [j for _, j in sorted(zip(order, axial_space_points), key=lambda pair: pair[0])]

        # #this is to get into pyqtgraph space
        # if dest_orientation == Orientation.sagittal and src_orientation is not Orientation.sagittal:
        #     dest_points[0] = dest_dims[1] - dest_points[0]
        #     dest_points[2] = dest_dims[0] - dest_points[2]
        #
        # if src_orientation == Orientation.sagittal and dest_orientation is Orientation.coronal:
        #     dest_points[0] = dest_dims[0] - dest_points[0]
        #     dest_points[2] = dest_dims[1] - dest_points[2]
        #
        # if src_orientation == Orientation.sagittal and dest_orientation is Orientation.axial:
        #     dest_points[1] = dest_dims[1] - dest_points[1]
        #     dest_points[0] = dest_dims[0] - dest_points[0]
        #
        # if self.impc_view:
        #     if src_orientation == Orientation.coronal and dest_orientation is Orientation.axial:
        #         dest_points[2] = dest_dims[2] - dest_points[2]
        #
        #     if src_orientation == Orientation.coronal and dest_orientation is Orientation.sagittal:
        #         dest_points[0] = dest_dims[1] - dest_points[0]
        #
        #     if src_orientation == Orientation.axial and dest_orientation in (Orientation.coronal, Orientation.sagittal):
        #         dest_points[1] = dest_dims[2] - dest_points[1]
        #
        #     if src_orientation == Orientation.axial and dest_orientation is Orientation.sagittal:
        #         dest_points[0] = dest_dims[1] - dest_points[0]
        #
        #     if src_orientation == Orientation.sagittal and dest_orientation is Orientation.coronal:
        #         dest_points[2] = dest_dims[1] - dest_points[2]
        #
        #     if src_orientation == Orientation.sagittal and dest_orientation is Orientation.axial:
        #         dest_points[1] = dest_dims[1] - dest_points[1]
        #         dest_points[2] = dest_dims[2] - dest_points[2]



        return dest_points

    def roi_to_view(self, xx, yy, zz):

        """
        Givn an roi is volume coordinates (z == axial), map the roi to other orthogonal views
        Parameters
        ----------
        xx: tuple
        yy: tuple
        zz: tuple

        Returns
        -------
        tuple
            Mapped coordinates ((x,x), (y,y), (z,z)
        """
        z = [int(x) for x in zz]
        y = [int(x) for x in yy]
        x = [int(x) for x in xx]

        mid_x = int(np.mean([x[0], x[1]]))
        mid_y = int(np.mean([y[0], y[1]]))
        mid_z = int(np.mean([z[0], z[1]]))

        for dest_view in self.views.values():
            # First map the annotation marker between views
            dest_dims = dest_view.main_volume.shape_xyz()

            flip_from_axial_order = {
                Orientation.axial:   [0, 1, 2],
                Orientation.coronal: [0, 2, 1],
                Orientation.sagittal:[2, 0, 1]
            }

            order = flip_from_axial_order[dest_view.orientation]
            x1, y1, z1 = [j for _, j in sorted(zip(order, [x[0], y[0], z[0]]), key=lambda pair: pair[0])]
            x2, y2, z2 = [j for _, j in sorted(zip(order, [x[1], y[1], z[1]]), key=lambda pair: pair[0])]

            x1 = dest_dims[0] - x1
            x2 = dest_dims[0] - x2

            if self.flip_info['impc_view'] and dest_view.orientation == Orientation.axial:
                z1 = dest_dims[2] - z1
                z2 = dest_dims[2] - z2

                y1 = dest_dims[1] - y1
                y2 = dest_dims[1] - y2

            if self.flip_info['impc_view'] and dest_view.orientation == Orientation.coronal:
                z1 = dest_dims[1] - z1
                z2 = dest_dims[1] - z2

            w = x2 - x1
            h = y2 - y1

            if dest_view.orientation == Orientation.sagittal:
                x1 -= w
                x2 -= w

            idx_centre = int(z2 - ((z2 - z1)/2))

            # As pyqtgraph orders the x back to front, we need to flip x
            # dest_dims = dest_view.main_volume.shape_xyz()
            # x_1 = dest_dims[0] - x_1

            dest_view.set_slice(idx_centre) # works
            dest_view.set_roi(x1, y1, w, h)


def convert_volume(vol, direction):
    return vol
    if direction == (1, 0, 0, 0, 1, 0, 0, 0, 1): # LPS
        vol = vol[:, ::-1, :]
    if direction == (-1, 0, 0, 0, -1, 0, 0, 0, 1): # RAS
        print("ras?")
        vol = vol
        # vol = vol[:, :, ::-1]

    return vol
