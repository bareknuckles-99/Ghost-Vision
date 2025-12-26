import React, { useState, useEffect } from 'react';
import io from 'socket.io-client';
import './App.css';

//Python Flask server
const socket = io('http://127.0.0.1:5000', {
  transports: ['websocket'],
  upgrade: false
});

function App() {
  const [image, setImage] = useState('');
  const [status, setStatus] = useState({ level: 'INITIALIZING', color: [255, 255, 255] });
  const [logs, setLogs] = useState([]);
  
  // NEW: State to track the previous status to prevent duplicate logs
  const [prevStatusLevel, setPrevStatusLevel] = useState('');

  useEffect(() => {
    // 1. Listen for the video frames
    socket.on('video_frame', (data) => {
      setImage(`data:image/jpeg;base64,${data.image}`);
    });

    // 2. Listen for threat status updates
    socket.on('threat_status', (data) => {
      setStatus(data);

      // LOGIC BUFFER: Only add a log if the status has CHANGED and contains "THREAT"
      if (data.level.includes('THREAT') && data.level !== prevStatusLevel) {
        const newLog = {
          time: new Date().toLocaleTimeString(),
          msg: data.level
        };
        // Add new log to the top and keep only the last 10
        setLogs(prev => [newLog, ...prev].slice(0, 10));
        setPrevStatusLevel(data.level); // Update tracker
      } 
      // Reset tracker if status returns to clear/identified so it can trigger again later
      else if (!data.level.includes('THREAT') && data.level !== prevStatusLevel) {
        setPrevStatusLevel(data.level);
      }
    });

    return () => {
      socket.off('video_frame');
      socket.off('threat_status');
    };
  }, [prevStatusLevel]); // Added prevStatusLevel to dependencies

  // Convert BGR (Python) to RGB (CSS)
  const statusColor = `rgb(${status.color[2]}, ${status.color[1]}, ${status.color[0]})`;

  return (
    <div className="dashboard">
      <header className="header">
        <h1>GHOST-VISION v1.0</h1>
        <div className="status-badge" style={{ backgroundColor: statusColor }}>
          {status.level}
        </div>
      </header>

      <div className="main-content">
        <div className="video-container">
          {image ? (
            <img src={image} alt="AI Feed" className="live-feed" />
          ) : (
            <div className="loading">WAITING FOR BACKEND...</div>
          )}
        </div>

        <div className="sidebar">
          <h3>SECURITY LOGS</h3>
          <div className="log-list">
            {logs.length > 0 ? (
              logs.map((log, i) => (
                <div key={i} className="log-item">
                  <span className="log-time">[{log.time}]</span> {log.msg}
                </div>
              ))
            ) : (
              <div className="no-logs">System Secure - No Threats</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;