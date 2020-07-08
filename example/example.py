# -*- coding: utf-8 -*-

import sys
import pathlib
import json

sys.path.append('..')

import multidepparser


strarr_inputFiles = [
    r'example-dep-files\hello world\hello.dep',
    r'example-dep-files\hello world\objs\hello\hello.d',
    r'example-dep-files\s p a c e\hello.dep',
    r'example-dep-files\s p a c e\objs\other s p a c e.d',
    r'example-dep-files\s p a c e\objs\s p a c e.d',
    r'example-dep-files\s p a c e\objs\hello\hello.d'
]
str_enc = 'utf-8'

strarr_filePaths = []

for str_tmp in strarr_inputFiles:

    cls_ast = multidepparser.AST(str_tmp, str_enc)
    obj_ast = cls_ast.getAsObject()

    if (obj_ast is None):
        print('[Error] specified file "' + str_tmp + '" does not exist')
        exit

    for obj_def in obj_ast['definitions']:
        if (
            isinstance(obj_def['left'], list) and
            (len(obj_def['left']) == 1) and
            obj_def['operator'] == ':' and
            isinstance(obj_def['right'], list)
        ):

            for str_path in obj_def['right']:
                
                if(not str_path in strarr_filePaths):
                    strarr_filePaths.append(str_path)

print('')
print('Here is list of dependency files')
print('')
print(json.dumps(strarr_filePaths, indent=4))
