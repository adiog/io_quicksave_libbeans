import json
import sys
import re
from jinja2 import Markup, Environment, FileSystemLoader

sql_dict = {
    "Int": "INT32",
    "String": "STRING",
    "Bool": "BOOL",
    "Base64": "STRING",
    "SerializedDict": "STRING"
}

type_dict = {
    "Int": "int32",
    "String": "string",
    "Bool": "bool",
    "Base64": "string",
    "SerializedDict": "string"
}

inserter_dict = {
    "Int": "Int32",
    "String": "String",
    "Bool": "Bool",
    "Base64": "String",
    "SerializedDict": "String"
}

def create_row(bean_name, name, row_type):
    if 'List' in row_type:
        raise RuntimeError
    else:
        if 'Optional(' in row_type:
            row_type = row_type[9:-1]
            nullable = 'NULLABLE'
        else:
            nullable = 'NOT_NULLABLE'
        row_type = sql_dict.get(row_type, row_type.lower())

        return f'schema.add_attribute(Attribute("{name}", {row_type}, {nullable}));'



def insert_field(field, row_type):
    if 'List' in row_type:
        raise RuntimeError
    else:
        use_deoptional = 'Optional(' in row_type

        nullable = 'NULLABLE' if use_deoptional else 'NOT_NULLABLE'
        row_type = row_type[9:-1] if use_deoptional else row_type
        row_type_inserter = inserter_dict.get(row_type, row_type.lower())
        row_type_typedef = sql_dict.get(row_type, row_type.lower())
        if use_deoptional:
            return f'if (bean.{field}) {{ add_row.{row_type}((ValueRef<{row_type_typedef}>(*bean.{field})).value()); }} else {{ add_row.Null(); }}'
        else:
            return f'add_row.{row_type}((ValueRef<{row_type_typedef}>(bean.{field})).value());'

def decode_field(field, row_type):
    is_optional = 'Optional(' in row_type
    row_type = row_type[9:-1] if is_optional else row_type
    source = sql_dict.get(row_type, row_type.lower())
    target = type_dict.get(row_type, row_type.lower())
    if is_optional:
        return f'bean.{field} = QuicksaveOptionalCast<{source}, {target}>()'
    else:
        return f'bean.{field} = QuicksaveCast<{source}, {target}>()'




def make_bean(bean_path, bean_filename):
    env = Environment(loader=FileSystemLoader('.'))
    bean_class = bean_filename[:-5] + 'Bean'
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

        remaining_fields = [field for field in bean_spec if field != bean_pk]

        if bean_pk in bean_spec:
            primary_key = bean_pk
        else:
            primary_key = None

        if primary_key:
            primary_key_list = [primary_key]
        else:
            primary_key_list = []

        fields = primary_key_list + sorted([bean_field for bean_field in remaining_fields])

        add_attribute_statements = [create_row(bean_name, bean_key, bean_spec[bean_key]) for bean_key in fields]

        insert_fields = [insert_field(field, bean_spec[field]) for field in fields]

        decode_fields = [decode_field(field, bean_spec[field]) for field in fields]

        template = env.get_template('template_supersonic_memory.h')
        print(template.render(bean_class=bean_class,
                              add_attribute_statements=add_attribute_statements,
                              insert_fields=insert_fields,
                              bean_spec=bean_spec,
                              bean_name=bean_name,
                              decode_fields=decode_fields,
                              primary_key=primary_key,
                              fields=fields))



if __name__ == '__main__':
    make_bean(sys.argv[1], sys.argv[2])
