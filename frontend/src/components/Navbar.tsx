"use client"

import type React from "react"
import { Link, useNavigate } from "react-router-dom"
import { useAuth } from "../contexts/AuthContext"
import { LogOut, User, Calendar } from "lucide-react"
import NotificationSystem from "./NotificationSystem"

const Navbar: React.FC = () => {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate("/")
  }

  return (
    <nav className="bg-white shadow-lg">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          <Link to="/" className="text-xl font-bold text-blue-600">
            BookingSystem
          </Link>

          <div className="flex items-center space-x-4">
            {user ? (
              <>
                <Link 
                  to={user.role === "facilitator" ? "/facilitator" : "/dashboard"} 
                  className="flex items-center space-x-1 text-gray-700 hover:text-blue-600"
                >
                  <User size={18} />
                  <span>Dashboard</span>
                </Link>

                <Link to="/sessions" className="flex items-center space-x-1 text-gray-700 hover:text-blue-600">
                  <Calendar size={18} />
                  <span>Sessions</span>
                </Link>

                {user.role === "user" && (
                  <Link to="/bookings" className="flex items-center space-x-1 text-gray-700 hover:text-blue-600">
                    <Calendar size={18} />
                    <span>My Bookings</span>
                  </Link>
                )}

                {/* Add NotificationSystem here */}
                <NotificationSystem />

                <div className="flex items-center space-x-2">
                  <span className="text-gray-700">Hello, {user.name}</span>
                  <button
                    onClick={handleLogout}
                    className="flex items-center space-x-1 text-gray-700 hover:text-red-600"
                  >
                    <LogOut size={18} />
                    <span>Logout</span>
                  </button>
                </div>
              </>
            ) : (
              <>
                <Link to="/login" className="text-gray-700 hover:text-blue-600">
                  Login
                </Link>
                <Link to="/register" className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">
                  Register
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  )
}

export default Navbar
