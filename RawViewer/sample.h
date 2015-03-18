/**
 * \file sample.h
 *
 * \ingroup EventViewer
 * 
 * \brief Class def header for a class sample
 *
 * @author cadams
 */

/** \addtogroup EventViewer

    @{*/
#ifndef ARGONEUT_ELECTRONS_EVENTVIEWER_SAMPLE_H
#define ARGONEUT_ELECTRONS_EVENTVIEWER_SAMPLE_H

#include <iostream>

/**
   \class sample
   User defined class EventViewer ... these comments are used to generate
   doxygen documentation!
 */
class sample{

public:

  /// Default constructor
  sample(){}

  /// Default destructor
  virtual ~sample(){};

  void HelloWorld(){std::cout << "Fuck you." << std::endl;}

};

#endif
/** @} */ // end of doxygen group 

