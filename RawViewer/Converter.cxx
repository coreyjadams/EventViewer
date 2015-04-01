#ifndef CONVERTER_CXX
#define CONVERTER_CXX

#include "Converter.h"
#include <iostream>
#include <exception>

namespace larlite {

  PyObject* Converter::Convert(const std::vector<std::string>& str_array) const
  {
    PyObject* pvec = PyList_New(str_array.size());

    for(size_t i=0; i<str_array.size(); ++i) {

      if(PyList_SetItem(pvec, i, PyString_FromString(str_array[i].c_str()))) {

        Py_DECREF(pvec);
        std::cerr<<"<<Convert>> failed!"<<std::endl;
        throw std::exception();
      }
    }
    return pvec;
  }

  PyObject* Converter::Convert(const std::vector<float>& flt_array) const
  {
    PyObject* pvec = PyList_New(flt_array.size());

    for(size_t i=0; i<flt_array.size(); ++i) {

      if(PyList_SetItem(pvec, i, PyFloat_FromDouble(flt_array[i]))) {

        Py_DECREF(pvec);
        std::cerr<<"<<Convert>> failed!"<<std::endl;
        throw std::exception();
      }
    }
    return pvec;
  }

  PyObject* Converter::Convert(const std::vector<std::vector<float>>& fltflt_array) const
  {
    PyObject* pvec = PyList_New(fltflt_array.size());

    for(size_t i=0; i<fltflt_array.size(); ++i) {

      if(PyList_SetItem(pvec, i, Convert(fltflt_array[i]))) {

        Py_DECREF(pvec);
        std::cerr<<"<<Convert>> failed!"<<std::endl;
        throw std::exception();
      }
    }
    return pvec;
  }

}


#endif
