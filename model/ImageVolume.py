from .volume import Volume
from .annotations import VolumeAnnotations


class ImageVolume(Volume):
    def __init__(self, *args):
        super(ImageVolume, self).__init__(*args)

        # We have annotations only on ImageVolumes
        self.annotations = VolumeAnnotations(list(reversed(list(self.shape_zyx()))))
        self.levels = [float(self._arr_data.min()), float(self._arr_data.max())]

