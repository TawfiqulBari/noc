import React, { useState, useEffect } from 'react';
import { Line, Bar } from 'react-chartjs-2';
import axios from 'axios';
import { format } from 'date-fns';
import './Dashboard.css';

const Dashboard = () => {
  const [metrics, setMetrics] = useState({
    cpu: [],
    memory: [],
    containers: []
  });
  const [loading, setLoading] = useState(true);
  const [summary, setSummary] = useState({
    cpu: 0,
    memory: 0,
    containers: 0
  });

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const response = await axios.get('/api/metrics');
        setMetrics(response.data);
        
        // Calculate summary stats
        if (response.data.cpu.length > 0) {
          const latestCpu = response.data.cpu[response.data.cpu.length - 1].value;
          const latestMemory = response.data.memory[response.data.memory.length - 1].value;
          const latestContainers = response.data.containers[response.data.containers.length - 1].value;
          
          setSummary({
            cpu: latestCpu,
            memory: latestMemory,
            containers: latestContainers
          });
        }
        
        setLoading(false);
      } catch (error) {
        console.error('Error fetching metrics:', error);
      }
    };

    fetchMetrics();
    const interval = setInterval(fetchMetrics, 10000); // Refresh every 10 seconds

    return () => clearInterval(interval);
  }, []);

  const cpuData = {
    labels: metrics.cpu.map(m => format(new Date(m.timestamp), 'HH:mm:ss')),
    datasets: [{
      label: 'CPU Usage %',
      data: metrics.cpu.map(m => m.value),
      borderColor: 'rgb(75, 192, 192)',
      backgroundColor: 'rgba(75, 192, 192, 0.2)',
      tension: 0.1,
      fill: true
    }]
  };

  const memoryData = {
    labels: metrics.memory.map(m => format(new Date(m.timestamp), 'HH:mm:ss')),
    datasets: [{
      label: 'Memory Usage %',
      data: metrics.memory.map(m => m.value),
      borderColor: 'rgb(54, 162, 235)',
      backgroundColor: 'rgba(54, 162, 235, 0.2)',
      tension: 0.1,
      fill: true
    }]
  };

  const containersData = {
    labels: metrics.containers.map(m => format(new Date(m.timestamp), 'HH:mm:ss')),
    datasets: [{
      label: 'Running Containers',
      data: metrics.containers.map(m => m.value),
      backgroundColor: 'rgba(255, 99, 132, 0.5)',
    }]
  };

  return (
    <div className="dashboard">
      <h1>Server Monitoring Dashboard</h1>
      
      {loading ? (
        <div className="loading">Loading metrics...</div>
      ) : (
        <>
          <div className="summary-cards">
            <div className={`summary-card ${summary.cpu > 80 ? 'warning' : ''}`}>
              <h3>CPU Usage</h3>
              <p>{summary.cpu.toFixed(1)}%</p>
            </div>
            <div className={`summary-card ${summary.memory > 80 ? 'warning' : ''}`}>
              <h3>Memory Usage</h3>
              <p>{summary.memory.toFixed(1)}%</p>
            </div>
            <div className="summary-card">
              <h3>Containers</h3>
              <p>{summary.containers}</p>
            </div>
          </div>

          <div className="metrics-grid">
            <div className="metric-card">
              <h2>CPU Usage</h2>
              <Line data={cpuData} />
            </div>
            <div className="metric-card">
              <h2>Memory Usage</h2>
              <Line data={memoryData} />
            </div>
            <div className="metric-card">
              <h2>Running Containers</h2>
              <Bar data={containersData} />
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default Dashboard;