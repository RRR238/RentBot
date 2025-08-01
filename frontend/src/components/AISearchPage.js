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

const allTypes = [...flatTypes.map(t => t.key), "house"];

const OFFERS_PER_PAGE = 20;
const MAX_CHAT_MESSAGES = 40;

function AISearchPage() {
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("jwtToken");
    if (!token) {
      navigate("/login");
    }
  }, [navigate]);

 
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

  const [notification, setNotification] = useState("");
  const [offersShown, setOffersShown] = useState(false);

  const [filtersDirty, setFiltersDirty] = useState(false);
  const [showFilterInfo, setShowFilterInfo] = useState(false);

  const [showFilters, setShowFilters] = useState(false);

  const [appliedFilters, setAppliedFilters] = useState({
  maxPrice: 5000,
  size: { from: "", to: "" },
  selectedTypes: [],
  locations: [""]  // Add this line
});

const [locations, setLocations] = useState([""]);

   useEffect(() => {
    setChatOpen(true);
  }, []);

useEffect(() => {
  if (chatOpen) {
    const token = localStorage.getItem("jwtToken");
    fetch("http://localhost:5000/chat/fetch-history", {
  method: "GET",
  headers: {
    "Authorization": `Bearer ${token}`,
  },
})
  .then(res => {
    if (res.status === 401) {
      navigate("/login");
      return null;
    }
    if (res.status === 404) {
      setChatMessages([]);
      setChatSessionId(null);
      return null;
    }
    return res.json();
  })
  .then(data => {
  if (!data) return;
  if (data.status === "session expired") {
    setChatMessages([]);
    setChatSessionId(null);
  } else if (Array.isArray(data.history)) {
    setChatMessages(
      data.history.map(msg => ({
        sender: msg.role === "Human" ? "user" : "bot",
        text: msg.message
      }))
    );
    setChatSessionId(data.session_id || null);
  } else {
    setChatMessages([]);
    setChatSessionId(data.session_id || null);
  }
})
  .catch(() => {
    setChatMessages([]);
  });
  }
}, [chatOpen]);

  useEffect(() => {
    if (chatWindowRef.current) {
      chatWindowRef.current.scrollTop = chatWindowRef.current.scrollHeight;
    }
  }, [chatMessages, chatOpen]);

  useEffect(() => {
  // Only fetch when appliedFilters actually changes and we have offers
  if (appliedFilters.locations.length > 0 && offers.length > 0) {
    fetchAISearchResults(currentPage);
  }
}, [appliedFilters]);

  

  const handleTypeToggle = (type) => {
    setSelectedTypes(selectedTypes =>
      selectedTypes.includes(type)
        ? selectedTypes.filter(t => t !== type)
        : [...selectedTypes, type]
    );
    setFiltersDirty(true);
  };

  const handleMaxPriceChange = (e) => {setMaxPrice(Number(e.target.value));
                                        setFiltersDirty(true);
                                        };
  const handleSizeChange = (e) => {setSize({ ...size, [e.target.name]: e.target.value });
                                    setFiltersDirty(true);
                                };
  const handleRoomsChange = (e) => {setRooms(e.target.value);
                                      setFiltersDirty(true);
                                    };

  const handleLocationChange = (index, value) => {
  const newLocations = [...locations];
  newLocations[index] = value;
  setLocations(newLocations);
  setFiltersDirty(true);
};

const handleAddLocation = () => {
  setLocations([...locations, ""]);
  setFiltersDirty(true);
};

const handleRemoveLocation = (index) => {
  if (locations.length > 1) {
    const newLocations = locations.filter((_, i) => i !== index);
    setLocations(newLocations);
    setFiltersDirty(true);
  }
};

