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
        if not p:
            res.append(None)
        if '*' in str(p):
            try:
                p = next(root.glob(str(p)))
            except StopIteration:
                raise FileNotFoundError(f'The pattern {p} is yielding no images') # Debug

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
        # Override template with view-specific options
        if v.get('ori'):
            view['ori'] = v['ori']
        if v.get('top'):
            for k, p in v['top'].items():
                view['top'][k] = p
        if v.get('bottom'):
            for k, p in v['bottom'].items():
                view['bottom'][k] = p
        views.append(view)

    app = QtGui.QApplication([])
    ex = Vpv()

    top_ids = []
    bottom_ids = []

    already_loaded = {}  # path: vpv_id

    for view in views:
        try:
            top_vol = Path(view['top']['path'])
        except KeyError:
            top_vol = None

        try:
            bottom_vol = Path(view['bottom']['path'])
        except KeyError:
            bottom_vol = None

        top_path = resolve_wildcard_paths([top_vol], root_dir)[0]
        bottom_path = resolve_wildcard_paths([bottom_vol], root_dir)[0]

        if not top_path:
            top_ids.append(None)
        elif top_path in already_loaded:
            top_ids.append(already_loaded[top_path])
        else:
            top_ids.extend(ex.load_volumes([top_path], 'vol'))
            already_loaded[top_path] = top_ids[-1]

        if not bottom_path:
            bottom_ids.append(None)
        elif bottom_path in already_loaded:
            bottom_ids.append(already_loaded[bottom_path])
        else:
            bottom_ids.extend(ex.load_volumes([bottom_path], 'vol'))
            already_loaded[bottom_path] = bottom_ids[-1]


    for i, view in enumerate(views):

        top_vol_id = top_ids[i]
        if top_vol_id:
            ex.views[i].layers[Layers.vol1].set_volume(top_vol_id)

        bottom_vol_id = bottom_ids[i]
        if bottom_vol_id:
            ex.views[i].layers[Layers.vol2].set_volume(bottom_vol_id)

        ex.views[i].set_orientation(Orientation[view['ori']])

        if view.get('bottom') and view['bottom'].get('opacity'):
            ex.views[i].layers[Layers.vol2].set_opacity(view['bottom']['opacity'])

        if view.get('top') and view['top'].get('color'):
            ex.views[i].layers[Layers.vol1].set_lut(view['top']['color'])
        if view.get('bottom') and view['bottom'].get('color'):
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