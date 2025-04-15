
import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/')({
    component: () => RouteComponent(),
  })
  
function RouteComponent() {
    return(
    <div className="mainPage_div" >
        <h1>
            Welcome to the Car Rental App! <br />
            This is the main page. <br />
        </h1>
    </div>)
  }