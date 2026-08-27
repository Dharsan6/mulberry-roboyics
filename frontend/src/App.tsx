import { useState } from 'react';
import { Navbar } from './components/Navbar';
import { Header } from './components/Header';
import { OverviewView } from './views/OverviewView';
import { RoverControlView } from './views/RoverControlView';
import { AgronomyView } from './views/AgronomyView';
import { SpatialMLView } from './views/SpatialMLView';
import { PrescriptionsView } from './views/PrescriptionsView';
import { SamplesView } from './views/SamplesView';

export function App() {
  const [activeTab, setActiveTab] = useState<string>('overview');

  const renderActiveView = () => {
    switch (activeTab) {
      case 'overview':
        return <OverviewView onNavigate={(tab) => setActiveTab(tab)} />;
      case 'rover':
        return <RoverControlView />;
      case 'agronomy':
        return <AgronomyView />;
      case 'spatial':
        return <SpatialMLView />;
      case 'prescriptions':
        return <PrescriptionsView />;
      case 'samples':
        return <SamplesView />;
      default:
        return <OverviewView onNavigate={(tab) => setActiveTab(tab)} />;
    }
  };

  return (
    <div className="flex min-h-screen bg-slate-950 text-slate-100 font-sans">
      {/* Sidebar Navigation */}
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        <Header />
        <main className="flex-1 p-6 overflow-y-auto">
          {renderActiveView()}
        </main>
      </div>
    </div>
  );
}

export default App;
