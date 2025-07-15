import type React from "react"
import { createContext, useContext, useState, useEffect } from "react"
import axios from "axios"
import { buildApiUrl, API_CONFIG } from "../config/api"

interface User {
  id: number
  email: string
  name: string
  role: string
}

interface AuthContextType {
  user: User | null
  token: string | null
  login: (email: string, password: string) => Promise<void>
  register: (userData: any) => Promise<void>
  googleLogin: (googleData: any) => Promise<void>
  logout: () => void
  loading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(localStorage.getItem("token"))
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (token) {
      axios.defaults.headers.common["Authorization"] = `Bearer ${token}`
      // In a real app, you might want to validate the token here
    }
    setLoading(false)
  }, [token])

  const login = async (email: string, password: string) => {
    try {
      const response = await axios.post(buildApiUrl(API_CONFIG.ENDPOINTS.auth.login), {
        email,
        password,
      })

      const { access_token, user: userData } = response.data
      setToken(access_token)
      setUser(userData)
      localStorage.setItem("token", access_token)
      localStorage.setItem("user", JSON.stringify(userData))
      axios.defaults.headers.common["Authorization"] = `Bearer ${access_token}`
    } catch (error) {
      throw error
    }
  }

  const register = async (userData: any) => {
    try {
      const response = await axios.post(buildApiUrl(API_CONFIG.ENDPOINTS.auth.register), userData)

      const { access_token, user: newUser } = response.data
      setToken(access_token)
      setUser(newUser)
      localStorage.setItem("token", access_token)
      localStorage.setItem("user", JSON.stringify(newUser))
      axios.defaults.headers.common["Authorization"] = `Bearer ${access_token}`
    } catch (error) {
      throw error
    }
  }

  const googleLogin = async (googleData: any) => {
    try {
      const response = await axios.post(buildApiUrl(API_CONFIG.ENDPOINTS.auth.google), {
        google_id: googleData.sub,
        email: googleData.email,
        name: googleData.name,
      })

      const { access_token, user: userData } = response.data
      setToken(access_token)
      setUser(userData)
      localStorage.setItem("token", access_token)
      localStorage.setItem("user", JSON.stringify(userData))
      axios.defaults.headers.common["Authorization"] = `Bearer ${access_token}`
    } catch (error) {
      throw error
    }
  }

  const logout = () => {
    setToken(null)
    setUser(null)
    localStorage.removeItem("token")
    localStorage.removeItem("user")
    delete axios.defaults.headers.common["Authorization"]
  }

  // Load user from localStorage on mount
  useEffect(() => {
    const savedUser = localStorage.getItem("user")
    if (savedUser && token) {
      setUser(JSON.parse(savedUser))
    }
  }, [token])

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        login,
        register,
        googleLogin,
        logout,
        loading,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}