const filterToggleFunction = () => {
  if (showFilters) {
    // Hiding filters - reset to applied values
    setMaxPrice(appliedFilters.maxPrice);
    setSize(appliedFilters.size);
    setSelectedTypes(appliedFilters.selectedTypes);
    setLocations(appliedFilters.locations || [""]);  // Add fallback
  }
  setShowFilters(!showFilters);
};

  const handleShowOffers = () => {
    setLoading(true);
  setShowFilters(false); // Close filter card when showing offers

  // Uncomment this block to use real backend fetching:
  const token = localStorage.getItem("jwtToken");
  fetch(`http://localhost:5000/search/find-results/${chatSessionId}`, {
    method: "GET",
    headers: {
      "Authorization": `Bearer ${token}`,
    },
    // ...other options...
  })
  .then(res => {
    if (res.status === 401) {
      navigate("/login");
      return null;
    }
    return res.json();
  })
  .then(data => {
    if (!data) return;
    setOffers(data.offers || []);
    setTotalPages(Math.ceil(data.total / OFFERS_PER_PAGE));
    setLoading(false);
    setOffersShown(true);
  })
  .catch(() => setLoading(false));
  

    // Mock data for development:
    // const mockOffers = [
    //   {
    //     url: 'https://www.reality.sk/byty/prenajom-penthouse-novostavba-safranova-zahrada-4-izb-byt-s-terasou-2x-garazove-statie/JuUemf05CHR/',
    //     price: 2000,
    //     location: 'Bratislava'
    //   },
    //   {
    //     url: 'https://www.reality.sk/byty/luxusny-penthouse-na-prenajom/Ju_3cQtsESZ/',
    //     price: 1200,
    //     location: 'Bratislava'
    //   },
    //   {
    //     url: 'https://www.reality.sk/byty/prenajom/JuEaCQ1rVQq/',
    //     price: 800,
    //     location: 'Bratislava'
    //   }
    //   // Add more mock offers as needed
    // ];
    // setTimeout(() => {
    //   setOffers(mockOffers);
    //   setTotalPages(Math.ceil(mockOffers.length/OFFERS_PER_PAGE)); // Example: 2 pages
    //   setLoading(false);
    // }, 500);
  };

  // Function to fetch AI search results (mocked)
  const fetchAISearchResults = (page = currentPage) => {
    setLoading(true);

  const token = localStorage.getItem("jwtToken");
  
  // Add locations to params
  const validLocations = appliedFilters.locations.filter(loc => loc.trim() !== "");
  const locationString = validLocations.length === 0 ? "Slovakia" : validLocations.join(",");
  
  const params = new URLSearchParams({
    page,
    limit: OFFERS_PER_PAGE,
    price_min: 0,
    price_max: appliedFilters.maxPrice,
    size_min: appliedFilters.size.from === "" ? 0 : appliedFilters.size.from,
    size_max: appliedFilters.size.to === "" ? 1000 : appliedFilters.size.to,
    types: appliedFilters.selectedTypes.length === 0 ? allTypes.join(",") : appliedFilters.selectedTypes.join(","),
    locations: locationString,  // Add this
  });
   fetch(`http://localhost:5000/search/fetch-filtered-results/${chatSessionId}?${params.toString()}`, {
  method: "GET",
  headers: {
    "Authorization": `Bearer ${token}`,
  },
  // ...other options...
})
  .then(res => {
    if (res.status === 401) {
      navigate("/login");
      return null;
    }
    if (res.status === 404) {
      setOffers([]);
      setNotification("Session expired");
      setTimeout(() => setNotification(""), 3000); // Hide after 3 seconds
      setLoading(false);
      return null;
    }
    return res.json();
  })
  .then(data => {
    if (!data) return;
    setOffers(data.offers || []);
    setTotalPages(Math.ceil(data.total / OFFERS_PER_PAGE));
    setLoading(false);
  })
  .catch(() => setLoading(false));
    

    // Mock data for development:
    // const mockOffers = [
    //   {
    //     url: 'https://www.reality.sk/byty/prenajom-penthouse-novostavba-safranova-zahrada-4-izb-byt-s-terasou-2x-garazove-statie/JuUemf05CHR/',
    //     price: 2000,
    //     location: 'Bratislava'
    //   },
    //   {
    //     url: 'https://www.reality.sk/byty/luxusny-penthouse-na-prenajom/Ju_3cQtsESZ/',
    //     price: 1200,
    //     location: 'Bratislava'
    //   },
    //   {
    //     url: 'https://www.reality.sk/byty/prenajom/JuEaCQ1rVQq/',
    //     price: 800,
    //     location: 'Bratislava'
    //   }
    //   // Add more mock offers as needed
    // ];
    // setTimeout(() => {
    //   setOffers(mockOffers);
    //   setTotalPages(Math.ceil(mockOffers.length/OFFERS_PER_PAGE)); // Example: 3 pages
    //   setLoading(false);
    // }, 500);
  };

  const handleSearch = () => {
  setAppliedFilters({
    maxPrice,
    size,
    selectedTypes,
    locations  // This will trigger the useEffect above
  });
  
  setCurrentPage(1);
  // Remove this line: fetchAISearchResults(1);
  setShowFilters(false);
  setFiltersDirty(false);
};

  const handlePrevPage = () => {
  if (filtersDirty) {
    setShowFilterInfo(true);
    return;
  }
  if (currentPage > 1) {
    const newPage = currentPage - 1;
    setCurrentPage(newPage);
    fetchAISearchResults(newPage);
  }
};

  const handleNextPage = () => {
  if (filtersDirty) {
    setShowFilterInfo(true);
    return;
  }
  if (currentPage < totalPages) {
    const newPage = currentPage + 1;
    setCurrentPage(newPage);
    fetchAISearchResults(newPage);
  }
};

  const handleClearChat = () => {
  // Uncomment for real backend:
  const token = localStorage.getItem("jwtToken");
  fetch("http://localhost:5000/chat/close-session", {
  method: "POST",
  headers: { 
    "Content-Type": "application/json",
    "Authorization": `Bearer ${token}` 
  },
  body: JSON.stringify({ session_id: chatSessionId }),
})
  .then(res => {
    if (res.status === 401) {
      navigate("/login");
      return null;
    }
    // Optionally handle other statuses if needed
    return res.json();
  })
  .catch(() => {
    // Optionally handle network errors
  });

setChatMessages([]);
setChatSessionId(null);
  }

  // --- Chat logic ---
  const handleSendChat = async (e) => {
  e.preventDefault();
  if (!chatInput.trim() || chatMessages.length >= MAX_CHAT_MESSAGES) return;

  const userMessage = { sender: "user", text: chatInput };
  setChatMessages((msgs) => [...msgs, userMessage]);
  setChatLoading(true);

  

  if (!chatSessionId) {
    // Uncomment for real backend:
    const token = localStorage.getItem("jwtToken");
    const sessionRes = await fetch("http://localhost:5000/chat/create-session", { method: "POST",headers:{"Content-Type": "application/json",
    "Authorization": `Bearer ${token}` }
    });

    if (sessionRes.status === 401) {
  navigate("/login");
  return;
}

    if (!sessionRes.ok) {
      setChatMessages(msgs => [...msgs, { sender: "bot", text: "Failed to start chat session." }]);
      setChatLoading(false);
      return;
    }
    const sessionData = await sessionRes.json();
    setChatSessionId(sessionData.session_id);
    
    // Mock session creation:
    setTimeout(() => {
      // const mockSessionId = "mock-session-123";
      // setChatSessionId(mockSessionId);

      // 2. Send message to chatbot (mock)
      // Uncomment for real backend:
      
      fetch("http://localhost:5000/chat/generate-answer", {
  method: "POST",
  headers: { 
    "Content-Type": "application/json",
    "Authorization": `Bearer ${token}` 
  },
  body: JSON.stringify({ session_id: sessionData.session_id, message: chatInput }),
})
  .then(res => {
    if (res.status === 401) {
      navigate("/login");
      return null;
    }
    if (res.status === 404) {
      setChatMessages([]);
      setChatSessionId(null);
      setNotification("Session expired. Please start a new chat.");
      setChatLoading(false);
      setTimeout(() => setNotification(""), 3000); // Hide after 3 seconds
      return null;
    }
    return res.json();
  })
  .then(data => {
    if (!data) return;
    // If backend returns array of {role, message}
    if (Array.isArray(data)) {
      setChatMessages(
        data.map(msg => ({
          sender: msg.role === "Human" ? "user" : "bot",
          text: msg.message
        }))
      );
    } else if (data.reply) {
      // fallback for single reply
      setChatMessages(msgs => [...msgs, { sender: "bot", text: data.reply }]);
    }
    setChatLoading(false);
  })
  .catch(() => {
    setChatMessages(msgs => [...msgs, { sender: "bot", text: "Error contacting chatbot." }]);
    setChatLoading(false);
  });
      
      // Mock bot reply:
      // setTimeout(() => {
      //   setChatMessages(msgs => [
      //     ...msgs,
      //     { sender: "bot", text: "This is a mock reply from the AI chatbot." }
      //   ]);
      //   setChatLoading(false);
      // }, 1000);
    }, 700);
  } else {
    // Session already exists, just send message (mock)
    // Uncomment for real backend:
    const token = localStorage.getItem("jwtToken");
    fetch("http://localhost:5000/chat/generate-answer", {
  method: "POST",
  headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` },
  body: JSON.stringify({ session_id: chatSessionId, message: chatInput }),
})
  .then(res => {
    if (res.status === 401) {
      navigate("/login");
      return null;
    }
    if (res.status === 404) {
      setChatMessages([]);
      setChatSessionId(null);
      setNotification("Session expired. Please start a new chat.");
      setChatLoading(false);
      setTimeout(() => setNotification(""), 3000); // Hide after 3 seconds
      return null;
    }
    return res.json();
  })
  .then(data => {
    if (!data) return;
    setChatMessages(msgs => [...msgs, { sender: "bot", text: data.reply }]);
    setChatLoading(false);
  })
  .catch(() => {
    setChatMessages(msgs => [...msgs, { sender: "bot", text: "Error contacting chatbot." }]);
    setChatLoading(false);
  });
    
    // Mock bot reply:
    // setTimeout(() => {
    //   setChatMessages(msgs => [
    //     ...msgs,
    //     { sender: "bot", text: "This is a mock reply from the AI chatbot." }
    //   ]);
    //   setChatLoading(false);
    // }, 1000);
  }

  setChatInput("");
  setOffersShown(false);
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
        <button
          onClick={() => {
                        if (showFilters) {
                          // Hiding filters - reset to applied values
                          setMaxPrice(appliedFilters.maxPrice);
                          setSize(appliedFilters.size);
                          setSelectedTypes(appliedFilters.selectedTypes);
                        }
                        setShowFilters(!showFilters);
                      }}
          style={{
                marginBottom: "1rem",
                background: "#007bff",
                color: "#fff",
                border: "none",
                borderRadius: "4px",
                padding: "0.75rem 1.5rem", // Changed from "0.5rem 1rem"
                fontWeight: "bold",
                cursor: "pointer",
                alignSelf: "flex-start",
                opacity: (chatMessages.length === 0 || offers.length === 0 || chatLoading) ? 0.6 : 1,
              }}
              disabled={chatMessages.length === 0 || offers.length === 0 || chatLoading}
        >
          {showFilters ? "Hide Filters" : "Show Filters"}
          
        </button>
       {/* Filters Card */}
        {showFilters && (
          <div
            style={{
              background: "#f8f9fa",
              border: "1px solid #ddd",
              borderRadius: "8px",
              padding: "1.5rem",
              marginBottom: "2rem",
              display: "flex",
              flexDirection: "column",
              gap: "1.5rem",
            }}
          >
          {/* Price Fields */}
    <div>
      <label style={{ fontWeight: "bold" }}>Price (€):</label>
      <div style={{ display: "flex", gap: "0.5rem", marginTop: "0.5rem" }}>
        <input
          type="number"
          placeholder="Min"
          value={0}
          style={{ width: "80px", padding: "0.25rem" }}
          disabled={offers.length === 0}
        />
        <input
          type="number"
          placeholder="Max"
          value={maxPrice}
          onChange={handleMaxPriceChange}
          style={{ width: "80px", padding: "0.25rem" }}
          disabled={offers.length === 0}
        />
      </div>
    </div>

    {/* Size Fields */}
    <div>
      <label style={{ fontWeight: "bold" }}>Size (m²):</label>
      <div style={{ display: "flex", gap: "0.5rem", marginTop: "0.5rem" }}>
        <input
          type="number"
          name="from"
          placeholder="From"
          value={size.from}
          onChange={handleSizeChange}
          style={{ width: "80px", padding: "0.25rem" }}
          disabled={offers.length === 0}
        />
        <input
          type="number"
          name="to"
          placeholder="To"
          value={size.to}
          onChange={handleSizeChange}
          style={{ width: "80px", padding: "0.25rem" }}
          disabled={offers.length === 0}
        />
      </div>
    </div>

    {/* Location Fields */}
<div>
  <label style={{ fontWeight: "bold" }}>Locations:</label>
  <div style={{ marginTop: "0.5rem", display: "flex", flexDirection: "column", gap: "0.5rem" }}>
    {locations.map((location, index) => (
      <div key={index} style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
        <input
          type="text"
          placeholder="Enter location (e.g., Bratislava, Prague...)"
          value={location}
          onChange={(e) => handleLocationChange(index, e.target.value)}
          style={{ 
            flex: 1,
            padding: "0.5rem", 
            borderRadius: "4px", 
            border: "1px solid #ccc",
            fontSize: "0.95rem"
          }}
          disabled={offers.length === 0}
        />
        {locations.length > 1 && (
          <button
            onClick={() => handleRemoveLocation(index)}
            style={{
              background: "#dc3545",
              color: "#fff",
              border: "none",
              borderRadius: "4px",
              padding: "0.5rem",
              cursor: "pointer",
              fontSize: "0.9rem",
              minWidth: "30px"
            }}
            title="Remove location"
            disabled={offers.length === 0}
          >
            ✕
          </button>
        )}
      </div>
    ))}
    <button
      onClick={handleAddLocation}
      style={{
        background: "#28a745",
        color: "#fff",
        border: "none",
        borderRadius: "4px",
        padding: "0.5rem 1rem",
        cursor: "pointer",
        fontSize: "0.9rem",
        alignSelf: "flex-start",
        marginTop: "0.5rem"
      }}
      disabled={offers.length === 0}
    >
      + Add Location
    </button>
  </div>
</div>

    {/* Property Types - Flats */}
    <div>
      <label style={{ fontWeight: "bold" }}>Flats:</label>
      <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem", marginTop: "0.5rem" }}>
        {/* First row: first 4 categories */}
        <div style={{ display: "flex", gap: "1.5rem", flexWrap: "wrap" }}>
          {flatTypes.slice(0, 4).map(type => (
            <label key={type.key} style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <input
                type="checkbox"
                checked={selectedTypes.includes(type.key)}
                onChange={() => handleTypeToggle(type.key)}
                disabled={offers.length === 0}
              />
              {type.label}
            </label>
          ))}
        </div>
        {/* Second row: remaining categories */}
        <div style={{ display: "flex", gap: "1.5rem", flexWrap: "wrap" }}>
          {flatTypes.slice(4).map(type => (
            <label key={type.key} style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <input
                type="checkbox"
                checked={selectedTypes.includes(type.key)}
                onChange={() => handleTypeToggle(type.key)}
                disabled={offers.length === 0}
              />
              {type.label}
            </label>
          ))}
        </div>
      </div>
    </div>

    {/* Property Types - House */}
    <div>
      <label style={{ fontWeight: "bold" }}>House:</label>
      <div style={{ marginTop: "0.5rem" }}>
        <label style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <input
            type="checkbox"
            checked={selectedTypes.includes("house")}
            onChange={() => handleTypeToggle("house")}
            disabled={offers.length === 0}
          />
          House
        </label>
      </div>
    </div>

    {/* Buttons */}
    <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
      <button
              onClick={handleSearch}
              style={{
                background: "#28a745",
                color: "#fff",
                border: "none",
                borderRadius: "4px",
                padding: "0.75rem 1.5rem",
                fontWeight: "bold",
                cursor: "pointer",
                alignSelf: "flex-start",
              }}
            >
              Apply Filters
            </button>
    </div>
  </div>
)}
{/* Show offers and Clear results buttons */}
<div style={{ display: "flex", flexDirection: "column", gap: "0.5rem", marginBottom: "2rem" }}>
  <button
    style={{
      background: "#28a745",
      color: "#fff",
      border: "none",
      borderRadius: "4px",
      padding: "0.75rem 1.5rem",
      fontWeight: "bold",
      cursor: "pointer",
      alignSelf: "flex-start",
      opacity: (chatMessages.length === 0 || chatLoading || offersShown) ? 0.6 : 1,
    }}
    onClick={handleShowOffers}
    disabled={chatMessages.length === 0 || chatLoading || offersShown}
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
    alignSelf: "flex-start",
    opacity: (offers.length === 0) ? 0.6 : 1,
  }}
  onClick={() => {
    setOffers([]);
    setOffersShown(false);
    setShowFilters(false); // Close filter card automatically
  }}
  disabled={offers.length === 0}
>
  Clear results
</button>
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
            disabled={currentPage === 1 || filtersDirty}
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
            disabled={currentPage === totalPages || filtersDirty}
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
        {notification && (
  <div
    style={{
      position: "fixed",
      bottom: "100px",
      right: "40px",
      background: "#dc3545",
      color: "#fff",
      padding: "0.75rem 1.5rem",
      borderRadius: "8px",
      boxShadow: "0 2px 8px rgba(0,0,0,0.18)",
      zIndex: 2000,
      fontWeight: "bold",
      fontSize: "1rem"
    }}
  >
    {notification}
  </div>
)}
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