import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { LandingPage } from './components/LandingPage';
import { AppScreen } from './components/AppScreen';
import { Footer } from './components/Footer';
import { DemoModal } from './components/DemoModal';
import './i18n';

export const App: React.FC = () => {
  const [currentPath, setCurrentPath] = useState<string>(() => {
    if (typeof window !== 'undefined') {
      return window.location.pathname.startsWith('/app') ? '/app' : '/';
    }
    return '/';
  });

  const [isDemoModalOpen, setIsDemoModalOpen] = useState(false);

  useEffect(() => {
    const handlePopState = () => {
      setCurrentPath(window.location.pathname.startsWith('/app') ? '/app' : '/');
    };
    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  const navigate = (path: string) => {
    setCurrentPath(path);
    if (typeof window !== 'undefined' && window.history) {
      window.history.pushState({}, '', path);
    }
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen flex flex-col bg-white">
      {/* Top Navbar */}
      <Navbar
        onOpenDemo={() => setIsDemoModalOpen(true)}
        currentPath={currentPath}
        onNavigate={navigate}
      />

      {/* Main View Router */}
      <main className="flex-1">
        {currentPath === '/app' ? (
          <AppScreen onNavigateHome={() => navigate('/')} />
        ) : (
          <LandingPage
            onOpenDemo={() => setIsDemoModalOpen(true)}
            onNavigateApp={() => navigate('/app')}
          />
        )}
      </main>

      {/* Footer */}
      <Footer />

      {/* Enterprise Demo Request Modal */}
      <DemoModal
        isOpen={isDemoModalOpen}
        onClose={() => setIsDemoModalOpen(false)}
      />
    </div>
  );
};

export default App;
