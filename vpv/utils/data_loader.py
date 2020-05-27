"""
This script loads a series of volumes and associated labels from a config file
And displays them according to some options that can be set.

Currently works with the data structure as output by lama, but will add option to specify paths

Examples
--------

Example toml file

labels_dir = 'inverted_labels/similarity'
vol_dir = 'registrations/rigid'
orientation = 'sagittal'


[top]
specimens = ['/mnt/IMPC_research/neil/E14.5/baselines/output/baseline/20150916_RBMS1_E14.5_14.3f_WT_XY_rec_scaled_4.6878_pixel_14',
'/mnt/IMPC_research/neil/E14.5/baselines/output/baseline/20170214_1200014J11RIK_E14.5_1.5h_WT_XX_REC_scaled_4.7297_pixel_13',
'/mnt/IMPC_research/neil/E14.5/baselines/output/baseline/20140121_RIC8B_E14.5_15.4b_wt_xy_rec_scaled_3.125_pixel_14']

[bottom]
specimens = ['/mnt/IMPC_research/neil/E14.5/mutants/output/1200014J11RIK/20170214_1200014J11RIK_E14.5_1.5f_HOM_XX_REC_scaled_4.7297_pixel_13.9999',
'/mnt/IMPC_research/neil/E14.5/mutants/output/1200014J11RIK/20170214_1200014J11RIK_E14.5_2.4c_HOM_XX_REC_scaled_4.7297_pixel_13.9999',
'/mnt/IMPC_research/neil/E14.5/mutants/output/1200014J11RIK/20170214_1200014J11RIK_E14.5_2.4i_HOM_XY_REC_scaled_4.7297_pixel_13.9999']

"""
import sys
from pathlib import Path
from itertools import chain

import toml
from PyQt5 import QtGui

from vpv.vpv_temp import Vpv
from vpv.common import Layers, Orientation


def load(loader_file):

    config = toml.load(loader_file)
    print(config)

    vol_dir = Path(config['vol_dir'])
    labels_dir = config['labels_dir']

    top = config['top']
    top_specs = [Path(x) for x in top['specimens']]
    top_vols = [x / 'output' / vol_dir / x.name / f'{x.name}.nrrd' for x in top_specs]
    top_labels = [x / 'output' / labels_dir / x.name / f'{x.name}.nrrd' for x in top_specs]

    bottom = config['bottom']
    if bottom: # We allow only top tier visible
        bottom_specs = [Path(x) for x in bottom['specimens']]
        bottom_vols = [x / 'output' / vol_dir / x.name / f'{x.name}.nrrd' for x in bottom_specs]
        bottom_labels = [x / 'output' / labels_dir / x.name / f'{x.name}.nrrd' for x in bottom_specs]
    else:
        bottom_specs = []
        bottom_vols = []
        bottom_labels = []

    app = QtGui.QApplication([])
    ex = Vpv()

    p2s = lambda x: [str(z) for z in x]



    all_vols = top_vols + bottom_vols
    all_labels = top_labels + bottom_labels


    ex.load_volumes(chain(p2s(top_vols), p2s(bottom_vols), p2s(top_labels), p2s(bottom_labels)), 'vol')


    # Set the top row of views
    for i in range(3):
        try:
            vol_id = top_vols[i].stem
            label_id = top_labels[i].stem
            if label_id == vol_id:
                label_id = f'{label_id}(1)'
            ex.views[i].layers[Layers.vol1].set_volume(vol_id)
            ex.views[i].layers[Layers.vol2].set_volume(label_id)
        except IndexError:
            continue

    if bottom:
        # Set the top row of views
        for i in range(3):
            try:
                vol_id = bottom_vols[i].stem
                label_id = bottom_labels[i].stem
                if label_id ==vol_id:
                    label_id = f'{label_id}(1)'
                ex.views[i + 3].layers[Layers.vol1].set_volume(vol_id)
                ex.views[i + 3].layers[Layers.vol2].set_volume(label_id)
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
    ex.data_manager.modify_layer(Layers.vol2, 'set_opacity', 0.6)

    sys.exit(app.exec_())


if __name__ == '__main__':
    load()