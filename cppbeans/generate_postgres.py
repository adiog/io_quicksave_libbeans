import json
import sys
import re

from genbeans.common import sql_order

BODY="""// This file is an AUTOGENERATED part of beans project.
// Copyright (c) 2017 Aleksander Gajewski <adiog@quicksave.io>.

#pragma once

#include <SQLiteCpp/SQLiteCpp.h>
#include <CppBeans.h>
#include <string>
#include <iostream>
#include <util/format.h>
#include <hash>
#include <database/PostgresTransaction.h>

___INC___
#include <bean/___BEAN___Bean.h>


template<typename DB, typename T>
class DatabaseBean;

using PostgresTransactionImpl = tao::postgres::transaction;

template<>
class DatabaseBean<PostgresTransactionImpl, ___BEAN___Bean>
{
public:
    static absl::optional<___BEAN___Bean> get(PostgresTransactionImpl* tr, std::string hash)
    {
        try
        {
            const char * query = "SELECT * FROM public.___TABLE___ WHERE ___PK___ = $1";

            auto result = tr->execute(query, hash);
            auto row = result[0];

            ___BEAN___Bean bean;

            int getIndex = 0;

            ___RETRIEVE___

            return bean;
        }
        catch (std::exception& e)
        {
            std::cout << "exception: " << e.what() << std::endl;
            return absl::nullopt;
        }
    }

    template<typename FIELD_VALUE>
    static List<___BEAN___Bean> get_by(PostgresTransactionImpl* tr, std::string field, FIELD_VALUE field_value)
    {
        List<___BEAN___Bean> result(0);

        try
        {
            std::string query_str = Format::format("SELECT * FROM public.___TABLE___ WHERE %s = $1", field.c_str());
            const char * query = query_str.c_str();

            auto query_result = tr->execute(query, field_value);

            for(int rowIndex = 0; rowIndex < query_result.size(); ++rowIndex){
                auto row = query_result.at(rowIndex);

                ___BEAN___Bean bean;

                int getIndex = 0;

                ___RETRIEVE___

                result.push_back(bean);
            }
        }
        catch (std::exception& e)
        {
            std::cout << "exception: " << e.what() << std::endl;
            return result;
        }

        return result;
    }

    static void remove(PostgresTransactionImpl* tr, std::string hash)
    {
        try
        {
            const char * query = "DELETE FROM public.___TABLE___ WHERE ___PK___ = $1";

            tr->execute(query, hash);
        }
        catch (std::exception& e)
        {
            std::cout << "exception: " << e.what() << std::endl;
        }
    }

    template<typename FIELD_VALUE>
    static void remove_by(PostgresTransactionImpl* tr, std::string field, FIELD_VALUE field_value)
    {
        try
        {
            std::string query_str = Format::format("DELETE FROM public.___TABLE___ WHERE %s = $1", field.c_str());
            const char * query = query_str.c_str();

            tr->execute(query, field_value);
        }
        catch (std::exception& e)
        {
            std::cout << "exception: " << e.what() << std::endl;
        }

    }

    static List<___BEAN___Bean> sql(PostgresTransactionImpl* tr, std::string sql)
    {
        List<___BEAN___Bean> result(0);

        try
        {
            const char * query = sql.c_str();

            auto query_result = tr->execute(query);

            for(int rowIndex = 0; rowIndex < query_result.size(); ++rowIndex){
                auto row = query_result.at(rowIndex);

                ___BEAN___Bean bean;

                int getIndex = 0;

                ___RETRIEVE___

                result.push_back(bean);
            }
        }
        catch (std::exception& e)
        {
            std::cout << "exception: " << e.what() << std::endl;
            return result;
        }

        return result;
    }

    static std::string insert(PostgresTransactionImpl* tr, ___BEAN___Bean bean)
    {
        try
        {
            const char * query = "INSERT INTO public.___TABLE___ (___FIELDS___) VALUES (___BIND_MARK___)";

            int bindIndex = 1;
            ___GET_HASH___

            tr->execute(query, ___BIND_ALL___);

            return *bean.___BEAN_HASH___;
        }
        catch (std::exception& e)
        {
            std::cout << "exception: " << e.what() << std::endl;
        }
    }

    static void insert_with_pk(PostgresTransactionImpl* tr, ___BEAN___Bean bean)
    {
        try
        {
            const char * query = "INSERT INTO public.___TABLE___ (___FIELDS___) VALUES (___BIND_PK_MARK___)";

            tr->execute(query, ___BIND_ALL___);

        }
        catch (std::exception& e)
        {
            std::cout << "exception: " << e.what() << std::endl;
        }
    }

    static void update(PostgresTransactionImpl* tr, ___BEAN___Bean bean)
    {
        try
        {
            std::string setBuilder = "";
            ___UPDATE_SET_BUILDER___
            std::string query_template = Format::format("UPDATE public.___TABLE___ SET %s WHERE ___PK___ = $1", setBuilder.c_str());
            const char * query = query_template.c_str();

            tr->execute(query, *bean.___BEAN_HASH___);
        }
        catch (std::exception& e)
        {
            std::cout << "exception: " << e.what() << std::endl;
        }
    }
/*
    static void override(PostgresTransactionImpl* tr, ___BEAN___Bean bean)
    {
        try
        {
            const char * query = "UPDATE public.___TABLE___ SET ___SET_OVERRIDE___ WHERE ___PK___ = ?";

            int bindIndex = 1;
        
            ___BIND___
            ___BIND_PK___

            query.exec();
        }
        catch (std::exception& e)
        {
            std::cout << "exception: " << e.what() << std::endl;
        }
    }*/
};

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

cpp_cast = {
    "Int": "int",
    "String": "std::string",
    "Bool": "bool",
    "Base64": "std::string",
    "SerializedDict": "std::string",
    "List": "List"
}

sqlite_api = {
    "Int": 'Int',
    "String": 'String',
    "SerializedDict": 'String'
}

def make_bean(bean_path, bean_filename):
    bean_name = bean_filename[:-5]
    bean_name_lower = bean_name.lower()

    bean_json = json.load(open(bean_path + '/' + bean_filename, 'r'))
    bean_pk, other_fields = sql_order(bean_name_lower, bean_json)
    if not bean_pk is None:
        fields = [bean_pk] + other_fields
    else:
        fields = other_fields
    bind_stmt = ''
    bind_update_stmt = ''
    bind_all_stmt = []
    retrieve_stmt = ''
    set_stmt = []
    set_builder_stmt = []
    bind_placeholder = []
    bind_with_pk_placeholder = []
    to_be_included = set()

    bind_index = 1
    for i, bean_key in enumerate(fields):
        l = split_to_list(bean_json[bean_key], [])

        is_optional = l[0] == 'Optional'
        if l[0] == 'Optional':
            l = l[1:]

        if bean_pk == bean_key:
            bind_placeholder.append('$%d' % (i+1))
            get_hash = 'if (!bean.%s) bean.%s = Hash::get();' % (bean_key, bean_key)
        else:
            bind_placeholder.append('$%d' % (i+1))
            if 'String' in bean_json[bean_key]:
                if is_optional:
                    set_builder_stmt.append('if (bean.%s) {setBuilder += ((setBuilder != "") ? std::string(", ") : std::string("")) + Format::format(std::string("\\\"%s\\\" = \'%%s\'"), bean.%s->c_str());}' % (bean_key, bean_key, bean_key))
                else:
                    set_builder_stmt.append('setBuilder += ((setBuilder != "") ? std::string(", ") : std::string("")) + Format::format(std::string("\\\"%s\\\" = \'%%s\'"), bean.%s.c_str());' % (bean_key, bean_key))
            else:
                if is_optional:
                    set_builder_stmt.append('if (bean.%s) {setBuilder += ((setBuilder != "") ? std::string(", ") : std::string("")) + Format::format(std::string("\\\"%s\\\" = \'%%d\'"), bean.%s));}' % (bean_key, bean_key, bean_key))
                else:
                    set_builder_stmt.append('setBuilder += ((setBuilder != "") ? std::string(", ") : std::string("")) + Format::format(std::string("\\\"%s\\\" = \'%%d\'"), bean.%s);' % (bean_key, bean_key))
        bind_with_pk_placeholder.append('$%d' % (i+1))

        set_stmt.append('%s = $%d' % (bean_key, (i+1)))


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

        if is_optional:
            if bean_pk != bean_key:
                bind_update_stmt += 'if (bean.%s) query.bind(bindIndex++, *bean.%s);\n' % (bean_key, bean_key)
                bind_stmt += 'if (bean.%s) query.bind(bindIndex++, *bean.%s); else query.bind(bindIndex++);\n' % (bean_key, bean_key)
            bind_all_stmt.append('((bean.%s) ? (*bean.%s) : std::string(""))' % (bean_key, bean_key))
            retrieve_stmt += 'bean.%s = absl::make_optional<%s>(row.get<%s>(getIndex++));\n' % (bean_key, cpp_type, cpp_cast[l[-1]])
        else:
            if bean_pk != bean_key:
                bind_stmt += 'query.bind(bindIndex++, bean.%s);\n' % (bean_key)
                bind_update_stmt += 'query.bind(bindIndex++, bean.%s);\n' % (bean_key)
            bind_all_stmt.append('bean.%s' % (bean_key))
            retrieve_stmt += 'bean.%s = row.get<%s>(getIndex++);\n' % (bean_key, cpp_cast[l[-1]])

    if 'Optional' in bean_json[bean_pk]:
        bind_pk_stmt = 'query.bind(bindIndex++, *bean.%s);' % (bean_pk)
    else:
        bind_pk_stmt = 'query.bind(bindIndex++, bean.%s);' % (bean_pk)

#    print('-------query.bind(%s, *bean.%s);' % (len(bean_json), bean_pk))

    include_stmt = ''
    for inc in to_be_included:
        include_stmt += '#include <bean/%sBean.h>\n' % inc
    print(
        re.sub('___GUARD___', bean_name.upper() + '_DB_H',
        re.sub('___PK___', bean_pk,
        re.sub('___GET_HASH___', get_hash,
        re.sub('___BEAN___', bean_name,
        re.sub('___BEAN_HASH___', bean_pk,
        re.sub('___BIND___', bind_stmt,
        re.sub('___BIND_UPDATE___', ''.join(bind_update_stmt),
        re.sub('___BIND_ALL___', ','.join(bind_all_stmt),
        re.sub('___BIND_PK___', bind_pk_stmt,
        re.sub('___BIND_MARK___', ', '.join(bind_placeholder),
        re.sub('___BIND_PK_MARK___', ', '.join(bind_with_pk_placeholder),
        re.sub('___RETRIEVE___', retrieve_stmt,
        re.sub('___TABLE___', bean_name_lower,
        re.sub('___FIELDS___', ', '.join(['\\"' + field + '\\"' for field in fields]),
        re.sub('___INC___', include_stmt,
        re.sub('___UPDATE_SET_BUILDER___', ''.join(set_builder_stmt),
        re.sub('___SET_OVERRIDE___', ', '.join(set_stmt),
                 BODY))))))))))))))))))

if __name__ == '__main__':
    make_bean(bean_path=sys.argv[1], bean_filename=sys.argv[2])
