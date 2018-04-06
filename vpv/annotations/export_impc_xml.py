from lxml import etree
import pprint
import yaml

from vpv.annotations.annotations_model import EmapaAnnotation

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

        md = load_metadata(metadata)
        self.metadata= md['meta_data']

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
        for id_, param_value in self.metadata.items():
            parameter = etree.SubElement(self.procedure_element, 'procedureMetadata', parameterID=id_)
            # Create value element
            value = etree.SubElement(parameter, 'value')
            value.text = str(param_value)

    def write(self, file_path):
        self.add_metadata()
        # print etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8', standalone='yes')
        etree.ElementTree(self.root).write(file_path, pretty_print=True, xml_declaration=True, encoding='UTF-8',
                                      standalone='yes')

    def add_parameter(self, param_id, param_value):
        """
        Add a manual annotation parameter to the XML

        Parameters
        ----------
        parameter: EmapaAnnotation


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
