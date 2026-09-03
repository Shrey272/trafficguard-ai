import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/layout/Layout';
import Dashboard from './pages/Dashboard';
import LiveCameras from './pages/LiveCameras';
import CameraManagement from './pages/CameraManagement';
import MapView from './pages/Map';
import Analytics from './pages/Analytics';
import Hospitals from './pages/Hospitals';
import Incidents from './pages/Incidents';
import IncidentDetails from './pages/IncidentDetails';
import ANPR from './pages/ANPR';
import WatchlistManagement from './pages/WatchlistManagement';
import AuditLogs from './pages/AuditLogs';
import SystemHealth from './pages/SystemHealth';
import { AuthProvider } from './context/AuthContext';
import { RealtimeProvider } from './context/RealtimeContext';

function App() {
  return (
    <AuthProvider>
      <RealtimeProvider>
        <BrowserRouter>
          <Layout>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/cameras" element={<LiveCameras />} />
              <Route path="/cameras/manage" element={<CameraManagement />} />
              <Route path="/anpr" element={<ANPR />} />
              <Route path="/watchlist" element={<WatchlistManagement />} />
              <Route path="/map" element={<MapView />} />
              <Route path="/incidents" element={<Incidents />} />
              <Route path="/incidents/:id" element={<IncidentDetails />} />
              <Route path="/analytics" element={<Analytics />} />
              <Route path="/hospitals" element={<Hospitals />} />
              <Route path="/audit-logs" element={<AuditLogs />} />
              <Route path="/system-health" element={<SystemHealth />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </Layout>
        </BrowserRouter>
      </RealtimeProvider>
    </AuthProvider>
  );
}

export default App;
