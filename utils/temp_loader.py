from pathlib import Path
import sys

from PyQt5 import QtGui

from vpv.vpv import Vpv
from lama.paths import specimen_iterator

root_dir = Path('/mnt/IMPC_research/neil/E14.5/baselines/output')


app = QtGui.QApplication([])
ex = Vpv()

vols = []

t = 0
for line_dir, spec_dir in specimen_iterator(root_dir):
    def_img = spec_dir / 'output' / 'registrations' / 'deformable_50_to_10' / spec_dir.name / (spec_dir.name + '.nrrd')

    if not def_img.is_file():
        print(f'{def_img} not found')
        continue
    if 'xy' in spec_dir.name.lower():
        vols.append(def_img)
        # if t > 5:
        #     break
        # t +=1


ex.load_volumes(vols, 'vol')

sys.exit(app.exec_())



