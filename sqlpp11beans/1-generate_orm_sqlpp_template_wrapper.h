namespace qsgen {
namespace orm {

using namespace sqlpp;

template<>
class ORM<{{ bean_class }}>
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

    static absl::optional<{{ bean_class }}> get(sqlpp::connection &db, const std::string& hash)
    {
        if (db.getRTTI() == sqlpp::connection::connection_backend::SQLITE3) {
            return getImplementation(*dynamic_cast<sqlpp::sqlite3::connection*>(&db), hash);
        } else if (db.getRTTI() == sqlpp::connection::connection_backend::POSTGRESQL) {
            return getImplementation(*dynamic_cast<sqlpp::postgresql::connection*>(&db), hash);
        }else {
            throw std::runtime_error("");
        }
    }

    template<typename ColumnName, typename ColumnType>
    static List<{{ bean_class }}> getBy(sqlpp::connection &db, const ColumnName& column, const ColumnType& column_value)
    {
        if (db.getRTTI() == sqlpp::connection::connection_backend::SQLITE3) {
            return getByImplementation(*dynamic_cast<sqlpp::sqlite3::connection*>(&db), column, column_value);
        } else if (db.getRTTI() == sqlpp::connection::connection_backend::POSTGRESQL) {
            return getByImplementation(*dynamic_cast<sqlpp::postgresql::connection*>(&db), column, column_value);
        }else {
            throw std::runtime_error("");
        }
    }

    static void remove(sqlpp::connection &db, const std::string& hash)
    {
        if (db.getRTTI() == sqlpp::connection::connection_backend::SQLITE3) {
            return removeImplementation(*dynamic_cast<sqlpp::sqlite3::connection*>(&db), hash);
        } else if (db.getRTTI() == sqlpp::connection::connection_backend::POSTGRESQL) {
            return removeImplementation(*dynamic_cast<sqlpp::postgresql::connection*>(&db), hash);
        }else {
            throw std::runtime_error("");
        }
    }

    template<typename ColumnName, typename ColumnType>
    static void removeBy(sqlpp::connection &db, const ColumnName& column, const ColumnType& column_value)
    {
        if (db.getRTTI() == sqlpp::connection::connection_backend::SQLITE3) {
            return removeByImplementation(*dynamic_cast<sqlpp::sqlite3::connection*>(&db), column, column_value);
        } else if (db.getRTTI() == sqlpp::connection::connection_backend::POSTGRESQL) {
            return removeByImplementation(*dynamic_cast<sqlpp::postgresql::connection*>(&db), column, column_value);
        }else {
            throw std::runtime_error("");
        }
    }

    static std::string insert(sqlpp::connection &db, {{ bean_class }}& bean)
    {
        if (db.getRTTI() == sqlpp::connection::connection_backend::SQLITE3) {
            return insertImplementation(*dynamic_cast<sqlpp::sqlite3::connection*>(&db), bean);
        } else if (db.getRTTI() == sqlpp::connection::connection_backend::POSTGRESQL) {
            return insertImplementation(*dynamic_cast<sqlpp::postgresql::connection*>(&db), bean);
        }else {
            throw std::runtime_error("");
        }
    }

    static void update(sqlpp::connection &db, const {{ bean_class }}& bean)
    {
        if (db.getRTTI() == sqlpp::connection::connection_backend::SQLITE3) {
            return updateImplementation(*dynamic_cast<sqlpp::sqlite3::connection*>(&db), bean);
        } else if (db.getRTTI() == sqlpp::connection::connection_backend::POSTGRESQL) {
            return updateImplementation(*dynamic_cast<sqlpp::postgresql::connection*>(&db), bean);
        }else {
            throw std::runtime_error("");
        }
    }

    static void override(sqlpp::connection &db, const {{ bean_class }}& bean)
    {
        if (db.getRTTI() == sqlpp::connection::connection_backend::SQLITE3) {
            return overrideImplementation(*dynamic_cast<sqlpp::sqlite3::connection*>(&db), bean);
        } else if (db.getRTTI() == sqlpp::connection::connection_backend::POSTGRESQL) {
            return overrideImplementation(*dynamic_cast<sqlpp::postgresql::connection*>(&db), bean);
        }else {
            throw std::runtime_error("");
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
private:
    template <typename DatabaseConnection>
    static absl::optional<{{ bean_class }}> getImplementation(DatabaseConnection &db, const std::string& hash)
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

    template<typename DatabaseConnection, typename ColumnName, typename ColumnType>
    static List<{{ bean_class }}> getByImplementation(DatabaseConnection &db, const ColumnName& column, const ColumnType& column_value)
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

    template<typename DatabaseConnection>
    static void removeImplementation(DatabaseConnection &db, const std::string& hash)
    {
        const auto table = getTable();

        db(remove_from(table).where(table.{{ table_primary_key }} == hash));
    }

    template<typename DatabaseConnection, typename ColumnName, typename ColumnType>
    static void removeByImplementation(sqlpp::connection &db, const ColumnName& column, const ColumnType& column_value)
    {
        const auto table = getTable();

        db(remove_from(table).where(column == column_value));
    }

    template<typename DatabaseConnection>
    static std::string insertImplementation(DatabaseConnection &db, {{ bean_class }}& bean)
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

    template<typename DatabaseConnection>
    static void updateImplementation(DatabaseConnection &db, const {{ bean_class }}& bean)
    {
        try
        {
            const auto table = getTable();

            auto prepare_update = db.prepare(sqlpp::update(table).set(
                    {{ param_setting }}
            ).where(table.{{ table_primary_key }} == *bean.{{ bean_primary_key }})
            );

            {{ update_setting }}
        }
        catch (std::exception& e)
        {
            std::cout << "exception: " << e.what() << std::endl;
        }
    }

    template<typename DatabaseConnection>
    static void overrideImplementation(DatabaseConnection &db, const {{ bean_class }}& bean)
    {
        try
        {
            const auto table = getTable();

            auto prepare_update = db.prepare(sqlpp::update(table).set(
                    {{ param_setting }}
            ).where(table.{{ table_primary_key }} == *bean.{{ bean_primary_key }})
            );

            {{ override_setting }}
        }
        catch (std::exception& e)
        {
            std::cout << "exception: " << e.what() << std::endl;
        }
    }

};
}
}

