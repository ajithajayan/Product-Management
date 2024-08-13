import React, { useEffect, useRef } from "react";
import { Link } from "react-router-dom";
import DoctorConsultation from "../../../assets/tailor/tail3.png";
import banner2 from "../../../assets/tailor/tail4.png";

function BannerSection2() {

  const consultationRef = useRef(null);
  const patientRef = useRef(null);

  useEffect(() => {
    const handleScroll = () => {
      const consultationOffset = consultationRef.current.offsetTop;
      const patientOffset = patientRef.current.offsetTop;
      const scrollPosition = window.pageYOffset;

      const consultationParallax = (scrollPosition - consultationOffset) * 0.4;
      const patientParallax = (scrollPosition - patientOffset) * 0.4;

      consultationRef.current.style.backgroundPositionY = `${consultationParallax}px`;
      patientRef.current.style.backgroundPositionY = `${patientParallax}px`;
    };

    window.addEventListener("scroll", handleScroll);
    return () => {
      window.removeEventListener("scroll", handleScroll);
    };
  }, [])
  return (

    <div>
    <div
      ref={consultationRef}
      className="relative bg-gradient-to-r from-purple-600 to-blue-600 h-screen text-white overflow-hidden"
      style={{
        backgroundImage: `url(${DoctorConsultation})`,
        backgroundSize: "cover",
      }}
    >
      <div className="absolute inset-0 bg-black opacity-50"></div>
      <div className="relative z-10 flex flex-col justify-center items-center h-full text-center">
        <h1 className="text-5xl font-bold leading-tight mb-4">
          Welcome to CSRM
        </h1>
        <p className="text-lg text-gray-300 mb-8">
        Experience the finest tailoring services crafted just for you.
        </p>
        <Link
          to="/create-order"
          className="bg-yellow-400 text-gray-900 hover:bg-yellow-300 py-2 px-6 rounded-full text-lg font-semibold transition duration-300 ease-in-out transform hover:scale-105 hover:shadow-lg"
        >
          Explore
        </Link>
      </div>
    </div>
    <div
      ref={patientRef}
      className="relative bg-gradient-to-r from-purple-600 to-blue-600 h-screen text-white overflow-hidden"
      style={{
        backgroundImage: `url(${banner2})`,
        backgroundSize: "cover",
      }}
    >
      <div className="absolute inset-0 bg-black opacity-50"></div>
      <div className="relative z-10 flex flex-col justify-center items-center h-full text-center">
        <h1 className="text-5xl font-bold leading-tight mb-4">
        Update Your Measurements
        </h1>
        <p className="text-lg text-gray-300 mb-8">
        Ensure a perfect fit with our precise measurement updates.
        </p>
        <Link
          to="/orders"
          className="bg-yellow-400 text-gray-900 hover:bg-yellow-300 py-2 px-6 rounded-full text-lg font-semibold transition duration-300 ease-in-out transform hover:scale-105 hover:shadow-lg"
        >
          Update Now
        </Link>
      </div>
    </div>
  </div>
   
  );
}

export default BannerSection2;
