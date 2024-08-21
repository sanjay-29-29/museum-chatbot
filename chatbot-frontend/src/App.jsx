import "./App.css";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faMessage,
  faFileDownload,
  faPaperPlane,
} from "@fortawesome/free-solid-svg-icons";
import { useState, useEffect, useRef } from "react";
import axios from "axios";
import { v4 as uuidv4 } from "uuid";

const PaymentMessageBubble = ({ order_id, setMessages }) => {
  const handlePayment = () => {
    var options = {
      key: import.meta.env.VITE_RAZORPAY,
      amount: "50000",
      name: "Museum",
      description: "Test Transaction",
      order_id: order_id,
      handler: async function (response) {
        try {
          const res = await axios.post(
            import.meta.env.VITE_BACKEND_URL + "/validate",
            {
              payment_id: response.razorpay_payment_id,
              order_id: response.razorpay_order_id,
              razor_signature: response.razorpay_signature,
            }
          );
          if (res.status === 200) {
            setMessages((prevMessages) => [
              ...prevMessages,
              {
                user: "bot",
                type: "content",
                pdf: res.data.pdf,
                message: res.data.message,
              },
            ]);
          } else {
            setMessages((prevMessages) => [
              ...prevMessages,
              {
                user: "bot",
                type: "message",
                message: "Validation failed",
              },
            ]);
          }
        } catch (e) {
          setMessages((prevMessages) => [
            ...prevMessages,
            {
              user: "bot",
              type: "message",
              message: "Some error has occurred",
            },
          ]);
        }
      },
      prefill: {
        name: "Gaurav Kumar",
        email: "gaurav.kumar@example.com",
        contact: "9000090000",
      },
      notes: {
        address: "Razorpay Corporate Office",
      },
      theme: {
        color: "#3399cc",
      },
    };
    var rzp1 = new Razorpay(options);
    rzp1.on("payment.failed", function (response) {
      setMessages((prevMessages) => [
        ...prevMessages,
        {
          user: "bot",
          type: "message",
          message: "Some error has occurred",
        },
      ]);
    });
    rzp1.open();
  };

  return (
    <button
      onClick={handlePayment}
      className="mr-auto ml-2 text-left rounded-lg p-2 flex flex-row items-center justify-start bg-gradient-to-r from-purple-700 to-purple-900 hover:from-purple-800 hover:to-purple-900 text-white shadow-lg transition-colors duration-300 ease-in-out"
    >
      Payment
    </button>
  );
};

const BotMessageBubble = ({ message }) => {
  return (
    <div className="bg-[#334155] text-white m-2 rounded-t-3xl rounded-br-3xl p-3 shadow-lg max-w-[70%] bubble">
      <div className="font-semibold text-white">Assistant</div>
      <p>{message}</p>
    </div>
  );
};

const UserMessageBubble = ({ message }) => {
  return (
    <div className="bg-[#6b7280] text-white m-2 rounded-t-2xl rounded-bl-2xl p-3 shadow-lg max-w-[70%] ml-auto bubble">
      <div className="font-bold text-gray-700">You</div>
      <p>{message}</p>
    </div>
  );
};

const LoadingBubble = () => {
  return (
    <div className="bg-[#334155] text-white m-2 rounded-t-3xl rounded-br-3xl p-3 shadow-lg max-w-[70%] bubble">
      <div className="font-semibold text-white">Assistant</div>
      <p className="loading-bubble">Loading</p>
    </div>
  );
};

const DownloadTicket = ({ pdfBase64 }) => {
  const handleDownload = () => {
    const byteCharacters = atob(pdfBase64);
    const byteNumbers = new Array(byteCharacters.length)
      .fill()
      .map((_, i) => byteCharacters.charCodeAt(i));
    const byteArray = new Uint8Array(byteNumbers);
    const blob = new Blob([byteArray], { type: "application/pdf" });

    const blobUrl = URL.createObjectURL(blob);

    const link = document.createElement("a");
    link.href = blobUrl;
    link.download = "ticket.pdf";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <button
      onClick={handleDownload}
      className="mr-auto ml-2 text-left rounded-lg p-2 flex flex-row items-center justify-start bg-gradient-to-r from-teal-500 via-purple-600 to-blue-700 hover:opacity-90"
    >
      <div className="text-base mr-2 font-light">Ticket.pdf</div>
      <FontAwesomeIcon icon={faFileDownload} color="white" />
    </button>
  );
};

