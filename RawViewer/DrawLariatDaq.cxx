#ifndef LARLITE_DRAWLARIATDAQ_CXX
#define LARLITE_DRAWLARIATDAQ_CXX

#include "DrawLariatDaq.h"
#include "DataFormat/wire.h"
#include <fstream>
#include "TChain.h"

namespace larlite {

  DrawLariatDaq::DrawLariatDaq(int ticks){ 
    wiredata = new std::vector<std::vector<std::vector<unsigned short> > > ;
    wiredataOUT = new std::vector<std::vector<std::vector<float> > > ;
    branches.resize(64);
    if (ticks == -1)
      _n_time_ticks = 1536;
    else
      _n_time_ticks = ticks;
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

    _event_no=0;
    _run=0;

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
          vec.resize(_n_time_ticks);
        }
    }

    if (wiredataOUT -> size() != geoService -> Nviews())
      wiredataOUT->resize(geoService -> Nviews());
     
    // resize to the right number of planes
    for (unsigned int p = 0; p < geoService -> Nviews(); p ++){
      // resize to the right number of wires
      if (wiredataOUT->at(p).size() != geoService->Nwires(p) )
        wiredataOUT->at(p).resize(geoService->Nwires(p));
        // Resize the wires to the right length
        for (auto & vec : wiredataOUT->at(p)){
          vec.resize(_n_time_ticks);
        }
    }

    // std::cout << "\n\nCompleted initialize.\n\n";
    return;

  }
  
  void DrawLariatDaq::readData(){


    // Want to be sure that the TChain is ready to go...
    // Do that later.

    std::map<int,int> lar_channel_usage;

    // Need to loop over the file 7 times to get all the cards
    for (int i_card = 0; i_card < _n_cards; i_card ++){
      // Set all the branch addresses for this card.
      // For each channel, can use card + channel to map
      // to larsoft channel.  Then, use larsoft channel
      // to map to the wire location.
      c -> SetBranchAddress("run",&_run);
      c -> SetBranchAddress("spill",&_event_no);

      for(int channel = 0; channel < _n_channels; channel ++ ){

        // // Skip the extra channels:
        // if (i_card == _n_cards -1 && channel >= _n_channels/2) {
        //   continue;
        // }

        // int lar_channel = getLarsoftChannel(i_card, channel);
        // lar_channel_usage[lar_channel] ++;
        // if (lar_channel_usage[lar_channel] > 1){
        //   std::cout << "Found a duplicate channel at " << lar_channel << std::endl;
        //   // continue;
        // }
        // // std::cout << "Card " << i_card << "\tchannel " << channel << "\tlarCH " << lar_channel << std::endl;
        // int plane = geoService->ChannelToPlane(lar_channel);
        // int wire  = geoService->ChannelToWire(lar_channel);
        int plane(0),wire(0);
        // Try another, more stupid and simple way
        int ch = i_card*_n_channels + channel;
        // if (ch >= 480 ) continue;
        if (ch < 240 ){
          plane = 0;
          wire = 239 - ch;
        }
        else if (ch < 480 && ch >= 240){
          plane = 1;
          wire = 479-ch;
        }

        // if (plane == 1)
          // std::cout << "["<<i_card <<", " << channel << "] -> "
                    // << ch << " -> [" << plane << ", " << wire << "]\n";
        // else if (i_card == 7)
          // std::cout << "Wire is " << wire << std::endl;
        // if (wire < 0) continue;
        // if (wire > 239) continue;
        // std::cout << "Card" << i_card << "\tchannel " << channel << "\t(p,w) " << plane << ", " << wire << std::endl;
        // Now we know which part of the data to read this channel into;
        char name[20];
        sprintf(name,"channel_%i",channel);
        c -> SetBranchAddress(name,
            &(wiredata->at(plane).at(wire)[0]),
            & (branches.at(channel)) );

        if (lar_channel_usage[ch] > 1){
          std::cout << "Found a duplicate channel at " << ch << std::endl;
        }
      }
      c -> GetEntry(_current_event*_n_cards + i_card);
    }

    // The wire data needs to be pedestal subtracted.
    int i_plane = 0;
    for (auto & plane : *wiredata){
      float pedestal =0;
      int i_wire = 0;
      for (auto & wire : plane){
        // debug printout: get the first value of each wire:
        // if (i_plane == 1 && i_wire < 64)
        //   std::cout << "[" << i_plane << ", " << i_wire << "]: {"
        //             << wire.at(0) << ", " << wire.at(1)
        //             << ", " << wire.at(2) << "...}\n"; 
        for (auto & tick : wire){
          pedestal += tick;
        }
        pedestal /= _n_time_ticks;
        for (unsigned int tick = 0; tick < wire.size(); tick++){
          wiredataOUT->at(i_plane).at(i_wire).at(tick) = wire.at(tick) - pedestal;
        }
        i_wire ++;
      }
      i_plane ++;
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
    std::cout << "Attempting to open file " << s << std::endl;
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
      if (_n_events == 0){
        _run = 0;
        _event_no = 0;
        return;
      }
      readData();
    }
  }

  int DrawLariatDaq::getLarsoftChannel(int & asic, int & channelOnBoard){
    int lar_channel = asic*_n_channels + channelOnBoard;
    if (lar_channel < 240)
      lar_channel = 239 - lar_channel;
    else{
      lar_channel = 479 - (lar_channel-240);
    }
    return lar_channel;
  }

  const std::vector<std::vector<float>> & DrawLariatDaq::getDataByPlane(unsigned int p) const{
    static std::vector<std::vector<float>> returnNull;
    if (p >= geoService->Nviews()){
      std::cerr << "ERROR: Request for nonexistant plane " << p << std::endl;
      return returnNull;
    }
    else{
      if (wiredataOUT !=0){
        // std::cout << "Called get wire, printing a couple values...\n";
        // std::cout << wiredataOUT->at(p).at(0)[0] << std::endl;
        // std::cout << wiredataOUT->at(p).at(0)[1] << std::endl;
        // std::cout << wiredataOUT->at(p).at(0)[2] << std::endl;
        // std::cout << wiredataOUT->at(p).at(0)[3] << std::endl;
        return wiredataOUT->at(p);
      }
      else{
        return returnNull;
      }
    }
    
  }

  const std::vector<float> & DrawLariatDaq::getWireData(unsigned int plane, unsigned int wire) const{
    static std::vector<float> returnNull;
    if (plane >= geoService->Nviews()){
      std::cerr << "ERROR: Request for nonexistant plane " << plane << std::endl;
      return returnNull;
    }
    if (wire >= geoService->Nwires(plane)){
        std::cerr << "ERROR: Request for nonexistant wire " << wire << std::endl;
        return returnNull;
    }
    else{

      if (wiredataOUT !=0){
        return wiredataOUT->at(plane).at(wire);
      }
      else{
        return returnNull;
      }
    }
    
  }


}
#endif
