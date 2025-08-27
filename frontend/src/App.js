import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';
import { ThemeProvider } from './context/ThemeContext';
import { ToastProvider } from './components/ui/toast';

// Import pages
import LogUpload from './pages/LogUpload';
import Analysis from './pages/Analysis';
import Reports from './pages/Reports';

function App() {
  return (
    <ThemeProvider>
      <ToastProvider>
        <Router>
          <div className="App">
            <Routes>
              <Route path="/" element={<LogUpload />} />
              <Route path="/upload" element={<LogUpload />} />
              <Route path="/analysis" element={<Analysis />} />
              <Route path="/reports" element={<Reports />} />
            </Routes>
          </div>
        </Router>
      </ToastProvider>
    </ThemeProvider>
  );
}

export default App; 