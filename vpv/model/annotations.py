import os
import yaml
from vpv.lib.addict import Dict
from vpv.common import Stage, AnnotationOption

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OPTIONS_CONFIG_PATH = os.path.join(SCRIPT_DIR, '../options/annotation_conf.yaml')


class Annotation(object):
    """
    Records a single manual annotation
    """
    def __init__(self, x, y, z, dims, stage):
        self.x = None
        self.y = None
        self.z = None
        self.x_percent = None
        self.y_percent = None
        self.z_percent = None
        self.dims = dims  # x,y,z
        self.set_xyz(z, y, z)
        self.stage = stage

    def __getitem__(self, index):
        if index == 0:  # First row of column (dimensions)
            return "{}, {}, {}".format(self.x, self.y, self.z)  # Convert enum member to string for table
        else: # The terms and stages columns
            return self.indexes[index - 1]

    def set_xyz(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.set_percentages()

    def set_percentages(self):
        dims = self.dims
        if None in (self.x, self.y, self.z):  # Annotations at startup. No position when not annotated
            return None, None, None
        self.x_percent = 100.0 / dims[0] * self.x
        self.y_percent = 100.0 / dims[1] * self.y
        self.z_percent = 100.0 / dims[2] * self.z


class EmapaAnnotation(Annotation):
    def __init__(self, x, y, z, emapa_term, option, dims, stage, category):
        super(EmapaAnnotation, self).__init__(x, y, z, dims, stage)
        self.term = str(emapa_term)
        self.option = option
        self.indexes = [self.term, self.option, self.stage.value]
        self.type = 'emapa'
        self.category = category


class VolumeAnnotations(object):
    """
    Associated with a single Volume instance
    Holds coordinates, ontological term, and option associated with manual annotations
    
    For testing we're just doing the E15.5 stage. We will have to have multiple stages later and there will need
    to be some way of only allowing one stage of annotation per volume
    """

    def __init__(self, dims):
        self.annotations = []
        self.col_count = 4
        self.dims = dims
        self.load_annotation_options()
        self.index = len(self.annotations)

    def add_emap_annotation(self, x, y, z, emapa, option, stage, category=None):
        """
        Add an emap/pato type annotaiotn from available terms on file, or update if the term is present already
        """
        assert isinstance(option, AnnotationOption)
        assert isinstance(stage, Stage)

        for a in self.annotations:

            if emapa == a.term:  # Update existing term
                a.set_xyz(x, y, z)
                a.option = option
                return
        ann = EmapaAnnotation(x, y, z, emapa, option, self.dims, stage, category)
        self.annotations.append(ann)

    def remove(self, row):
        del self.annotations[row]

    def __getitem__(self, index):
        return self.annotations[index]

    def __len__(self):
        return len(self.annotations)

    def __iter__(self):
        return self

    def __next__(self):
        if self.index == 0:
            self.index = len(self.annotations)
            raise StopIteration
        self.index -= 1
        return self.annotations[self.index]

    def get_by_term(self, term: str) -> Annotation:
        for annotation in self:
            if annotation.term == term:
                self.index = len(self.annotations)  # Bodge. How am I supposed to reset index
                return annotation
        self.index = len(self.annotations)
        return False

    def load_annotation_options(self):

        try:
            with open(OPTIONS_CONFIG_PATH, 'r') as fh:
                opts = yaml.load(fh)

        except OSError:
            print('could not open the annotations yaml file {}'.format(OPTIONS_CONFIG_PATH))
            raise

        for center_id, centre_data in opts['centres'].items():
            stages = centre_data
        # for category, terms in emap_terms.items():
        #     for term in terms:
        #         # Add a default annotation for the term, with no coordinates and option of unobserved
        #         self.add_emap_annotation(None, None, None, term,
        #                                  AnnotationOption.image_only, Stage.e15_5, category)