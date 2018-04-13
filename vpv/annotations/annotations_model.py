import os
from os.path import join, dirname, abspath
import yaml
from vpv.common import Stage, AnnotationOption, load_yaml

SCRIPT_DIR = dirname(abspath(__file__))
OPTIONS_DIR = join(SCRIPT_DIR, 'options')
OPTIONS_CONFIG_PATH = os.path.join(OPTIONS_DIR, 'annotation_conf.yaml')



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
        # self.set_xyz(x, y, z)
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


class ImpcAnnotation(Annotation):
    def __init__(self, x, y, z, emapa_term, name, options, default_option, dims, stage, order, is_mandatory):
        super(ImpcAnnotation, self).__init__(x, y, z, dims, stage)
        self.term = str(emapa_term)
        self.name = name
        self.options = options
        self.selected_option = default_option
        self.dims = dims
        self.order = order
        self.is_mandatory = is_mandatory
        self.indexes = [self.term, self.selected_option, self.stage]
        self.type = 'emapa'
        # self.category = category


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
        # self.load_annotation_options() # We don't load annotations until center + stage is selected
        self.index = len(self.annotations)

        # The center where the annotation is taking place
        self.center = None
        # The developmental stage of the embryo being annotated
        self._stage = None

    @property
    def stage(self):
        return self._stage

    @stage.setter
    def stage(self, stage):
        self._stage = stage
        if all([self.center, self.stage]):
            self._load_annotations()

    def _load_annotations(self):
        """
        Once the center and stage have been set on this VolumeAnnotations object we can now load the respective default
        parameters

        Returns
        -------

        """
        cso = centre_stage_options.opts
        for _, data in cso['centers'][self.center]['stages'][self.stage]['parameters'].items():

            options = centre_stage_options.opts['available_options'][data['options']]
            default = data['default_option']

            self.add_emap_annotation(None,
                                     None,
                                     None,
                                     data['impc_id'],
                                     data['name'],
                                     options,
                                     default,
                                     self.stage,
                                     data['order'],
                                     data['mandatory']
                                     )
        # Sort the list and set the interator index
        self.annotations.sort(key=lambda x: x.order, reverse=True)
        self.index = len(self.annotations)

    def update_annotation(self, term, x, y, z, selected_option: str):
        """
        Update an annotation
        Returns
        -------

        """
        ann = self.get_by_term(term)
        ann.x, ann.y, ann.z = x, y, z
        ann.selected_option = selected_option

    def add_emap_annotation(self, x, y, z, emapa, name, options, default_option, stage, order, is_mandatory):
        """
        Add an emap type annotaiotn from available terms on file
        """
        ann = ImpcAnnotation(x, y, z, emapa, name, options, default_option, self.dims, stage, order, is_mandatory)
        self.annotations.append(ann)

    def remove(self, row):
        del self.annotations[row]

    def clear(self):
        self.annotations = []
        self.index = 0

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


class CenterStageOptions(object):
    def __init__(self):
        # Add assert for default in options
        try:
            opts = load_yaml(OPTIONS_CONFIG_PATH)
        except OSError:
            print('could not open the annotations yaml file {}'.format(OPTIONS_CONFIG_PATH))
            raise
        self.opts = opts
        self.available_options = self.opts['available_options']

        for center in opts['centers']:
            for stage_id, stage_data in opts['centers'][center]['stages'].items():
                stage_file = stage_data['file_']
                # now add the parameters from each individual centre/stage file to the main options config
                opts['centers'][center]['stages'][stage_id]['parameters'] = self.load_centre_stage_file(stage_file)

    def load_centre_stage_file(self, yaml_name):
        path = join(OPTIONS_DIR, yaml_name)
        opts = load_yaml(path)
        return opts['parameters']

    def all_stages(self, center):
        return [x for x in self.opts['centers'][center]['stages'].keys()]

    def all_centers(self):
        return [x for x in self.opts['centers']]

centre_stage_options = CenterStageOptions()