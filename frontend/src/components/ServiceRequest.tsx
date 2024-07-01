import React, { useEffect, useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

const ServiceRequest: React.FC = () => {
  const navigate = useNavigate();
  const [services, setServices] = useState<any[]>([]); //list of approved services
  const [selectedService, setSelectedService] = useState<string>("");
  const [predictedImage, setPredictedImage] = useState<string>("")
  const [base64String, setBase64String] = useState<string>("");

  useEffect(() => {
    const fetchData = async () => {
      try {
        const accessToken = localStorage.getItem("access_token");

        if (!accessToken) {
          navigate("/auth");
          return;
        }

        const response = await axios.post(
          "http://127.0.0.1:8000/ai_service/user_check/request/",
          {
            headers: {
              Authorization: `Bearer ${accessToken}`,
              "Content-Type": "application/json",
            },
          }
        );

        const responseData = response.data;

        if ("approved_services" in responseData) {
          setServices(responseData.approved_services);
          setSelectedService(responseData.approved_services[0].name); // Default to the first service
        } else if ("error" in responseData) {
          localStorage.removeItem("access_token");
          navigate("/auth");
        }
      } catch (error) {
        console.error("Error:", error);
      }
    };

    fetchData();
  }, [navigate]);

  const convertToBase64 = (file: File) => {
    const reader = new FileReader();
    reader.onload = () => {
      const base64 = reader.result as string;
      setBase64String(base64.split(",")[1]); // Extract base64 string without 'data:image/jpeg;base64,' prefix
    };
    reader.readAsDataURL(file);
  };
  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      convertToBase64(file);
    }
  };


  const handleSubmit = async () => {
    try {
      const accessToken = localStorage.getItem("access_token");
      if (!accessToken) {
        navigate("/auth");
        return;
      }
      const response = await axios.post(
        `http://127.0.0.1:8000/ai_service/user_ai_service_${selectedService}/`,
        {
          headers: {
            image_base64 : base64String,
            Authorization: `Bearer ${accessToken}`,
            "Content-Type": "application/json",
            service : selectedService,

          },
        }
      );
      if (response.data.status === "success") {
        setPredictedImage(response.data.image); // Update state with returned image
      }
    } catch (error) {
      console.error("Error processing image:", error);
    }
  };

  return (
    <div className="container mt-5">
      <h2 className="mb-4">Select Service and Submit Base64 Image</h2>
      <input
        required
        type="file"
        accept=".jpg,.jpeg"
        className="form-control mb-3"
        onChange={handleFileChange}
      />
      <select
        value={selectedService}
        onChange={(e) => setSelectedService(e.target.value)}
        className="form-select mb-3"
      >
        {services.map(service => (
          <option  value={service.name}>
            {service.name}
          </option>
        ))}
      </select>
      <button onClick={handleSubmit} className="btn btn-primary">
        Submit
      </button>
      {predictedImage && (
        <div className="mt-4">
          <h3>Predicted Image</h3>
          <img src={`data:image/jpeg;base64,${predictedImage}`} alt="Predicted" className="img-fluid" />
        </div>
      )}
    </div>
  );
};

export default ServiceRequest;
