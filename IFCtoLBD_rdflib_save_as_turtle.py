# !/usr/bin/env python3
import pprint

import jpype
from rdflib import Graph, Literal, RDF, URIRef
# Enable Java imports
import jpype.imports
import os

# Pull in types
from jpype.types import *

jpype.startJVM(classpath=['jars/*'])

from org.linkedbuildingdata.ifc2lbd import IFCtoLBDConverter
from org.linkedbuildingdata.ifc2lbd import ConversionProperties

# Convert the IFC file into LBD level 3 model
def process_ifc_file(ifc_folder_path, ifc_file_name):
    lbdconverter = IFCtoLBDConverter("https://example.domain.de/", 3)
    
    props = ConversionProperties()
    props.setHasGeometry(False)
    props.setHasBuildingProperties(True)
    props.setHasBuildingElements(True)
    props.setHasUnits(True)
    props.setHasNonLBDElement(True)
    props.setExportIfcOWL(True)
    props.setHasGeolocation(True)

    # Increase Java heap space
    os.environ["JAVA_OPTS"] = "-Xmx8g"  # Change 4g to the amount of memory you want to allocate
    
    model = lbdconverter.convert(os.path.join(ifc_folder_path, ifc_file_name), props)
    statements = model.listStatements()

    g = Graph()

    # Copy triples to the Python rdflib library
    # Apache Jena  operations:
    # -------------------
    while statements.hasNext():
        triple = statements.next()
        rdf_subject = URIRef(triple.getSubject().toString())
        rdf_predicate = URIRef(triple.getPredicate().toString())
        if triple.getObject().isLiteral():
            rdf_object = Literal(triple.getObject().toString())
        else:
            rdf_object = URIRef(triple.getObject().toString())
        g.add((rdf_subject, rdf_predicate, rdf_object))

    # rdflib operations:
    # -------------------

    lbd_folder_path = "LBD files\sampleFiles"
    
    output_file_path = os.path.join(lbd_folder_path, f"output{ifc_file_name}.ttl")
    g.serialize(destination=output_file_path)
    
# Specify the folder containing IFC files
ifc_folder_path = "IFC files\sampleFiles"

# Get a list of all files in the folder
ifc_files = [f for f in os.listdir(ifc_folder_path) if f.endswith(".ifc")]

# Process each IFC file in the folder
for ifc_file in ifc_files:
    process_ifc_file(ifc_folder_path, ifc_file)
    
jpype.shutdownJVM()
