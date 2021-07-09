import unittest

from linkml_runtime.utils.compile_python import compile_python
from linkml_runtime.dumpers import json_dumper

from linkml.generators.pythongen import PythonGenerator
from tests.test_issues.environment import env
from tests.utils.test_environment import TestEnvironmentTestCase


class Issue157TestCase(TestEnvironmentTestCase):
    env = env

    def test_issue_157(self):
        """ Test to check if prefixes of CURIEs from granular mappings show up in the json-ld context """
        x = env.generate_single_file('issue_157.py',
                                 lambda: PythonGenerator(env.input_path('issue_157.yaml'),
                                 importmap=env.import_map, emit_metadata=False).serialize(), value_is_returned=True)
        module = compile_python(env.expected_path('issue_157.py'))
        m = module.Model(state="1")
        jsonld = json_dumper.dumps(m)
        print(jsonld)
        m2 = module.Model(namedstate=module.ModelStates.production)
        jsonld = json_dumper.dumps(m2)
        print(jsonld)


if __name__ == '__main__':
    unittest.main()
