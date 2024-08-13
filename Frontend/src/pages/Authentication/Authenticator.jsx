import React, { useState, useEffect, useRef } from "react";
import BIRDS from "vanta/dist/vanta.waves.min";
import * as THREE from "three";
import "../../assets/Styles/auth.scss";
import { Route, Routes } from "react-router-dom";
import Register from "../userSide/UserRegiser";
import UserLogin from "../userSide/UserLogin";
import ResetPasswordPage from "../userSide/ResetPassword";
import PrivateRoute from "../../components/Private/PrivateRoute";


const Authenticator = () => {
  const [vantaEffect, setVantaEffect] = useState(0);
  const vantaRef = useRef(null);

  useEffect(() => {
    if (!vantaEffect) {
      setVantaEffect(
        BIRDS({
          el: vantaRef.current,
          THREE: THREE,
          mouseControls: true,
          touchControls: true,
          gyroControls: false,
          minHeight: 200.0,
          minWidth: 200.0,
          scale: 1.0,
          scaleMobile: 1.0,
          color: 0x10384f,
          waveSpeed: 1.3,
        })
      );
    }
    return () => {
      if (vantaEffect) vantaEffect.destroy();
    };
  }, [vantaEffect]);
  return (
    <div className="auth" ref={vantaRef}>
      <p style={{ color: "#fff", paddingTop: "20px" }}>
        <Routes>

          

          <Route path="/login" element={<PrivateRoute><UserLogin /></PrivateRoute>} />
          
        </Routes>
      </p>
    </div>
  );
};

export default Authenticator;
