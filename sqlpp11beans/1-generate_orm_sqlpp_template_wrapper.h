namespace qs {

template<>
class ORM<{{ bean_class }}>
{
public:
    static qs::orm::{{ bean_table_class }}& getTable() {
        static qs::orm::{{ bean_table_class }} table{};
        return table;
    }

    template<typename Row>
    static {{ bean_class }} constructor(const Row& row) {
        {{ bean_class }} bean;
        {{ constructor }}
        return bean;
    }

    static List<{{ bean_class }}> query(sqlpp::connection &db, const std::string& sqlQuery)
    {
        if (db.getRTTI() == sqlpp::connection::connection_backend::SQLITE3) {
            return queryImplementation(*dynamic_cast<sqlpp::sqlite3::connection*>(&db), sqlQuery);
        } else if (db.getRTTI() == sqlpp::connection::connection_backend::POSTGRESQL) {
            return queryImplementation(*dynamic_cast<sqlpp::postgresql::connection*>(&db), sqlQuery);
        }else {
            throw std::runtime_error("");
        }
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

private:
    template <typename DatabaseConnection>
    static List<{{ bean_class }}> queryImplementation(DatabaseConnection &db, const std::string& sqlQuery)
    {
        const auto table = getTable();

        List<{{ bean_class }}> result(0);

        try
        {
            for (const auto& row : db(
                    sqlpp::custom_query(sqlpp::verbatim(sqlQuery))
                            .with_result_type_of(sqlpp::select(all_of(table)))))
            {
                result.push_back(constructor(row));
            }
        }
        catch (std::exception& e)
        {
            std::cout << "exception: " << e.what() << std::endl;
            return result;
        }

        return result;
    }

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
                result.push_back(constructor(row));
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
    static void removeByImplementation(DatabaseConnection &db, const ColumnName& column, const ColumnType& column_value)
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

            auto prepareStatement = db.prepare(sqlpp::insert_into(table).set(
                    {{ param_setting }}
            ));

            {{ override_setting }}

            db(prepareStatement);

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

            auto optOrigBean = getImplementation(db, *bean.{{ bean_primary_key }});
            auto& origBean = *optOrigBean;

            {{ update_setting }}

            overrideImplementation(db, origBean);
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

            auto prepareStatement = db.prepare(sqlpp::update(table).set(
                    {{ param_setting }}
            ).where(table.{{ table_primary_key }} == *bean.{{ bean_primary_key }})
            );

            {{ override_setting }}

            db(prepareStatement);
        }
        catch (std::exception& e)
        {
            std::cout << "exception: " << e.what() << std::endl;
        }
    }

};
}

