import json
import sys
import re

schema = 'public'

sql_dict = {
    "Int": "integer",
    "String": "text",
    "Bool": "bool",
    "Base64": "text",
    "SerializedDict": "text",
    "List": "List"
}

def create_row(name, row_type, suffix):
    if not 'List' in row_type:
        if '_hash' in name:
            print('    "%s" text NOT NULL REFERENCES "%s" ("%s")%s' % (name, name[:-5], name, suffix))
        elif '_id' in name:
            print('    "%s" integer NOT NULL REFERENCES "%s" ("%s")%s' % (name, name[:-3], name, suffix))
        else:
            if 'Optional(' in row_type:
                row_type = row_type[9:-1]
                print('    "%s" %s NULL%s' % (name, sql_dict.get(row_type, row_type.lower()), suffix))
            else:
                print('    "%s" %s NOT NULL%s' % (name, sql_dict.get(row_type, row_type.lower()), suffix))

def make_bean(bean_path, bean_filename, schema):
    bean_name = bean_filename[:-5].lower()
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

        print('CREATE TABLE %s.%s (' % (schema, bean_name))

        if bean_pk in bean_spec:
            if 'Int' in bean_spec[bean_pk]:
                print('    "%s" serial NOT NULL PRIMARY KEY,' % bean_pk)
            else:
                print('    "%s" text NOT NULL PRIMARY KEY,' % bean_pk)
            bean_spec.pop(bean_pk)

        fields = sorted(bean_spec)
        for bean_key in fields[:-1]:
            create_row(bean_key, bean_spec[bean_key], ',')
        create_row(fields[-1], bean_spec[fields[-1]], '')
        print(');')
        print()



if __name__ == '__main__':
    if len(sys.argv) == 4:
        schema = sys.argv[3]
    make_bean(sys.argv[1], sys.argv[2], schema)
