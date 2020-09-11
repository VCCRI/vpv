"""
This script loads a series of volumes and associated labels from a config file
And displays them according to some options that can be set.

Currently works with the data structure as output by lama, but will add option to specify paths

Examples
--------

Example yaml config file



TODO:
Set opacity and label maps per view

"""
import sys
from pathlib import Path
from itertools import chain

import yaml
from PyQt5 import QtGui

from vpv.vpv_temp import Vpv
from vpv.common import Layers, Orientation
import addict


def load(loader_file):

    with open(loader_file, 'r') as fh:
        config = addict.Dict(yaml.load(fh))

    top = config['top_row']
    top_vols = [Path(x.vol.path) for x in top.values()]
    top_labels = [Path(x.labels.path) for x in top.values()]

    bottom = config['bottom_row']
    if bottom:
        bottom_vols = [Path(x.vol.path) for x in bottom.values()]
        bottom_labels = [Path(x.labels.path) for x in bottom.values()]
    else: # We allow only top tier visible
        bottom_vols = []
        bottom_labels = []

    app = QtGui.QApplication([])
    ex = Vpv()

    s_ = lambda x: [str(z) for z in x] # Get strs from Paths and TODO: prevent duplicate loading

    ex.load_volumes(chain(s_(top_vols), s_(top_labels), s_(bottom_vols), s_(bottom_labels)), 'vol')

    # Vpv deals with images with the same name by appending parenthetical digits. We need to know the ids it will assign
    # if we are to get a handle once loaded
    img_ids = ex.img_ids()
    num_top_views = len(top_vols)
    num_bottom_views = len(bottom_vols)

    # Set the top row of views
    counter = 0
    for i in range(num_top_views):
        try:
            # vol_id = top_vols[i].stem
            vol_id = img_ids[counter]
            # label_id = top_labels[i].stem
            label_id = img_ids[counter + len(top_vols)]
            # if label_id == vol_id:
            #     label_id = f'{label_id}(1)'
            ex.views[i].layers[Layers.vol1].set_volume(vol_id)
            ex.views[i].layers[Layers.vol2].set_volume(label_id)
            counter += 1
        except IndexError:
            continue

    if bottom:
        # Set the bottom row of views
        for i in range(num_bottom_views):
            try:
                # vol_id = top_vols[i].stem
                vol_id = img_ids[counter + num_bottom_views]
                # label_id = top_labels[i].stem
                label_id = img_ids[counter + num_bottom_views *2]
                # if label_id ==vol_id:
                #     label_id = f'{label_id}(1)'
                ex.views[i + 3].layers[Layers.vol1].set_volume(vol_id)
                ex.views[i + 3].layers[Layers.vol2].set_volume(label_id)
                counter += 1
            except IndexError:
                continue

    print('Finished loading')

    # Show two rows
    ex.data_manager.show2Rows(True if bottom else False)

    # Set orientation
    ex.data_manager.on_orientation('sagittal')

    # Set colormap
    ex.data_manager.on_vol2_lut_changed('anatomy_labels')

    # opacity
    ex.data_manager.modify_layer(Layers.vol2, 'set_opacity', config.opacity)

    # Set title
    ex.mainwindow.setWindowTitle(config['title'])

    sys.exit(app.exec_())


if __name__ == '__main__':
    import sys
    load(sys.argv[1])