import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faMessage, faRobot } from '@fortawesome/free-solid-svg-icons';
import { useState } from 'react';
import axios from 'axios';

const BotMessageBubble = ({message}) => {
  return (
    <>
      <div className="m-2 rounded-lg inline-block ml-2 p-2">
        <div className="font-bold">Ticket Bot</div>
         {message}
      </div>
    </>
  )
}

const UserMessageBubble = ({message}) => {  
  return (
    <div className="m-2 p-2 inline-block rounded-lg mr-5 text-right">
        <div className="font-bold">User</div>
      {message}
    </div>
  );
};

function App() {
  const [visible, setVisible] = useState(false);
  const [messages, setMessages] = useState([]);

  const handleKeyDown = async (event) => {
    if (event.key === 'Enter') {
      const newMessage = event.target.value;
      if (newMessage.trim() !== '') {
        setMessages((prevMessages) => [
          ...prevMessages,
          {
            user: 'user',
            message: newMessage,
          },
        ]);
        try {
          const response = await axios.post(import.meta.env.VITE_BACKEND_URL + '/chatbot', {
            message: newMessage,
          });
          if (response.status === 200) {
            setMessages((prevMessages) => [
              ...prevMessages,
              {
                user: 'bot',
                message: response.data.message,
              },
            ]);
            event.target.value = '';
          }
        } catch (e) {
          setMessages((prevMessages) => [
            ...prevMessages,
            {
              user: 'bot',
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
        <div className="absolute sm:right-[2vw] sm:bottom-[10vh] h-[50vh] w-[40vh] rounded-lg bottom-[15vh] right-4 drop-shadow-2xl">
          <div className="h-[6vh] bg-blue-400 rounded-t-lg"></div>
          <div className="h-[44vh] border-2 flex-grow rounded-b-lg grid">
            <div className="overflow-auto h-[38vh] flex flex-col">
            {messages.length>=1 && (messages.map((item, index) => (item.user === "user" ? <UserMessageBubble message={item.message} key={index}/> : <BotMessageBubble message={item.message} key={index}/>)))}
            </div>
            <input type="text" placeholder="Enter your message" className="p-2 rounded-lg h-[4vh] mx-2" onKeyDown={handleKeyDown}/>
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
