import LoginPage from "./components/login";
import RegisterPage from "./components/register";
import "./utils/fetches";

function App() {
  return (
    <div className="container mx-auto p-1 bg-gray-200 dark:bg-black w-full h-full">
      {/* <LoginPage /> */}
      <RegisterPage />
    </div>
  );
}
export default App;
