// This file is a part of beans project.
// Copyright (c) 2017 Aleksander Gajewski <adiog@quicksave.io>.

#ifndef CPPBEANS_H
#define CPPBEANS_H

#include <boost/optional.hpp>
using STRING = std::string;
namespace std {
using boost::optional;
using boost::none;
using boost::make_optional;
}

#include "rapidjson/document.h"
#include "rapidjson/stringbuffer.h"
#include "rapidjson/writer.h"
#include <vector>

using Value = rapidjson::GenericValue<rapidjson::UTF8<>>;

template <typename ElementType>
struct Typoid
{
    static ElementType FromValue(const Value& value)
    {
        return ElementType(value);
    }

    template <typename Writer>
    static void Serialize(const ElementType& elementType, Writer& writer)
    {
        elementType.Serialize(writer);
    }
};

template <>
struct Typoid<int>
{
    static int FromValue(const Value& value)
    {
        return value.GetInt();
    }

    template <typename Writer>
    static void Serialize(const int& elementType, Writer& writer)
    {
        writer.Int(elementType);
    }
};

template <>
struct Typoid<std::string>
{
    static std::string FromValue(const Value& value)
    {
        return value.GetString();
    }

    template <typename Writer>
    static void Serialize(const std::string& elementType, Writer& writer)
    {
        writer.String(elementType.c_str());
    }
};

template <typename ElementType>
class List : public std::vector<ElementType>
{
public:
    using std::vector<ElementType>::vector;

    List() = default;

    List(const rapidjson::Value& value)
    {
        for (rapidjson::Value::ConstValueIterator itr = value.Begin(); itr != value.End(); ++itr)
        {
            this->push_back(Typoid<ElementType>::FromValue(*itr));
        }
    }

    template <typename Writer>
    void Serialize(Writer& writer) const
    {
        writer.StartArray();
        for (typename std::vector<ElementType>::const_iterator dependentItr = this->begin(); dependentItr != this->end(); ++dependentItr)
        {
            Typoid<ElementType>::Serialize(*dependentItr, writer);
        }
        writer.EndArray();
    }
};

class Base64 : public std::string {
public:
    using std::string::string;

    Base64() = default;

    Base64(const rapidjson::Value& value) : std::string{value.GetString()}
    {
    }

    template <typename Writer>
    void Serialize(Writer& writer) const
    {
        writer.String(this->c_str());
    }
};

class SerializedDict : public std::string {
public:
    using std::string::string;

    SerializedDict() = default;
    //SerializedDict& operator=(const SerializedDict&) = default;

    SerializedDict(const rapidjson::Value& value) : std::string{value.GetString()}
    {
    }

    template <typename Writer>
    void Serialize(Writer& writer) const
    {
        writer.String(this->c_str());
    }
};

template<typename T>
std::string serialize(const T& t)
{
    rapidjson::StringBuffer s;
    rapidjson::Writer<rapidjson::StringBuffer> writer(s);
    Typoid<T>::Serialize(t, writer);

    return s.GetString();
}

class missing_mandatory_field : public std::runtime_error
{
    using std::runtime_error::runtime_error;
};

#endif
