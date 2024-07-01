import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import "../styles/History.css";

const History: React.FC = () => {
  const navigate = useNavigate();
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [historyEntries,setHistoryEntries] = useState<any[]>([])
  useEffect(() => {
    const fetchData = async () => {
      try {
        const accessToken = localStorage.getItem('access_token');

        if (!accessToken) {
          navigate('/auth'); // Navigate to /auth if no access token is found
          return;
        }
        const response = await axios.post(  "http://127.0.0.1:8000/ai_service/user_check/history/",
        {
          headers: {
            // Include the token in the Authorization header
            "Authorization": `Bearer ${accessToken}`,
            'Content-Type': 'application/json',
          },
        }
        );

        const responseData = response.data;

        if ('error' in responseData) {
            localStorage.removeItem('access_token');
          navigate('/auth'); // Navigate to /auth if there's an error response
        } else {
          setHistoryEntries(responseData.history);
        }

      } catch (error) {
        console.error('Error:', error);
      }
    };

    fetchData();
  },[navigate]);

  return (
    <div className="history-container">
      <h2>Request History</h2>
      <table className="history-table">
        <thead>
          <tr>
            <th>Service</th>
            <th>Subscription</th>
            <th>Request Time</th>
            <th>Status</th>
            <th>Processing Time (milliseconds)</th>
          </tr>
        </thead>
        <tbody>
          {historyEntries.map((entry) => (
            <tr key={entry.id}>
              <td>{entry.service}</td>
              <td>{entry.subscription}</td>
              <td>{entry.request_time}</td>
              <td>{entry.status}</td>
              <td>{entry.processing_time}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default History;
