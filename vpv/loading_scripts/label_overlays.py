"""
A work in progress.
An example script for loading propagated atlas labels from a single spcimen from a LAMA run over the rigidly-aligned speciemn image.

Given a root directory, load image, inverted labels and set opacity etc.

"""

from pathlib import Path
import sys
from itertools import chain
from PyQt5 import QtGui
from vpv.vpv_temp import Vpv
from vpv.common import Layers, Orientation
from lama.common import get_file_paths
from lama.elastix import RESOLUTION_IMGS_DIR, IMG_PYRAMID_DIR
import yaml



ORIS = ['sagittal', 'coronal', 'axial']
VOL_CMAP = 'grey'
LAB_CMAP = 'anatomy_labels'

# root_dir = Path('/mnt/bit_nfs/neil/impc_e15_5/phenotyping_tests/TCP_E15_5_test_060720/output/baseline/output/baseline/1677880_download/try_configs/reg/new')
# outdir = Path('/mnt/bit_nfs/neil/impc_e15_5/phenotyping_tests/TCP_E15_5_test_060720/output/baseline/output/baseline/1677880_download/try_configs/reg/vpvloaders')
IGNORE = [RESOLUTION_IMGS_DIR, IMG_PYRAMID_DIR]

OPACITY = 0.4


def load(line_dir: Path, rev=False, title=None):
    app = QtGui.QApplication([])
    ex = Vpv()

    try:
        invert_yaml = next(line_dir.glob('**/inverted_transforms/propagate.yaml'))
    except StopIteration:

        try: # Old version name of config file
            invert_yaml = next(line_dir.glob('**/inverted_transforms/invert.yaml'))
        except StopIteration:
            raise FileNotFoundError("Cannot find 'inverted_transforms/propagate.yaml' in LAMA output directory")

    with open(invert_yaml, 'r') as fh:
        try:
            invert_order = yaml.load(fh)['label_propagation_order']
        except KeyError:
            try:
                invert_order = yaml.load(fh)['inversion_order']
            except KeyError:
                raise

    if not rev:
        vol_dir = next(line_dir.rglob('**/inputs'))
    else:
        vol_dir = next(line_dir.rglob('**/reg*/*rigid*'))
    lab_dir = next(line_dir.glob(f'**/inverted_labels'))


    vol = get_file_paths(vol_dir, ignore_folders=IGNORE)[0]

    lab = get_file_paths(lab_dir, ignore_folders=IGNORE)[0]

    ex.load_volumes([vol, lab], 'vol')

    # Vpv deals with images with the same name by appending parenthetical digits. We need to know the ids it will assign
    # if we are to get a handle once loaded
    img_ids = ex.img_ids()

    num_top_views = 3

    # Set the top row of views
    for i in range(num_top_views):

        vol_id = img_ids[0]
        # label_id = top_labels[i].stem
        label_id = img_ids[1]
        # if label_id == vol_id:
        #     label_id = f'{label_id}(1)'
        ex.views[i].layers[Layers.vol1].set_volume(vol_id)
        ex.views[i].layers[Layers.vol2].set_volume(label_id)

    if not title:
        title = line_dir.name
    ex.mainwindow.setWindowTitle(title)

    print('Finished loading')

    # Show two rows
    ex.data_manager.show2Rows(False)

    # Set orientation
    # ex.data_manager.on_orientation('sagittal')

    # Set colormap
    ex.data_manager.on_vol2_lut_changed('anatomy_labels')

    # opacity
    ex.data_manager.modify_layer(Layers.vol2, 'set_opacity', OPACITY)

    sys.exit(app.exec_())


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser("Overlay LAMA-propagated labels")
    parser.add_argument('dir_', help='LAMA specimen directory')
    parser.add_argument('-r', '--rev', dest='rev',  help='If set we look for overlays in final def folder',
                        required=False, default=False, action='store_true')
    parser.add_argument('-t', '--title', dest='title',  help='VPV window title',
                        required=False, default=None)
    args = parser.parse_args()

    load(Path(args.dir_), args.rev, args.title)

