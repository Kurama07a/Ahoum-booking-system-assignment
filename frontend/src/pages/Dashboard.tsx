"use client"

import type React from "react"
import { useState, useEffect } from "react"
import { useAuth } from "../contexts/AuthContext"
import { Link } from "react-router-dom"
import axios from "axios"
import { buildApiUrl } from "../config/api"
import { Calendar, Users, Clock, TrendingUp } from "lucide-react"

interface DashboardStats {
  totalBookings: number
  upcomingBookings: number
  completedSessions: number
  totalSpent: number
}

const Dashboard: React.FC = () => {
  const { user } = useAuth()
  const [stats, setStats] = useState<DashboardStats>({
    totalBookings: 0,
    upcomingBookings: 0,
    completedSessions: 0,
    totalSpent: 0,
  })
  const [recentBookings, setRecentBookings] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      const response = await axios.get(buildApiUrl("/api/bookings/my"))
      const bookings = response.data

      // Calculate stats
      const now = new Date()
      const upcoming = bookings.filter(
        (booking: any) => new Date(booking.session.start_time) > now && booking.booking_status === "confirmed",
      )
      const completed = bookings.filter(
        (booking: any) => new Date(booking.session.start_time) <= now && booking.booking_status === "confirmed",
      )

      setStats({
        totalBookings: bookings.length,
        upcomingBookings: upcoming.length,
        completedSessions: completed.length,
        totalSpent: 0, // This would be calculated from actual session prices
      })

      setRecentBookings(bookings.slice(0, 3))
    } catch (error) {
      console.error("Failed to fetch dashboard data:", error)
    } finally {
      setLoading(false)
    }
  }

  const formatDateTime = (dateTime: string) => {
    return new Date(dateTime).toLocaleDateString()
  }

  if (loading) {
    return <div className="flex justify-center items-center h-64">Loading dashboard...</div>
  }

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Welcome back, {user?.name}!</h1>
        <p className="text-gray-600 mt-2">Here's your wellness journey overview</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Bookings</p>
              <p className="text-2xl font-bold text-gray-900">{stats.totalBookings}</p>
            </div>
            <Calendar className="text-blue-600" size={24} />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Upcoming</p>
              <p className="text-2xl font-bold text-gray-900">{stats.upcomingBookings}</p>
            </div>
            <Clock className="text-green-600" size={24} />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Completed</p>
              <p className="text-2xl font-bold text-gray-900">{stats.completedSessions}</p>
            </div>
            <Users className="text-purple-600" size={24} />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Growth</p>
              <p className="text-2xl font-bold text-gray-900">+{stats.upcomingBookings}</p>
            </div>
            <TrendingUp className="text-orange-600" size={24} />
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid md:grid-cols-2 gap-8">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
          <div className="space-y-3">
            <Link
              to="/sessions"
              className="block w-full bg-blue-600 text-white py-3 px-4 rounded-md hover:bg-blue-700 text-center"
            >
              Browse Available Sessions
            </Link>
            <Link
              to="/bookings"
              className="block w-full border border-blue-600 text-blue-600 py-3 px-4 rounded-md hover:bg-blue-50 text-center"
            >
              View My Bookings
            </Link>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Recent Bookings</h2>
          {recentBookings.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No bookings yet</p>
          ) : (
            <div className="space-y-3">
              {recentBookings.map((booking: any) => (
                <div key={booking.id} className="border border-gray-200 rounded-md p-3">
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="font-medium">{booking.session.title}</h3>
                      <p className="text-sm text-gray-600">{formatDateTime(booking.session.start_time)}</p>
                    </div>
                    <span
                      className={`px-2 py-1 rounded-full text-xs font-medium ${
                        booking.booking_status === "confirmed"
                          ? "bg-green-100 text-green-800"
                          : "bg-red-100 text-red-800"
                      }`}
                    >
                      {booking.booking_status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Dashboard
