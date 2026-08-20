import React, { useEffect, useState } from 'react';

function Monitor() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // استدعاء خادم الذكاء الاصطناعي لجلب السجلات
    fetch(`${import.meta.env.VITE_API_URL}/logs`)
      .then(res => res.json())
      .then(data => {
        setLogs(data.logs || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  return (
    <div style={{ padding: '20px', background: '#0f172a', color: '#fff', minHeight: '100vh' }}>
      <h1 style={{ color: '#fbbf24' }}>📊 لوحة مراقبة مجد</h1>
      <p>آخر 10 عمليات بناء للعقول المدبرة:</p>
      {loading ? <p>جاري التحميل...</p> : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginTop: '20px' }}>
          {logs.slice(-10).reverse().map((log, idx) => (
            <div key={idx} style={{
              padding: '15px',
              background: '#1e293b',
              borderRadius: '8px',
              border: `1px solid ${log.status === 'SUCCESS' ? '#22c55e' : '#ef4444'}`
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <strong>{log.status}</strong>
                <span style={{ fontSize: '0.8em', color: '#94a3b8' }}>{new Date(log.timestamp).toLocaleString()}</span>
              </div>
              <p style={{ margin: '10px 0 0', fontSize: '0.9em' }}>Game ID: {log.game_id}</p>
              {log.details?.game_path && <a href={log.details.game_path} target="_blank" style={{ color: '#60a5fa' }}>🔗 رابط اللعبة</a>}
              {log.details?.error && <p style={{ color: '#f87171' }}>خطأ: {log.details.error}</p>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default Monitor;
