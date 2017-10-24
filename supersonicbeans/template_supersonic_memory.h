{% block body %}// This file is an AUTOGENERATED part of quicksave project.
// Copyright (c) 2017 Aleksander Gajewski <adiog@quicksave.io>.

#pragma once

#include "supersonic/cursor/core/sort.h"
#include "supersonic/cursor/infrastructure/ordering.h"
#include "supersonic/supersonic.h"
#include "supersonic/utils/strings/stringpiece.h"

#include "supersonic/utils/map_util.h"

#include <SupersonicCast.h>

#include <qsgen/bean/{{ bean_class}}.h>
#include <hash.h>

namespace supersonic {

template <typename Bean>
struct SupersonicBeanTable;

template<>
struct SupersonicBeanTable<{{ bean_class }}> {
    TupleSchema schema;
    std::unique_ptr<Table> table;
    std::unique_ptr<TableRowWriter> table_writer;

    SupersonicBeanTable()
    {   {% for add_attribute_statement in add_attribute_statements %}
        {{ add_attribute_statement }}{% endfor %}

        table.reset(new Table(schema, HeapBufferAllocator::Get()));

        table_writer.reset(new TableRowWriter(table.get()));
    }

    void insert({{bean_class}}& bean)
    {
        {% if primary_key %}if (!bean.{{ primary_key }}) bean.{{ primary_key }} = qs::util::Hash::get();{% endif %}

        auto& add_row = table_writer->AddRow();
        {% for insert_field in insert_fields %}
        {{ insert_field }}{% endfor %}

        add_row.CheckSuccess();
    }

    static {{bean_class}} decode(const View& view)
    {
        {{bean_class}} bean;
        {% for decode_field in decode_fields %}
        {{ decode_field }}(view.column({{ loop.index - 1}}));{% endfor %}

        return std::move(bean);
    }
};
}
{% endblock %}