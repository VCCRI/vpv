from lxml import etree
import yaml
from vpv import common

"""
Generate an IMPC xml submsiion form for the manual annotation procedure
"""


class ExportXML(object):
    """
    TODO: project
    """
    def __init__(self,
                 date_of_annotation,
                 annotator_id,
                 metadata
                 ):
        """

        Parameters
        ----------
        date_of_annotation: str
            yyy-mm-dd
        annotator_id: str
            annonymized annotator id
        metadata: str
            path to procedure_metadata.yaml
        """

        self.metadata = load_metadata(metadata)
        md = self.metadata

        # Create separate file for each modality
        self.root = etree.Element('centreProcedureSet',
                             xmlns="http://www.mousephenotype.org/dcc/exportlibrary/datastructure/core/procedure")
        centre = etree.SubElement(self.root, 'centre', project=md['project'], pipeline=md['pipeline'],
                                  centreID=md['centre_id'])

        # Create an experiment element
        self.experiment = etree.SubElement(centre, 'experiment', dateOfExperiment=md['dateofexperiment'],
                                      experimentID=md['experiment_id'])

        # Append specimen
        specimen = etree.SubElement(self.experiment, 'specimenID')
        specimen.text = md['specimenid']

        self.procedure_element = etree.SubElement(self.experiment, 'procedure', procedureID=md['procedure_id'])

        # Add metadata parameters that are not supplied in the procedure_metadata.yaml
        self.metadata['metadata']['IMPC_EMO_178_001'] = annotator_id
        self.metadata['metadata']['IMPC_EMO_179_001'] = date_of_annotation

    def add_metadata(self):
        for id_, param_value in self.metadata['metadata'].items():
            parameter = etree.SubElement(self.procedure_element, 'procedureMetadata', parameterID=id_)
            # Create value element
            value = etree.SubElement(parameter, 'value')
            value.text = str(param_value)

    def write(self, file_path):
        # print etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8', standalone='yes')
        etree.ElementTree(self.root).write(file_path, pretty_print=True, xml_declaration=True, encoding='UTF-8',
                                      standalone='yes')

    def add_series_media_parameter(self):
        # Get parameter info and append to procedure
        smp = etree.SubElement(self.procedure_element,
                               'seriesMediaParameter',
                               parameterID="IMPC_EMO_001_001")

        smp_value = etree.SubElement(smp, 'value',
                                     {"incrementValue": "1",  "URI": self.metadata['reconstruction_url']})

        # Add the deafault imagages parameter
        self.series_media_parameter = smp_value

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

        param_assoc = etree.SubElement(self.series_media_parameter,
                                       'parameterAssociation',
                                       {'parameterID': param_id})

        def put_in_point(id_, idx):
            etree.SubElement(param_assoc,
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
        return parameter


def load_metadata(yaml_path):
    """
    Load in the procedure_metadata yaml file
    Override the procedureID as this needs to be version 2

    Parameters
    ----------
    yaml_path: str
        path to config file

    Returns
    -------
    dict

    """

    with open(yaml_path, 'r') as fh:
        data = yaml.load(fh)

    # override the procedure ID
    data['procedure_id'] = common.ANNOTATIONS_PROC_VERSION
    return data


def load_xml(xml_file):
    """
    Reads in a manual annotation xml file
    """
    from addict import Dict
    root = etree.parse(xml_file)
    root = strip_ns_prefix(root)

    simple_params = Dict()
    procedure_metadata = []

    for a in root.iter():
        if a.tag == 'centre':
            centreID = a.attrib['centreID']
            pipeline = a.attrib['pipeline']
            project = a.attrib['project']

        elif a.tag == 'experiment':
            doe = a.attrib['dateOfExperiment']
            ex_id = a.attrib['experimentID']

        elif a.tag == 'specimenID':
            spec_id = a.text

        elif a.tag == 'procedure':
            # proc_id = a.attrib['procedureID']  hard code to v2
            proc_id = common.ANNOTATIONS_PROC_VERSION

        elif a.tag == 'simpleParameter':
            param_id = a.attrib['parameterID']
            value = a.find('value').text
            simple_params[param_id].option = value

        elif a.tag == 'procedureMetadata':
            param_id = a.attrib['parameterID']
            value = a.find('value').text
            procedure_metadata.append((param_id, value))

        elif a.tag == 'seriesMediaParameter':
            for b in a.iter():
                param_assocs = b.findall('parameterAssociation')
                for assoc in param_assocs:
                    param_id = assoc.attrib['parameterID']
                    for dim in assoc.findall('dim'):
                        if dim.attrib['id'] == 'x':
                            x = dim.text
                        elif dim.attrib['id'] == 'y':
                            y = dim.text
                        elif dim.attrib['id'] == 'z':
                            z = dim.text
                    simple_params[param_id].xyz = (x, y, z)

    return centreID, pipeline, project, doe, ex_id, spec_id, proc_id, simple_params, procedure_metadata


def strip_ns_prefix(tree):
    """
    remove the namespace from the tree
    Parameters
    ----------
    tree

    Returns
    -------

    """
    #xpath query for selecting all element nodes in namespace
    query = "descendant-or-self::*[namespace-uri()!='']"
    #for each element returned by the above xpath query...
    for element in tree.xpath(query):
        #replace element name with its local name
        element.tag = etree.QName(element).localname
    return tree