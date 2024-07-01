import axios from "axios";


const response = await axios.post(
  "http://127.0.0.1:8000/ai_service/user_check/request/",
  {
    headers: {
      // Include the token in the Authorization header
      "Authorization": `Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzE4Nzk4MDE3LCJpYXQiOjE3MTg3OTYyMTcsImp0aSI6ImUwZWMzYzBiYjIwMzRkMTRhMGFkZGNkZjQ5NjVjMDdlIiwidXNlcl9pZCI6NH0.jJLLXjseEk8imDCB80l1a4PLI30OdC_R_WA2dSZqm2A`,
      'Content-Type': 'application/json',
    },
  }
);
console.log(response.data)
