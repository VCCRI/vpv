"""
Given a directory of images, this script will load them based on a config.

See example 'loader.yaml'
"""

import copy
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
        view = copy.deepcopy(template)
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

    already_loaded = {}
    for view in views:
        top_vol = Path(view['top']['path'])
        bottom_vol = Path(view['bottom']['path'])
        vols = resolve_wildcard_paths([top_vol, bottom_vol], root_dir)

        for v in vols:
            if v in already_loaded:
                vpv_ids.append(already_loaded[v])
            else:
                vpv_ids.extend(ex.load_volumes([v], 'vol'))
                already_loaded[v] = vpv_ids[-1]

    for i, view in enumerate(views):

        top_vol_id = vpv_ids[i * 2]
        # label_id = top_labels[i].stem
        bottom_vol_id = vpv_ids[i * 2 + 1]
        # if label_id == vol_id:
        #     label_id = f'{label_id}(1)'
        ex.views[i].layers[Layers.vol1].set_volume(top_vol_id)
        ex.views[i].layers[Layers.vol2].set_volume(bottom_vol_id)

        ex.views[i].set_orientation(Orientation[view['ori']])

        if view['bottom'].get('opacity'):
            ex.views[i].layers[Layers.vol2].set_opacity(view['bottom']['opacity'])

        ex.views[i].layers[Layers.vol1].set_lut(view['top']['color'])
        ex.views[i].layers[Layers.vol2].set_lut(view['bottom']['color'])

    # Show two rows
    ex.data_manager.show2Rows(True if len(views) > 3 else False)

    sys.exit(app.exec_())


if __name__ == '__main__':
    import sys

    import sys

    # load(cfg)
    _config = sys.argv[1]
    _root_dir = sys.argv[2]

    load(_config, Path(_root_dir))