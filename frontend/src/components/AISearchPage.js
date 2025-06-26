import React, { useState, useRef, useEffect } from "react";
import OfferCard from "./OfferCard";
import { useNavigate } from "react-router-dom";


const flatTypes = [
  { key: "studio", label: "Studio" },
  { key: "1room", label: "1 room" },
  { key: "2rooms", label: "2 rooms" },
  { key: "3rooms", label: "3 rooms" },
  { key: "4rooms", label: "4 rooms" },
  { key: "5plus", label: "5 and more rooms" },
  { key: "mezonet", label: "Mezonet" },
  { key: "penthouse", label: "Penthouse" },
  { key: "loft", label: "Loft" },
];

const OFFERS_PER_PAGE = 20;
const MAX_CHAT_MESSAGES = 40;

function AISearchPage() {

  useEffect(() => {
    const token = localStorage.getItem("jwtToken");
    if (!token) {
      navigate("/login");
    }
  }, [navigate]);
}

useEffect(() => {
  if (chatOpen) {
    const token = localStorage.getItem("jwtToken");
    fetch("http://localhost:5000/chat/history", {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${token}`,
      },
    })
      .then(res => res.json())
      .then(data => {
        if (data.status === "session expired") {
          setChatMessages([]);
          setChatSessionId(null);
        } else {
          setChatMessages(data.history);
          setChatSessionId(data.session_id || null);
        }
      })
      .catch(() => {
        setChatMessages([{ sender: "bot", text: "Failed to load chat history." }]);
      });
  }
}, [chatOpen]);
  // Filter states
  const [maxPrice, setMaxPrice] = useState(5000);
  const [size, setSize] = useState({ from: "", to: "" });
  const [selectedTypes, setSelectedTypes] = useState([]);
  const [rooms, setRooms] = useState("");
  const [offers, setOffers] = useState([]);
  const [loading, setLoading] = useState(false);

  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  // Chat states
  const [chatOpen, setChatOpen] = useState(true);
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState("");
  const [chatSessionId, setChatSessionId] = useState(null);
  const [chatLoading, setChatLoading] = useState(false);
  const chatWindowRef = useRef(null);

  useEffect(() => {
    setChatOpen(true);
  }, []);

  useEffect(() => {
    if (chatWindowRef.current) {
      chatWindowRef.current.scrollTop = chatWindowRef.current.scrollHeight;
    }
  }, [chatMessages, chatOpen]);

  const handleTypeToggle = (type) => {
    setSelectedTypes(selectedTypes =>
      selectedTypes.includes(type)
        ? selectedTypes.filter(t => t !== type)
        : [...selectedTypes, type]
    );
  };

  const handleMaxPriceChange = (e) => setMaxPrice(Number(e.target.value));
  const handleSizeChange = (e) => setSize({ ...size, [e.target.name]: e.target.value });
  const handleRoomsChange = (e) => setRooms(e.target.value);

  const handleShowOffers = () => {
    setLoading(true);

    // Uncomment this block to use real backend fetching:
    /*
    const params = new URLSearchParams({
      page: currentPage,
      limit: OFFERS_PER_PAGE,
      price_min: 0,
      price_max: maxPrice,
      size_min: size.from,
      size_max: size.to,
      types: selectedTypes.join(","),
      rooms,
    });
    fetch(`http://localhost:5000/ai-show-offers?${params.toString()}`,{
  method: "GET",
  headers: {
    "Authorization": `Bearer ${token}`,
  },
  // ...other options...
})
      .then(res => res.json())
      .then(data => {
        setOffers(data.offers || []);
        setTotalPages(Math.ceil(data.total / OFFERS_PER_PAGE));
        setLoading(false);
      })
      .catch(() => setLoading(false));
    */

    // Mock data for development:
    const mockOffers = [
      {
        url: 'https://www.reality.sk/byty/prenajom-penthouse-novostavba-safranova-zahrada-4-izb-byt-s-terasou-2x-garazove-statie/JuUemf05CHR/',
        price: 2000,
        location: 'Bratislava'
      },
      {
        url: 'https://www.reality.sk/byty/luxusny-penthouse-na-prenajom/Ju_3cQtsESZ/',
        price: 1200,
        location: 'Bratislava'
      },
      {
        url: 'https://www.reality.sk/byty/prenajom/JuEaCQ1rVQq/',
        price: 800,
        location: 'Bratislava'
      }
      // Add more mock offers as needed
    ];
    setTimeout(() => {
      setOffers(mockOffers);
      setTotalPages(Math.ceil(mockOffers.length/OFFERS_PER_PAGE)); // Example: 2 pages
      setLoading(false);
    }, 500);
  };

  // Function to fetch AI search results (mocked)
  const fetchAISearchResults = (page = currentPage) => {
    setLoading(true);

    // Uncomment this block to use real backend fetching:
    /*
    const params = new URLSearchParams({
      page,
      limit: OFFERS_PER_PAGE,
      price_min: 0,
      price_max: maxPrice,
      size_min: size.from,
      size_max: size.to,
      types: selectedTypes.join(","),
      rooms,
    });
    fetch(`http://localhost:5000/ai-search?${params.toString()}`,{
  method: "GET",
  headers: {
    "Authorization": `Bearer ${token}`,
  },
  // ...other options...
})
      .then(res => res.json())
      .then(data => {
        setOffers(data.offers || []);
        setTotalPages(Math.ceil(data.total / OFFERS_PER_PAGE));
        setLoading(false);
      })
      .catch(() => setLoading(false));
    */

    // Mock data for development:
    const mockOffers = [
      {
        url: 'https://www.reality.sk/byty/prenajom-penthouse-novostavba-safranova-zahrada-4-izb-byt-s-terasou-2x-garazove-statie/JuUemf05CHR/',
        price: 2000,
        location: 'Bratislava'
      },
      {
        url: 'https://www.reality.sk/byty/luxusny-penthouse-na-prenajom/Ju_3cQtsESZ/',
        price: 1200,
        location: 'Bratislava'
      },
      {
        url: 'https://www.reality.sk/byty/prenajom/JuEaCQ1rVQq/',
        price: 800,
        location: 'Bratislava'
      }
      // Add more mock offers as needed
    ];
    setTimeout(() => {
      setOffers(mockOffers);
      setTotalPages(Math.ceil(mockOffers.length/OFFERS_PER_PAGE)); // Example: 3 pages
      setLoading(false);
    }, 500);
  };

  const handleSearch = () => {
    setCurrentPage(1);
    fetchAISearchResults(1);
  };

  const handlePrevPage = () => {
    if (currentPage > 1) {
      const newPage = currentPage - 1;
      setCurrentPage(newPage);
      fetchAISearchResults(newPage);
    }
  };

  const handleNextPage = () => {
    if (currentPage < totalPages) {
      const newPage = currentPage + 1;
      setCurrentPage(newPage);
      fetchAISearchResults(newPage);
    }
  };

  const handleClearChat = () => {
  // Uncomment for real backend:
  /*
  fetch("http://localhost:5000/chat/session", {
    method: "DELETE",
    headers: { "Content-Type": "application/json",
              "Authorization": `Bearer ${token}` },
    body: JSON.stringify({ session_id: chatSessionId }),
  });
  */
  setChatMessages([]);
  setChatSessionId(null);
};

  // --- Chat logic ---
  const handleSendChat = async (e) => {
  e.preventDefault();
  if (!chatInput.trim() || chatMessages.length >= MAX_CHAT_MESSAGES) return;

  const userMessage = { sender: "user", text: chatInput };
  setChatMessages((msgs) => [...msgs, userMessage]);
  setChatLoading(true);

  

  if (!chatSessionId) {
    // Uncomment for real backend:
    /*
    const sessionRes = await fetch("http://localhost:5000/chat/session", { method: "POST",headers:{"Content-Type": "application/json",
    "Authorization": `Bearer ${token}` }
    });
    if (!sessionRes.ok) {
      setChatMessages(msgs => [...msgs, { sender: "bot", text: "Failed to start chat session." }]);
      setChatLoading(false);
      return;
    }
    const sessionData = await sessionRes.json();
    setChatSessionId(sessionData.session_id);
    */
    // Mock session creation:
    setTimeout(() => {
      const mockSessionId = "mock-session-123";
      setChatSessionId(mockSessionId);

      // 2. Send message to chatbot (mock)
      // Uncomment for real backend:
      /*
      fetch("http://localhost:5000/chat/message", {
        method: "POST",
        headers: { "Content-Type": "application/json",
                  "Authorization": `Bearer ${token}` },
        body: JSON.stringify({ session_id: sessionData.session_id, message: chatInput }),
      })
        .then(res => res.json())
        .then(data => {
          setChatMessages(msgs => [...msgs, { sender: "bot", text: data.reply }]);
          setChatLoading(false);
        })
        .catch(() => {
          setChatMessages(msgs => [...msgs, { sender: "bot", text: "Error contacting chatbot." }]);
          setChatLoading(false);
        });
      */
      // Mock bot reply:
      setTimeout(() => {
        setChatMessages(msgs => [
          ...msgs,
          { sender: "bot", text: "This is a mock reply from the AI chatbot." }
        ]);
        setChatLoading(false);
      }, 1000);
    }, 700);
  } else {
    // Session already exists, just send message (mock)
    // Uncomment for real backend:
    /*
    fetch("http://localhost:5000/chat/message", {
      method: "POST",
      headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` },
      body: JSON.stringify({ session_id: chatSessionId, message: chatInput }),
    })
      .then(res => res.json())
      .then(data => {
        setChatMessages(msgs => [...msgs, { sender: "bot", text: data.reply }]);
        setChatLoading(false);
      })
      .catch(() => {
        setChatMessages(msgs => [...msgs, { sender: "bot", text: "Error contacting chatbot." }]);
        setChatLoading(false);
      });
    */
    // Mock bot reply:
    setTimeout(() => {
      setChatMessages(msgs => [
        ...msgs,
        { sender: "bot", text: "This is a mock reply from the AI chatbot." }
      ]);
      setChatLoading(false);
    }, 1000);
  }

  setChatInput("");
};

  return (
    <div style={{ display: "flex", height: "100vh" }}>
      {/* Left Navigation */}
      <nav
        style={{
          width: "200px",
          background: "#f0f0f0",
          padding: "2rem 1rem",
          display: "flex",
          flexDirection: "column",
          gap: "1rem",
        }}
      >
        <button
          style={{
            padding: "0.75rem",
            fontWeight: "bold",
            background: "#fff",
            border: "none",
            borderRadius: "4px",
            cursor: "pointer",
          }}
          onClick={() => window.location.href = "/offers"}
        >
          All Offers
        </button>
        <button
          style={{
            padding: "0.75rem",
            background: "#e0e0e0",
            border: "none",
            borderRadius: "4px",
            fontWeight: "bold",
          }}
          disabled
        >
          AI Search
        </button>
      </nav>
      {/* Main Content */}
      <main style={{
        flex: 1,
        padding: "2rem",
        display: "flex",
        flexDirection: "column",
        minHeight: "100vh",
        boxSizing: "border-box",
        position: "relative"
      }}>
        {/* Filters */}
        <div style={{ marginBottom: "2rem", display: "flex", gap: "2rem", alignItems: "center", flexWrap: "wrap" }}>
          {/* Price Slider */}
          <div>
            <label style={{ color: "#007bff", fontWeight: "bold" }}>Max Price:</label>
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <input
                type="range"
                min={0}
                max={5000}
                value={maxPrice}
                onChange={handleMaxPriceChange}
                style={{ accentColor: "#007bff" }}
              />
              <span style={{ color: "#007bff" }}>{maxPrice} €</span>
            </div>
          </div>
          {/* Size Fields */}
          <div>
            <label style={{ fontWeight: "bold" }}>Size (m²):</label>
            <input
              type="number"
              name="from"
              placeholder="From"
              value={size.from}
              onChange={handleSizeChange}
              style={{ width: "60px", margin: "0 0.5rem" }}
            />
            <input
              type="number"
              name="to"
              placeholder="To"
              value={size.to}
              onChange={handleSizeChange}
              style={{ width: "60px" }}
            />
          </div>
          {/* Property Types as checkboxes */}
          <div>
            <label style={{ fontWeight: "bold" }}>Flats:</label>
            <div style={{ display: "flex", flexDirection: "column", gap: "0.25rem" }}>
              {/* First row: first 4 categories */}
              <div style={{ display: "flex", gap: "1.5rem", marginBottom: "0.5rem" }}>
                {flatTypes.slice(0, 4).map(type => (
                  <label key={type.key} style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                    <input
                      type="checkbox"
                      checked={selectedTypes.includes(type.key)}
                      onChange={() => handleTypeToggle(type.key)}
                    />
                    {type.label}
                  </label>
                ))}
              </div>
              {/* Second row: next 5 categories */}
              <div style={{ display: "flex", gap: "1.5rem" }}>
                {flatTypes.slice(4).map(type => (
                  <label key={type.key} style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                    <input
                      type="checkbox"
                      checked={selectedTypes.includes(type.key)}
                      onChange={() => handleTypeToggle(type.key)}
                    />
                    {type.label}
                  </label>
                ))}
              </div>
            </div>
          </div>
          <div>
            <label style={{ fontWeight: "bold" }}>House:</label>
            <div>
              <label style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                <input
                  type="checkbox"
                  checked={selectedTypes.includes("house")}
                  onChange={() => handleTypeToggle("house")}
                />
                House
              </label>
            </div>
          </div>
          {/* Search & Show Offers Buttons */}
          <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
  <button
    onClick={handleSearch}
    style={{
      background: "#007bff",
      color: "#fff",
      border: "none",
      borderRadius: "4px",
      padding: "0.75rem 1.5rem",
      fontWeight: "bold",
      cursor: "pointer",
    }}
    disabled={offers.length === 0 || chatLoading}
  >
    Filter
  </button>
  <button
    style={{
      background: "#28a745",
      color: "#fff",
      border: "none",
      borderRadius: "4px",
      padding: "0.75rem 1.5rem",
      fontWeight: "bold",
      cursor: "pointer",
    }}
    onClick={handleShowOffers}
    disabled={chatMessages.length === 0 || chatLoading}
  >
    Show offers
  </button>
  <button
    style={{
      background: "#dc3545",
      color: "#fff",
      border: "none",
      borderRadius: "4px",
      padding: "0.75rem 1.5rem",
      fontWeight: "bold",
      cursor: "pointer",
    }}
    onClick={() => setOffers([])}
    //disabled={chatMessages.length === 0 || chatLoading}
  >
    Clear results
  </button>
</div>
        </div>
        {/* AI search results */}
        {loading ? (
          <p>Loading offers...</p>
        ) : (
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: "1.5rem",
              marginTop: "2rem",
              marginBottom: "3rem"
            }}
          >
            {offers.map((offer, idx) => (
              <OfferCard key={idx} offer={offer} />
            ))}
          </div>
        )}
        {/* Pagination at the bottom */}
        <div
          style={{
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            marginTop: "auto",
            gap: "1rem",
            marginBottom: "1rem",
          }}
        >
          <button
            onClick={handlePrevPage}
            disabled={currentPage === 1}
            style={{
              background: "#007bff",
              color: "#fff",
              border: "none",
              borderRadius: "50%",
              width: "40px",
              height: "40px",
              fontSize: "1.5rem",
              cursor: currentPage === 1 ? "not-allowed" : "pointer",
            }}
            aria-label="Previous page"
          >
            &#8592;
          </button>
          <span>
            Page {currentPage} of {totalPages}
          </span>
          <button
            onClick={handleNextPage}
            disabled={currentPage === totalPages}
            style={{
              background: "#007bff",
              color: "#fff",
              border: "none",
              borderRadius: "50%",
              width: "40px",
              height: "40px",
              fontSize: "1.5rem",
              cursor: currentPage === totalPages ? "not-allowed" : "pointer",
            }}
            aria-label="Next page"
          >
            &#8594;
          </button>
        </div>
        {/* Chat Window */}
        {chatOpen && (
          <div
            style={{
              position: "fixed",
              bottom: "24px",
              right: "24px",
              width: "340px",
              height: "420px",
              background: "#fff",
              borderRadius: "12px 12px 0 12px",
              boxShadow: "0 2px 16px rgba(0,0,0,0.18)",
              display: "flex",
              flexDirection: "column",
              zIndex: 1000,
            }}
          >
            <div
  style={{
    background: "#007bff",
    color: "#fff",
    padding: "0.75rem 1rem",
    borderRadius: "12px 12px 0 0",
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    fontWeight: "bold",
    fontSize: "1.1rem",
    position: "relative"
  }}
>
  AI Chat
  <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
    <button
      onClick={handleClearChat}
      style={{
        background: "#fff",
        color: "#007bff",
        border: "none",
        borderRadius: "4px",
        padding: "0.2rem 0.7rem",
        fontWeight: "bold",
        fontSize: "0.95rem",
        cursor: "pointer",
        marginRight: "0.5rem"
      }}
      title="Clear chat history"
    >
      🗑
    </button>
    <button
      style={{
        background: "transparent",
        border: "none",
        color: "#fff",
        fontSize: "1.2rem",
        cursor: "pointer"
      }}
      onClick={() => setChatOpen(false)}
      aria-label="Minimize chat"
    >
      &minus;
    </button>
  </div>
</div>
            <div
              ref={chatWindowRef}
              style={{
                flex: 1,
                overflowY: "auto",
                padding: "1rem",
                background: "#f8f9fa",
                display: "flex",
                flexDirection: "column",
                gap: "0.5rem"
              }}
            >
              {chatMessages.length === 0 && (
                <div style={{ color: "#888", textAlign: "center", marginTop: "2rem" }}>
                  Start a conversation with our AI assistant.
                </div>
              )}
              {chatMessages.map((msg, idx) => (
                <div
                  key={idx}
                  style={{
                    alignSelf: msg.sender === "user" ? "flex-end" : "flex-start",
                    background: msg.sender === "user" ? "#007bff" : "#e9ecef",
                    color: msg.sender === "user" ? "#fff" : "#222",
                    borderRadius: "16px",
                    padding: "0.5rem 1rem",
                    maxWidth: "80%",
                    marginBottom: "0.25rem"
                  }}
                >
                  {msg.text}
                </div>
              ))}
              {chatLoading && (
                <div style={{ color: "#888", fontStyle: "italic", marginTop: "0.5rem" }}>
                  AI is typing...
                </div>
              )}
            </div>
            <form
              onSubmit={handleSendChat}
              style={{
                display: "flex",
                borderTop: "1px solid #eee",
                padding: "0.5rem",
                background: "#fff"
              }}
            >
              <input
  type="text"
  value={chatInput}
  onChange={e => setChatInput(e.target.value)}
  placeholder={
    chatMessages.length >= MAX_CHAT_MESSAGES
      ? "Message limit reached. Clear chat to continue."
      : "Type your message..."
  }
  style={{
    flex: 1,
    border: "none",
    outline: "none",
    padding: "0.5rem",
    borderRadius: "6px",
    fontSize: "1rem",
    background: "#f4f4f4"
  }}
  disabled={chatLoading || chatMessages.length >= MAX_CHAT_MESSAGES}
/>
<button
  type="submit"
  disabled={
    chatLoading ||
    !chatInput.trim() ||
    chatMessages.length >= MAX_CHAT_MESSAGES
  }
  style={{
    background: "#007bff",
    color: "#fff",
    border: "none",
    borderRadius: "6px",
    padding: "0.5rem 1rem",
    marginLeft: "0.5rem",
    fontWeight: "bold",
    cursor:
      chatLoading ||
      !chatInput.trim() ||
      chatMessages.length >= MAX_CHAT_MESSAGES
        ? "not-allowed"
        : "pointer"
  }}
>
  Send
</button>
            </form>
          </div>
        )}
        {/* Minimized chat button */}
        {!chatOpen && (
          <button
            style={{
              position: "fixed",
              bottom: "24px",
              right: "24px",
              width: "60px",
              height: "60px",
              borderRadius: "50%",
              background: "#007bff",
              color: "#fff",
              border: "none",
              boxShadow: "0 2px 8px rgba(0,0,0,0.18)",
              fontSize: "2rem",
              cursor: "pointer",
              zIndex: 1000
            }}
            onClick={() => setChatOpen(true)}
            aria-label="Open chat"
          >
            💬
          </button>
        )}
      </main>
    </div>
  );
}

export default AISearchPage;