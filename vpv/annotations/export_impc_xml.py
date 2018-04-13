from lxml import etree
import pprint
import yaml

from vpv.annotations.annotations_model import ImpcAnnotation

"""
Generate an IMPC xml submsiion form for the manual annotation procedure
"""

class ExportXML(object):
    """
    TODO: project
    """
    def __init__(self,
                 date_of_annotation,
                 experiment_id,
                 metadata
                 ):

        self.metadata = load_metadata(metadata)
        md = self.metadata

        # Create separate file for each modality
        self.root = etree.Element('centreProcedureSet',
                             xmlns="http://www.mousephenotype.org/dcc/exportlibrary/datastructure/core/procedure")
        centre = etree.SubElement(self.root, 'centre', project=md['project'], pipeline=md['pipeline'],
                                  centreID=md['centre_id'])

        # Create an experiment element
        self.experiment = etree.SubElement(centre, 'experiment', dateOfExperiment=date_of_annotation.toString(),
                                      experimentID=experiment_id)

        # Append specimen
        specimen = etree.SubElement(self.experiment, 'specimenID')
        specimen.text = md['specimen_id']

        self.procedure_element = etree.SubElement(self.experiment, 'procedure', procedureID=md['procedure_id'])

    def add_metadata(self):
        for id_, param_value in self.metadata['procedureMetadata'].items():
            parameter = etree.SubElement(self.procedure_element, 'procedureMetadata', parameterID=id_)
            # Create value element
            value = etree.SubElement(parameter, 'value')
            value.text = str(param_value)

    def write(self, file_path):
        self.add_metadata()
        # print etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8', standalone='yes')
        etree.ElementTree(self.root).write(file_path, pretty_print=True, xml_declaration=True, encoding='UTF-8',
                                      standalone='yes')

    def add_point(self, param_id, xyz):
        """
        Annotation ppoints cannot be added to the manual annotation call as it is a simpleParameter
        Instead, we have to create a seriesMediaParameter and add it there with a link to the manual annotaiton
        parameter

        Parameters
        ----------
        param_id: str
            The parameter ID to link the point to
        reconstruction_param_and_id: tuple
            The parameter
        xyz: tuple (int)
            the location of the annotation mark

        Notes
        -----
        IMPC_EMO_001_001 is the parameter ID for embryo reconstructions
        """

        # Get parameter info and append to procedure
        point_smp = etree.SubElement(self.procedure_element,
                                     'seriesMediaParameter',
                                     parameterID="IMPC_EMO_001_001")
        value = etree.SubElement(point_smp,
                         'value',
                         {"incrementValue": "1",
                          "url": self.metadata['reconstruction_uri']})

        p_assoc = etree.SubElement(value,
                         'parameterAssociation',
                         {'parameterID': param_id})

        def put_in_point(id_, idx):
            etree.SubElement(p_assoc,
                             'dim',
                             {'origin': 'RAS',
                              'id': id_}).text = str(xyz[idx])

        for idx, id_ in enumerate(['x', 'y', 'z']):
            put_in_point(id_, idx)

    def add_parameter(self, param_id, param_value):
        """
        Add a manual annotation parameter to the XML

        Parameters
        ----------
        param_id: str
            The parameter ID for this annotation. Now ewe are using IMPRESS paarameters
            eg: IMPC_EMO_022_001  see https://www.mousephenotype.org/impress/parameterontologies/19112/495

        param_value: str
            Value associated with this annotation.
            for example: "abnormal"
        x,y,z: int or None
            the optional points associated with this annotation (can be None)
        Notes
        -----
        Adapted from James Brown's http://phobos/james.brown/export_xml_generation

        """

        # Get parameter info and append to procedure
        parameter = etree.SubElement(self.procedure_element, 'simpleParameter', parameterID=param_id)

        # Create value element
        value = etree.SubElement(parameter, 'value')
        value.text = param_value


def load_metadata(yaml_path):
    with open(yaml_path, 'r') as fh:
        data = yaml.load(fh)
    return data
