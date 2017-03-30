import os
import yaml
from lib.addict import Dict
from common import Stage, AnnotationOption

# E145_PATO_TERMS_FILE = 'ontologies/e14.5/pato_terms.csv'
# E145_EMAP_TERMS_FILE = 'ontologies/e14.5/emap_terms.csv'

E155_OPTIONS_FILE = 'ontologies/e15.5/options.csv'
# E155_EMAP_TERMS_FILE = 'ontologies/e15.5/emap_terms.csv'
E155_EMAP_TERMS_FILE = '../annotations/ontologies/e15.5/VPV_e15_5_terms.yaml'
# E185_PATO_TERMS_FILE = 'ontologies/e18.5/pato_terms.csv'
# E185_EMAP_TERMS_FILE = 'ontologies/e18.5/emap_terms.csv'
#
# E125_PATO_TERMS_FILE = 'ontologies/e12.5/pato_terms.csv'
# E125_EMAP_TERMS_FILE = 'ontologies/e12.5/emap_terms.csv'


EMAP_OPTIONS = ['unobserved', 'normal', 'abnormal']

#        self.terms[Stage.e15_5]['option'] = self.parse_options(E155_OPTIONS_FILE)
#        # self.terms[Stage.e15_5]['emap'] = self.parse_emap(E155_EMAP_TERMS_FILE)
#        self.terms[Stage.e15_5]['emap'] = self.parse_emap_yaml(E155_EMAP_TERMS_FILE)
#

class Annotation(object):
    """
    Records a single manual annotation
    """
    def __init__(self, x, y, z, dims, stage):
        self.x = x
        self.y = y
        self.z = z
        self.dims = dims  # x,y,z
        self.x_percent, self.y_percent, self.z_percent = self.set_percentages()
        self.stage = stage

    def __getitem__(self, index):
        if index == 0:  # First row of column (dimensions)
            return "{}, {}, {}".format(self.x, self.y, self.z)  # Convert enum member to string for table
        else: # The terms and stages columns
            return self.indexes[index - 1]

    def set_percentages(self):
        dims = self.dims
        if None in (self.x, self.y, self.z):  # Annotations at startup. No position when not annotated
            return None, None, None
        xp = 100.0 / dims[0] * self.x
        yp = 100.0 / dims[1] * self.y
        zp = 100.0 / dims[2] * self.z
        return xp, yp, zp


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
    Associated with a volume class
    Holds coordinates, ontological term, and option associated with manual annotations
    
    For testing we re just doing the E15.5 stage. We will have to have multiple stages later and there will need
    to be some way of only allowing one stage of annotation per volume
    """

    def __init__(self, dims):
        self.annotations = []
        self.col_count = 4
        self.dims = dims
        self.load_emap_yaml(E155_EMAP_TERMS_FILE)
        self.index = len(self.annotations)

    def add_emap_annotation(self, x, y, z, emapa, option, stage, category=None):
        """
        Add an emap/pato type annotaiotn unless exact is already present
        """
        t = type(option)
        assert isinstance(option, AnnotationOption)
        assert isinstance(stage, Stage)

        for a in self.annotations:

            if emapa == a.term:
                a.x = x
                a.y = y
                a.z = z
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
            raise StopIteration
        self.index -= 1
        return self.annotations[self.index]

    def check_term(self, term: str) -> bool:
        for annotation in self:
            if annotation.term == term:
                return annotation.op
        return False

    def load_emap_yaml(self, emap_file):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        emap_path = os.path.join(script_dir, emap_file)
        try:
            with open(emap_path, 'r') as fh:
                emap_terms = yaml.load(fh)
                for category, terms in emap_terms.items():
                    for term in terms:
                        # Add a default annotation for the term, with no coordinates and option of unobserved
                        self.add_emap_annotation(None, None, None, term,
                                                 AnnotationOption.unobserved, Stage.e15_5, category)

        except OSError:
            print('could not open the annotations yaml file {}'.format(emap_path))
            raise


            # # Create a dict to store all the annotation terms for each stage
 #        self.terms = Dict()
 #        self.terms[Stage.e12_5]['pato'] = self.parse_options(E125_PATO_TERMS_FILE)
 #        self.terms[Stage.e12_5]['emap'] = self.parse_emap(E125_EMAP_TERMS_FILE)
 #
 #        self.terms[Stage.e14_5]['option'] = self.parse_options(E145_PATO_TERMS_FILE)
 #        self.terms[Stage.e14_5]['emap'] = self.parse_emap(E145_EMAP_TERMS_FILE)
 #
 #        self.terms[Stage.e15_5]['option'] = self.parse_options(E155_OPTIONS_FILE)
 #        # self.terms[Stage.e15_5]['emap'] = self.parse_emap(E155_EMAP_TERMS_FILE)
 #        self.terms[Stage.e15_5]['emap'] = self.parse_emap_yaml(E155_EMAP_TERMS_FILE)
 #
 #        self.terms[Stage.e18_5]['pato'] = self.parse_options(E185_PATO_TERMS_FILE)
 #        self.terms[Stage.e18_5]['emap'] = self.parse_emap(E185_EMAP_TERMS_FILE)