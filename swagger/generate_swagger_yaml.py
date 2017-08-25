import json
import sys
import re

swagger_dict = {
    "Int": "integer",
    "String": "string",
    "Bool": "boolean",
    "Base64": "string",
    "SerializedDict": "string",
    "List": "List"
}


def print_indent(level, text, fill='  '):
    prefix = ''
    for i in range(level):
        prefix += fill
    print('%s%s' % (prefix, text))


def print_type(l, t, o=False):
    if t == 'Int':
        print_indent(l, 'type: integer')
        print_indent(l, 'format: int64')
    elif t == 'String':
        print_indent(l, 'type: string')
    elif t == 'Bool':
        print_indent(l, 'type: boolean')
    elif t == 'Base64':
        print_indent(l, 'type: string')
        print_indent(l, 'format: base64')
    elif t == 'SerializedDict':
        print_indent(l, 'type: string')
    else:
        print_indent(l, '$ref: \'#/definitions/%s\'' % t)


def create_property(l, name, row_type):
    print_indent(l, '%s:' % name)
    if 'Optional(' in row_type:
        row_type = row_type[9:-1]
        is_optional = True
    else:
        is_optional = False
    if not 'List' in row_type:
        if '_hash' in name:
            print_type(l+1, 'String', is_optional)
            print_indent(l+1, 'description: "Refers to %s"' % (name[:-5].capitalize()))
        elif '_id' in name:
            print_type(l+1, 'Int', is_optional)
            print_indent(l+1, 'description: "Refers to %s"' % (name[:-3].capitalize()))
        else:
            print_type(l+1, row_type, is_optional)
    else:
        row_type = row_type[5:-1]
        print_indent(l+1, 'type: array')
        print_indent(l+1, 'items:')
        print_type(l+2, row_type)


def make_bean(bean_path, bean_filename):
    name = bean_filename[:-5]
    print_indent(1, '%s:' % name)
    bean_name = name.lower()
    print_indent(2, 'type: object')
    print_indent(2, 'properties:')
    with open(bean_path + '/' + bean_filename, 'r') as bean_file:
        bean_spec = json.load(bean_file)

        bean_id = bean_name + '_id'
        bean_hash = bean_name + '_hash'
        if bean_id in bean_spec:
            bean_pk = bean_id
        elif bean_hash in bean_spec:
            bean_pk = bean_hash
        else:
            bean_pk = None

        if bean_pk in bean_spec:
            print_indent(3, '%s:' % bean_pk)
            if 'Int' in bean_spec[bean_pk]:
                print_type(4, 'Int')
                print_indent(4, 'description: "Primary Key"')
            else:
                print_type(4, 'String')
                print_indent(4, 'description: "Primary Key"')
            bean_spec.pop(bean_pk)

        fields = sorted(bean_spec)
        for bean_key in fields:
            create_property(3, bean_key, bean_spec[bean_key])
    print_indent(2, 'xml:')
    print_indent(3, 'name: "%s"' % name)



if __name__ == '__main__':
    try:
        make_bean(sys.argv[1], sys.argv[2])
    except:
        print(sys.argv)
