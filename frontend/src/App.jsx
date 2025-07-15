import React from 'react';
import './NxtFarmLandingPage.css'

function App() {
  
  return (
    <div className="flex flex-col items-center justify-center text-gray-100 select-none relative min-h-screen greenwave-bg">
      <div className="bg-future-glow"></div>

      <main className="flex flex-col items-center justify-center w-full min-h-screen p-6 z-10 relative">
        <h1 className="text-4xl md:text-5xl future-title font-extrabold mb-9 text-center transition-all duration-700 tracking-wide leading-tight drop-shadow-md">
          Welcome to NxtForm
        </h1>

        {/* Search Bar */}
        <div className="search-animate search-future bg-[#101615]/95 rounded-2xl p-5 w-full max-w-xl shadow-2xl border border-[#54ffbc] flex items-center focus-within:ring-2 focus-within:ring-[#22ffc4] transition backdrop-blur-lg">
          <input
            type="text"
            placeholder="Search seeds, weather, mandi price, crop advisory…"
            className="w-full future-font text-base bg-transparent outline-none px-3 py-2 text-[#afffd1] font-semibold placeholder-[#51ffcf] transition focus:placeholder-[#22ffc4]"
          />
          <button
            type="button"
            title="Activate microphone"
            className="mic-animate ml-3 p-2 rounded-full bg-gradient-to-br from-[#22ffc4] to-[#70ffae] hover:from-[#1afdd8] hover:to-[#afffd1] text-[#131d16] transition-all focus:ring-2 focus:ring-[#22ffc4] focus:outline-none shadow-md border border-[#22ffc4]"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <rect x="9" y="5" width="6" height="10" rx="3" />
              <path d="M19 13v1a7 7 0 01-14 0v-1m7 7v-2" strokeLinecap="round" />
            </svg>
          </button>
        </div>

        <hr className="divider" />

        {/* Actions */}
        <div className="suggestion-animate flex flex-wrap gap-4 mb-4 max-w-xl justify-center w-full z-20">
          <button className="action-btn px-6 py-2 bg-[#101615] text-[#22ffc4] rounded-lg">🌾 Weather forecast</button>
          <button className="action-btn px-6 py-2 bg-[#0e1614] text-[#22ffc4] rounded-lg">💹 Mandi rates</button>
          <button className="action-btn px-6 py-2 bg-[#161d18] text-[#51ffcf] rounded-lg">🧬 Buy seeds</button>
          <button className="action-btn px-6 py-2 bg-[#191c19] text-[#70ffae] rounded-lg">📋 Crop advisory</button>
          <button className="action-btn px-6 py-2 bg-[#181e19] text-[#afffd1] rounded-lg">🏬 Find agri shops</button>
        </div>

        <div className="mt-8 text-center">
          <span className="inline-block bg-gradient-to-r from-[#101615] to-[#161d18] text-[#22ffc4] px-6 py-3 rounded-2xl font-semibold text-lg shadow-md border border-[#51ffcf] future-font">
            <span className="font-extrabold text-[#51ffcf]">NxtFarm:</span> Empowering Farmers With Digital Intelligence & Next-Gen Insights.
          </span>
        </div>
      </main>
    </div>

  )
}

export default App;
