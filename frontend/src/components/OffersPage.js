import React, { useEffect, useState } from "react";
import OfferCard from "./OfferCard";
import { useNavigate } from "react-router-dom";

// Property type categories for checkboxes
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

const houseTypes = [
  { key: "house", label: "House" }
];

const OFFERS_PER_PAGE = 20;

function OffersPage() {
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("jwtToken");
    if (!token) {
      navigate("/login");
    }
  }, [navigate]);

  const [offers, setOffers] = useState([]);
  const [loading, setLoading] = useState(true);

  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  // Filters
  const [maxPrice, setMaxPrice] = useState(5000);
  const [minPrice, setMinPrice] = useState(0);
  const [size, setSize] = useState({ from: "", to: "" });
  const [selectedTypes, setSelectedTypes] = useState([]);
  const [rooms, setRooms] = useState("");
  const [location, setLocation] = useState("");

  const [showFilters, setShowFilters] = useState(false);

  const [appliedFilters, setAppliedFilters] = useState({
  maxPrice: 5000,
  minPrice: 0,
  size: { from: "", to: "" },
  selectedTypes: [],
  location: ""
});

  // Fetch offers (with filters and page)
  const fetchOffers = (page = currentPage) => {
    setLoading(true);

    const token = localStorage.getItem("jwtToken");
    const allTypes = [...flatTypes.map(t => t.key), ...houseTypes.map(t => t.key)];

    const params = new URLSearchParams({
      page,
      limit: OFFERS_PER_PAGE,
      price_min: minPrice,
      price_max: maxPrice,
      size_min: size.from === "" ? 0 : size.from,
      size_max: size.to === "" ? 1000 : size.to,
      types: selectedTypes.length === 0 ? allTypes.join(",") : selectedTypes.join(","),
      location: location === "" ? "Slovakia" : location,
    });

    fetch(`http://localhost:5000/offers?${params.toString()}`, {
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
        return res.json();
      })
      .then(data => {
  if (!data) return;
  
  // Handle different response formats
  let offersArray = [];
  if (Array.isArray(data)) {
    offersArray = data;
  } else if (data.offers && Array.isArray(data.offers)) {
    offersArray = data.offers;
  } else if (data.data && Array.isArray(data.data)) {
    offersArray = data.data;
  }
  
  setOffers(offersArray);
  setTotalPages(Math.ceil((data.total || offersArray.length || 0) / OFFERS_PER_PAGE));
  setLoading(false);
})
      .catch(() => setLoading(false));
  };

  // Initial fetch
  useEffect(() => {
    fetchOffers(1);
    // eslint-disable-next-line
  }, []);

  // Handlers
  const handleTypeToggle = (type) => {
    setSelectedTypes(selectedTypes =>
      selectedTypes.includes(type)
        ? selectedTypes.filter(t => t !== type)
        : [...selectedTypes, type]
    );
  };

  const handleMinPriceChange = (e) => {
  setMinPrice(Number(e.target.value));
};

const handleMaxPriceChange = (e) => {
  setMaxPrice(Number(e.target.value));
};

  const handleSizeChange = (e) => {
    setSize({ ...size, [e.target.name]: e.target.value });
  };

  const handleRoomsChange = (e) => setRooms(e.target.value);

  const handleSearch = () => {
  // Save current filter values as applied filters
  setAppliedFilters({
    maxPrice,
    minPrice,
    size,
    selectedTypes,
    location
  });
  
  setCurrentPage(1);
  fetchOffers(1);
  setShowFilters(false); // Close filters after applying
};

const handleToggleFilters = () => {
  if (showFilters) {
    // Hiding filters - reset to applied values
    setMaxPrice(appliedFilters.maxPrice);
    setMinPrice(appliedFilters.minPrice);
    setSize(appliedFilters.size);
    setSelectedTypes(appliedFilters.selectedTypes);
    setLocation(appliedFilters.location);
  }
  setShowFilters(!showFilters);
};

  const handleLocationChange = (e) => {
  setLocation(e.target.value);
};

  const handlePrevPage = () => {
    if (currentPage > 1) {
      const newPage = currentPage - 1;
      setCurrentPage(newPage);
      fetchOffers(newPage);
    }
  };

  const handleNextPage = () => {
    if (currentPage < totalPages) {
      const newPage = currentPage + 1;
      setCurrentPage(newPage);
      fetchOffers(newPage);
    }
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
          style={{ padding: "0.75rem", fontWeight: "bold", background: "#e0e0e0", border: "none", borderRadius: "4px" }}
          disabled
        >
          All Offers
        </button>
        <button
          style={{ padding: "0.75rem", background: "#fff", border: "none", borderRadius: "4px", cursor: "pointer" }}
          onClick={() => window.location.href = "/ai-search"}
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
      }}>
        
        {/* Filter Toggle Button */}
        <button
          onClick={handleToggleFilters}
          style={{
            marginBottom: "1rem",
            background: "#007bff",
            color: "#fff",
            border: "none",
            borderRadius: "4px",
            padding: "0.5rem 1rem",
            fontWeight: "bold",
            cursor: "pointer",
            alignSelf: "flex-start",
          }}
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
            {/* Price Slider */}
            <div>
              <label style={{ fontWeight: "bold" }}>Price (€):</label>
              <div style={{ display: "flex", gap: "0.5rem", marginTop: "0.5rem" }}>
                <input
                  type="number"
                  placeholder="Min"
                  value={minPrice}
                  onChange={handleMinPriceChange}
                  style={{ width: "80px", padding: "0.25rem" }}
                />
                <input
                  type="number"
                  placeholder="Max"
                  value={maxPrice}
                  onChange={handleMaxPriceChange}
                  style={{ width: "80px", padding: "0.25rem" }}
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
                />
                <input
                  type="number"
                  name="to"
                  placeholder="To"
                  value={size.to}
                  onChange={handleSizeChange}
                  style={{ width: "80px", padding: "0.25rem" }}
                />
              </div>
            </div>
              {/* Location Field */}
                <div>
                  <label style={{ fontWeight: "bold" }}>Location:</label>
                  <div style={{ marginTop: "0.5rem" }}>
                    <input
                      type="text"
                      placeholder="Enter location (e.g., Bratislava, Prague...)"
                      value={location}
                      onChange={handleLocationChange}
                      style={{ 
                        width: "100%", 
                        padding: "0.5rem", 
                        borderRadius: "4px", 
                        border: "1px solid #ccc",
                        fontSize: "0.95rem"
                      }}
                    />
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
                  />
                  House
                </label>
              </div>
            </div>

            {/* Apply Button */}
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
        )}

        {/* Offers List */}
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
      </main>
    </div>
  );
}

export default OffersPage;