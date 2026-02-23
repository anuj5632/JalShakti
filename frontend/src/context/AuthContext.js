import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { useGoogleLogin } from '@react-oauth/google';
import axios from 'axios';
import toast from 'react-hot-toast';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

// Helper to safely encode/decode tokens
const encodeToken = (user) => btoa(unescape(encodeURIComponent(JSON.stringify(user))));
const decodeToken = (token) => {
  try {
    return JSON.parse(decodeURIComponent(escape(atob(token))));
  } catch {
    return null;
  }
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [homeSetupComplete, setHomeSetupComplete] = useState(false);

  // Load user from localStorage on mount
  useEffect(() => {
    const loadUser = () => {
      const storedToken = localStorage.getItem('aquaguard_token');
      if (storedToken) {
        const decoded = decodeToken(storedToken);
        if (decoded && decoded.uid) {
          setUser(decoded);
          setHomeSetupComplete(decoded.home_setup_complete || false);
        } else {
          localStorage.removeItem('aquaguard_token');
        }
      }
      setLoading(false);
    };
    loadUser();
  }, []);

  // Google OAuth login
  const googleLogin = useGoogleLogin({
    flow: 'implicit',
    onSuccess: async (codeResponse) => {
      try {
        setLoading(true);
        
        // Get user info from Google
        const googleUserInfo = await axios.get(
          'https://www.googleapis.com/oauth2/v3/userinfo',
          { headers: { Authorization: `Bearer ${codeResponse.access_token}` } }
        );

        const googleUser = {
          uid: googleUserInfo.data.sub,
          email: googleUserInfo.data.email,
          name: googleUserInfo.data.name,
          picture: googleUserInfo.data.picture,
          home_setup_complete: false,
          auth_type: 'google'
        };

        // Save user
        const token = encodeToken(googleUser);
        localStorage.setItem('aquaguard_token', token);
        setUser(googleUser);
        setHomeSetupComplete(false);
        
        toast.success(`Welcome, ${googleUser.name}!`);
      } catch (error) {
        console.error('Google login failed:', error);
        toast.error('Login failed. Please try Demo Mode.');
      } finally {
        setLoading(false);
      }
    },
    onError: (error) => {
      console.error('Google OAuth error:', error);
      toast.error('Google login failed. Try Demo Mode instead.');
      setLoading(false);
    }
  });

  const login = useCallback(() => {
    googleLogin();
  }, [googleLogin]);

  // Demo login - works without any external services
  const demoLogin = useCallback(() => {
    const demoUser = {
      uid: 'demo-' + Date.now(),
      email: 'demo@aquaguard.com',
      name: 'Demo User',
      picture: 'https://ui-avatars.com/api/?name=Demo+User&background=0ea5e9&color=fff&size=200',
      home_setup_complete: false,
      auth_type: 'demo'
    };

    const token = encodeToken(demoUser);
    localStorage.setItem('aquaguard_token', token);
    setUser(demoUser);
    setHomeSetupComplete(false);
    
    toast.success('Welcome to AquaGuard Demo!');
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('aquaguard_token');
    setUser(null);
    setHomeSetupComplete(false);
    toast.success('Logged out successfully');
  }, []);

  const completeHomeSetup = useCallback(async (data) => {
    try {
      const updatedUser = { 
        ...user, 
        ...data, 
        home_setup_complete: true 
      };
      
      const token = encodeToken(updatedUser);
      localStorage.setItem('aquaguard_token', token);
      setUser(updatedUser);
      setHomeSetupComplete(true);
      
      toast.success('Home setup complete!');
      return true;
    } catch (error) {
      console.error('Home setup failed:', error);
      toast.error('Failed to save. Please try again.');
      return false;
    }
  }, [user]);

  const value = {
    user,
    loading,
    homeSetupComplete,
    isAuthenticated: !!user,
    login,
    demoLogin,
    logout,
    completeHomeSetup
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