function App() {
  const [visible, setVisible] = useState(false);
  const [messages, setMessages] = useState([]);
  const [userId, setUserId] = useState("");
  const messageEndRef = useRef(null);

  useEffect(() => {
    const generatedUserId = uuidv4();
    setUserId(generatedUserId);
  }, []);

  useEffect(() => {
    if (messageEndRef.current) {
      messageEndRef.current.scrollIntoView({ behavior: "smooth" });
    } else {
      console.log("messageEndRef is not set");
    }
  }, [messages]);

  const handleKeyDown = async (event) => {
    if (event.key === "Enter") {
      await sendMessage(event);
    }
  };

  const handleClick = async (event) => {
    await sendMessage(event);
  };

  const sendMessage = async (event) => {
    const newMessage = event.target.value;
    if (newMessage.trim() !== "") {
      setMessages((prevMessages) => [
        ...prevMessages,
        {
          user: "user",
          type: "message",
          message: newMessage,
        },
        {
          user: "bot",
          type: "loading",
          message: "Loading",
        },
      ]);

      try {
        const response = await axios.post(
          import.meta.env.VITE_BACKEND_URL + "/chatbot",
          {
            message: newMessage,
            user_id: userId,
          }
        );
        if (response.status === 200) {
          setMessages((prevMessages) =>
            prevMessages.filter((msg) => msg.type !== "loading")
          );

          if (response.data.type === "order_id") {
            setMessages((prevMessages) => [
              ...prevMessages,
              {
                user: "bot",
                type: "order_id",
                message: response.data.message,
              },
            ]);
          } else {
            setMessages((prevMessages) => [
              ...prevMessages,
              {
                user: "bot",
                type: "message",
                message: response.data.message,
              },
            ]);
          }
          event.target.value = "";
        }
      } catch (e) {
        console.error(e);
        setMessages((prevMessages) => [
          ...prevMessages.filter((msg) => msg.type !== "loading"),
          {
            user: "bot",
            type: "message",
            message: "Some Error has occurred",
          },
        ]);
        event.target.value = "";
      }
    }
  };

  return (
    <>
      <button
        className="absolute right-2 bottom-4 m-2 bg-gradient-to-r from-gray-600 to-gray-700 hover:from-gray-500 hover:to-gray-600 rounded-full w-14 h-14 flex items-center justify-center shadow-lg"
        onClick={() => setVisible((prevVisible) => !prevVisible)}
      >
        <FontAwesomeIcon icon={faMessage} color="white" />
      </button>
      {visible && (
        <div className="absolute bg-gradient-to-b from-[#1a003a] to-black sm:right-[2vw] sm:bottom-[12vh] h-[80vh] w-[40vh] rounded-xl bottom-[11vh] right-4 shadow-2xl border border-gray-700">
          <div className="h-[8vh] bg-[#0f172a] rounded-t-xl flex items-center justify-center shadow-md">
            <div className="text-white text-2xl font-bold">Museo-Mate</div>
          </div>

          <div className="h-[72vh] flex-grow rounded-b-xl grid bg-white">
            <div className="overflow-y-auto h-[65vh] flex flex-col p-2 space-y-2">
              {messages.map((item, index) => {
                if (item.user === "user") {
                  return (
                    <UserMessageBubble message={item.message} key={index} />
                  );
                } else if (item.type === "content") {
                  return (
                    <div key={index}>
                      <BotMessageBubble message={item.message} />
                      <DownloadTicket pdfBase64={item.pdf} />
                    </div>
                  );
                } else if (item.type === "order_id") {
                  return (
                    <PaymentMessageBubble
                      order_id={item.message}
                      setMessages={setMessages}
                      key={index}
                    />
                  );
                } else if (item.type === "loading") {
                  return <LoadingBubble key={index} />;
                } else {
                  return (
                    <BotMessageBubble message={item.message} key={index} />
                  );
                }
              })}
              <div ref={messageEndRef}></div>
            </div>
            <div className="flex items-center p-2">
              <input
                type="text"
                placeholder="Enter your message"
                className="p-2 flex-grow rounded-lg border border-gray-600 bg-gray-700 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-black"
                onKeyDown={handleKeyDown}
              />
              <button
                onClick={handleClick}
                className="ml-2 rounded-lg w-10 h-10 flex items-center justify-center bg-[#94a3b8] hover:bg-[#3f3f46] text-[#d4d4d8] shadow-lg transition-colors duration-300 ease-in-out"
              >
                <FontAwesomeIcon icon={faPaperPlane} color="#d4d4d8" />
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

export default App;
