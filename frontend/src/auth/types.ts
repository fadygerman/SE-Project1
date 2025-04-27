export interface userAttributesType {
    email: string;
    email_verified: 'true' | 'false';
    family_name: string;
    name: string;
    phone_number: string;
    phone_number_verified: 'true' | 'false';
    sub: string; // unique user ID
}

export interface AuthContextType {
  user: {
    signInDetails: {
      loginId: string;
      authFlowType: string;
    };
    username: string;
    userId: string;
  };

  signOut: () => void;
  updateUserAttributes: (attributes: { [key: string]: string }) => Promise<void>;
  getUserAttributes: () => Promise<userAttributesType>;
}

