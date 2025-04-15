import {Amplify} from "aws-amplify";
import { withAuthenticator } from "@aws-amplify/ui-react";
import "@aws-amplify/ui-react/styles.css";
// @ts-expect-error aws-exports.js is a JavaScript file and not typed
import awsExports from "./aws-exports.js";
Amplify.configure(awsExports);




// ts-expect-error Amplify is not typed
function App() {

  return (
    <>
      <div>
          <h1>Welcome</h1>
      </div>
    </>
  )
}

export default withAuthenticator(App);
