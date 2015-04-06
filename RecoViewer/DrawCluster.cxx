#ifndef LARLITE_DRAWCLUSTER_CXX
#define LARLITE_DRAWCLUSTER_CXX

#include "DrawCluster.h"
#include "DataFormat/hit.h"
#include "DataFormat/cluster.h"

namespace larlite {

  DrawCluster::DrawCluster(){
    _name="DrawCluster";
    _fout=0;

    wireByPlaneByCluster     
      = new std::vector<std::vector<std::vector<int > > >;
    hitStartByPlaneByCluster 
      = new std::vector<std::vector<std::vector<float > > >;
    hitEndByPlaneByCluster   
      = new std::vector<std::vector<std::vector<float > > >;
  }

  bool DrawCluster::initialize() {

    //
    // This function is called in the beginning of event loop
    // Do all variable initialization you wish to do here.
    // If you have a histogram to fill in the event loop, for example,
    // here is a good place to create one on the heap (i.e. "new TH1D"). 
    //

    // Initialize the geoService object:
    geoService = larutil::Geometry::GetME();


    // Resize data holder to accomodate planes and wires:
    if (wireByPlaneByCluster -> size() != geoService -> Nviews()){
      // std::cout << "resizing vectors to: " << geoService -> Nviews() << std::endl;
      wireByPlaneByCluster     -> resize(geoService -> Nviews());
      hitStartByPlaneByCluster -> resize(geoService -> Nviews());
      hitEndByPlaneByCluster   -> resize(geoService -> Nviews());
    }

    return true;
  }
  
  bool DrawCluster::analyze(storage_manager* storage) {
  
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

    // clear the spots that hold the data:
  // Obtain event-wise data object pointers
    //
    auto ev_clus = storage->get_data<event_cluster>(producer);
    if(!ev_clus)
      return false;
    if(!ev_clus->size()) {
      print(msg::kWARNING,__FUNCTION__,
      Form("Skipping event %d since no cluster found...",ev_clus->event_id()));
      return false;
    }

    auto associated_hit_producers = ev_clus->association_keys(data::kHit);
    
    if(!(associated_hit_producers.size()))
      return false;

    auto ev_hit  = storage->get_data<event_hit>(associated_hit_producers[0]);

    if(!ev_hit){
      std::cout << "Did not find hit data product by "
                << associated_hit_producers[0].c_str()
                << "!" << std::endl;
      return false;
    }
    // Clear out the hit data but reserve some space for the hits
    for (unsigned int p = 0; p < geoService -> Nviews(); p ++){
      wireByPlaneByCluster     ->at(p).clear();
      hitStartByPlaneByCluster ->at(p).clear();
      hitEndByPlaneByCluster   ->at(p).clear();

      wireByPlaneByCluster     ->at(p).reserve(ev_clus->size());
      hitStartByPlaneByCluster ->at(p).reserve(ev_clus->size());
      hitEndByPlaneByCluster   ->at(p).reserve(ev_clus->size());
    }

    // Loop over the clusters and fill the necessary vectors.  
    // I don't know how clusters are stored so I'm taking a conservative
    // approach to packaging them for drawing
    int cluster_index = 0;
    auto ass_info = ev_clus->association(ev_hit->id());
    int view = ev_hit->at(ass_info.front()[0]).View();
    std::vector<int>  nullIntVec;
    std::vector<float>  nullFltVec;
    for(auto const& hit_indices : ass_info) {
      if (view != ev_hit->at(hit_indices[0]).View()){
        view = ev_hit->at(hit_indices[0]).View();
        cluster_index = 0;
      }
      for(auto const& hit_index : hit_indices){
        // std::cout << "Got a hit, seems to be view " << view
        //           << " and cluster " << cluster_index << std::endl;
        
        if (wireByPlaneByCluster -> at(view).size() != cluster_index-1){
          wireByPlaneByCluster -> at(view).push_back(nullIntVec);
        }
        wireByPlaneByCluster -> at(view).at(cluster_index).push_back(ev_hit->at(hit_index).Wire());
        
        if (hitStartByPlaneByCluster -> at(view).size() != cluster_index-1){
          hitStartByPlaneByCluster -> at(view).push_back(nullFltVec);
        }
        hitStartByPlaneByCluster -> at(view).at(cluster_index).push_back(ev_hit->at(hit_index).StartTime());
        
        if (hitEndByPlaneByCluster -> at(view).size() != cluster_index-1){
          hitEndByPlaneByCluster -> at(view).push_back(nullFltVec);
        }
        hitEndByPlaneByCluster -> at(view).at(cluster_index).push_back(ev_hit->at(hit_index).EndTime());
      }
      cluster_index ++;
    }
    
    return true;
  }

  bool DrawCluster::finalize() {

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
      //
    

    return true;
  }

  DrawCluster::~DrawCluster(){
    delete wireByPlaneByCluster;
    delete hitStartByPlaneByCluster;
    delete hitEndByPlaneByCluster;
  }

  int DrawCluster::getNClustersByPlane(unsigned int p) const{
      if (p >= geoService->Nviews() || p < 0){
        std::cerr << "ERROR: Request for nonexistent plane " << p << std::endl;
        return 0;
      }
      else if (wireByPlaneByCluster !=0){
        return wireByPlaneByCluster->at(p).size();
      }
      else{
        return 0;
      }
  }

  const std::vector<int>   & 
    DrawCluster::getWireByPlaneAndCluster(unsigned int p, unsigned int c) const{
      static std::vector<int> returnNull;
      if (p >= geoService->Nviews() || p < 0){
        std::cerr << "ERROR: Request for nonexistent plane " << p << std::endl;
        return returnNull;
      }
      else{
        if (wireByPlaneByCluster !=0){
          if (c >= wireByPlaneByCluster->at(p).size()){
            std::cerr << "ERROR: Request for nonexistent cluster " << c << std::endl;
            return returnNull;
          }
          return wireByPlaneByCluster->at(p).at(c);
        }
        else{
          return returnNull;
        }
      }
    }
  const std::vector<float> & 
    DrawCluster::getHitStartByPlaneAndCluster(unsigned int p, unsigned int c) const{
      static std::vector<float> returnNull;
      if (p >= geoService->Nviews() || p < 0){
        std::cerr << "ERROR: Request for nonexistent plane " << p << std::endl;
        return returnNull;
      }
      else{
        if (hitStartByPlaneByCluster !=0){
          if (c >= hitStartByPlaneByCluster->at(p).size()){
            std::cerr << "ERROR: Request for nonexistent cluster " << c << std::endl;
            return returnNull;
          }
          return hitStartByPlaneByCluster->at(p).at(c);
        }
        else{
          return returnNull;
        }
      }
    }
  const std::vector<float> & 
    DrawCluster::getHitEndByPlaneAndCluster(unsigned int p, unsigned int c) const{
      static std::vector<float> returnNull;
      if (p >= geoService->Nviews() || p < 0){
        std::cerr << "ERROR: Request for nonexistent plane " << p << std::endl;
        return returnNull;
      }
      else{
        if (hitEndByPlaneByCluster !=0){
          if (c >= hitEndByPlaneByCluster->at(p).size()){
            std::cerr << "ERROR: Request for nonexistent cluster " << c << std::endl;
            return returnNull;
          }
          return hitEndByPlaneByCluster->at(p).at(c);
        }
        else{
          return returnNull;
        }
      }
    }



}
#endif
