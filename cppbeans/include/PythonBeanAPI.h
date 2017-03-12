// This file is a part of quicksave project.
// Copyright (c) 2017 Aleksander Gajewski <adiog@quicksave.io>.

#ifndef QUICKSAVE_PYENGINE_H
#define QUICKSAVE_PYENGINE_H

#include <Python.h>
#include <iostream>


class PythonBeanAPIError : public std::runtime_error
{
    using std::runtime_error::runtime_error;
};


class PyObjectPtr
{
public:
    PyObjectPtr(PyObject *pyObject)
            : pyObject(pyObject)
    {
        if (pyObject == nullptr)
        {
            if (PyErr_Occurred())
            {
                PyErr_Print();
            }
            throw PythonBeanAPIError("");
        }
    }

    ~PyObjectPtr()
    {
        Py_XDECREF(pyObject);
    }

    PyObject * steal()
    {
        PyObject * stolen = pyObject;
        pyObject = nullptr;
        return stolen;
    }

    operator PyObject *()
    {
        return pyObject;
    }

    operator bool()
    {
        return pyObject != nullptr;
    }

private:
    PyObject *pyObject;
};


class PythonBeanAPI
{
public:

    template <typename InputBean, typename OutputBean>
    static OutputBean call(
        const char *pythonFunctionName,
        const InputBean &inputBean)
    {
        with_python();

        PyObjectPtr pyInputBean = bean_to_pybean<InputBean>(inputBean);
        PyObjectPtr pyOutputBean = call(pythonFunctionName, pyInputBean);
        return pybean_to_bean<OutputBean>(pyOutputBean);
    }

private:
    PythonBeanAPI()
    {
        Py_Initialize();
    }

    ~PythonBeanAPI()
    {
        Py_Finalize();
    }

    static void with_python()
    {
        static PythonBeanAPI pythonBeanAPI;
    }

    static PyObject * getModule()
    {
        static const char *pythonModuleName = "PythonBeanAPI";
        static PyObjectPtr pyModule = PyImport_ImportModule(pythonModuleName);
        return pyModule;
    }

    template <typename Bean>
    static PyObject *bean_to_pybean(const Bean &bean)
    {
        PyObjectPtr pyBeanString = PyUnicode_FromString(bean.to_string().c_str());
        return call(bean.__name__, pyBeanString);
    }

    template <typename Bean>
    static Bean pybean_to_bean(PyObjectPtr& pyBean)
    {
        PyObjectPtr pyOutputBean = call("to_string", pyBean);
        //std::cout << PyUnicode_AsUTF8(pyOutputBean) << std::endl;
        return Bean{PyUnicode_AsUTF8(pyOutputBean)};
    }

    static PyObject *call(PyObjectPtr &pyFunction, PyObjectPtr &pyArgument)
    {
        if (pyFunction && PyCallable_Check(pyFunction))
        {
            PyObjectPtr pyArguments = PyTuple_New(1);
            PyTuple_SetItem(pyArguments, 0, pyArgument.steal());
            return PyObject_CallObject(pyFunction, pyArguments);
        }
        else
        {
            throw PythonBeanAPIError("");
        }
    }

    static PyObject* call(const char * pythonCallableName, PyObjectPtr& pyArgument)
    {
        PyObjectPtr pyFunction = PyObject_GetAttrString(PythonBeanAPI::getModule(), pythonCallableName);
        return call(pyFunction, pyArgument);
    }
};


#endif
