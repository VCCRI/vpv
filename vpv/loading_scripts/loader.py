"""
Given a directory of images, this script will load them based on a config.

See example 'loader.yaml'
"""


from pathlib import Path
import yaml
from PyQt5 import QtGui
from vpv.vpv_temp import Vpv
from vpv.common import Layers, Orientation


def resolve_wildcard_paths(paths, root):
    res = []
    for p in paths:
        if '*' in str(p):
            p = next(root.glob(str(p)))
        res.append(p)
    return res

def load(config_path, root_dir):

    with open(config_path, 'r') as fh:
        config = yaml.load(fh)

    template = config['view_template']

    # Build the views from the templates
    views = []
    for v in config['views']:
        view = template.copy()
        if v.get('top'):
            for k, p in v['top'].items():
                view['top'][k] = p
        if v.get('bottom'):
            for k, p in v['bottom'].items():
                view['bottom'][k] = p
        views.append(view)

    app = QtGui.QApplication([])
    ex = Vpv()

    vpv_ids = []
    for view in views:
        top_vol = Path(view['top']['path'])
        bottom_vol = Path(view['bottom']['path'])
        vols = resolve_wildcard_paths([top_vol, bottom_vol], root_dir)

        vpv_ids.extend(ex.load_volumes(vols, 'vol'))

    for i, view in enumerate(views):

        top_vol_id = vpv_ids[i]
        # label_id = top_labels[i].stem
        bottom_vol_id = vpv_ids[i+1]
        # if label_id == vol_id:
        #     label_id = f'{label_id}(1)'
        ex.views[i].layers[Layers.vol1].set_volume(top_vol_id)
        ex.views[i].layers[Layers.vol2].set_volume(bottom_vol_id)
        ex.views[i].set_orientation(Orientation[view['ori']])
        ex.views[i].layers[Layers.vol2].set_opacity(view['top']['opacity'])
        ex.views[i].layers[Layers.vol1].set_lut(view['top']['color'])
        ex.views[i].layers[Layers.vol2].set_lut(view['bottom']['color'])


    # Show two rows
    ex.data_manager.show2Rows(True if len(views) > 3 else False)

    # Set orientation
    # ex.data_manager.on_orientation('sagittal')

    # Set colormap
    # ex.data_manager.on_vol2_lut_changed('anatomy_labels')

    # opacity
    # ex.data_manager.modify_layer(Layers.vol2, 'set_opacity', config.opacity)

    # Set title
    # ex.mainwindow.setWindowTitle(config['title'])

    sys.exit(app.exec_())


if __name__ == '__main__':
    import sys

    import sys

    # load(cfg)
    _config = sys.argv[1]
    _root_dir = sys.argv[2]

    load(_config, Path(_root_dir))