/* eslint-disable @typescript-eslint/no-explicit-any */
import React, { useEffect, useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import "../styles/Services.css"; // Import CSS file for styling

const Services: React.FC = () => {
  const navigate = useNavigate();
  const [subscribedServices, setSubscribedServices] = useState<any[]>([]);
  const [subscriptionDetails, setSubscriptionDetails] = useState<any[]>([]);
  const [nonSubscribedServices, setNonSubscribedServices] = useState<any[]>([]);
  const [pendingSubscribedServices, setPendingSubscribedServices] = useState<any[]>([]);
  const [selectedService, setSelectedService] = useState<string>(""); // State to store selected service name
  const [selectedPlan, setSelectedPlan] = useState<string>("Monthly"); // State to store selected plan (default to monthly)
  const [submitting, setSubmitting] = useState<boolean>(false); // State to track form submission status
  const [submitError, setSubmitError] = useState<string>(""); // State to hold submission error messages

  const fetchData1 = async () => {
    try {
      const accessToken = localStorage.getItem("access_token");

      if (!accessToken) { 
        navigate("/auth"); // Navigate to /auth if no access token is found
        return;
      }

      const response = await axios.post(
        "http://127.0.0.1:8000/ai_service/user_check/services/",
        {
          headers: {
            // Include the token in the Authorization header
            Authorization: `Bearer ${accessToken}`,
            "Content-Type": "application/json",
          },
        }
      );

      const responseData = response.data;

      if ("error" in responseData) {
        localStorage.removeItem("access_token");
        navigate("/auth"); // Navigate to /auth if there's an error response
      } else {
        setSubscribedServices(responseData.subscribed_services);
        setSubscriptionDetails(responseData.subscription_details);
        setNonSubscribedServices(responseData.non_subscribed_services);
        setPendingSubscribedServices(responseData.pending_services)
      }
    } catch (error) {
      console.error("Error:", error);
    }
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        const accessToken = localStorage.getItem("access_token");

        if (!accessToken) {
          navigate("/auth"); // Navigate to /auth if no access token is found
          return;
        }

        const response = await axios.post(
          "http://127.0.0.1:8000/ai_service/user_check/services/",
          {
            headers: {
              // Include the token in the Authorization header
              Authorization: `Bearer ${accessToken}`,
              "Content-Type": "application/json",
            },
          }
        );

        const responseData = response.data;

        if ("error" in responseData) {
          localStorage.removeItem("access_token");
          navigate("/auth"); // Navigate to /auth if there's an error response
        } else {
          setSubscribedServices(responseData.subscribed_services);
          setSubscriptionDetails(responseData.subscription_details);
          setNonSubscribedServices(responseData.non_subscribed_services);
          setPendingSubscribedServices(responseData.pending_services);
        }
      } catch (error) {
        console.error("Error:", error);
      }
    };

    fetchData();
  }, [navigate]);

  const handleDeleteService = async (serviceName: string) => {
    try {
      const accessToken = localStorage.getItem("access_token");

      if (!accessToken) {
        navigate("/auth"); // Navigate to /auth if no access token is found
        return;
      }

      const response = await axios.post(
        "http://127.0.0.1:8000/ai_service/user_delete_service/",
        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
            "Content-Type": "application/json",
            "serviceName" : serviceName,
          },
        }
      );

      if ("error" in response.data) {
        localStorage.removeItem("access_token");
        navigate("/auth"); // Navigate to /auth if there's an error response
      // Refresh data after deletion
      } else {
        fetchData1()
      }
    } catch (error) {
      console.error("Error deleting service:", error);
    }
  };

  const handleSubmit = async () => {
    try {
      setSubmitting(true);
      setSubmitError("");
  
      const accessToken = localStorage.getItem("access_token");
  
      if (!accessToken) {
        navigate("/auth");
        return;
      }
  
      const response = await axios.post(
        "http://127.0.0.1:8000/ai_service/user_subscribe/",

        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
            "Content-Type": "application/json",
            serviceName: selectedService,
            subscriptionType: selectedPlan,
          },
        }
      );
  
      if ("error" in response.data) {
        setSubmitError(response.data.error);
      } else {
        // Refresh data after successful subscription
        setSelectedService("")
        fetchData1()
      }
    } catch (error) {
      console.error("Error subscribing to service:", error);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="service-request-container">
      <h2>Subscribed Services</h2>
      <table className="services-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Description</th>
            <th>Monthly Price</th>
            <th>Yearly Price</th>
            <th>Enterprise Price Per Request</th>
            <th>Date Subscribed</th>
            <th>Date Ended</th>
            <th>Active</th>
            <th>Type</th>
            <th>Actions</th> {/* New column for delete button */}

          </tr>
        </thead>
        <tbody>
          {subscribedServices.map((service) => (
            <tr key={service.id}>
              <td>{service.id}</td>
              <td>{service.name}</td>
              <td>{service.description}</td>
              <td>{service.monthly_price}</td>
              <td>{service.yearly_price}</td>
              <td>{service.enterprise_price_per_request}</td>
              {/* Assume subscription details are in the same order as services */}
              <td>
                {
                  subscriptionDetails[subscribedServices.indexOf(service)]
                    .date_subscribed
                }
              </td>
              <td>
                {
                  subscriptionDetails[subscribedServices.indexOf(service)]
                    .date_ended
                }
              </td>
              <td>
                {
                  subscriptionDetails[subscribedServices.indexOf(service)]
                    .active
                }
              </td>
              <td>
                {subscriptionDetails[subscribedServices.indexOf(service)].type}
              </td>
              <td>
                <button
                  onClick={() => handleDeleteService(service.name)}
                  className="delete-button"
                >
                  Delete
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <h2>Pending Subscription</h2>
      <table className="services-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Description</th>
            <th>Monthly Price</th>
            <th>Yearly Price</th>
            <th>Enterprise Price Per Request</th>
            <th>Active</th>
            <th>Type</th>

          </tr>
        </thead>
        <tbody>
          {pendingSubscribedServices.map((service) => (
            <tr key={service.id}>
              <td>{service.id}</td>
              <td>{service.name}</td>
              <td>{service.description}</td>
              <td>{service.monthly_price}</td>
              <td>{service.yearly_price}</td>
              <td>{service.enterprise_price_per_request}</td>
              <td>
                  {service.active}
              </td>
              <td>
                {service.type}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <h2>Non-subscribed Services</h2>
      <table className="services-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Description</th>
            <th>Monthly Price</th>
            <th>Yearly Price</th>
            <th>Enterprise Price Per Request</th>
            <th></th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {nonSubscribedServices.map((service) => (
            <tr key={service.id}>
              <td>{service.id}</td>
              <td>{service.name}</td>
              <td>{service.description}</td>
              <td>{service.monthly_price}</td>
              <td>{service.yearly_price}</td>
              <td>{service.enterprise_price_per_request}</td>
              <td>
            <select
              value={selectedPlan}
              onChange={(e) => setSelectedPlan(e.target.value)}
            >
              <option value="monthly">Monthly</option>
              <option value="yearly">Yearly</option>
              <option value="enterprise">Enterprise</option>
            </select>
          </td>
          <td>
            <button
              onClick={() => {
                setSelectedService(service.name);
                handleSubmit();
              }}
              disabled={submitting}
              className="subscribe-button"
            >
              {submitting ? "Subscribing..." : "Subscribe"}
            </button>
            {submitError && <p className="error-message">{submitError}</p>}
          </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default Services;
