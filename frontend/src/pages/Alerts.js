import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { format } from 'date-fns';
import './Alerts.css';

const Alerts = () => {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        const response = await axios.get('/api/alerts');
        setAlerts(response.data);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching alerts:', error);
      }
    };

    fetchAlerts();
    const interval = setInterval(fetchAlerts, 30000); // Refresh every 30 seconds

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="alerts">
      <h1>System Alerts</h1>
      
      {loading ? (
        <div className="loading">Loading alerts...</div>
      ) : (
        <table className="alerts-table">
          <thead>
            <tr>
              <th>Severity</th>
              <th>Message</th>
              <th>Timestamp</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {alerts.map((alert, index) => (
              <tr key={index} className={`alert-row ${alert.severity}`}>
                <td>{alert.severity}</td>
                <td>{alert.message}</td>
                <td>{format(new Date(alert.timestamp), 'MMM dd, yyyy HH:mm:ss')}</td>
                <td>{alert.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default Alerts;