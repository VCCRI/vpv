from .volume import Volume
from vpv.annotations.annotations_model import VolumeAnnotations


class ImageVolume(Volume):
    def __init__(self, *args):
        super(ImageVolume, self).__init__(*args)

        # We have annotations only on ImageVolumes
        self.annotations = VolumeAnnotations(self.shape_xyz())
        self.levels = [float(self._arr_data.min()), float(self._arr_data.max())]

