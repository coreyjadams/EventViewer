#ifndef CTONUMPY_CXX
#define CTONUMPY_CXX

#include "CToNumpy.h"

  // template <class T>
  // PyArrayObject* CToNumpy::Convert(const std::vector<T>& _array) const
  // {
  //   PyObject* pvec = PyList_New(_array.size());

  //   // for(size_t i=0; i<_array.size(); ++i) {

  //     // if(PyList_SetItem(pvec, i, PyString_FromString(_array[i].c_str()))) {

  //       // Py_DECREF(pvec);
  //       // std::cerr<<"<<Convert>> failed!"<<std::endl;
  //       // throw std::exception();
  //     // }
  //   // }
  //   return (PyArrayObject*) pvec;
  // }

  std::vector<float> CToNumpy::getTestVector(){
    std::vector<float> ret;
    ret.resize(10);
    for (int i = 0; i < ret.size(); i ++) ret[i] = i;
    return ret;
  }

  PyObject* CToNumpy::Convert(const std::vector<float>& _array) const{
    // Needs an array of the dimensions
    npy_intp dims[1];
    dims[0] = _array.size();
    std::cout << "dims[0] is " << dims[0] << std::endl;
    // dims.push_back(_array.size());
    PyObject* pvec
      = PyArray_SimpleNew(1,dims,NPY_FLOAT64);

    // for(size_t i=0; i<_array.size(); ++i) {

      // if(PyList_SetItem(pvec, i, PyString_FromString(_array[i].c_str()))) {

        // Py_DECREF(pvec);
        // std::cerr<<"<<Convert>> failed!"<<std::endl;
        // throw std::exception();
      // }
    // }
    return  pvec;

  }

#endif
