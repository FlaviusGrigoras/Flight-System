import { useAuth } from "../context/AuthContext";
import { Link } from "react-router-dom";

export default function HomePage() {
  const { user, isLoading, logout } = useAuth();

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <h1>Home page</h1>
      {user ? (
        <div>
          <p>
            Hello {user.username}! You are logged in with the role: {user.role}
          </p>
          {user.role === "airline" && (
            <p>
              <Link to="/airline/dashboard">Go to airline dashboard</Link>
            </p>
          )}
          <button type="button" onClick={logout}>
            Logout
          </button>
        </div>
      ) : (
        <div>
          <p>You are not logged in! Please log in</p>
        </div>
      )}
    </div>
  );
}
