import React from 'react';
import './EldLogSheet.css';

const EldLogSheet = ({ dailyLog }) => {
  if (!dailyLog || dailyLog.length === 0) {
    return <p>No log data for this day.</p>;
  }

  const getMinutesFromMidnight = (isoString) => {
    const date = new Date(isoString);
    return date.getHours() * 60 + date.getMinutes() + date.getSeconds() / 60;
  };

  const logEntriesWithPositions = dailyLog.map((entry, index) => {
    const startTimeMinutes = getMinutesFromMidnight(entry.start_time);
    const endTimeMinutes = getMinutesFromMidnight(entry.end_time);
    
    let durationMinutes = endTimeMinutes - startTimeMinutes;
    if (durationMinutes < 0) {
        durationMinutes = (24 * 60) - startTimeMinutes + endTimeMinutes;
    }
    
    const leftPercentage = (startTimeMinutes / (24 * 60)) * 100;
    const widthPercentage = (durationMinutes / (24 * 60)) * 100;

    return {
      ...entry,
      left: leftPercentage,
      width: widthPercentage,
    };
  });

  const dutyStatuses = [
    { label: 'OFF', className: 'off-duty' },
    { label: 'SB', className: 'sleeper-berth' },
    { label: 'DR', className: 'driving' },
    { label: 'ON', className: 'on-duty' },
  ];

  return (
    <div className="eld-log-sheet-container">
      <div className="log-grid-header">
        <div className="status-column-header">Status</div>
        <div className="timeline-header">
          {[...Array(25).keys()].map(hour => (
            <div key={hour} className="hour-label">
              {hour % 24 === 0 && hour !== 0 ? '24' : hour}
            </div>
          ))}
        </div>
      </div>
      <div className="log-grid-body">
        {dutyStatuses.map(statusObj => (
          <div key={statusObj.label} className="log-row">
            <div className="status-label">{statusObj.label}</div>
            <div className="timeline-row">
              {[...Array(25).keys()].map(hour => (
                <div key={hour} className="vertical-hour-line" style={{ left: `${(hour / 24) * 100}%` }}></div>
              ))}
              {logEntriesWithPositions.filter(e => e.status === statusObj.label).map((entry, index) => (
                <div
                  key={index}
                  className={`log-bar ${statusObj.className}`}
                  style={{ left: `${entry.left}%`, width: `${entry.width}%` }}
                  title={`${new Date(entry.start_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} - ${new Date(entry.end_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} (${entry.description})`}
                ></div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default EldLogSheet;
