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
import logo from './assets/keclogo.png'
import razor from './assets/razor.jpeg'

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
      onClick={handlePayment}>
      <img
        src={razor}
        className="sm:h-[5vh] rounded-md ml-2 border-2 hover:shadow-lg border-black sm:w-[8vw] h-[8vh]"
      />
    </button>
  );
};

const BotMessageBubble = ({ message }) => {
  return (
    <div>
      <div className="ml-5 font-medium text-black">Assistant</div>
      <pre className="bg-[#334155] text-white m-3 font-sans rounded-t-3xl rounded-br-3xl p-3 text-wrap shadow-lg max-w-[70%] bubble">
        <p>{message}</p>
      </pre>
    </div>
  );
};

const UserMessageBubble = ({ message }) => {
  return (
    <div className="max-w-[70%] ml-auto">
      <div className="m-2">User</div>
      <p className="bg-[#6b7280] text-white m-2 rounded-t-2xl rounded-bl-2xl p-3 shadow-lg bubble">{message}</p>
    </div>
  );
};

const LoadingBubble = () => {
  return (
    <div>
      <div className="ml-3 font-medium text-black">Assistant</div>
      <pre className="bg-[#334155] text-white m-3 font-sans rounded-t-3xl rounded-br-3xl p-3 text-wrap shadow-lg max-w-[70%] bubble">
        <p className="loading-bubble bubble">Loading</p>
      </pre>
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
      className="mr-auto ml-2 text-left rounded-lg p-2 flex flex-row items-center justify-start bg-[#334155] text-white" 
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
  const [input, setInput] = useState('');
  const [disableInput, setDisableInput] = useState(false);
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


  const sendMessage = async () => {
    if (input.trim() == "") {
      return;
    }
    setInput('')
    setMessages((prevMessages) => [
      ...prevMessages,
      {
        user: "user",
        type: "message",
        message: input,
      },
      {
        user: "bot",
        type: "loading",
        message: "Loading",
      },
    ]);

    try {
      setDisableInput(true);
      const response = await axios.post(
        import.meta.env.VITE_BACKEND_URL + "/chatbot",
        {
          message: input,
          user_id: userId,
        }
      );
      if (response.status === 200) {
        setMessages((prevMessages) =>[
          ...prevMessages.filter((msg) => msg.type !== "loading"),
          response.data
        ])
        setInput('');
        setDisableInput(false);
      }else{
        setMessages((prevMessages) => [
          ...prevMessages.filter((msg) => msg.type !== "loading"),
          {
            user: "bot",
            type: "message",
            message: "Some Error has occurred",
          },
        ]); 
        setDisableInput(false);
        setInput('')
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
      setInput('')
      setDisableInput(false);
    }
  };

  return (
    <><nav class="bg-white border-gray-200 dark:bg-gray-900 dark:border-gray-700">
        <div class="max-w-screen-xl flex flex-wrap items-center justify-between mx-auto p-4">
          <a href="#" class="flex items-center space-x-3 rtl:space-x-reverse">
            <img
              src="https://flowbite.com/docs/images/logo.svg"
              class="h-8"
              alt="Flowbite Logo"
            />
            <span class="self-center text-2xl font-semibold whitespace-nowrap dark:text-white">
              KEC Museum
            </span>
          </a>
          <button
            data-collapse-toggle="navbar-dropdown"
            type="button"
            class="inline-flex items-center p-2 w-10 h-10 justify-center text-sm text-gray-500 rounded-lg md:hidden hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-gray-200 dark:text-gray-400 dark:hover:bg-gray-700 dark:focus:ring-gray-600"
            aria-controls="navbar-dropdown"
            aria-expanded="false"
          >
            <span class="sr-only">Open main menu</span>
            <svg
              class="w-5 h-5"
              aria-hidden="true"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 17 14"
            >
              <path
                stroke="currentColor"
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M1 1h15M1 7h15M1 13h15"
              />
            </svg>
          </button>
          <div class="hidden w-full md:block md:w-auto" id="navbar-dropdown">
            <ul class="flex flex-col font-medium p-4 md:p-0 mt-4 border border-gray-100 rounded-lg bg-gray-50 md:space-x-8 rtl:space-x-reverse md:flex-row md:mt-0 md:border-0 md:bg-white dark:bg-gray-800 md:dark:bg-gray-900 dark:border-gray-700">
              <li>
                <a
                  href="#"
                  class="block py-2 px-3 text-white bg-blue-700 rounded md:bg-transparent md:text-blue-700 md:p-0 md:dark:text-blue-500 dark:bg-blue-600 md:dark:bg-transparent"
                  aria-current="page"
                >
                  Home
                </a>
              </li>

              <li>
                <a
                  href="#"
                  class="block py-2 px-3 text-gray-900 rounded hover:bg-gray-100 md:hover:bg-transparent md:border-0 md:hover:text-blue-700 md:p-0 dark:text-white md:dark:hover:text-blue-500 dark:hover:bg-gray-700 dark:hover:text-white md:dark:hover:bg-transparent"
                >
                  Ticket & Pricing
                </a>
              </li>
              <li>
                <a
                  href="#"
                  class="block py-2 px-3 text-gray-900 rounded hover:bg-gray-100 md:hover:bg-transparent md:border-0 md:hover:text-blue-700 md:p-0 dark:text-white md:dark:hover:text-blue-500 dark:hover:bg-gray-700 dark:hover:text-white md:dark:hover:bg-transparent"
                >
                  Art & Info
                </a>
              </li>
              <li>
                <a
                  href="#"
                  class="block py-2 px-3 text-gray-900 rounded hover:bg-gray-100 md:hover:bg-transparent md:border-0 md:hover:text-blue-700 md:p-0 dark:text-white md:dark:hover:text-blue-500 dark:hover:bg-gray-700 dark:hover:text-white md:dark:hover:bg-transparent"
                >
                  About
                </a>
              </li>
            </ul>
          </div>
        </div>
      </nav>

      <section class="bg-center bg-no-repeat bg-[url('https://images.alphacoders.com/133/1331567.png')] bg-gray-700 bg-blend-multiply">
        <div class="px-4 mx-auto max-w-screen-xl text-center py-24 lg:py-56">
          <img
            src={logo}
            alt="KEC Museum"
            class="mx-auto mt-4 mb-6 w-32 h-32 object-contain"
          />
          <h1 class="mb-7 text-4xl font-extrabold tracking-tight leading-none text-white md:text-5xl lg:text-6xl mt-24">
            Preserving the Past, Inspiring the Future
          </h1>
          <p class="mb-8 text-lg font-normal text-gray-300 lg:text-xl sm:px-16 lg:px-48">
            Celebrating human achievement and creativity, KEC Museum bridges
            history and innovation. Embark on a journey that inspires curiosity
            and a deeper understanding of our world
          </p>
          <div class="flex flex-col space-y-4 sm:flex-row sm:justify-center sm:space-y-0">
            <a
              href="#"
              class="inline-flex justify-center items-center py-3 px-5 text-base font-medium text-center text-white rounded-lg bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 dark:focus:ring-blue-900"
            >
              Get started
              <svg
                class="w-3.5 h-3.5 ms-2 rtl:rotate-180"
                aria-hidden="true"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 14 10"
              >
                <path
                  stroke="currentColor"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M1 5h12m0 0L9 1m4 4L9 9"
                />
              </svg>
            </a>
            <a
              href="#"
              class="inline-flex justify-center hover:text-gray-900 items-center py-3 px-5 sm:ms-4 text-base font-medium text-center text-white rounded-lg border border-white hover:bg-gray-100 focus:ring-4 focus:ring-gray-400"
            >
              Learn more
            </a>
          </div>
        </div>
      </section>
      <div class="bg-gray-900 text-white py-6">
        <div class="max-w-screen-xl mx-auto px-4">
          <h2 class="text-2xl font-bold mb-4">About KEC Museum</h2>
          <p class="text-lg">
            Welcome to KEC Museum, where history meets innovation! Explore our
            diverse exhibits that showcase art, science, and technology from
            around the world. Our interactive displays provide a unique
            experience, making learning both fun and engaging for visitors of
            all ages.
          </p>
          <p class="mt-4">
            Step into the past with our ancient artifact collection or journey
            into the future with cutting-edge tech exhibits. The KEC Museum is a
            place of wonder, curiosity, and inspiration. Join us for guided
            tours, special workshops, and exclusive events that bring stories to
            life.
          </p>
          <p class="mt-4">
            Step into the past with our ancient artifact collection or journey
            into the future with cutting-edge tech exhibits. The KEC Museum is a
            place of wonder, curiosity, and inspiration. Join us for guided
            tours, special workshops, and exclusive events that bring stories to
            life.
          </p>
          <p class="mt-8 text-xl font-bold mb-4">
            Visit KEC Museum today and discover a world of knowledge and
            imagination!
          </p>
        </div>
      </div>
      <button
        className="fixed right-2 bottom-4 m-2 bg-gradient-to-r from-gray-600 to-gray-700 hover:from-gray-500 hover:to-gray-600 rounded-full w-14 h-14 flex items-center justify-center shadow-lg"
        onClick={() => setVisible((prevVisible) => !prevVisible)}
      >
        <FontAwesomeIcon icon={faMessage} color="white" />
      </button>
      {visible && (
        <div className="fixed bg-gradient-to-b from-[#1a003a] to-black sm:right-[2vw] sm:bottom-[12vh] h-[80vh] sm:w-[30vw] w-[90vw] rounded-xl bottom-[11vh] right-4 shadow-2xl border border-gray-700">
          <div className="h-[8vh] bg-[#0f172a] rounded-t-xl flex items-center justify-center shadow-md">
            <div className="text-white text-2xl font-bold">Museum Chatbot</div>
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
            <form onSubmit={sendMessage} className="flex flex-row items-center p-2">
              <input
                onChange={(e)=>{setInput(e.target.value)}}
                type="text"
                disabled = {disableInput}
                value={input}
                placeholder="Enter your message"
                className="p-2 flex-grow rounded-lg border border-gray-600 bg-gray-700 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-black"
              />
              <button
                type = 'submit'
                onClick={sendMessage}
                disabled={disableInput}
                className="ml-2 rounded-lg w-10 h-10 flex items-center justify-center hover:bg-[#94a3b8] bg-[#3f3f46] text-[#d4d4d8] shadow-lg transition-colors duration-300 ease-in-out">
                <FontAwesomeIcon icon={faPaperPlane} color="#d4d4d8" />
              </button>
            </form> 
          </div>
        </div>
      )}
    </>
  );
}

export default App;
