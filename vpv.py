#! /usr/bin/env python

from PyQt5 import QtGui
import sys
from vpv.vpv import Vpv

if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser("Volume Phenptype Viewer")
    parser.add_argument('-v', '-volumes',  dest='volumes', nargs='*', help='Volume paths seperated by spaces', default=False)
    parser.add_argument('-hm', '-heatmaps', dest='heatmaps', nargs='*', help='Heatmap paths seperated by spaces', default=False)
    args = parser.parse_args()

    app = QtGui.QApplication(sys.argv)
    ex = Vpv()

    if args.volumes:
        ex.load_volumes(args.volumes, 'vol')
        # Can't have heatmaps loaded without any volumes loaded first
        if args.heatmaps:
            ex.load_volumes(args.heatmaps, 'heatmap')
    sys.exit(app.exec_())