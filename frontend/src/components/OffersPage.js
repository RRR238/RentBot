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
  const [locations, setLocations] = useState([""]);

  const [showFilters, setShowFilters] = useState(false);

  const [appliedFilters, setAppliedFilters] = useState({
    maxPrice: 5000,
    minPrice: 0,
    size: { from: "", to: "" },
    selectedTypes: [],
    locations: [""]
  });

  useEffect(() => {
  // Only fetch when appliedFilters actually changes (not on initial mount)
  if (appliedFilters.locations.length > 0) {
    fetchOffers(currentPage, false);
  }
}, [appliedFilters]);

  // Fetch offers (with filters and page)
  // Replace the fetchOffers function with better error handling:
const fetchOffers = (page = currentPage, useCurrentFilters = true) => {
  console.log("fetchOffers called - START");
  setLoading(true);

  const token = localStorage.getItem("jwtToken");
  if (!token) {
    console.log("No token found!");
    setLoading(false);
    navigate("/login");
    return;
  }

  const allTypes = [...flatTypes.map(t => t.key), ...houseTypes.map(t => t.key)];
  
  const filtersToUse = useCurrentFilters ? {
    maxPrice,
    minPrice,
    size,
    selectedTypes,
    locations
  } : appliedFilters;
  
  console.log("Filters to use:", filtersToUse);
  
  const validLocations = filtersToUse.locations.filter(loc => loc.trim() !== "");
  const locationString = validLocations.length === 0 ? "Slovakia" : validLocations.join(",");

  const params = new URLSearchParams({
    page,
    limit: OFFERS_PER_PAGE,
    price_min: filtersToUse.minPrice,
    price_max: filtersToUse.maxPrice,
    size_min: filtersToUse.size.from === "" ? 0 : filtersToUse.size.from,
    size_max: filtersToUse.size.to === "" ? 1000 : filtersToUse.size.to,
    types: filtersToUse.selectedTypes.length === 0 ? allTypes.join(",") : filtersToUse.selectedTypes.join(","),
    locations: locationString,
  });

  const url = `http://localhost:5000/offers?${params.toString()}`;
  console.log("Fetching URL:", url);

  fetch(url, {
    method: "GET",
    headers: {
      "Authorization": `Bearer ${token}`,
      "Content-Type": "application/json"
    },
  })
    .then(res => {
      console.log("Response received:", res.status, res.statusText);
      
      if (res.status === 401) {
        navigate("/login");
        return null;
      }
      
      if (res.status === 404) {
        console.log("404 - No offers found");
        setOffers([]);
        setTotalPages(1);
        setLoading(false);
        return null;
      }

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}: ${res.statusText}`);
      }

      return res.json();
    })
    .then(data => {
      console.log("JSON data:", data);
      if (!data) {
        setLoading(false);
        return;
      }
      
      let offersArray = [];
      if (Array.isArray(data)) {
        offersArray = data;
      } else if (data.offers && Array.isArray(data.offers)) {
        offersArray = data.offers;
      } else if (data.data && Array.isArray(data.data)) {
        offersArray = data.data;
      }
      
      console.log("Final offers:", offersArray);
      setOffers(offersArray);
      setTotalPages(Math.ceil((data.total || offersArray.length || 0) / OFFERS_PER_PAGE));
      setLoading(false);
    })
    .catch(error => {
      console.error("FETCH ERROR:", error);
      setLoading(false);
      setOffers([]); // Set empty array so something shows
    });
};

  // Initial fetch
  useEffect(() => {
    fetchOffers(1, true); // Use current filters for initial load
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
  const newAppliedFilters = {
    maxPrice,
    minPrice,
    size,
    selectedTypes,
    locations
  };
  
  setAppliedFilters(newAppliedFilters); // This will trigger the useEffect above
  setCurrentPage(1);
  setShowFilters(false);
};

  const handleToggleFilters = () => {
    if (showFilters) {
      // Hiding filters - reset to applied values
      setMaxPrice(appliedFilters.maxPrice);
      setMinPrice(appliedFilters.minPrice);
      setSize(appliedFilters.size);
      setSelectedTypes(appliedFilters.selectedTypes);
      setLocations(appliedFilters.locations);
    }
    setShowFilters(!showFilters);
  };

  const handleLocationChange = (index, value) => {
    const newLocations = [...locations];
    newLocations[index] = value;
    setLocations(newLocations);
  };

  const handleAddLocation = () => {
    setLocations([...locations, ""]);
  };

  const handleRemoveLocation = (index) => {
    if (locations.length > 1) {
      const newLocations = locations.filter((_, i) => i !== index);
      setLocations(newLocations);
    }
  };

  const handlePrevPage = () => {
    if (currentPage > 1) {
      const newPage = currentPage - 1;
      setCurrentPage(newPage);
      fetchOffers(newPage, false); // Use applied filters for pagination
    }
  };

  const handleNextPage = () => {
    if (currentPage < totalPages) {
      const newPage = currentPage + 1;
      setCurrentPage(newPage);
      fetchOffers(newPage, false); // Use applied filters for pagination
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