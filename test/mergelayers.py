#!/usr/bin/env python

import h5py
import sys
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import SimpleITK as sitk

def run(img, overlay):
    img_minc = sitk.ReadImage(img)
    img_volume = sitk.GetArrayFromImage(img_minc)
    img_slice = img_volume[100, :, :]
    # Set all values below 0 to 0
    img_slice[img_slice < 0] = 0
    img_slice = img_slice.astype(np.uint8)

    print img_slice.shape

    overlay_minc = sitk.ReadImage(overlay)
    overlay_volume = sitk.GetArrayFromImage(overlay_minc)
    overlay_slice = overlay_volume[100, :, :]
    overlay_slice[overlay_slice > 0] = 0
    overlay_slice = np.absolute(overlay_slice).astype(np.uint8)

    print overlay_slice.shape



    green = np.zeros((img_slice.shape[0], img_slice.shape[1]), np.uint8)

    rgb = np.dstack((img_slice, green, overlay_slice))

    plt.imshow(rgb)
    plt.show()

    #
    # plt.imshow(img_slice)
    # plt.show()


if __name__ == '__main__':
    run(sys.argv[1], sys.argv[2])



# # r, g, and b are 512x512 float arrays with values >= 0 and < 1.
# from PIL import Image
# import numpy as np
# rgbArray = np.zeros((512,512,3), 'uint8')
# rgbArray[..., 0] = r*256
# rgbArray[..., 1] = g*256
# rgbArray[..., 2] = b*256