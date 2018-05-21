import os
from os.path import join, dirname, abspath
import yaml
from vpv.common import get_stage_from_proc_id, load_yaml, info_dialog
from os.path import splitext, isfile, isdir
import fnmatch

SCRIPT_DIR = dirname(abspath(__file__))
OPTIONS_DIR = join(SCRIPT_DIR, 'options')
OPTIONS_CONFIG_PATH = os.path.join(OPTIONS_DIR, 'annotation_conf.yaml')
PROCEDURE_METADATA = 'procedure_metadata.yaml'

ANNOTATION_DONE_METADATA_FILE = '.doneList.yaml'


class Annotation(object):
    """
    Records a single manual annotation

    Attributes
    ----------
    looked_at: bool
        Whether an annotator has looked at this term and checked the done box
    """
    def __init__(self, x, y, z, dims, stage):
        self.x = x
        self.y = y
        self.z = z
        self.x_percent = None
        self.y_percent = None
        self.z_percent = None
        self.dims = dims  # x,y,z
        # self.set_xyz(x, y, z)
        self.stage = stage
        self._looked_at = False

    @property
    def looked_at(self):
        return self._looked_at

    @looked_at.setter
    def looked_at(self, done):
        self._looked_at = done

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

    def __init__(self, dims: tuple, vol_path: str):
        """
        Parameters
        ----------
        dims: The dimensions of the image being annotated
        vol_path: The original path of the volume being annotated
            The vol_path is used in order to look for associated procedure metadata file
        """
        self.vol_path = vol_path
        self.annotation_dir = splitext(self.vol_path)[0]
        if not isdir(self.annotation_dir):
            self.annotation_dir = None
        self.annotations = []
        self.col_count = 4  # is this needed?
        self.dims = dims
        # self.load_annotation_options() # We don't load annotations until center + stage is selected
        self.index = len(self.annotations)

        # The center where the annotation is taking place
        self.center = None
        # The developmental stage of the embryo being annotated
        self._stage = None

        self.date_of_annotation = None  # Will be set from the annotation gui_load_done_status

        self._load_options_and_metadata()
        # self._load_done_status()

    @property
    def stage(self):
        return self._stage

    @stage.setter
    def stage(self, stage):
        # After setting stage we can then set the avaialble annotiton objects
        self._stage = stage

    def _load_done_status(self):
        if self.annotation_dir:
            done_file = join(self.annotation_dir, ANNOTATION_DONE_METADATA_FILE)
            if not isfile(done_file):
                return
            with open(done_file, 'r') as fh:
                done_status = yaml.load(fh)
                if not done_status:
                    return
            self.index = len(self.annotations)  # bodge
            for ann in self:
                done = done_status.get(ann.term, 'notpresent')
                if done is 'notpresent':
                    print('Cannot find term in done metadata\n{}'.format(done_file))
                if done is False:
                    print('p')
                else:
                    ann.looked_at = done
        print('f')

    def _load_options_and_metadata(self):
        """
        The volume has been loaded. Now see if there is an associated annotation folder that will contain the IMPC
        metadata parameter file. Also load in any partially completed xml fannotation files

        Returns
        -------

        """
        if not self.annotation_dir:
            return

        self.metadata_parameter_file = join(self.annotation_dir, PROCEDURE_METADATA)
        if not isfile(self.metadata_parameter_file):
            self.metadata_parameter_file = None
            return

        cso = centre_stage_options.opts

        with open(self.metadata_parameter_file, 'r') as fh:
            metadata_params = yaml.load(fh)
            proc_id = metadata_params['procedure_id']
            center_id = metadata_params['centre_id']
            stage_id = get_stage_from_proc_id(proc_id, center_id)

            self.stage = stage_id
            self.center = center_id

        # Get the procedure parameters for the given center/stage
        center_stage_default_params = cso['centers'][center_id]['stages'][stage_id]['parameters']

        for _, stage_params in center_stage_default_params.items():

            options = centre_stage_options.opts['available_options'][stage_params['options']]
            default = stage_params['default_option']

            self.add_impc_annotation(None,
                                     None,
                                     None,
                                     stage_params['impc_id'],
                                     stage_params['name'],
                                     options,
                                     default,
                                     self.stage,
                                     stage_params['order'],
                                     stage_params['mandatory'],
                                     self.dims
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

    def add_impc_annotation(self, x: int, y:int, z:int, impc_param, name, options, default_option, stage, order, is_mandatory, dims):
        """
        Add an emap type annotation from available terms on file
        """
        ann = ImpcAnnotation(x, y, z, impc_param, name, options, default_option, dims, stage, order, is_mandatory)
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
        # Now add the IMPC as key insterad of useless param_1, param_2 etc
        renamed = {}
        for k in list(opts['parameters']):
            new_key =  opts['parameters'][k]['impc_id']
            renamed[new_key] = opts['parameters'][k]
        opts['parameters'] = renamed
        return opts['parameters']

    def all_stages(self, center):
        return [x for x in self.opts['centers'][center]['stages'].keys()]

    def all_centers(self):
        return [x for x in self.opts['centers']]

centre_stage_options = CenterStageOptions()
