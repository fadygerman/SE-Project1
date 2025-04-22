import React, { useEffect, useState } from 'react';
import { useAuth } from '../auth/AuthWrapper';
import EditProfile from './EditProfile';
import { userAttributesType } from './types';

const Profile: React.FC = () => {
  const { user, signOut, getUserAttributes } = useAuth();

  const [userAttributes, setUserAttributes] = useState<userAttributesType>({
    email: '',
    email_verified: 'false',
    family_name: '',
    name: '',
    phone_number: '',
    phone_number_verified: 'false',
    sub: '',
  });

  const [isHovered, setIsHovered] = useState(false);

  const fetchUser = async (): Promise<userAttributesType> => {
    try {
      const attributes = await getUserAttributes();
      const updatedAttributes = {
        email: attributes.email || '',
        email_verified: (attributes.email_verified === 'true' ? 'true' : 'false') as 'true' | 'false',
        family_name: attributes.family_name || '',
        name: attributes.name || '',
        phone_number: attributes.phone_number || '',
        phone_number_verified: (attributes.phone_number_verified === 'true' ? 'true' : 'false') as 'true' | 'false',
        sub: attributes.sub || '',
      };
      setUserAttributes(updatedAttributes);
      return updatedAttributes;
    } catch (error) {
      console.error('Failed to get user attributes:', error);
      throw error;
    }
  };

  useEffect(() => {
    fetchUser();
  }, []);

  return (
    <div
      className="profile-container"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div className="row">
        <div className="profile-info">
          <h3><b>Profile</b></h3>
          <h2><a href="">{user.signInDetails.loginId}</a></h2>
        </div>
      </div>
      <EditProfile
        userAttributes={userAttributes}
        fetchUser={fetchUser}
        isVisible={isHovered}
      />
      <div className="slide-down">
        <button onClick={signOut} className="sign-out-button">
          <b>Sign out</b>
        </button>
      </div>
    </div>
  );
};

export default Profile;
