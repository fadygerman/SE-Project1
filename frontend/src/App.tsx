import {Amplify} from "aws-amplify";
import { withAuthenticator } from "@aws-amplify/ui-react";
import "@aws-amplify/ui-react/styles.css";
// @ts-expect-error aws-exports.js is a JavaScript file and not typed
import awsExports from "./aws-exports.js";
Amplify.configure(awsExports);

import { RouterProvider, createRouter } from '@tanstack/react-router'

// Import the generated route tree
import { routeTree } from './routeTree.gen'


// Create a new router instance
const router = createRouter({ routeTree })

// Register the router instance for type safety
declare module '@tanstack/react-router' {
    interface Register {
        router: typeof router
    }
}


// @ts-expect-error Amplify is not typed
function App({ signOut, user }) {

  return (
    <>
      <div>
          <RouterProvider router={router} />
          <h1>Hello {user.username}</h1>
          <button onClick={signOut}>ADD SIGN OUT BUTTON -- SIGN OUT</button>
      </div>
    </>
  )
}

export default withAuthenticator(App);
