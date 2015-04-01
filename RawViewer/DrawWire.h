/**
 * \file DrawWire.h
 *
 * \ingroup RawViewer
 * 
 * \brief Class def header for a class DrawWire
 *
 * @author cadams
 */

/** \addtogroup RawViewer

    @{*/
#ifndef DRAWWIRE_H
#define DRAWWIRE_H

#include <iostream>

/**
   \class DrawWire
   User defined class DrawWire ... these comments are used to generate
   doxygen documentation!
 */
namespace larlite {

class DrawWire{

public:

  /// Default constructor
  DrawWire(){}

  /// Default destructor
  ~DrawWire(){}

protected:
    //vector of [tpc][wire][time]
    std::vector<std::vector<std::vector<float>>> * wiredata;
    // std::vector<float> * data;

    const larutil::Geometry * geoService;


};
} // larlite

#endif
/** @} */ // end of doxygen group 

