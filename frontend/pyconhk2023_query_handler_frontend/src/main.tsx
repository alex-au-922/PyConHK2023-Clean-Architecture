import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'
import { IsLoadingProvider } from "./contexts/isLoading.tsx";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <IsLoadingProvider>
    <App />
  </IsLoadingProvider>
);