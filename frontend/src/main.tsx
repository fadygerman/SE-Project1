import './index.css'
import App from './App'
import ReactDOM from 'react-dom/client'


// Render the app
const rootElement = document.getElementById('root')!
if (!rootElement.innerHTML) {
    const root = ReactDOM.createRoot(rootElement)
    root.render(
        <div>
        <App signOut={undefined} user={undefined}></App>
        </div>
        
    )
}
