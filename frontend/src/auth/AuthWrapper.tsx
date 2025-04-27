import { createContext, useContext } from 'react';
import {Amplify} from 'aws-amplify';
import { updateUserAttributes, fetchUserAttributes } from 'aws-amplify/auth';
// @ts-expect-error aws-exports.js is a JavaScript file and not typed
import awsExports from '../aws-exports';
import "@aws-amplify/ui-react/styles.css";
import { withAuthenticator } from '@aws-amplify/ui-react';
import {AuthContextType, userAttributesType} from './types';


// Configure Amplify
Amplify.configure(awsExports);








const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
      throw new Error('useAuth must be used within an AuthWrapper');
  }
  return context;
};


// @ts-expect-error Amplify is not typed
function AuthWrapper({ user, signOut, children }) {


  const getUserAttributesFn = async (): Promise<userAttributesType> => {
    try {
      const attributes = await fetchUserAttributes();
      return {
        email: attributes.email || '',
        email_verified: (attributes.email_verified === 'true' ? 'true' : 'false') as 'true' | 'false',
        family_name: attributes.family_name || '',
        name: attributes.name || '',
        phone_number: attributes.phone_number || '',
        phone_number_verified: (attributes.phone_number_verified === 'true' ? 'true' : 'false') as 'true' | 'false',
        sub: attributes.sub || '',
      };
    } catch (error) {
      console.error('Failed to fetch user attributes:', error);
      throw error;
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        signOut,
        updateUserAttributes: async (attributes: { [key: string]: string }) => {
          await updateUserAttributes({ userAttributes: attributes });
        },
        getUserAttributes: getUserAttributesFn,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export default withAuthenticator(AuthWrapper);