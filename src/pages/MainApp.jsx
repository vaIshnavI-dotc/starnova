import React from 'react';
import TopBar from '../components/TopBar';
import ChatWindow from '../components/ChatWindow';
import AlertsDrawer from '../components/AlertsDrawer';

export function MainApp() {
  return (
    <div className="min-h-screen bg-canvas text-ink flex flex-col relative selection:bg-accent/20">
      <TopBar />
      <main className="flex-1 flex flex-col relative">
        <ChatWindow />
      </main>
      <AlertsDrawer />
    </div>
  );
}

export default MainApp;
