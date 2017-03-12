import json
import sys
import re

BODY="""
@pybeans.register_bean_spec('___BEAN___', '''
___SPEC___
''')
class ___BEAN___Bean(pybeans.Bean):
    pass
"""


def make_bean(bean_path, bean_filename):
    with open(bean_path + '/' + bean_filename, 'r') as bean_file:
        bean_spec = bean_file.read()
    print(
        re.sub('___BEAN___', bean_filename[:-5],
        re.sub('___SPEC___', bean_spec,
                 BODY)))

if __name__ == '__main__':
    make_bean(sys.argv[1], sys.argv[2])
