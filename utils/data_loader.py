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

import toml

from vpv.vpv import Vpv

test_file = '/mnt/IMPC_research/neil/E14.5/img_loaders/rik_loader.toml'

config = toml.load(test_file)
print(config)

ex = Vpv()


vols_to_load = ""

ex.load_volumes(args.volumes, 'vol')
# Can't have heatmaps loaded without any volumes loaded first
if args.heatmaps:
    ex.load_volumes(args.heatmaps, 'heatmap')
if args.annotations:
    ex.load_annotations(args.annotations)

sys.exit(app.exec_())