namespace sqlpp {

template<>
class DatabaseBean<{{ bean_class }}>
{
public:
    static qsgen::orm::{{ bean_table_class }}& getTable() {
        static qsgen::orm::{{ bean_table_class }} table{};
        return table;
    }

    template<typename Row>
    static {{ bean_class }} constructor(const Row& row) {
        {{ bean_class }} bean;
        {{ constructor }}
        return bean;
    }

    template<typename DB>
    static absl::optional<{{ bean_class }}> get(DB& db, const std::string& hash)
    {
        const auto table = getTable();

        try
        {
            for(const auto& row : db(select(all_of(table)).from(table).where(table.{{ table_primary_key }} == hash).limit(1U)))
            {
                return constructor(row);
            }
        }
        catch (std::exception& e)
        {
            std::cout << "exception: " << e.what() << std::endl;
        }

        return absl::nullopt;
    }

    template<typename DB, typename ColumnName, typename ColumnType>
    static List<{{ bean_class }}> get_by(DB &db, ColumnName column, ColumnType column_value)
    {
        const auto table = getTable();

        List<{{ bean_class }}> result(0);

        try
        {
            for(const auto& row : db(select(all_of(table)).from(table).where(column == column_value))) {
                result.emplace_back(constructor(row));
            }
        }
        catch (std::exception& e)
        {
            std::cout << "exception: " << e.what() << std::endl;
        }

        return result;
    }

    template<typename DB>
    static void remove(DB& db, const std::string& hash)
    {
        const auto table = getTable();

        db(remove_from(table).where(table.{{ table_primary_key }} == hash));
    }

    template<typename DB, typename ColumnName, typename ColumnType>
    static void remove_by(DB &db, ColumnName column, ColumnType column_value)
    {
        const auto table = getTable();

        db(remove_from(table).where(column == column_value));
    }

    template<typename DB>
    static std::string insert(DB& db, {{ bean_class }} bean)
    {
        try
        {
            const auto table = getTable();

            {{ get_hash }}

            db(sqlpp::insert_into(table).set(
                    {{ insert_setting }})
            );

            return *bean.{{ bean_primary_key }};
        }
        catch (std::exception& e)
        {
            std::cout << "exception: " << e.what() << std::endl;
        }
    }

    template<typename DB>
    static void update(DB& db, {{ bean_class }} bean)
    {
        try
        {
            const auto table = getTable();

            auto prepare_update = db.prepare(sqlpp::update(table).set(
                    {{ param_setting }}
                ).where(table.{{ table_primary_key }} = bean.{{ bean_primary_key }})
            );

            {{ update_setting }}
        }
        catch (std::exception& e)
        {
            std::cout << "exception: " << e.what() << std::endl;
        }
    }

    template<typename DB>
    static void override(DB& db, {{ bean_class }} bean)
    {
        try
        {
            const auto table = getTable();

            auto prepare_update = db.prepare(sqlpp::update(table).set(
                    {{ param_setting }}
            ).where(table.{{ table_primary_key }} = bean.{{ bean_primary_key }})
            );

            {{ override_setting }}
        }
        catch (std::exception& e)
        {
            std::cout << "exception: " << e.what() << std::endl;
        }
    }

/*
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
*/
};
}