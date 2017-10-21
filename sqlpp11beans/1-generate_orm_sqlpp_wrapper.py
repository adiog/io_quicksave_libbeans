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
            return f'add_row.{row_type_inserter}((ValueRef<{row_type_typedef}>(bean.{field})).value());'

def decode_field(field, row_type):
    is_optional = 'Optional(' in row_type
    row_type = row_type[9:-1] if is_optional else row_type
    source = sql_dict.get(row_type, row_type.lower())
    target = type_dict.get(row_type, row_type.lower())
    if is_optional:
        return f'bean.{field} = QuicksaveOptionalCast<{source}, {target}>()'
    else:
        return f'bean.{field} = QuicksaveCast<{source}, {target}>()'

def first_lower(text):
    return text[0].lower() + text[1:]

def first_upper(text):
    return text[0].upper() + text[1:]

def camel_case(text):
    return ''.join([first_upper(x) for x in text.split('_')])

def mule_case(text):
    text = camel_case(text)
    return text[0].lower() + text[1:]


def cast_column(field, row_type):
    is_optional = 'Optional(' in row_type
    row_type = row_type[9:-1] if is_optional else row_type
    source = sql_dict.get(row_type, row_type.lower())
    target = type_dict.get(row_type, row_type.lower())
    if is_optional:
        return f'if (!row.{mule_case(field)}.is_null()) bean.{field} = row.{mule_case(field)}.value();'
    else:
        return f'bean.{field} = row.{mule_case(field)}.value();'

def param_column(field, row_type):
    is_optional = 'Optional(' in row_type
    row_type = row_type[9:-1] if is_optional else row_type
    source = sql_dict.get(row_type, row_type.lower())
    target = type_dict.get(row_type, row_type.lower())
    return f'(table.{mule_case(field)} = parameter(table.{mule_case(field)}))'

def up_column(field, row_type):
    is_optional = 'Optional(' in row_type
    row_type = row_type[9:-1] if is_optional else row_type
    source = sql_dict.get(row_type, row_type.lower())
    target = type_dict.get(row_type, row_type.lower())
    if is_optional:
        return f'if (bean.{field}) {{ origBean.{field} = bean.{field}; }}'
    else:
        return f'origBean.{field} = bean.{field};'

def over_column(field, row_type):
    is_optional = 'Optional(' in row_type
    row_type = row_type[9:-1] if is_optional else row_type
    source = sql_dict.get(row_type, row_type.lower())
    target = type_dict.get(row_type, row_type.lower())
    if is_optional:
        return f'if (bean.{field}) {{prepareStatement.params.{mule_case(field)} = (*bean.{field}); }}'#  else {{prepareStatement.params.{mule_case(field)} = sqlpp::null;}}'
    else:
        return f'prepareStatement.params.{mule_case(field)} = bean.{field};'

def set_column(field, row_type):
    is_optional = 'Optional(' in row_type
    row_type = row_type[9:-1] if is_optional else row_type
    source = sql_dict.get(row_type, row_type.lower())
    target = type_dict.get(row_type, row_type.lower())
    if is_optional:
        return f'(table.{mule_case(field)} = ((bean.{field}) ? (*bean.{field}) : sqlpp::null))'
    else:
        return f'(table.{mule_case(field)} = bean.{field})'


def make_bean(bean_path, bean_filename):
    env = Environment(loader=FileSystemLoader('.'))
    bean_base = bean_filename[:-5]
    bean_class = bean_base + 'Bean'
    bean_table_class = bean_base
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

        constr = ''.join([cast_column(field, bean_spec[field]) for field in fields])

        bean_primary_key = primary_key

        get_hash = f'if (!bean.{primary_key}) bean.{primary_key} = qs::util::Hash::get();'

        insert_setting = ',\n'.join([set_column(field, bean_spec[field]) for field in fields])
        update_setting = '\n'.join([up_column(field, bean_spec[field]) for field in fields])
        override_setting = '\n'.join([over_column(field, bean_spec[field]) for field in fields])
        param_setting = ',\n'.join([param_column(field, bean_spec[field]) for field in fields])

        table_primary_key = mule_case(primary_key)

        template = env.get_template('1-generate_orm_sqlpp_template_wrapper.h')
        print(template.render(bean_table_class=bean_table_class,
                              bean_class=bean_class,
                              bean_primary_key=bean_primary_key,
                              table_primary_key=table_primary_key,
                              insert_setting=insert_setting,
                              update_setting=update_setting,
                              param_setting=param_setting,
                              override_setting=override_setting,
                              get_hash=get_hash,
                              constructor=constr))
#                              add_attribute_statements=add_attribute_statements,
#                              insert_fields=insert_fields,
#                              bean_spec=bean_spec,
#                              bean_name=bean_name,
#                              decode_fields=decode_fields,
#                              primary_key=primary_key,
#                              fields=fields))



if __name__ == '__main__':
    make_bean(sys.argv[1], sys.argv[2])
