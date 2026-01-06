import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import FloatingChatbot from './components/FloatingChatbot';

const WEBSOCKET_URL = 'ws://localhost:8000/ws';

function App() {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [sessionId] = useState(() => Math.random().toString(36).substr(2, 9));
  const [showUpload, setShowUpload] = useState(false);
  const [showMainChat, setShowMainChat] = useState(false);
  
  const websocket = useRef(null);
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    connectWebSocket();
    return () => {
      if (websocket.current) {
        websocket.current.close();
      }
    };
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const connectWebSocket = () => {
    websocket.current = new WebSocket(`${WEBSOCKET_URL}/${sessionId}`);
    
    websocket.current.onopen = () => {
      setIsConnected(true);
      console.log('Connected to chatbot');
    };
    
    websocket.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setIsTyping(false);
      
      setMessages(prev => [...prev, {
        id: Date.now(),
        content: data.content,
        sender: 'bot',
        timestamp: data.timestamp,
        metadata: {
          ...data.metadata || {},
          suggestions: data.suggestions || []
        }
      }]);
      
      // Check if salary slip upload is required
      if (data.metadata?.salary_required) {
        setShowUpload(true);
      }
    };
    
    websocket.current.onclose = () => {
      setIsConnected(false);
      console.log('Disconnected from chatbot');
    };
    
    websocket.current.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  };

  const sendMessage = (messageText = null) => {
    const textToSend = messageText || inputMessage.trim();
    
    if (textToSend && websocket.current && isConnected) {
      const message = {
        content: textToSend,
        sender: 'user',
        timestamp: new Date().toISOString()
      };
      
      // Add to local messages
      setMessages(prev => [...prev, { ...message, id: Date.now() }]);
      
      // Send to server
      websocket.current.send(JSON.stringify(message));
      
      setInputMessage('');
      setIsTyping(true);
    }
  };

  const handleSuggestionClick = (suggestion) => {
    sendMessage(suggestion);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`http://localhost:8000/upload-salary-slip/${sessionId}`, {
        method: 'POST',
        body: formData
      });
      
      const result = await response.json();
      
      // Add upload confirmation message
      setMessages(prev => [...prev, {
        id: Date.now(),
        content: `📎 Salary slip uploaded: ${file.name}`,
        sender: 'user',
        timestamp: new Date().toISOString()
      }]);
      
      // Add bot response
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        content: result.message,
        sender: 'bot',
        timestamp: new Date().toISOString()
      }]);
      
      setShowUpload(false);
      
    } catch (error) {
      console.error('Upload error:', error);
      alert('Failed to upload file. Please try again.');
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleOpenChat = () => {
    setShowMainChat(true);
    // Start the conversation when chat is opened
    if (messages.length === 0) {
      // Auto-start conversation
      setTimeout(() => {
        if (websocket.current && isConnected) {
          const welcomeMessage = {
            content: "start",
            sender: 'user',
            timestamp: new Date().toISOString()
          };
          websocket.current.send(JSON.stringify(welcomeMessage));
          setIsTyping(true);
        }
      }, 500);
    }
  };

  const formatMessage = (content) => {
    // Convert markdown-like formatting to HTML
    return content
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/✅/g, '<span class="checkmark">✅</span>')
      .replace(/❌/g, '<span class="cross">❌</span>')
      .replace(/🎉/g, '<span class="celebration">🎉</span>')
      .replace(/💰/g, '<span class="money">💰</span>')
      .replace(/📱/g, '<span class="phone">📱</span>')
      .replace(/🏦/g, '<span class="bank">🏦</span>');
  };

  return (
    <div className="App">
      {!showMainChat ? (
        // Show only the floating chatbot when main chat is not open
        <div className="landing-page">
          <div className="landing-content">
            <div className="tata-capital-header">
              <img src="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEAAkGBwgHBgkIBwgKCgkLDRYPDQwMDRsUFRAWIB0iIiAdHx8kKDQsJCYxJx8fLT0tMTU3Ojo6Iys/RD84QzQ5OjcBCgoKDQwNGg8PGjclHyU3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3N//AABEIAI4A/wMBIgACEQEDEQH/xAAcAAEAAwEBAQEBAAAAAAAAAAAABAUGBwMCAQj/xABLEAABAwMBBAYFCAcFBgcAAAABAAIDBAURBhITIZEHFTFRUoEiQVRhcRQyNnJ0obGyFzVCU4KTwmJzkqKzFiQzlNHwIyYnNDdDRP/EABoBAQADAQEBAAAAAAAAAAAAAAABAgQDBQb/xAAvEQABAwEECgIDAQADAAAAAAABAAIDEQQSITETFBZBUlNhkaHhUXEiMsHwBSMk/9oADAMBAAIRAxEAPwDuKIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiLH/AKSdOfvan+QVY2LV9pv1a6kt75nStjMhD4i0bIIHb/EF1dBK0VLSuQnjcaBwV+ip9QaktunxB1lI9pn2tgMYXE4xn8Qqf9JGnf3tT/IKNhkcKtaSFLpo2mhcFsEXhQ1cNdRwVdM7ahnYHsOMZBGVna7X1ioayekqJKgSwyGN+ISRkHB4qrY3uNGiql0jGiritSix/wCknTn72p/kFP0k6c/e1P8AIKvq03CeyprEPEO62CLP2PWFovlb8jt75nTbsyYfEWjAIB4+YUrUGobdp+KGS5SPaJnFrAxhcTjtOO7s5hUMTw67TFXEjC29XBWyLH/pJ05+9qf5BWnt1bBcaGCspHbUMzA9hIwce/3qXxPYKuFEZKx+DTVSURFzV0RFn7zrKx2eV0FTV7yob86GBpe4HuOOAPxIVmsc80aKqrnNaKuNFoEWIj6T7G5+y+nuEY8TomEfc4la+grILhRQ1lI8vgmaHscWluR8DxVnxPj/AGFFVkrH/qaqQirb9fKKw0bKq4ue2N8gjbsN2iXEE9nwBUOwattV/qpKa3vl3rI94WyR7OW5A4cxzUCN5beAwUmRgddrir5EWavOuLNZ6+WhqnVDqiLG22OIkDIBHHs7CFDGOeaNFVLntYKuNFpUWOi6StPvcBJ8riHifDkf5SStRb6+kuVK2poKiOeF3Y9hz5e4+5WfE9n7CihsrH/qaqSiz101labXdTbat04qAWj0Y8j0sY4+a+r9q+1WGtbSXB0wldGJRu49obJJH9JQRSGlAcVBlYK1OSv0WO/STp7xVX8gp+knT3iqv5BVtXm4T2VdYi4gtiij0NZFX0MFZBnczxtkYXDB2SMhZj9I+ndvZ3tRjONvcnZ+Oe5UbE91borRXdIxtKla9EByqy/32i0/SR1VwMgiklETdhm0dogn8GlVa0uNArFwaKlcMtFnuN5mkitdMaiSNu05oe1uB3+kQt70c6avNnv8tVc6EwQupHxhxlY7Li5hAw1xPYCoPQ9+t6/7M38y6Fqe6CzWGsr8jbjjxED63ng37yF6lrtD75hAzXmWWBlwTE5LkvSHdetNUVAY7MFL/u8fHhlvzj/iJHkFmkOTxLiT2kk5JV7ftPyWqz2auc1wNbCXS5/Zfnab8DsuA/hK3tuxBrFidekLnrddEt1+UWmotkh9OkftR/Ufx+521zCzN/0bqKqvtwqKe2OfDLUyPjfv4hlpcSDguyqzQ11Fn1NSTvOIZTuJT/Zfjj5O2T8Au6rzZ3us0xc0fsvQha20Qhrjkv5zrKSooaqWkrI91PEdl7NoHZPxHBe1qtNfeKl1PbKczzNYXloe1uGggZ9IgdpCn63+l11/v/6Qrvoj+ktT9if+di3vlLYNJvpVYmRB02j3VVj0eaYvVo1C6quVAYIDTPZtmVjvSJbgYa4n1FUPSTdestTSxMdmGiG4bg8NrteefD+FdY1Fc22ay1lwdgmGMlgP7TzwaPMkBfz89znvc+V5c9ztpzj2uJ7TzWWyF00hmcMsFotQbDGIm/a/F1Loiuu9oaq1SO9KndvYgfA7tA+DuP8AEsTeLBJbtPWa5kEfLWuMnuJO1HzZ+C+NH3XqbUVHVudiIu3U3H9h3A5+HA+S0TtE8Ju/6i4wuMMor/qrvaIi8Be4sX0mailtFtioqKQx1VZtDeNODGwdpHcTkAefcqHQuhKe40LLneg90UvGGna4ty3xOI48fUB6u/PCD0ulx1NC0ngKFmyPV8+RdSsYjFlt4hxuhTR7GOzGyML0HOMNmbczdvWBrRNaHXsmqtm0VpuWLdutMLRjGYy5ruYOVdUdNFRUkNLTt2YYY2xsHc0DAXsvwkAEk4A7SsLnucKE1W0Ma3EBcr6WK2StvNBaKc5dG0HHfJIcNHkAP8SrqVv+yXSKyFpIp2ziM5PbFIBjyG0D/CvK03ShuGvnXi6VDIaQTOna6TOHBoxGPj80/wAKk9JtZabrW0lba62Kd5iMUwZnIAOWn/M77l7DGlt2EjAjH7K8l7g69MDiDh9BdiXFtXsbL0kTRSNDo5KunY5p9YLYwQup6VuXW+nqGtJy98QEn128HfeCuUa3mNP0gVk7W7Top4JA3xEMjOPuWWwtIlc3fQrTbXAxNO6oXSLjoewVlK+GOgjpnkehLANlzT6j3H4FYboprJ6bUktDtgxTxO3jAcjbbjDh948171uv79dYHUltthhkkGyXwtfJIAfDgcD7+KuejbSNTaHyXO5sEVQ+PdwwZBLG5BJdjhk4HD1D44FqOiheJjnkK1VatkmaYhlmclmdfj/z6T/ag/Bq6XeNLWa9VTaq50ZmmbGIw4TPZ6IJIGGuA7SVzTX/ANPT9eD8GrsipaHObHGWmmC6QNa58gI3rjHSRZLfY7hSxWuAwskhLnAyOfk57fSJW3tmhdN1FtpZpbcXSSQse4/KZRkkAn9pZnpi/WtD9md+ZdJsv6nofs0f5QpmleIIyHGuKrFEwzvBApgqnVdRFp7RtQyjG6bHAKanGSS3PojBPE4HHyXJH2dw0nHeNl2HVroPdsbIwf8AEHBbDphuWZaC2NdnYBqZG+85az+tSJq7Th0H1E260xnbTcO3BmHp57PW9dLOXRRNcBW8cfpc5w2SRzSch5Wn0NcutNL0UznbUsbNzJ37TOGT8Rg+apOmD6O0X29v+nIqnoeuWzUV1rcQBI0VEY94w133FnIq26YPo7Rfb2/6ci5CPR2wDquukv2WvRUXQ9+t6/7M38ykdL912pqO0xu4MHyib4nIaPzHzC2OntJ27T1RLPQOnL5WbDt68OGM57lEuuhLTdbhPXVclWZpiC7ZlAHAAADh3AKdYiNp0pyTQSCz6MZrklgtxu96o6AfNmlAf9QcXf5QV1/pBtYuOlaprGf+JSgTxADs2e3H8O0PNfVi0ZarFX/LaPfum2Cwb14IAOMkcO3h95Wic0OaWuAIIwQfWq2i1B8jXMyCmCzXI3NdvX82YBGDxBXeNGXY3rTlJVvdmYN3c3128CfPt81TjozsA4B1YB/fD/or3TunaPT0M0NA+cxzOD3NleHYOMZHDuxyCva7RFMwUzCrZbPLE7HIrj2t/pddf7/+kK76I/pLU/Yn/nYtnc9BWa53CeuqXVQmndtP2JQBnGOHD3KVp/SFssFa+roHVBlfGYzvHgjBIPd7grPtcZguDOiqyyyCa/uqsr0vXX0aO0RO7T8omAPq4hg57R8gsBaaB90ulJQR5zUStYSO0N/aPkMnyXYrvoa1Xi4y19ZJVmaXGdmUAAAYAAxwC+7Jom0WW4NrqT5Q6ZjS1u9eHAZ4E9nbjh5pFa44obrc/wCpLZZJJbxy/i+9bWltw0nV0sMeHQxiSFrfUWccD4gEea4X85vxC/pVY13RpYC4kGraCchrZRge4cFSx2psTS16varM6UgtVjoO7db6apZXv2p4RuJjnjtN9Z95GD5rQqm07pui062dlA+oLJiC5srw4Aj1jh/3gK5WOUtLyW5LXGHBgDs1g+lSwzV9FBc6NhkkpA4SsaMkxnjkfA/cT3Kr0LrulobfFbLy5zGRDEFSGlzdn1NcBxGPUezHbjGT1BZe76CsN0ldNuH0srzlz6Zwbk/VILfuWiKdhj0Uow3FZ5IXiTSRZ71Kl1npyKPeOu9M4YzhhL3cgMqNrS9R0+jJ6ylf/wC8ibHA7sJ3g7fJpJ8lWw9F9lZIHSVVfKB+y57ADyblXdz0nbblbaK3SmdlLRgCJkcncMDJOc4Gear/AOdr2kEn5Vv+9zSCAPhYLo80jQ32gqqu5skMbZRHCGPLOwZceHb2geRVtqvQVqodP1lZbY5m1NOzejblLhsg5dw+rlbey2qmstujoaIO3MZcQXnJJJJOT5qZIxssbo5GhzHAhwPrBUvtkhlvAmlclVlkYI7pAquddD9xLoa+2PPFjhPGCfUeDh5EN/xKg1T/APJr/ttN+WNdBsOirXYa9tbQSVW9DCzD5AQQfUeHuB8l+12i7VXXo3eZ1SKkyMk9GQBuW4xwx/ZC6i0RCZzxkQuZs8hhaw5grSIiLz1vXG9f/T0/Wg/Bq7Is5dtF2q63Y3OqdU/KCWn0JAG+jjHDHuWjWmeVr2MA3BZ4Y3Me8neVynpi/WtD9md+ZdJsv6nofs0f5Qq7UWk7bqGoinrzOHxM2G7p+yMZz3K3jpmxUbaWNz2sZGI2uB9IADGfikkrXRMYMwkcTmyvecjRccqWjVvSG6PLnU8tSY8t4YijHHB9WQ0+blu/0cacx/waj/mHKbp/RlqsFaauh37pd2YxvX7QAJHZw9y0SvNajUCIkABUiswoTIASSuJQD/ZHXzWFzhDT1WyST/8AS8dp78Ndn4hbLpg+jtF9vb/pyK4v+jLTf675ZXb8S7sRndSbIIGe3h28VLvOnaO82ynoK587ooHNe1zXgOJDS3JOOPAlXNpY57HnMZqrbO9rHsGRyVtvGeNvNN4zxt5rH4HcEwO4L4jaJ3L8+l6mh6rYbxnjbzTeM8beax+B3BMDuCbRO5fn0mh6rYbxnjbzTeM8beax+B3BMDuCbRO5fn0mh6rYbxnjbzTeM8beax+B3BMDuCbRO5fn0mh6rYbxnjbzTeM8beax+B3BMDuCbRO5fn0mh6rYbxnjbzTeM8beax+B3BMDuCbRO5fn0mh6rYbxnjbzTeM8beax+B3BMDuCbRO5fn0mh6rYbxnjbzTeM8beax+B3BMDuCbRO5fn0mh6rYbxnjbzTeM8beax+B3BMDuCbRO5fn0mh6rYbxnjbzTeM8beax+B3BMDuCbRO5fn0mh6rYbxnjbzTeM8beax+B3BMDuCbRO5fn0mh6rYbxnjbzTeM8beax+B3BMDuCbRO5fn0mh6rYbxnjbzTeM8beax+B3BMDuCbRO5fn0mh6rYbxnjbzTeM8beax+B3BMDuCbRO5fn0mh6rYbxnjbzTeM8beax+B3BMDuCbRO5fn0mh6rYbxnjbzTeM8beax+B3BMDuCbRO5fn0mh6rUdX0fs7OSdX0fs7OSlIvodVg4B2C43iovV9H7OzknV9H7OzkpSJqsHAOwS8VF6vo/Z2ck6vo/Z2clKVVqO+0mn7a6srCXZOzHG350ju4f8AVS2yQuNBGOwUOfdFSVL6vo/Z2ck6vo/Z2cliIbvr65xirobXSQUzvSjjkxtOH8TgT8cBWWl9YTV1xdZ77R/Ibo35o4hsnDOAD2HHHtII9a7O/wCNiAJuNNPii5NtIJpiK/K0vV9H7OzknV9H7OzkpSLhqsHAOwXa8VF6vo/Z2ck6vo/Z2clKRNVg4B2CXiovV9H7OzknV9H7OzkpSJqsHAOwS8VF6vo/Z2ck6vo/Z2clKVNadRU90u9xtkUErJaB2y97sbLuJHDB93rUixwkEiMYdAoL6EAnNT+r6P2dnJOr6P2dnJSkUarBwDsFN4qL1fR+zs5J1fR+zs5KUiarBwDsEvFRer6P2dnJOr6P2dnJSkTVYOAdgl4qL1fR+zs5J1fR+zs5KUiarBwDsEvFRer6P2dnJOr6P2dnJSkTVYOAdglSovV9H7OzknV9H7OzkpSJqsHAOwS8VF6vo/Z2ck6vo/Z2clKRNVg4B2CXiovV9H7OzknV9H7OzkpSJqsHAOwS8UREXdQiIiIi57rBrbh0iWG21TdqmbGJdk9hJc4kH+W0LoSxfSFZq2c0V7s7XPrre7aMbRkvZnPAevBHZ6wStFmIEmO+q4WgEsw6LaKruOn7bcbhS3CqgcaulIMUjJHMIwcjODxGfUfes/Q9JNimpWurTNS1AGHw7pz8H14IH44UG2XW7ax1NDUW91XRWOkILyHbO+IOdk44Ek4BHHAz6ypbBK2pP403qDPG6gGNV7ahuV2vmqXaaslWaGOCPbqqhmdvsB4EccDab2EEk9uAoV4oL/ouFl2o73UXGlY9raiCqcSOJwO0ntJAyMEZHavS51B0jr+a7VsTzbLjHsb1gzsOw3Pnlmcdx4ZwvzWmrKK920WTT5krause0YZG5uACHY4gceHwAyThaGB1WBo/AgV/tSs73No4uP5DL+YKVry8TOtdgrLbVVEEdXOx+YpHMLmOaDg4+PYtncnOZbqpzHFrmwvIIOCDgrCa8tFTQ6Os4hG+NqdHvSAcYDcF3wyBzU25dINmqLJJ8jdNLW1ERZHS7p20HuGME4xw9xPuyuRjL2NuCuJXUSBj3XzTAKDYLhXSdGN0q5K2pfUsE2zO+Zxe3AGMOzkLx09Zb9qWyQVtZqOtpo8FtOyNztogEjaeQ4FxyD254etfGnMfomu/H1TfgFrOj76HW36jvzuXSV2jDy3O8ucTb5aHcKodK1V5quu9LXK4P+WU8ZbBWglz2Z4ZzkE9rXDJzxPFZ6w6cuddqG8UVPqGppZ6V2Jalm3tT+kRk4eD6s8Se1aXTZ/9TdQ/3Q/oVba79b9Pa11G67SvhE0g2AInOJ4k9gHcQVcOcC+4MSAcvpVIaQ2+cASM/tdNHALD6pul1uepY9MWKo+SER7yqqR85oxnA9YABb2cSXAZAytwOIXPL/K7Suvm36ohkfb66ERSysGdg4aMfH0Gn3jOOxZLMKuPzTD7Wq0GjR8Vx+l8Xe03/SNJ1vb79VV8UTh8ogqi5wIJxnBJ4Z7cYIHHK9+kC+zP0fabpbaiopPlE7HndSFjsGN5LTjt4j7l8av1lbrraHWmxGStrK4iMNbE4bIzk9oGTwx7u09ihdIdvfauj2zUMpBkgma15HZtbqTP3rVGCXMMgxr4WZ5ADxGcKeVY1elNST0T7hJqSrFy2d4KeN7mRA9uwMHHuzhXegL3PftOsqash1RHIYpHgY2yACDjvwRn35Whl/4L/qn8Fh+h0g6Xnwf/ANbv9NizlxkhcXbiP6uwbclaBvBV7rqeam0pcJqaaSGVrG7MkTy1w9JvYRxXtpCWWfTFslnlfLK+naXPkcXOccdpJ7V+axoprhpi40tMwvmdFljB2uIIOB7zhZfSeubLQ6bpqW4zPgqKSPdmPdudtY7CCBjnjBUNYXw/iKmv8VnPDJvyNBRe+jq+sl1RqmOapqKiOCU7mKSVzmt9OTg0Hs7AOCodPOm1YJ6u6atqKGrL8R0sMxiDRjIIbtDI444ceHEqf0cVMtTf9TVbYC2WUiVsEh2SC58hDSfV2gZXg2t0VeXzv1BbBariyR29iDpASfWfQABPeCM/itRF17gB8ZUNMPhZgbzGmvznUb/lbDSMN9pYKimvsrKlkbv92qQ4F0jOPzuQPHjx9y0C590VOk3l3jpHzvszJQKV0wxxy7s8tnPlwC6CsVobdkIWyB16MFERFxXVERERERERERERERERQaqzWqrm31XbKKeXxy07HO5kKZGxsbGsja1rGjAa0YAC+kUkkqAAF5zQxTxuinjZJG4Ycx7QQfiCvCitlvoC40NDS0xd84wwtZn44ClolTSiUGa/CAQQRkHtCh09pttLM6amt9JDK7g58cDWuPxICmogJCUBXhHRUsdO6njpoWwO+dE2MBp8uxfcMMUEbYoI2Rxt7GMaAB5BeiKKqaLxZS08cz544ImzP+fI1gDnfE+tfFRQUdU4OqqSCZwGAZIw4/epKKalRQIF8SxRzRujlY17HDDmuGQfJfaKFKh0dqt1C9z6GgpaZ7uBdDC1hPIL2qaWnq2BlVBFMwHIbKwOAPfxXsikkk1UAACi/CMjB7F501NBSs3dNBHCwnOzGwNGfgF6ooUooT7RbZKv5XJb6R1TnO+dA0vz9bGVNRSCRkoIBzXlHTQRSySxQxskk+e9rAC74n1qPWWm210gkrbdSVDwMB00DXnmQpqICQaoQDgV8RRRwxtjiY1jGjDWsGAPJfaIoUoiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiL/2Q==" alt="Tata Capital" className="landing-logo" />
              <h1>TATA CAPITAL</h1>
              <p>India's Leading Financial Services Company</p>
            </div>
            <div className="hero-section">
              <h2>Get Personal Loans Starting from 10.99%*</h2>
              <p>Quick approval • Minimal documentation • Instant disbursal</p>
            </div>
          </div>
          <FloatingChatbot onOpenChat={handleOpenChat} />
        </div>
      ) : (
        // Show the main chat interface
        <>
          {/* Header */}
          <div className="chat-header">
            <div className="header-content">
              <div className="logo">
                <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTLYVK2xE18lGWv9LtcHDrCobJlMVmekxMCKw&s" alt="Tata Capital" className="logo-img" />
                <span className="logo-text">TATA CAPITAL</span>
              </div>
              <div className="connection-status">
                <span className={`status-indicator ${isConnected ? 'connected' : 'disconnected'}`}></span>
                {isConnected ? 'Connected' : 'Connecting...'}
              </div>
            </div>
          </div>

          {/* Chat Container */}
          <div className="chat-container">
            <div className="messages-container">
              {messages.map((message) => (
                <div key={message.id} className={`message ${message.sender}`}>
                  <div className="message-content">
                    <div 
                      className="message-text"
                      dangerouslySetInnerHTML={{ __html: formatMessage(message.content) }}
                    />
                    <div className="message-time">
                      {new Date(message.timestamp).toLocaleTimeString()}
                    </div>
                    
                    {/* Download button for sanction letter */}
                    {message.metadata?.download_url && (
                      <div className="download-section">
                        <a 
                          href={`http://localhost:8000${message.metadata.download_url}`}
                          download
                          className="download-btn"
                        >
                          📄 Download Sanction Letter
                        </a>
                      </div>
                    )}
                    
                    {/* Suggestion buttons for bot messages */}
                    {message.sender === 'bot' && message.metadata?.suggestions && (
                      <div className="suggestions-container">
                        {message.metadata.suggestions.map((suggestion, index) => (
                          <button
                            key={index}
                            className="suggestion-btn"
                            onClick={() => handleSuggestionClick(suggestion)}
                          >
                            {suggestion}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))}
              
              {isTyping && (
                <div className="message bot">
                  <div className="message-content">
                    <div className="typing-indicator">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="input-container">
              {showUpload && (
                <div className="upload-section">
                  <input
                    type="file"
                    ref={fileInputRef}
                    onChange={handleFileUpload}
                    accept=".pdf,.jpg,.jpeg,.png"
                    style={{ display: 'none' }}
                  />
                  <button 
                    className="upload-btn"
                    onClick={() => fileInputRef.current?.click()}
                  >
                    📎 Upload Salary Slip
                  </button>
                </div>
              )}
              
              <div className="input-row">
                <textarea
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Type your message..."
                  className="message-input"
                  rows="1"
                  disabled={!isConnected}
                />
                <button 
                  onClick={sendMessage}
                  className="send-btn"
                  disabled={!isConnected || !inputMessage.trim()}
                >
                  Send
                </button>
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="chat-footer">
            <p>🔒 Your data is secure with Tata Capital | Customer Care: 1800-209-8800</p>
          </div>
        </>
      )}
    </div>
  );
}

export default App;