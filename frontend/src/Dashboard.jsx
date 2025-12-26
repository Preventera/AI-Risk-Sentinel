import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, LineChart, Line, Cell, PieChart, Pie } from 'recharts';

// AgenticX5 Logo SVG Component
const AgenticX5Logo = ({ size = 60 }) => (
  <svg width={size} height={size} viewBox="0 0 100 100" className="logo-glow">
    <defs>
      <linearGradient id="neonGradient" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#00f0ff" />
        <stop offset="50%" stopColor="#7fff00" />
        <stop offset="100%" stopColor="#ff00ff" />
      </linearGradient>
      <filter id="glow">
        <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
        <feMerge>
          <feMergeNode in="coloredBlur"/>
          <feMergeNode in="SourceGraphic"/>
        </feMerge>
      </filter>
    </defs>
    <circle cx="50" cy="50" r="45" fill="none" stroke="url(#neonGradient)" strokeWidth="2" filter="url(#glow)" />
    <ellipse cx="50" cy="50" rx="25" ry="35" fill="none" stroke="#00f0ff" strokeWidth="1.5" opacity="0.8" />
    <circle cx="50" cy="35" r="8" fill="#00f0ff" filter="url(#glow)" />
    <path d="M35 55 Q50 70 65 55" fill="none" stroke="#7fff00" strokeWidth="2" />
    <circle cx="30" cy="40" r="3" fill="#ff00ff" />
    <circle cx="70" cy="40" r="3" fill="#ff00ff" />
    <circle cx="25" cy="55" r="2" fill="#ffff00" />
    <circle cx="75" cy="55" r="2" fill="#ffff00" />
    <line x1="50" y1="35" x2="30" y2="25" stroke="#7fff00" strokeWidth="1" opacity="0.6" />
    <line x1="50" y1="35" x2="70" y2="25" stroke="#7fff00" strokeWidth="1" opacity="0.6" />
    <line x1="50" y1="35" x2="50" y2="15" stroke="#00f0ff" strokeWidth="1" opacity="0.6" />
    <circle cx="30" cy="25" r="2" fill="#7fff00" />
    <circle cx="70" cy="25" r="2" fill="#7fff00" />
    <circle cx="50" cy="15" r="2" fill="#00f0ff" />
  </svg>
);

// Animated Number Counter
const AnimatedCounter = ({ value, duration = 2000, suffix = '', decimals = 0 }) => {
  const [count, setCount] = useState(0);
  
  useEffect(() => {
    let start = 0;
    const end = parseFloat(value);
    const increment = end / (duration / 16);
    const timer = setInterval(() => {
      start += increment;
      if (start >= end) {
        setCount(end);
        clearInterval(timer);
      } else {
        setCount(start);
      }
    }, 16);
    return () => clearInterval(timer);
  }, [value, duration]);
  
  return <span>{count.toFixed(decimals)}{suffix}</span>;
};

// Risk Category Data (from AI Model Risk Catalog)
const bsiData = [
  { name: 'Malicious Actors', documented: 4.0, incidents: 22.4, bsi: 0.82, color: '#ff0066' },
  { name: 'Privacy & Security', documented: 2.9, incidents: 8.2, bsi: 0.65, color: '#ff6600' },
  { name: 'Socioeconomic', documented: 0.5, incidents: 3.6, bsi: 0.86, color: '#ffcc00' },
  { name: 'Misinformation', documented: 10.2, incidents: 12.9, bsi: 0.21, color: '#00ff99' },
  { name: 'Human Interaction', documented: 0.6, incidents: 1.5, bsi: 0.60, color: '#00ccff' },
  { name: 'AI System Safety', documented: 37.3, incidents: 23.9, bsi: 0.36, color: '#9966ff' },
  { name: 'Discrimination', documented: 44.5, incidents: 27.5, bsi: 0.38, color: '#ff66cc' },
];

const radarData = bsiData.map(d => ({
  category: d.name.split(' ')[0],
  BSI: d.bsi * 100,
  fullMark: 100
}));

