import React, { useState } from 'react';

interface MetricProps {
  label: string;
  value: number;
}

const Metric: React.FC<MetricProps> = ({ label, value }) => (
  <div className="metric">
    <h3>{label}</h3>
    <p>{value}</p>
  </div>
);

const App: React.FC = () => {
  const [metrics] = useState([
    { label: 'Users', value: 1024 },
    { label: 'Revenue', value: 48200 },
    { label: 'Orders', value: 312 },
  ]);

  return (
    <div className="dashboard">
      <h1>Dashboard</h1>
      {metrics.map(m => <Metric key={m.label} {...m} />)}
    </div>
  );
};

export default App;
