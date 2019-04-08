"""
This script loads a series of volumes and associated labels from a config file
And dispays them accordign to some options that can be set.

Currently woeks with the data structure as output by lama, but will add option to specify paths

Examples
--------

Example toml file

root =

[volumes_top]  # The 3 top slice viewers
root = /mnt/IMPC_research/neil/E14.5/baselines/output/
dir = output/registrations/rigid
i1 = vol1.nrrd
i2 = vol2.nrrd
i3 = vol3.nrrd

[volumes_bottom]
root = /mnt/IMPC_research/neil/E14.5/mutants/output
dir = output/registrations/rigid
i1 = vol4.nrrd
i2 = vol5.nrrd
i3 = vol6.nrrd

[overlays]
inverted_labels/similarity

"""
import sys
from pathlib import Path
from itertools import chain

import toml
from PyQt5 import QtGui

from vpv.vpv import Vpv
from vpv.common import Layers

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

app = QtGui.QApplication([])
ex = Vpv()

top_vols.extend(bottom_vols)

ex.load_volumes(chain(top_vols, bottom_vols), 'vol')

#Load the volumes
for i, v in enumerate(ex.views.values()):
    vol_id = top_vols[i].stem
    v.layers[Layers.vol1].set_volume(vol_id)

# load the labels.
for i, v in enumerate(ex.views.values()):
    label_id = top_labels[i].stem
    # If same name as the associated volume, will have (1) suffix
    if label_id == top_vols[i].stem:
        label_id = f'{label_id}(1)'
    v.layers[Layers.vol2].set_volume(label_id)

# Add labels
# Show two rows
# Set orientation

# Can't have heatmaps loaded without any volumes loaded first

sys.exit(app.exec_())