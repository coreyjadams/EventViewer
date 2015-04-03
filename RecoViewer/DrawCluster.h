/**
 * \file DrawCluster.h
 *
 * \ingroup RecoViewer
 * 
 * \brief Class def header for a class DrawCluster
 *
 * @author cadams
 */

/** \addtogroup RecoViewer

    @{*/

#ifndef LARLITE_DRAWCLUSTER_H
#define LARLITE_DRAWCLUSTER_H

#include "Analysis/ana_base.h"

namespace larlite {
  /**
     \class DrawCluster
     User custom analysis class made by SHELL_USER_NAME
   */
  class DrawCluster : public ana_base{
  
  public:

    /// Default constructor
    DrawCluster(){ _name="DrawCluster"; _fout=0;}

    /// Default destructor
    virtual ~DrawCluster(){}

    /** IMPLEMENT in DrawCluster.cc!
        Initialization method to be called before the analysis event loop.
    */ 
    virtual bool initialize();

    /** IMPLEMENT in DrawCluster.cc! 
        Analyze a data event-by-event  
    */
    virtual bool analyze(storage_manager* storage);

    /** IMPLEMENT in DrawCluster.cc! 
        Finalize method to be called after all events processed.
    */
    virtual bool finalize();

  protected:
    
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
