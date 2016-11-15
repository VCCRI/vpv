#!/usr/bin/env python




import SimpleITK as sitk
import numpy as np
import sys


im_path = sys.argv[1]
im = sitk.ReadImage(im_path)
arr = sitk.GetArrayFromImage(im)