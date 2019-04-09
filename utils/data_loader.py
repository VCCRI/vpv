"""
This script loads a series of volumes and associated labels from a config file
And dispays them accordign to some options that can be set.

Currently woeks with the data structure as output by lama, but will add option to specify paths

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

from vpv.vpv import Vpv
from vpv.common import Layers, Orientation

test_file = '/mnt/IMPC_research/neil/E14.5/img_loaders/rik_loader.toml'

config = toml.load(test_file)
print(config)

vol_dir = Path(config['vol_dir'])
labels_dir = config['labels_dir']

top = config['top']
top_specs = [Path(x) for x in top['specimens']]
top_vols = [x / 'output' / vol_dir / x.name / f'{x.name}.nrrd' for x in top_specs]
top_labels = [x / 'output' / labels_dir / x.name / f'{x.name}.nrrd' for x in top_specs]

bottom = config['bottom']
bottom_specs = [Path(x) for x in bottom['specimens']]
bottom_vols = [x / 'output' / vol_dir / x.name / f'{x.name}.nrrd' for x in bottom_specs]
bottom_labels = [x / 'output' / labels_dir / x.name / f'{x.name}.nrrd' for x in bottom_specs]

app = QtGui.QApplication([])
ex = Vpv()

all_vols = top_vols + bottom_vols
all_labels = top_labels + bottom_labels

ex.load_volumes(chain(all_vols, all_labels), 'vol')

# Set the volumes to each slice view
for i, v in enumerate(ex.views.values()):
    vol_id = all_vols[i].stem
    v.layers[Layers.vol1].set_volume(vol_id)

# Set the label overlays
for i, v in enumerate(ex.views.values()):
    label_id = all_labels[i].stem
    # If label file has same name as the associated volume, it will have (1) suffix
    if label_id == v.layers[Layers.vol1].vol.name:
        label_id = f'{label_id}(1)'
    v.layers[Layers.vol2].set_volume(label_id)

# Show two rows
ex.data_manager.show2Rows(True)

# Set orientation
ex.data_manager.on_orientation('sagittal')

# Set colormap
ex.data_manager.on_vol2_lut_changed('anatomy_labels')

# opacity
ex.data_manager.modify_layer(Layers.vol2, 'set_opacity', 0.6)

sys.exit(app.exec_())