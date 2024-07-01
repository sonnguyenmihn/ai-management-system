import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import "../styles/Dashboard.css"

interface DashboardData {
  total_price: number;
  total_request: number;
  success_rate: number;
}

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [chart1, setChart1] = useState<string>("")
  const [chart2, setChart2] = useState<string>("")

  useEffect(() => {
    const fetchData = async () => {
      try {
        const accessToken = localStorage.getItem('access_token');

        if (!accessToken) {
          navigate('/auth'); // Navigate to /auth if no access token is found
          return;
        }
        const response = await axios.post(  "http://127.0.0.1:8000/ai_service/user_check/dashboard/",
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
          const { total_price, total_request, success_rate } = responseData;
          setDashboardData({ total_price, total_request, success_rate });
          setChart1(responseData.chart1);
          setChart2(responseData.chart2);

        }

      } catch (error) {
        console.error('Error:', error);
      }
    };

    fetchData();
  },[navigate]);

  return (
  <div>
      <div className="charts-container mt-4">
          <img src={`data:image/jpeg;base64,${chart1}`} alt="Success Rate Chart" className="chart img-fluid" />
          <img src={`data:image/jpeg;base64,${chart2}`} alt="Requests per Service Chart" className="chart img-fluid" />
      </div>
      {dashboardData ? (
          <div className="dashboard-data">
              <p className="total-price">Total Price: {dashboardData.total_price}</p>
              <p className="total-requests">Total Requests: {dashboardData.total_request}</p>
              <p className="success-rate">Success Rate: {dashboardData.success_rate}%</p>
          </div>
      ) : (
          <p className="loading">Loading...</p>
      )}
  </div>
  );
};

export default Dashboard;
