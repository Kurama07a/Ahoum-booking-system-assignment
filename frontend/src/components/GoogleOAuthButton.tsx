import React from 'react';
import { GoogleLogin } from '@react-oauth/google';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-hot-toast';

interface GoogleOAuthButtonProps {
  onSuccess?: () => void;
  onError?: (error: any) => void;
}

const GoogleOAuthButton: React.FC<GoogleOAuthButtonProps> = ({ onSuccess, onError }) => {
  const { googleLogin } = useAuth();
  const navigate = useNavigate();

  const handleGoogleSuccess = async (credentialResponse: any) => {
    try {
      // Decode the JWT token to get user info
      const credential = credentialResponse.credential;
      const payload = JSON.parse(atob(credential.split('.')[1]));
      
      const googleData = {
        sub: payload.sub,
        email: payload.email,
        name: payload.name,
        picture: payload.picture
      };

      await googleLogin(googleData);
      toast.success('Google login successful!');
      navigate('/dashboard');
      
      if (onSuccess) {
        onSuccess();
      }
    } catch (error: any) {
      console.error('Google login error:', error);
      toast.error(error.response?.data?.error || 'Google login failed');
      
      if (onError) {
        onError(error);
      }
    }
  };

  const handleGoogleError = () => {
    toast.error('Google login failed. Please try again.');
    if (onError) {
      onError(new Error('Google login failed'));
    }
  };

  return (
    <div className="w-full">
      <GoogleLogin
        onSuccess={handleGoogleSuccess}
        onError={handleGoogleError}
        theme="filled_blue"
        size="large"
        text="signin_with"
        shape="rectangular"
        width="100%"
      />
    </div>
  );
};

export default GoogleOAuthButton;