const trendData = [
  { month: 'Jan', bsi: 0.22, incidents: 45 },
  { month: 'Feb', bsi: 0.24, incidents: 52 },
  { month: 'Mar', bsi: 0.21, incidents: 48 },
  { month: 'Apr', bsi: 0.25, incidents: 61 },
  { month: 'May', bsi: 0.23, incidents: 55 },
  { month: 'Jun', bsi: 0.26, incidents: 68 },
];

const agentStatus = [
  { name: 'HF_Crawler', level: 'N1', status: 'active', processed: 2847 },
  { name: 'Incident_Monitor', level: 'N1', status: 'active', processed: 869 },
  { name: 'Gap_Detector', level: 'N3', status: 'active', processed: 2863 },
  { name: 'Compliance_Checker', level: 'N4', status: 'idle', processed: 156 },
  { name: 'RiskDoc_Filler', level: 'N5', status: 'standby', processed: 42 },
];

export default function AIRiskSentinelDashboard() {
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [isLoaded, setIsLoaded] = useState(false);
  
  useEffect(() => {
    setIsLoaded(true);
  }, []);

  const globalBSI = 0.18;
  const highRiskCount = bsiData.filter(d => d.bsi > 0.5).length;

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #0a0015 0%, #1a0a2e 50%, #0d1f3c 100%)',
      fontFamily: "'Orbitron', 'Rajdhani', sans-serif",
      color: '#e0e0ff',
      overflow: 'hidden',
      position: 'relative'
    }}>
      {/* Animated Background Grid */}
      <div style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundImage: `
          linear-gradient(rgba(0, 240, 255, 0.03) 1px, transparent 1px),
          linear-gradient(90deg, rgba(0, 240, 255, 0.03) 1px, transparent 1px)
        `,
        backgroundSize: '50px 50px',
        animation: 'gridMove 20s linear infinite',
        pointerEvents: 'none',
        zIndex: 0
      }} />
      
      {/* Floating Orbs */}
      <div style={{
        position: 'fixed',
        width: '300px',
        height: '300px',
        borderRadius: '50%',
        background: 'radial-gradient(circle, rgba(0, 240, 255, 0.15) 0%, transparent 70%)',
        top: '-100px',
        right: '-100px',
        animation: 'float 8s ease-in-out infinite',
        pointerEvents: 'none'
      }} />
      <div style={{
        position: 'fixed',
        width: '400px',
        height: '400px',
        borderRadius: '50%',
        background: 'radial-gradient(circle, rgba(255, 0, 255, 0.1) 0%, transparent 70%)',
        bottom: '-150px',
        left: '-150px',
        animation: 'float 10s ease-in-out infinite reverse',
        pointerEvents: 'none'
      }} />

      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;500;700&display=swap');
        
        @keyframes gridMove {
          0% { transform: translate(0, 0); }
          100% { transform: translate(50px, 50px); }
        }
        
        @keyframes float {
          0%, 100% { transform: translateY(0) scale(1); }
          50% { transform: translateY(-20px) scale(1.05); }
        }
        
        @keyframes pulse {
          0%, 100% { opacity: 1; box-shadow: 0 0 20px rgba(0, 240, 255, 0.5); }
          50% { opacity: 0.8; box-shadow: 0 0 40px rgba(0, 240, 255, 0.8); }
        }
        
        @keyframes slideIn {
          from { opacity: 0; transform: translateY(30px); }
          to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes glowPulse {
          0%, 100% { filter: drop-shadow(0 0 10px rgba(0, 240, 255, 0.8)); }
          50% { filter: drop-shadow(0 0 25px rgba(127, 255, 0, 0.9)); }
        }
        
        @keyframes borderGlow {
          0%, 100% { border-color: rgba(0, 240, 255, 0.5); }
          33% { border-color: rgba(127, 255, 0, 0.5); }
          66% { border-color: rgba(255, 0, 255, 0.5); }
        }
        
        @keyframes scanline {
          0% { top: -100%; }
          100% { top: 100%; }
        }
        
        .logo-glow {
          animation: glowPulse 3s ease-in-out infinite;
        }
        
        .card {
          background: linear-gradient(135deg, rgba(20, 10, 40, 0.9) 0%, rgba(10, 20, 50, 0.8) 100%);
          backdrop-filter: blur(20px);
          border: 1px solid rgba(0, 240, 255, 0.2);
          border-radius: 20px;
          padding: 24px;
          position: relative;
          overflow: hidden;
          transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
          animation: borderGlow 6s ease-in-out infinite;
        }
        
        .card::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          height: 1px;
          background: linear-gradient(90deg, transparent, rgba(0, 240, 255, 0.8), transparent);
        }
        
        .card::after {
          content: '';
          position: absolute;
          top: -100%;
          left: 0;
          right: 0;
          height: 50%;
          background: linear-gradient(180deg, rgba(0, 240, 255, 0.05), transparent);
          animation: scanline 8s linear infinite;
          pointer-events: none;
        }
        
        .card:hover {
          transform: translateY(-5px) scale(1.02);
          border-color: rgba(0, 240, 255, 0.6);
          box-shadow: 0 20px 60px rgba(0, 240, 255, 0.2), 0 0 100px rgba(127, 255, 0, 0.1);
        }
        
        .metric-value {
          font-family: 'Orbitron', monospace;
          font-size: 3rem;
          font-weight: 900;
          background: linear-gradient(135deg, #00f0ff, #7fff00);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
          text-shadow: 0 0 30px rgba(0, 240, 255, 0.5);
        }
        
        .status-dot {
          width: 10px;
          height: 10px;
          border-radius: 50%;
          animation: pulse 2s ease-in-out infinite;
        }
        
        .progress-bar {
          height: 8px;
          border-radius: 4px;
          background: rgba(255, 255, 255, 0.1);
          overflow: hidden;
          position: relative;
        }
        
        .progress-fill {
          height: 100%;
          border-radius: 4px;
          transition: width 1.5s cubic-bezier(0.4, 0, 0.2, 1);
          position: relative;
        }
        
        .progress-fill::after {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
          animation: shimmer 2s infinite;
        }
        
        @keyframes shimmer {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(100%); }
        }
        
        .neon-text {
          color: #00f0ff;
          text-shadow: 0 0 10px #00f0ff, 0 0 20px #00f0ff, 0 0 40px #00f0ff;
        }
        
        .warning-text {
          color: #ff0066;
          text-shadow: 0 0 10px #ff0066, 0 0 20px #ff0066;
        }
      `}</style>

      {/* Main Content */}
      <div style={{ position: 'relative', zIndex: 1, padding: '20px', maxWidth: '1600px', margin: '0 auto' }}>
        
        {/* Header */}
        <header style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: '30px',
          padding: '20px 30px',
          background: 'linear-gradient(135deg, rgba(20, 10, 40, 0.8) 0%, rgba(10, 20, 50, 0.6) 100%)',
          borderRadius: '20px',
          border: '1px solid rgba(0, 240, 255, 0.2)',
          backdropFilter: 'blur(10px)',
          opacity: isLoaded ? 1 : 0,
          transform: isLoaded ? 'translateY(0)' : 'translateY(-20px)',
          transition: 'all 0.8s ease-out'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
            <AgenticX5Logo size={70} />
            <div>
              <h1 style={{
                margin: 0,
                fontSize: '2.2rem',
                fontWeight: 900,
                letterSpacing: '3px',
                background: 'linear-gradient(135deg, #00f0ff 0%, #7fff00 50%, #ff00ff 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text'
              }}>
                AI RISK SENTINEL
              </h1>
              <p style={{ margin: '5px 0 0 0', color: 'rgba(0, 240, 255, 0.7)', fontSize: '0.9rem', letterSpacing: '2px' }}>
                AGENTICX5 • MULTI-AGENT RISK INTELLIGENCE
              </p>
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '30px' }}>
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '0.75rem', color: 'rgba(255, 255, 255, 0.5)', letterSpacing: '1px' }}>SYSTEM STATUS</div>
              <div style={{ color: '#7fff00', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '8px', justifyContent: 'flex-end' }}>
                <span className="status-dot" style={{ background: '#7fff00' }} />
                OPERATIONAL
              </div>
            </div>
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '0.75rem', color: 'rgba(255, 255, 255, 0.5)', letterSpacing: '1px' }}>LAST SYNC</div>
              <div style={{ fontFamily: 'Rajdhani', fontWeight: 500 }}>{new Date().toLocaleTimeString()}</div>
            </div>
          </div>
        </header>

        {/* KPI Cards Row */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(4, 1fr)',
          gap: '20px',
          marginBottom: '25px'
        }}>
          {/* Global BSI */}
          <div className="card" style={{
            opacity: isLoaded ? 1 : 0,
            transform: isLoaded ? 'translateY(0)' : 'translateY(30px)',
            transition: 'all 0.6s ease-out 0.1s'
          }}>
            <div style={{ fontSize: '0.8rem', color: 'rgba(0, 240, 255, 0.7)', letterSpacing: '2px', marginBottom: '10px' }}>
              GLOBAL BLIND SPOT INDEX
            </div>
            <div className="metric-value">
              <AnimatedCounter value={globalBSI} decimals={2} duration={2000} />
            </div>
            <div style={{ marginTop: '15px' }}>
              <div className="progress-bar">
                <div className="progress-fill" style={{
                  width: `${globalBSI * 100}%`,
                  background: 'linear-gradient(90deg, #00f0ff, #7fff00)'
                }} />
              </div>
            </div>
            <div style={{ fontSize: '0.75rem', color: 'rgba(255, 255, 255, 0.5)', marginTop: '10px' }}>
              ↓ 0.02 from last week
            </div>
          </div>

          {/* High Risk Categories */}
          <div className="card" style={{
            opacity: isLoaded ? 1 : 0,
            transform: isLoaded ? 'translateY(0)' : 'translateY(30px)',
            transition: 'all 0.6s ease-out 0.2s'
          }}>
            <div style={{ fontSize: '0.8rem', color: 'rgba(255, 0, 102, 0.8)', letterSpacing: '2px', marginBottom: '10px' }}>
              HIGH RISK CATEGORIES
            </div>
            <div className="metric-value" style={{
              background: 'linear-gradient(135deg, #ff0066, #ff6600)',
              WebkitBackgroundClip: 'text',
              backgroundClip: 'text'
            }}>
              <AnimatedCounter value={highRiskCount} duration={1500} />
            </div>
            <div style={{ fontSize: '0.9rem', color: 'rgba(255, 255, 255, 0.6)', marginTop: '10px' }}>
              of 7 categories above threshold
            </div>
            <div style={{ fontSize: '0.75rem', color: '#ff0066', marginTop: '5px' }}>
              ⚠ Requires attention
            </div>
          </div>

          {/* Models Analyzed */}
          <div className="card" style={{
            opacity: isLoaded ? 1 : 0,
            transform: isLoaded ? 'translateY(0)' : 'translateY(30px)',
            transition: 'all 0.6s ease-out 0.3s'
          }}>
            <div style={{ fontSize: '0.8rem', color: 'rgba(127, 255, 0, 0.8)', letterSpacing: '2px', marginBottom: '10px' }}>
              MODEL CARDS ANALYZED
            </div>
            <div className="metric-value" style={{
              background: 'linear-gradient(135deg, #7fff00, #00ff99)',
              WebkitBackgroundClip: 'text',
              backgroundClip: 'text'
            }}>
              <AnimatedCounter value={64116} duration={2500} />
            </div>
            <div style={{ fontSize: '0.9rem', color: 'rgba(255, 255, 255, 0.6)', marginTop: '10px' }}>
              from Hugging Face Hub
            </div>
            <div style={{ fontSize: '0.75rem', color: '#7fff00', marginTop: '5px' }}>
              ↑ 1,247 new this week
            </div>
          </div>

          {/* Incidents Tracked */}
          <div className="card" style={{
            opacity: isLoaded ? 1 : 0,
            transform: isLoaded ? 'translateY(0)' : 'translateY(30px)',
            transition: 'all 0.6s ease-out 0.4s'
          }}>
            <div style={{ fontSize: '0.8rem', color: 'rgba(153, 102, 255, 0.8)', letterSpacing: '2px', marginBottom: '10px' }}>
              REAL-WORLD INCIDENTS
            </div>
            <div className="metric-value" style={{
              background: 'linear-gradient(135deg, #9966ff, #ff66cc)',
              WebkitBackgroundClip: 'text',
              backgroundClip: 'text'
            }}>
              <AnimatedCounter value={869} duration={2000} />
            </div>
            <div style={{ fontSize: '0.9rem', color: 'rgba(255, 255, 255, 0.6)', marginTop: '10px' }}>
              from AI Incident Database
            </div>
            <div style={{ fontSize: '0.75rem', color: '#9966ff', marginTop: '5px' }}>
              + 23 new incidents tracked
            </div>
          </div>
        </div>

        {/* Main Charts Row */}
        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '20px', marginBottom: '25px' }}>
          
          {/* BSI by Category Chart */}
          <div className="card" style={{
            opacity: isLoaded ? 1 : 0,
            transform: isLoaded ? 'translateY(0)' : 'translateY(30px)',
            transition: 'all 0.6s ease-out 0.5s'
          }}>
            <h3 style={{ 
              margin: '0 0 20px 0', 
              fontSize: '1rem', 
              letterSpacing: '2px',
              color: '#00f0ff'
            }}>
              BLIND SPOT INDEX BY CATEGORY
            </h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={bsiData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(0, 240, 255, 0.1)" />
                <XAxis type="number" domain={[0, 1]} stroke="rgba(255,255,255,0.3)" tick={{ fill: 'rgba(255,255,255,0.6)', fontSize: 11 }} />
                <YAxis dataKey="name" type="category" width={120} stroke="rgba(255,255,255,0.3)" tick={{ fill: 'rgba(255,255,255,0.8)', fontSize: 11 }} />
                <Tooltip 
                  contentStyle={{ 
                    background: 'rgba(10, 20, 40, 0.95)', 
                    border: '1px solid rgba(0, 240, 255, 0.5)',
                    borderRadius: '10px',
                    boxShadow: '0 10px 40px rgba(0, 0, 0, 0.5)'
                  }}
                  labelStyle={{ color: '#00f0ff', fontWeight: 700 }}
                />
                <Bar dataKey="bsi" radius={[0, 8, 8, 0]}>
                  {bsiData.map((entry, index) => (
                    <Cell 
                      key={`cell-${index}`} 
                      fill={entry.bsi > 0.5 ? '#ff0066' : entry.bsi > 0.3 ? '#ff9900' : '#00ff99'}
                      style={{ filter: 'drop-shadow(0 0 8px currentColor)' }}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
            <div style={{ display: 'flex', gap: '20px', marginTop: '15px', fontSize: '0.75rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                <span style={{ width: '12px', height: '12px', borderRadius: '3px', background: '#ff0066' }} />
                Critical (&gt;0.5)
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                <span style={{ width: '12px', height: '12px', borderRadius: '3px', background: '#ff9900' }} />
                Warning (0.3-0.5)
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                <span style={{ width: '12px', height: '12px', borderRadius: '3px', background: '#00ff99' }} />
                Normal (&lt;0.3)
              </div>
            </div>
          </div>

          {/* Radar Chart */}
          <div className="card" style={{
            opacity: isLoaded ? 1 : 0,
            transform: isLoaded ? 'translateY(0)' : 'translateY(30px)',
            transition: 'all 0.6s ease-out 0.6s'
          }}>
            <h3 style={{ margin: '0 0 20px 0', fontSize: '1rem', letterSpacing: '2px', color: '#7fff00' }}>
              RISK RADAR
            </h3>
            <ResponsiveContainer width="100%" height={300}>
              <RadarChart data={radarData}>
                <PolarGrid stroke="rgba(0, 240, 255, 0.2)" />
                <PolarAngleAxis dataKey="category" tick={{ fill: 'rgba(255,255,255,0.7)', fontSize: 10 }} />
                <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 9 }} />
                <Radar name="BSI" dataKey="BSI" stroke="#00f0ff" fill="#00f0ff" fillOpacity={0.3} strokeWidth={2} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Bottom Row */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '20px' }}>
          
          {/* Documented vs Incidents */}
          <div className="card" style={{
            opacity: isLoaded ? 1 : 0,
            transform: isLoaded ? 'translateY(0)' : 'translateY(30px)',
            transition: 'all 0.6s ease-out 0.7s'
          }}>
            <h3 style={{ margin: '0 0 20px 0', fontSize: '1rem', letterSpacing: '2px', color: '#ff00ff' }}>
              DOC VS INCIDENTS GAP
            </h3>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={bsiData.slice(0, 5)}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 0, 255, 0.1)" />
                <XAxis dataKey="name" tick={{ fill: 'rgba(255,255,255,0.6)', fontSize: 9 }} angle={-45} textAnchor="end" height={60} />
                <YAxis tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 10 }} />
                <Tooltip contentStyle={{ background: 'rgba(10, 20, 40, 0.95)', border: '1px solid #ff00ff', borderRadius: '10px' }} />
                <Bar dataKey="documented" fill="#00f0ff" name="Documented %" radius={[4, 4, 0, 0]} />
                <Bar dataKey="incidents" fill="#ff0066" name="Incidents %" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Trend Chart */}
          <div className="card" style={{
            opacity: isLoaded ? 1 : 0,
            transform: isLoaded ? 'translateY(0)' : 'translateY(30px)',
            transition: 'all 0.6s ease-out 0.8s'
          }}>
            <h3 style={{ margin: '0 0 20px 0', fontSize: '1rem', letterSpacing: '2px', color: '#00ff99' }}>
              BSI TREND (6 MONTHS)
            </h3>
            <ResponsiveContainer width="100%" height={220}>
              <LineChart data={trendData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(0, 255, 153, 0.1)" />
                <XAxis dataKey="month" tick={{ fill: 'rgba(255,255,255,0.6)', fontSize: 11 }} />
                <YAxis tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 10 }} domain={[0.15, 0.30]} />
                <Tooltip contentStyle={{ background: 'rgba(10, 20, 40, 0.95)', border: '1px solid #00ff99', borderRadius: '10px' }} />
                <Line type="monotone" dataKey="bsi" stroke="#00f0ff" strokeWidth={3} dot={{ fill: '#00f0ff', r: 5 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Agent Status */}
          <div className="card" style={{
            opacity: isLoaded ? 1 : 0,
            transform: isLoaded ? 'translateY(0)' : 'translateY(30px)',
            transition: 'all 0.6s ease-out 0.9s'
          }}>
            <h3 style={{ margin: '0 0 20px 0', fontSize: '1rem', letterSpacing: '2px', color: '#ffcc00' }}>
              AGENTICX5 AGENTS
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {agentStatus.map((agent, i) => (
                <div key={i} style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '10px 15px',
                  background: 'rgba(255, 255, 255, 0.03)',
                  borderRadius: '10px',
                  border: '1px solid rgba(255, 255, 255, 0.05)'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <span className="status-dot" style={{
                      background: agent.status === 'active' ? '#7fff00' : agent.status === 'idle' ? '#ffcc00' : '#666'
                    }} />
                    <div>
                      <div style={{ fontWeight: 700, fontSize: '0.85rem' }}>{agent.name}</div>
                      <div style={{ fontSize: '0.7rem', color: 'rgba(255,255,255,0.4)' }}>{agent.level}</div>
                    </div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontFamily: 'Orbitron', fontSize: '0.9rem', color: '#00f0ff' }}>
                      {agent.processed.toLocaleString()}
                    </div>
                    <div style={{ fontSize: '0.65rem', color: 'rgba(255,255,255,0.4)' }}>processed</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Footer */}
        <footer style={{
          marginTop: '30px',
          padding: '20px',
          textAlign: 'center',
          borderTop: '1px solid rgba(0, 240, 255, 0.1)'
        }}>
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '15px', marginBottom: '10px' }}>
            <span style={{ fontSize: '0.8rem', color: 'rgba(255,255,255,0.4)' }}>Powered by</span>
            <span style={{ 
              fontWeight: 900, 
              letterSpacing: '3px',
              background: 'linear-gradient(90deg, #00f0ff, #7fff00, #ff00ff)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent'
            }}>
              AGENTICX5
            </span>
          </div>
          <div style={{ fontSize: '0.7rem', color: 'rgba(255,255,255,0.3)', letterSpacing: '1px' }}>
            GenAISafety • Preventera • SquadrAI
          </div>
        </footer>
      </div>
    </div>
  );
}
