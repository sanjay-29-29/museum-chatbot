import { Scanner } from '@yudiel/react-qr-scanner';
import axios from 'axios';
import { useRef, useState } from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';

const InPage = () => {
  const [success, setSuccess] = useState(false);
  const [failure, setFailure] = useState(false);
  const interval = useRef(null);

  const handleScanIn = async (result) => {
    const rawValue = result[0].rawValue;
    try {
      const response = await axios.post(import.meta.env.VITE_BACKEND_URL + '/qr/in', {
        'ticket_id': rawValue
      });
      console.log(response.data);
      if (response.status === 200) {
        setSuccess(true);
        if (interval.current) {
          clearInterval(interval.current);
        }
        interval.current = setInterval(() => {
          setSuccess(false);
          clearInterval(interval.current);
          interval.current = null;
        }, 1000);
      }
    } catch (e) {
      setFailure(true);
      if (interval.current) {
        clearInterval(interval.current);
      }
      interval.current = setInterval(() => {
        setFailure(false);
        clearInterval(interval.current);
        interval.current = null;
      }, 1000);
      console.log(e);
    }
  };

  return (
    <div className='flex flex-col h-screen items-center mx-auto'>
      <div className='h-[40vh]'>
        <Scanner onScan={handleScanIn} allowMultiple={true} scanDelay={1000} />
      </div>
      {success && (<div className='text-green-400 text-5xl font-bold'>Success</div>)}
      {failure && (<div className='text-red-800 text-5xl font-bold'>Failure</div>)}
    </div>
  );
};

const OutPage = () => {
  const [success, setSuccess] = useState(false);
  const [failure, setFailure] = useState(false);
  const interval = useRef(null);

  const handleScanOut = async (result) => {
    const rawValue = result[0].rawValue;
    try {
      const response = await axios.post(import.meta.env.VITE_BACKEND_URL + '/qr/out', {
        'ticket_id': rawValue
      });
      console.log(response.data);
      if (response.status === 200) {
        setSuccess(true);
        if (interval.current) {
          clearInterval(interval.current);
        }
        interval.current = setInterval(() => {
          setSuccess(false);
          clearInterval(interval.current);
          interval.current = null;
        }, 1000);
      }
    } catch (e) {
      setFailure(true);
      if (interval.current) {
        clearInterval(interval.current);
      }
      interval.current = setInterval(() => {
        setFailure(false);
        clearInterval(interval.current);
        interval.current = null;
      }, 1000);
      console.log(e);
    }
  };

  return (
    <div className='flex flex-col h-screen items-center mx-auto'>
      <div className='h-[40vh]'>
        <Scanner onScan={handleScanOut} allowMultiple={true} scanDelay={1000} />
      </div>
      {success && (<div className='text-green-400 text-5xl font-bold'>Success</div>)}
      {failure && (<div className='text-red-800 text-5xl font-bold'>Failure</div>)}
    </div>
  );
};

function App() {
  return (
    <Router>
      <div className='flex flex-col h-screen items-center mx-auto'>
        <div className='flex flex-col items-center justify-center'>
          <div className='flex flex-row space-x-4 m-2'>
            <Link to="/in">
              <button className='p-2 w-10 rounded-md text-white bg-gray-500'>
                In
              </button>
            </Link>
            <Link to="/out">
              <button className='p-2 w-10 rounded-md text-white bg-gray-500'>
                Out
              </button>
            </Link>
          </div>
        </div>
        <Routes>
          <Route path="/in" element={<InPage />} />
          <Route path="/out" element={<OutPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;