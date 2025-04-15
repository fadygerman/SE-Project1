import React from 'react';
import { useAuth } from '../auth/AuthWrapper';  // Assuming you already created the useAuth hook

const Profile: React.FC = () => {
    const { user, signOut } = useAuth();
    // const  [buttonState, setButtonState] = useState(false);

    // const toggleButtonState = () => {
    //     setButtonState(!buttonState);  // Toggle button state
    // }

    return (
        <div className="profile-container">
            <div className="row">
                <div className="profile-info">
                    <h3><b>Profile</b></h3>
                    <h2><a href="">{user.signInDetails.loginId}</a></h2>
                </div>
            </div>
            <div className="slide-down">
                <button onClick={signOut} className="sign-out-button">
                    <b>Sign out</b>
                </button>
            </div>
        </div>
        
        // <div className="profile-container" onMouseEnter={toggleButtonState} onMouseLeave={toggleButtonState}>
        //    <div className="row">
        //         <div className="profile-info">
        //             <h3><b>Profile</b></h3>
        //             <h2><a href="">{user.signInDetails.loginId}</a></h2> {/* email */}
        //         </div>
                
        //     </div>
        //     {buttonState && (
        //         <div  className={`fade-in ${buttonState ? 'visible' : ''}`}>
        //             <button onClick={signOut} className="sign-out-button">
        //                 <b>Sign out</b>
        //             </button>
        //         </div>  
        //     )}
        // </div>
    );
};

export default Profile;
