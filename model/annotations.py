class Annotation(object):
    """
    Records a single manual annotation
    """
    def __init__(self, x, y, z, dims, stage):
        self.x = x
        self.y = y
        self.z = z
        self.dims = dims  # x,y,z
        self.x_percent, self.y_percent, self.z_percent = self.set_percentages(dims)
        self.stage = stage

    def __getitem__(self, index):
        if index == 0:  # First row of column (dimensions)
            return "{}, {}, {}".format(self.x, self.y, self.z)  # Convert enum member to string for table
        else: # The terms and stages columns
            return self.indexes[index - 1]

    def set_percentages(self, dims):
        xp = 100.0 / dims[0] * self.x
        yp = 100.0 / dims[1] * self.y
        zp = 100.0 / dims[2] * self.z
        return xp, yp, zp


class MpAnnotation(Annotation):
    def __init__(self, x, y, z, mp_term, dims, stage):
        super(MpAnnotation, self).__init__(x, y, z, dims, stage)
        self.mp_term = str(mp_term)
        self.indexes = [self.mp_term, '', self.stage.value]
        self.type = 'mp'


class MaPatoAnnotation(Annotation):
    def __init__(self, x, y, z, ma_term, pato_term, dims, stage):
        super(MaPatoAnnotation, self).__init__(x, y, z, dims, stage)
        self.emap_term = str(ma_term)
        self.pato_term = str(pato_term)
        self.indexes = [self.emap_term, self.pato_term, self.stage.value]
        self.type = 'ma'


class VolumeAnnotations(object):
    """
    Associated with a volume class
    Holds positions and MP terms associated with manual annotations
    """

    def __init__(self, dims):
        self.annotations = []
        self.col_count = 4
        self.dims = dims

    def add_mapato(self, x, y, z, ma, pato, stage):
        """
        Add an emap/pato type annotaiotn unless exact is already present
        """
        for a in self.annotations:
            new_params = (x, y, z, ma, pato)
            old_parmas = (a.x, a.y, a.z, pato)
            if new_params == old_parmas:
                return
        ann = MaPatoAnnotation(x, y, z, ma, pato, self.dims, stage)
        self.annotations.append(ann)

    def add_mp(self,  x, y, z, mp, stage):
        """
        Add a n MP type annotation unless excat already present
        """
        for a in self.annotations:
            new_params = (x, y, z, mp)
            old_parmas = (a.x, a.y, a.z, mp)
            if new_params == old_parmas:
                return
        ann = MpAnnotation(x, y, z, mp, self.dims, stage)
        self.annotations.append(ann)

    def remove(self, row):
        del self.annotations[row]

    def __getitem__(self, index):
        return self.annotations[index]

    def __len__(self):
        return len(self.annotations)
