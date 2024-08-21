import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faMessage, faFileDownload } from '@fortawesome/free-solid-svg-icons';
import { useState, useEffect } from 'react';
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';

const PaymentMessageBubble = ({ order_id, setMessages }) => {
  const handlePayment = () => {
    var options = {
      "key": import.meta.env.VITE_RAZORPAY, 
      "amount": "50000",
      "name": "Mueseum", 
      "description": "Test Transaction",
      "order_id": order_id,
      "handler": async function (response) {
        try {
          const res = await axios.post(import.meta.env.VITE_BACKEND_URL + '/validate', {
            "payment_id": response.razorpay_payment_id,
            "order_id": response.razorpay_order_id,
            "razor_signature": response.razorpay_signature
          });
          if (res.status === 200) {
            console.log(res.data);
            setMessages((prevMessages) => [
              ...prevMessages,
              {
                user: 'bot',
                type: 'content',
                pdf: res.data.pdf,
                message: res.data.message,
              },
            ]);
          } else {
            setMessages((prevMessages) => [
              ...prevMessages,
              {
                user: 'bot',
                type: 'message',
                message: 'Validation failed'
              },
            ]);
          }
        } catch (e) {
          setMessages((prevMessages) => [
            ...prevMessages,
            {
              user: 'bot',
              type: 'message',
              message: 'Some error has occurred'
            },
          ]);
      }
    },
      "prefill": { 
        "name": "Gaurav Kumar", 
        "email": "gaurav.kumar@example.com",
        "contact": "9000090000" 
      },
      "notes": {
        "address": "Razorpay Corporate Office"
      },
      "theme": {
        "color": "#3399cc"
      }
    };
    var rzp1 = new Razorpay(options);
    rzp1.on('payment.failed', function (response) {
      setMessages((prevMessages) => [
        ...prevMessages,
        {
          user: 'bot',
          type: 'message',
          message: 'Some error has occurred'
        },
      ]);
    });
    rzp1.open();
  };

  return (
    <button onClick={handlePayment} className="mr-auto ml-2 h-[4vh] text-left rounded-lg p-2 flex flex-row items-center justify-start bg-blue-300 hover:bg-gray-400">
      Pay
    </button>
  );
}

const BotMessageBubble = ({ message }) => {
  return (
    <>
      <div className="m-2 rounded-lg inline-block ml-2 mb-4 sm:max-w-[15vw] max-w-[60vw] p-2 bg-blue-300 mr-auto">
        <div className="font-bold">Ticket Bot</div>
        {message}
      </div>
    </>
  )
}
 
const UserMessageBubble = ({ message }) => {
  return (
    <div className="p-2 inline-block rounded-lg mr-5 ml-auto mb-4 sm:max-w-[15vw] max-w-[60vw] bg-green-200 text-right">
      <div className="font-bold">User</div>
      {message}
    </div>
  );
};

const DownloadTicket = ({ pdfBase64 }) => {
  const handleDownload = () => {
    const byteCharacters = atob(pdfBase64);
    const byteNumbers = new Array(byteCharacters.length).fill().map((_, i) => byteCharacters.charCodeAt(i));
    const byteArray = new Uint8Array(byteNumbers);
    const blob = new Blob([byteArray], { type: 'application/pdf' });

    const blobUrl = URL.createObjectURL(blob);

    const link = document.createElement('a');
    link.href = blobUrl;
    link.download = 'ticket.pdf';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <button onClick={handleDownload} className="mr-auto ml-2 h-[4vh] text-left rounded-lg p-2 flex flex-row items-center justify-start bg-blue-300 hover:bg-gray-400">
      <div className='text-base mr-2 font-light'>Ticket.pdf</div>
      <FontAwesomeIcon icon={faFileDownload} color="black" />
    </button>
  );
};

function App() {
  const [visible, setVisible] = useState(false);
  const [messages, setMessages] = useState([]);
  const [userId, setUserId] = useState('');

  useEffect(() => {
    const generatedUserId = uuidv4();
    setUserId(generatedUserId);
  }, []);

  const handleKeyDown = async (event) => {
    if (event.key === 'Enter') {
      const newMessage = event.target.value;
      if (newMessage.trim() !== '') {
        setMessages((prevMessages) => [
          ...prevMessages,
          {
            user: 'user',
            type: 'message',
            message: newMessage,
          },
        ]);
        try {
          const response = await axios.post(import.meta.env.VITE_BACKEND_URL + '/chatbot', {
            message: newMessage,
            user_id: userId,
          });
          if (response.status === 200) {
            console.log(response.data)
          if (response.data.type == 'order_id') {
              setMessages((prevMessages) => [
                ...prevMessages,
                {
                  user: 'bot',
                  type: 'order_id',
                  message: response.data.message,
                },
              ]);
            } else {
              setMessages((prevMessages) => [
                ...prevMessages,
                {
                  user: 'bot',
                  type: 'message',
                  message: response.data.message
                }
              ])
            }
            event.target.value = '';
          }
        } catch (e) {
          setMessages((prevMessages) => [
            ...prevMessages,
            {
              user: 'bot',
              type: 'message',
              message: 'Some Error has occurred',
            },
          ]);
          event.target.value = '';
          console.log(e);
        }
      }
    }
  };

  console.log(messages)

  return (
    <>
      <button
        className="absolute right-2 bottom-4 m-2 bg-blue-400 rounded-lg border-0 w-14 h-14 flex flex-row justify-center items-center"
        onClick={() => setVisible((prevVisible) => !prevVisible)}
      >
        <FontAwesomeIcon icon={faMessage} color="white" />
      </button>
      {visible ? (
        <div className="absolute bg-red-100 sm:right-[2vw] sm:bottom-[10vh] h-[50vh] w-[40vh] rounded-lg bottom-[15vh] right-4">
          <div className="h-[6vh] bg-blue-400 rounded-t-lg flex flex-row items-center justify-center">
            <div className='text-black text-2xl font-bold'>ChatBot</div>
          </div>
          <div className="h-[44vh] flex-grow rounded-b-lg grid scroll-auto">
            <div className="overflow-auto h-[38vh] flex flex-col p-2">
              {messages.length >= 1 && (
                messages.map((item, index) => {
                  if (item.user === "user") {
                    return <UserMessageBubble message={item.message} key={index} />;
                  } else if (item.type === "content") {
                    return (<>
                      <BotMessageBubble message={item.message} key={index} />
                      <DownloadTicket pdfBase64={item.pdf} key={index} />
                    </>);
                  } else if (item.type === 'order_id') {
                    return (<>
                      <PaymentMessageBubble order_id={item.message} setMessages={setMessages} />
                    </>)
                  } else {
                    return <BotMessageBubble message={item.message} key={index} />;
                  }
                })
              )}
            </div>
            <input type="text" placeholder="Enter your message" className="p-2 rounded-lg h-[4vh] mx-2" onKeyDown={handleKeyDown} />
          </div>
        </div>
      ) : (
        <></>
      )
      }
    </>
  );
}



export default App;
