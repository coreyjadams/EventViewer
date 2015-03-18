#ifndef LARLITE_DRAWRAW_CXX
#define LARLITE_DRAWRAW_CXX

#include "DrawRaw.h"
#include "DataFormat/wire.h"

namespace larlite {

  bool DrawRaw::initialize() {

    //
    // This function is called in the beggining of event loop
    // Do all variable initialization you wish to do here.
    // If you have a histogram to fill in the event loop, for example,
    // here is a good place to create one on the heap (i.e. "new TH1D"). 
    //

    // Initialize the geoService object:
    geoService = larutil::Geometry::GetME();

    // Initialize data holder:
    wiredata = new std::vector<std::vector<std::vector<float> > > ;
    // Resize data holder to accomodate planes and wires:
    wiredata->resize(geoService -> Nplanes());
    for (unsigned int p = 0; p < geoService -> Nplanes(); p ++){
      wiredata->at(p).resize(geoService->Nwires(p));
    }


    return true;

  }
  
  bool DrawRaw::analyze(storage_manager* storage) {
  
    //
    // Do your event-by-event analysis here. This function is called for 
    // each event in the loop. You have "storage" pointer which contains 
    // event-wise data. To see what is available, check the "Manual.pdf":
    //
    // http://microboone-docdb.fnal.gov:8080/cgi-bin/ShowDocument?docid=3183
    // 
    // Or you can refer to Base/DataFormatConstants.hh for available data type
    // enum values. Here is one example of getting PMT waveform collection.
    //
    // event_fifo* my_pmtfifo_v = (event_fifo*)(storage->get_data(DATA::PMFIFO));
    //
    // if( event_fifo )
    //
    //   std::cout << "Event ID: " << my_pmtfifo_v->event_id() << std::endl;
    //

    // This is an event viewer.  In particular, this handles raw wire signal drawing.
    // So, obviously, first thing to do is to get the wires.
    auto WireHandle = storage->get_data<larlite::event_wire>("caldata");
    

    for (auto & wire: *WireHandle){
        unsigned int ch = wire.Channel();
        wiredata->at(geoService->ChannelToPlane(ch))[geoService->ChannelToWire(ch)] = wire.Signal();
    }

    return true;
  }

  bool DrawRaw::finalize() {

    // This function is called at the end of event loop.
    // Do all variable finalization you wish to do here.
    // If you need, you can store your ROOT class instance in the output
    // file. You have an access to the output file through "_fout" pointer.
    //
    // Say you made a histogram pointer h1 to store. You can do this:
    //
    // if(_fout) { _fout->cd(); h1->Write(); }
    //
    // else 
    //   print(MSG::ERROR,__FUNCTION__,"Did not find an output file pointer!!! File not opened?");
    //
  
    delete wiredata;

    return true;
  }

  const std::vector<std::vector<float>> & DrawRaw::getDataByPlane(unsigned int p) const{
    static std::vector<std::vector<float>> returnNull;
    if (p >= geoService->Nplanes()){
      std::cerr << "ERROR: Request for nonexistant plane " << p << std::endl;
      return returnNull;
    }
    else{
      if (wiredata !=0){
        return wiredata->at(p);
      }
      else{
        return returnNull;
      }
    }
    
  }


}
#endif
