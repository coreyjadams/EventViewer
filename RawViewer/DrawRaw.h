/**
 * \file DrawRaw.h
 *
 * \ingroup EventViewer
 * 
 * \brief Class def header for a class DrawRaw
 *
 * @author cadams
 */

/** \addtogroup EventViewer

    @{*/

#ifndef LARLITE_DRAWRAW_H
#define LARLITE_DRAWRAW_H

#include "Analysis/ana_base.h"
#include "LArUtil/Geometry.h"

namespace larlite {
  /**
     \class DrawRaw
     User custom analysis class made by SHELL_USER_NAME
   */
  class DrawRaw : public ana_base{
  
  public:

    /// Default constructor
    DrawRaw(){ _name="DrawRaw"; _fout=0;}

    /// Default destructor
    virtual ~DrawRaw(){}

    /** IMPLEMENT in DrawRaw.cc!
        Initialization method to be called before the analysis event loop.
    */ 
    virtual bool initialize();

    /** IMPLEMENT in DrawRaw.cc! 
        Analyze a data event-by-event  
    */
    virtual bool analyze(storage_manager* storage);

    /** IMPLEMENT in DrawRaw.cc! 
        Finalize method to be called after all events processed.
    */
    virtual bool finalize();

    // Function to get the data by plane:
    const std::vector<std::vector<float>> & getDataByPlane(unsigned int p) const;

  protected:
    
    //vector of [tpc][wire][time]
    std::vector<std::vector<std::vector<float>>> * wiredata;
    // std::vector<float> * data;

    const larutil::Geometry * geoService;

  };
}
#endif

//**************************************************************************
// 
// For Analysis framework documentation, read Manual.pdf here:
//
// http://microboone-docdb.fnal.gov:8080/cgi-bin/ShowDocument?docid=3183
//
//**************************************************************************

/** @} */ // end of doxygen group 
