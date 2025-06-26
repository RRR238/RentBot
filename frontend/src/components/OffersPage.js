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
  const [size, setSize] = useState({ from: "", to: "" });
  const [selectedTypes, setSelectedTypes] = useState([]);
  const [rooms, setRooms] = useState("");

  // Fetch offers (with filters and page)
  const fetchOffers = (page = currentPage) => {
    setLoading(true);
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
  fetch(`http://localhost:5000/offers?${params.toString()}`)
    .then(res => res.json())
    .then(data => {
      setOffers(data.offers || []);
      setTotalPages(Math.ceil(data.total / OFFERS_PER_PAGE));
      setLoading(false);
    })
    .catch(() => setLoading(false));
  */
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

  const handleMaxPriceChange = (e) => {
    setMaxPrice(Number(e.target.value));
  };

  const handleSizeChange = (e) => {
    setSize({ ...size, [e.target.name]: e.target.value });
  };

  const handleRoomsChange = (e) => setRooms(e.target.value);

  const handleSearch = () => {
    setCurrentPage(1);
    fetchOffers(1);
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
          
          {/* Search Button */}
          <div>
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
            >
              Search
            </button>
          </div>
        </div>
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