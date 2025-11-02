// ============================================
// STEP 1: Create Context (Reusable)
// ============================================
import { createContext } from "react";
export const AuthContext = createContext(null);


// ============================================
// STEP 2: Provider (Shared Value) - Reusable
// ============================================
import { AuthContext } from "./AuthContext";

const AuthProvider = ({ children }) => {  
    const value = {
        // object that shares to others
        user: null,
        login: () => {},
        logout: () => {}
    };
    
    return (
        <AuthContext value={value}>
            {children} 
        </AuthContext>
    );
};

export default AuthProvider;


// ============================================
// STEP 3: Wrap the Provider
// ============================================
<StrictMode>
    <AuthProvider>
        <RouterProvider router={router} />
    </AuthProvider>
</StrictMode>


// ============================================
// STEP 4: Use or Access the Data
// ============================================
import { use } from "react";
import { AuthContext } from "./AuthContext";

const { user, login, logout } = use(AuthContext);