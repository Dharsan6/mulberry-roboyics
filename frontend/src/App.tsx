import { useState, useEffect, useCallback } from 'react';
import { Navbar } from './components/Navbar';
import { Header } from './components/Header';
import { OverviewView } from './views/OverviewView';
import { RoverControlView } from './views/RoverControlView';
import { AgronomyView } from './views/AgronomyView';
import { SpatialMLView } from './views/SpatialMLView';
import { PrescriptionsView } from './views/PrescriptionsView';
import { SamplesView } from './views/SamplesView';
import { LandingPageView } from './views/LandingPageView';

export function App() {
  const [currentRoute, setCurrentRoute] = useState<'landing' | 'app'>(() => {
    return window.location.hash.startsWith('#/dashboard') ? 'app' : 'landing';
  });
  
  const [activeTab, setActiveTab] = useState<string>(() => {
    const hash = window.location.hash;
    const tabMatch = hash.match(/[?&]tab=([a-z]+)/);
    return tabMatch && tabMatch[1] ? tabMatch[1] : 'overview';
  });

  // Navigate to Dashboard
  const navigateToDashboard = useCallback((tabId: string = 'overview') => {
    setActiveTab(tabId);
    setCurrentRoute('app');
    const targetHash = `#/dashboard?tab=${tabId}`;
    if (window.location.hash !== targetHash) {
      window.history.pushState({ route: 'app', tab: tabId }, '', targetHash);
    }
  }, []);

  // Navigate back to Landing Page
  const navigateToLanding = useCallback(() => {
    setCurrentRoute('landing');
    if (window.location.hash && window.location.hash !== '#/' && window.location.hash !== '#') {
      window.history.pushState({ route: 'landing' }, '', '#/');
    }
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, []);

  // Handle Tab Switch within Dashboard
  const handleTabChange = useCallback((tabId: string) => {
    setActiveTab(tabId);
    const targetHash = `#/dashboard?tab=${tabId}`;
    if (window.location.hash !== targetHash) {
      window.history.pushState({ route: 'app', tab: tabId }, '', targetHash);
    }
  }, []);

  // Sync with browser Back / Forward buttons (popstate & hashchange)
  useEffect(() => {
    const handleLocationChange = () => {
      const hash = window.location.hash;
      if (hash.startsWith('#/dashboard')) {
        setCurrentRoute('app');
        const tabMatch = hash.match(/[?&]tab=([a-z]+)/);
        if (tabMatch && tabMatch[1]) {
          setActiveTab(tabMatch[1]);
        }
      } else {
        setCurrentRoute('landing');
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    };

    window.addEventListener('popstate', handleLocationChange);
    window.addEventListener('hashchange', handleLocationChange);

    return () => {
      window.removeEventListener('popstate', handleLocationChange);
      window.removeEventListener('hashchange', handleLocationChange);
    };
  }, []);

  const renderActiveView = () => {
    switch (activeTab) {
      case 'overview':
        return <OverviewView onNavigate={(tab) => handleTabChange(tab)} />;
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
        return <OverviewView onNavigate={(tab) => handleTabChange(tab)} />;
    }
  };

  if (currentRoute === 'landing') {
    return (
      <LandingPageView 
        onEnterDashboard={(tabId) => navigateToDashboard(tabId || 'overview')} 
      />
    );
  }

  return (
    <div className="flex min-h-screen bg-slate-950 text-slate-100 font-sans">
      {/* Sidebar Navigation */}
      <Navbar 
        activeTab={activeTab} 
        setActiveTab={handleTabChange} 
        onReturnHome={navigateToLanding} 
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        <Header onReturnHome={navigateToLanding} />
        <main className="flex-1 p-6 overflow-y-auto">
          {renderActiveView()}
        </main>
      </div>
    </div>
  );
}

export default App;
