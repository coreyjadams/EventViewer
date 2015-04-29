#ifndef LARLITE_DRAWLARIATDAQ_CXX
#define LARLITE_DRAWLARIATDAQ_CXX

#include "DrawLariatDaq.h"
#include "DataFormat/wire.h"
#include <fstream>
#include "TChain.h"

namespace larlite {

  DrawLariatDaq::DrawLariatDaq(){ 
    wiredata = new std::vector<std::vector<std::vector<unsigned short> > > ;
    branches.resize(64);
    c = new TChain("DataQuality/v1740");
    initialize();
  }

  DrawLariatDaq::~DrawLariatDaq(){
    // std::cout << "\n\n\nDestructing the drawer!\n\n\n";
    delete wiredata;
    delete c;
    // for (auto branch : branches){
      // delete branch;
    // }
  }

  void DrawLariatDaq::initialize() {

    // Initialize the geoService object:
    geoService = larutil::Geometry::GetME();

    // Initialize data holder:
    // Resize data holder to accomodate planes and wires:
    if (wiredata -> size() != geoService -> Nviews())
      wiredata->resize(geoService -> Nviews());
     
    // resize to the right number of planes
    for (unsigned int p = 0; p < geoService -> Nviews(); p ++){
      // resize to the right number of wires
      if (wiredata->at(p).size() != geoService->Nwires(p) )
        wiredata->at(p).resize(geoService->Nwires(p));
        // Resize the wires to the right length
        for (auto & vec : wiredata->at(p)){
          vec.resize(1536);
        }
    }

    // std::cout << "\n\nCompleted initialize.\n\n";
    return;

  }
  
  void DrawLariatDaq::readData(){


    // Want to be sure that the TChain is ready to go...
    // Do that later.

    // Need to loop over the file 7 times to get all the cards
    for (int i_card = 0; i_card < _n_cards; i_card ++){
      // Set all the branch addresses for this card.
      // For each channel, can use card + channel to map
      // to larsoft channel.  Then, use larsoft channel
      // to map to the wire location.
      c -> SetBranchAddress("run",&_run);
      c -> SetBranchAddress("spill",&_event_no);

      for(int channel = 0; channel < _n_channels; channel ++ ){

        int lar_channel = i_card*_n_channels + channel;
        int plane = geoService->ChannelToPlane(lar_channel);
        int wire  = geoService->ChannelToWire(lar_channel);
        // Now we know which part of the data to read this channel into;
        char name[20];
        sprintf(name,"channel_%i",channel);
        c -> SetBranchAddress(name,
            &(wiredata->at(plane).at(wire)[0]),
            & (branches.at(channel)) );
      }
      c -> GetEntry(_current_event*_n_cards + i_card);
    }

  }

  // This is the function that actually reads in an event
  void DrawLariatDaq::nextEvent(){

    if (_current_event >= _n_events){
      std::cout << "On Event " << _current_event << std::endl;
      std::cout << "Warning, end of file reached, select a new file.\n";
      return;
    }
    else{
      _current_event ++;
      readData();
    }

    return;
  }

  void DrawLariatDaq::prevEvent(){

    if (_current_event <= 0){
      std::cout << "On event " << _current_event << std::endl;
      std::cout << "Warning, at beginning of file, can not go backwards.\n";
      return;
    }
    else{
      _current_event --;
      readData();
    }

    return;

  }

  void DrawLariatDaq::goToEvent(int e){
    if (e < 0){
      std::cout << "Selected event is too low.\n";
      return;
    }
    if (e >= _n_events){
      std::cout << "Selected event is too high.\n";
      return;
    }
    _current_event = e;
    readData();

  }

  void DrawLariatDaq::setInputFile(std::string s){
    // if the file isn't new, do nothing:
    if (s == inputFile) return;
    // check to see if this file exists.
    std::ifstream ifile(s);
    if (!ifile.is_open()){
      std::cerr << "ERROR: Input file failed to open.\n";
      return;
    }
    else{
      // The file exists, try to read it.
      inputFile = s;
      _current_event = 0;
      c -> Reset();
      c -> Add(inputFile.c_str());
      _n_events  = c -> GetEntries() / _n_cards;
      readData();
    }
  }

  // bool DrawLariatDaq::analyze(storage_manager* storage) {
  
  //   //
  //   // Do your event-by-event analysis here. This function is called for 
  //   // each event in the loop. You have "storage" pointer which contains 
  //   // event-wise data. To see what is available, check the "Manual.pdf":
  //   //
  //   // http://microboone-docdb.fnal.gov:8080/cgi-bin/ShowDocument?docid=3183
  //   // 
  //   // Or you can refer to Base/DataFormatConstants.hh for available data type
  //   // enum values. Here is one example of getting PMT waveform collection.
  //   //
  //   // event_fifo* my_pmtfifo_v = (event_fifo*)(storage->get_data(DATA::PMFIFO));
  //   //
  //   // if( event_fifo )
  //   //
  //   //   std::cout << "Event ID: " << my_pmtfifo_v->event_id() << std::endl;
  //   //

  //   // This is an event viewer.  In particular, this handles raw wire signal drawing.
  //   // So, obviously, first thing to do is to get the wires.
  //   auto WireHandle = storage->get_data<larlite::event_wire>(producer);
    

  //   for (auto & wire: *WireHandle){
  //       unsigned int ch = wire.Channel();
  //       wiredata->at(geoService->ChannelToPlane(ch))[geoService->ChannelToWire(ch)] = wire.Signal();
  //   }

  //   return true;
  // }

  // bool DrawLariatDaq::finalize() {

  //   // This function is called at the end of event loop.
  //   // Do all variable finalization you wish to do here.
  //   // If you need, you can store your ROOT class instance in the output
  //   // file. You have an access to the output file through "_fout" pointer.
  //   //
  //   // Say you made a histogram pointer h1 to store. You can do this:
  //   //
  //   // if(_fout) { _fout->cd(); h1->Write(); }
  //   //
  //   // else 
  //   //   print(MSG::ERROR,__FUNCTION__,"Did not find an output file pointer!!! File not opened?");
  //   //
  
  //   delete wiredata;

  //   return true;
  // }

  const std::vector<std::vector<unsigned short>> & DrawLariatDaq::getDataByPlane(unsigned int p) const{
    static std::vector<std::vector<unsigned short>> returnNull;
    if (p >= geoService->Nviews()){
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

  const std::vector<unsigned short> & DrawLariatDaq::getWireData(unsigned int plane, unsigned int wire) const{
    static std::vector<unsigned short> returnNull;
    if (plane >= geoService->Nviews()){
      std::cerr << "ERROR: Request for nonexistant plane " << plane << std::endl;
      return returnNull;
    }
    if (wire >= geoService->Nwires(plane)){
        std::cerr << "ERROR: Request for nonexistant wire " << wire << std::endl;
        return returnNull;
    }
    else{
      // std::cout << "Called get wire, printing a couple values...\n";
      // std::cout << wiredata->at(plane).at(wire)[0] << std::endl;
      // std::cout << wiredata->at(plane).at(wire)[1] << std::endl;
      // std::cout << wiredata->at(plane).at(wire)[2] << std::endl;
      // std::cout << wiredata->at(plane).at(wire)[3] << std::endl;
      if (wiredata !=0){
        return wiredata->at(plane).at(wire);
      }
      else{
        return returnNull;
      }
    }
    
  }


}
#endif
