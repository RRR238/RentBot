import React, { useEffect, useState } from "react";

function OfferCard({ offer }) {
  // const [preview, setPreview] = useState(null);
  console.log("OfferCard received:", offer);

   useEffect(() => {
  //   fetch(`https://api.microlink.io/?url=${encodeURIComponent(offer.source_url)}`)
  //     .then(res => res.json())
  //     .then(data => setPreview(data.data));
   }, [offer.source_url]);

  return (
    <div
      style={{
        width: "600px",
        minHeight: "350px",
        background: "#fff",
        borderRadius: "12px",
        boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        padding: "1rem",
      }}
    >
      {offer && offer.preview_image && (
        <img
          src={offer.preview_image}
          alt={offer.title}
          style={{ width: "100%", height: "220px", objectFit: "cover", borderRadius: "8px" }}
        />
      )}
      <a
        href={offer.source_url}
        target="_blank"
        rel="noopener noreferrer"
        style={{
          fontWeight: "bold",
          color: "#007bff",
          textAlign: "center",
          margin: "0.5rem 0",
          textDecoration: "none",
          wordBreak: "break-all",
          fontSize: "1.1rem",
        }}
      >
        {offer ? offer.title : offer.source_url}
      </a>
      {/* {offer && offer.description && (
        <div style={{ color: "#555", fontSize: "0.95rem", marginBottom: "0.5rem", textAlign: "center" }}>
          {offer.description}
        </div>
      )} */}
      <div style={{ marginTop: "auto", width: "100%", textAlign: "center" }}>
        <div style={{ color: "#333", fontWeight: "bold" }}>{offer.price_total} €</div>
        <div style={{ color: "#666", fontSize: "0.95rem" }}>{offer.location}</div>
      </div>
    </div>
  );
}

export default OfferCard;