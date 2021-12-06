import os
import logging
from typing import Optional, Tuple, List, Union, TextIO, Callable, Dict, Iterator, Set
from copy import copy, deepcopy

import click
from rdflib import Graph, URIRef, BNode, Literal
from rdflib.collection import Collection
from rdflib.namespace import RDF, RDFS, SH, XSD
import yaml

from linkml_runtime.utils.schemaview import SchemaView

from linkml_runtime.linkml_model.meta import SchemaDefinition, TypeDefinition, ClassDefinition, Annotation
from linkml_runtime.utils.formatutils import camelcase, underscore

from linkml.utils.generator import shared_arguments, Generator

class PrettierDumper(yaml.Dumper):
    # Insert blank lines between top-level objects
    def write_line_break(self, data=None):
        super().write_line_break(data)
        if len(self.indents) == 1:
            super().write_line_break()
            super().write_line_break()
            super().write_line_break()
        if len(self.indents) == 2:
            super().write_line_break()


class RmlGenerator(Generator):
    generatorname = os.path.basename(__file__)
    generatorversion = '0.0.1'
    valid_formats = ['ttl']
    visit_all_class_slots = False

    def __init__(self, schema: Union[str, TextIO, SchemaDefinition],
                 format: str = valid_formats[0],
                 genmeta: bool=False, gen_classvars: bool=True, gen_slots: bool=True, **kwargs) -> None:
        self.sourcefile = schema
        self.schemaview = SchemaView(schema)
        self.schema = self.schemaview.schema
        self.format = format

    def serialize(self, **args) -> None:
        # g = self.as_graph()
        # data = g.serialize(format='turtle' if self.format in ['owl', 'ttl'] else self.format).decode()
        data = yaml.dump(
            self.as_dict(),
            Dumper=PrettierDumper,
            sort_keys=False,
            default_flow_style=False,
            allow_unicode = True, encoding = None
        )
        return data



    def as_dict(self) -> None:
        sv = self.schemaview

        prefixes = {}
        for pfx in self.schema.prefixes.values():
            # print(pfx.prefix_prefix)
            # print(pfx.prefix_reference)
            prefixes[str(pfx.prefix_prefix)] = str(pfx.prefix_reference)
        
        mappings = {}
        for c in sv.all_classes().values():
            def add_po(p, o):
                if o is not None:
                    # g.add((class_uri, p, v))
                    mappings[str(c.name)]['po'].append({
                        'p': p,
                        'o': o
                    })
                    # if slot.identifier or slot.key:
            class_uri = URIRef(sv.get_uri(c, expand=True))
            # add_pv(RDF.type, SH.NodeShape)
            mappings[str(c.name)] = {
                'sources': ['your_file.csv~csv'],
                'subject': f'{sv.schema.default_prefix}:$(subject_id)',
                'po': []
            }

            for s in sv.class_induced_slots(c.name):
                # Quick fix to build CURIE
                add_po(f'{sv.schema.default_prefix}:{s.name}', f'$({s.name})')


        return {
            'prefixes': prefixes,
            'mappings': mappings
        }




@shared_arguments(RmlGenerator)
@click.command()
def cli(yamlfile, **args):
    """Generate RML mappings in YAML (YARRRML) from a LinkML model"""
    gen = RmlGenerator(yamlfile, **args)
    print(gen.serialize())


if __name__ == '__main__':
    cli()
