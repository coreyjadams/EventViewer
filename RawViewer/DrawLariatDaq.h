/**
 * \file DrawLariatDaq.h
 *
 * \ingroup EventViewer
 * 
 * \brief Class def header for a class DrawLariatDaq
 *
 * @author cadams
 */

/** \addtogroup EventViewer

    @{*/

#ifndef LARLITE_DRAWLARIATDAQ_H
#define LARLITE_DRAWLARIATDAQ_H

#include "Analysis/ana_base.h"
#include "LArUtil/Geometry.h"

namespace larlite {
  /**
     \class DrawLariatDaq
     User custom analysis class made by SHELL_USER_NAME
   */
  class DrawLariatDaq{
  
  public:

    /// Default constructor
    DrawLariatDaq();

    /// Default destructor
    virtual ~DrawLariatDaq();

    // functions that would be necessary to do this on a larlite file
    /** IMPLEMENT in DrawLariatDaq.cc!
        Initialization method to be called before the analysis event loop.
    */ 
    void initialize();

    /** IMPLEMENT in DrawLariatDaq.cc! 
        Analyze a data event-by-event  
    */
    // virtual bool analyze(storage_manager* storage);

    /** IMPLEMENT in DrawLariatDaq.cc! 
        Finalize method to be called after all events processed.
    */
    // virtual bool finalize();

    // void setProducer(std::string s){producer = s;}

    void setInputFile(std::string s);

    // The following two functions are the interface
    // to the outside world in terms of passing data out.
    // Do not change their form without good reason!
    // If you are concerned about the speed of passing this 
    // vector, I think it is OK.  It is passed by reference 
    // and so later, a c++ -> numpy converter could turn this
    // data into numpy array.  This seems ideal; this class
    // here could be the owner of the data, responsible for
    // memory management, while numpy provides the streamlined
    // interface for python for drawing.  As such, I really
    // insist that the data continue to be stored as a vector
    // to make sure it is contiguous in memory!  Makes conversion 
    // much much easier.

    // Function to get the data by plane:
    const std::vector<std::vector<unsigned short>> & getDataByPlane(unsigned int p) const;

    // Function to get wire data by plane and wire:
    const std::vector<unsigned short> & getWireData(unsigned int plane, unsigned int wire) const;

    void nextEvent();
    void prevEvent();
    
  protected:
    
    //vector of [tpc][wire][time]
    std::vector<std::vector<std::vector<unsigned short>>> * wiredata;
    // std::vector<unsigned short> * data;

    std::vector< TBranch *> branches;

    const larutil::Geometry * geoService;

    // std::string producer;
    std::string inputFile;

    TChain * c;

    int n_events;
    int current_event;

    const int n_cards = 7;
    const int n_channels = 64;

    // Need some private worker functions to handle file i/o
    void readData();
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
