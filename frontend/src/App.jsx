import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/layout/Layout';
import Dashboard from './pages/Dashboard';
import LiveCameras from './pages/LiveCameras';
import MapView from './pages/Map';
import Analytics from './pages/Analytics';
import Hospitals from './pages/Hospitals';
import Incidents from './pages/Incidents';
import IncidentDetails from './pages/IncidentDetails';
import { RealtimeProvider } from './context/RealtimeContext';

function App() {
  return (
    <RealtimeProvider>
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
          <Route path="/cameras" element={<LiveCameras />} />
          <Route path="/map" element={<MapView />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/hospitals" element={<Hospitals />} />
          <Route path="/incidents" element={<Incidents />} />
          <Route path="/incidents/:id" element={<IncidentDetails />} />
        </Routes>
      </Layout>
    </BrowserRouter>
    </RealtimeProvider>
  );
}

export default App;
