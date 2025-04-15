
import React, { createContext, useContext } from 'react';
import {Amplify} from 'aws-amplify';
// @ts-expect-error aws-exports.js is a JavaScript file and not typed
import awsExports from '../aws-exports';
import "@aws-amplify/ui-react/styles.css";
import { withAuthenticator } from '@aws-amplify/ui-react';


// Configure Amplify
Amplify.configure(awsExports);



interface AuthContextType {
  user: {
    signInDetails: {
      loginId: string;
      authFlowType: string;
    };
    username: string;
    userId: string;
  };   
  signOut: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
      throw new Error('useAuth must be used within an AuthWrapper');
  }
  return context;
};

// @ts-expect-error Amplify is not typed
function AuthWrapper({user, signOut, children}) {
  return (
    <>
      <AuthContext.Provider value={{ user, signOut }}>
          {children}
      </AuthContext.Provider>
    </>
  )
}

export default withAuthenticator(AuthWrapper);
