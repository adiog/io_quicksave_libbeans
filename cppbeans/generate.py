import json
import sys
import re

from genbeans.common import sql_order

BODY="""// This file is an AUTOGENERATED part of beans project.
// Copyright (c) 2017 Aleksander Gajewski <adiog@quicksave.io>.

#ifndef ___GUARD___
#define ___GUARD___

#include <CppBeans.h>

#include <memory>
#include <folly/io/IOBuf.h>
#include <rapidjson/document.h>
#include <rapidjson/writer.h>
#include <rapidjson/stringbuffer.h>

___INC___

class ___BEAN___Bean
{
public:
    ___BEAN___Bean() = default;

    ___BEAN___Bean(const char * json) : ___BEAN___Bean(rapidjson::Document{}.Parse(json)) {

    }

    ___BEAN___Bean(___CONSTRUCTOR_ARGUMENTS___) : ___MEMBER_INITIALIZER_LIST___
    {
    }

    ___BEAN___Bean(const rapidjson::Value& value)
    {
        ___CONS___
    }

    void update(___BEAN___Bean bean)
    {
        ___UPDATE___
    }

    template <typename Writer>
    void Serialize(Writer& writer) const {
        writer.StartObject();
        ___SERIAL___ writer.EndObject();
    }

    std::string to_string() const
    {
        rapidjson::StringBuffer s;
        rapidjson::Writer<rapidjson::StringBuffer> writer(s);
        Serialize(writer);
        return s.GetString();
    }

    operator std::unique_ptr<folly::IOBuf>() const {return folly::IOBuf::copyBuffer(::serialize(*this));}

    const char * __name__ = "___BEAN___Bean";
    ___FIELDS___
};

#endif
"""


atoms = ["Int", "String", "List"]

def split_to_list(label, type_list):
    if re.match(r'^[A-Za-z0-9]+$', label):
        type_list.append(label)
        return type_list
    else:
        try:
            a_type = re.search(r'(\w+).*', label).group(1)
        except:
            raise RuntimeError('Unknown atom in "%s" of expected form "atom(...)"' % label)
        try:
            remaining_label = re.search(r'\((.*)\)', label).group(1)
        except:
            raise RuntimeError('Unknown atom in "%s" of expected form "...(atom)"' % label)
        type_list.append(a_type)
        return split_to_list(remaining_label, type_list)


cpp_dict = {
    "Int": "int",
    "String": "std::string",
    "Bool": "bool",
    "Base64": "Base64",
    "SerializedDict": "SerializedDict",
    "List": "List"
}


def make_bean(bean_path, bean_file):
    bean_json = json.load(open(bean_path + '/' + bean_file, 'r'))
    bean_name_lower = bean_file[:-5].lower()
    include_stmt = ''
    fields_stmt = ''
    cons_stmt = ''
    serial_stmt = ''
    update_stmt = ''
    to_be_included = set()

    cons_args = []
    init_list = []

    bean_pk, other_fields = sql_order(bean_name_lower, bean_json)
    if bean_pk:
        fields = [bean_pk] + other_fields
    else:
        fields = other_fields
    for bean_key in fields:
        l = split_to_list(bean_json[bean_key], [])


        is_optional = l[0] == 'Optional'
        if l[0] == 'Optional':
            l = l[1:]

        cpp_type = ''
        for t in reversed(l):
            if t not in cpp_dict:
                to_be_included.add(t)
            t = cpp_dict.get(t, t+'Bean')
            if cpp_type != '':
                cpp_type = '%s<%s>' % (t, cpp_type)
            else:
                cpp_type = t

        if is_optional:
            cpp_opt_type = 'absl::optional<%s>' % cpp_type
        else:
            cpp_opt_type = cpp_type

        cons_args.append('%s %s' % (cpp_opt_type, bean_key))
        init_list.append('%s(%s)' % (bean_key, bean_key))

        fields_stmt += '%s %s;\n' % (cpp_opt_type, bean_key)
        fields_stmt += 'const char * %s_label = "%s";\n' % (bean_key, bean_key)

        if is_optional:
            serial_stmt += 'if (%s) writer.String(%s_label);\n' % (bean_key, bean_key)
        else:
            serial_stmt += 'writer.String(%s_label);\n' % bean_key

        if is_optional:
            cons_stmt += 'if (value.HasMember(%s_label)) this->%s = absl::make_optional<%s>(Typoid<%s>::FromValue(value[%s_label]));\n' % (bean_key, bean_key, cpp_type, cpp_type, bean_key)
            serial_stmt += 'if (%s) Typoid<%s>::Serialize(*%s, writer);\n' % (bean_key, cpp_type, bean_key)
            update_stmt += 'if (bean.%s) %s = bean.%s;\n' % (bean_key, bean_key, bean_key)
        else:
            cons_stmt += 'if (value.HasMember(%s_label)) this->%s = Typoid<%s>::FromValue(value[%s_label]); else throw(missing_mandatory_field(%s_label));\n' % (bean_key, bean_key, cpp_type, bean_key, bean_key)
            serial_stmt += 'Typoid<%s>::Serialize(%s, writer);\n' % (cpp_type, bean_key)
            update_stmt += '%s = bean.%s;\n' % (bean_key, bean_key)
    for inc in to_be_included:
        include_stmt += '#include <qsgen/bean/%sBean.h>\n' % inc
    print(
        re.sub('___CONSTRUCTOR_ARGUMENTS___', ', '.join(cons_args),
        re.sub('___MEMBER_INITIALIZER_LIST___', ', '.join(init_list),
        re.sub('___GUARD___', bean_file[:-5].upper() + 'BEAN_H',
        re.sub('___BEAN___', bean_file[:-5],
        re.sub('___FIELDS___', fields_stmt,
        re.sub('___SERIAL___', serial_stmt,
        re.sub('___CONS___', cons_stmt,
        re.sub('___UPDATE___', update_stmt,
        re.sub('___INC___', include_stmt,
                 BODY))))))))))

if __name__ == '__main__':
    make_bean(sys.argv[1], sys.argv[2])
