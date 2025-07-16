"use client"

import type React from "react"
import { useState, useEffect } from "react"
import { useAuth } from "../contexts/AuthContext"
import { Link } from "react-router-dom"
import axios from "axios"
import { 
  Calendar, 
  Users, 
  DollarSign, 
  Plus,
  Edit3,
  Trash2,
  Eye,
  Bell,
  Clock,
  CheckCircle
} from "lucide-react"

interface FacilitatorMetrics {
  total_sessions: number
  active_sessions: number
  total_bookings: number
  total_revenue: number
  upcoming_sessions: number
}

interface Session {
  id: number
  title: string
  description: string
  session_type: string
  start_time: string
  end_time: string
  capacity: number
  price: number
  status: string
  bookings_count: number
  available_spots: number
  created_at: string
}

interface RecentBooking {
  id: number
  user: {
    name: string
    email: string
  }
  session: {
    title: string
    start_time: string
  }
  booking_date: string
  status: string
}

const FacilitatorDashboard: React.FC = () => {
  const { user } = useAuth()
  const [metrics, setMetrics] = useState<FacilitatorMetrics>({
    total_sessions: 0,
    active_sessions: 0,
    total_bookings: 0,
    total_revenue: 0,
    upcoming_sessions: 0
  })
  const [sessions, setSessions] = useState<Session[]>([])
  const [recentBookings, setRecentBookings] = useState<RecentBooking[]>([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'overview' | 'sessions' | 'bookings'>('overview')
  const [editingSession, setEditingSession] = useState<Session | null>(null)
  const [isEditModalOpen, setIsEditModalOpen] = useState(false)
  const [editFormData, setEditFormData] = useState({
    title: '',
    description: '',
    session_type: '',
    start_time: '',
    end_time: '',
    capacity: 1,
    price: 0
  })

  useEffect(() => {
    fetchDashboardData()
    fetchSessions()
    
    // Set up real-time updates for bookings
    const interval = setInterval(() => {
      fetchDashboardData()
    }, 10000) // Update every 10 seconds

    return () => clearInterval(interval)
  }, [])

  const fetchDashboardData = async () => {
    try {
      const response = await axios.get("http://localhost:5000/api/facilitator/dashboard")
      setMetrics(response.data.metrics)
      setRecentBookings(response.data.recent_bookings)
    } catch (error) {
      console.error("Failed to fetch dashboard data:", error)
    } finally {
      setLoading(false)
    }
  }

  const fetchSessions = async () => {
    try {
      const response = await axios.get("http://localhost:5000/api/facilitator/sessions")
      setSessions(response.data)
    } catch (error) {
      console.error("Failed to fetch sessions:", error)
    }
  }

  const handleDeleteSession = async (sessionId: number) => {
    if (window.confirm('Are you sure you want to cancel this session? This action cannot be undone.')) {
      try {
        await axios.delete(`http://localhost:5000/api/facilitator/sessions/${sessionId}`)
        fetchSessions() // Refresh the sessions list
        fetchDashboardData() // Refresh metrics
      } catch (error) {
        console.error('Failed to cancel session:', error)
        alert('Failed to cancel session. Please try again.')
      }
    }
  }

  const handleEditSession = (session: Session) => {
    setEditingSession(session)
    setEditFormData({
      title: session.title,
      description: session.description,
      session_type: session.session_type,
      start_time: new Date(session.start_time).toISOString().slice(0, 16),
      end_time: new Date(session.end_time).toISOString().slice(0, 16),
      capacity: session.capacity,
      price: session.price
    })
    setIsEditModalOpen(true)
  }

  const handleUpdateSession = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!editingSession) return

    try {
      await axios.put(`http://localhost:5000/api/sessions/${editingSession.id}`, editFormData)
      setIsEditModalOpen(false)
      setEditingSession(null)
      fetchSessions() // Refresh the sessions list
      fetchDashboardData() // Refresh metrics
      alert('Session updated successfully!')
    } catch (error) {
      console.error('Failed to update session:', error)
      alert('Failed to update session. Please try again.')
    }
  }

  const handleCloseEditModal = () => {
    setIsEditModalOpen(false)
    setEditingSession(null)
  }

  const formatDateTime = (dateTime: string) => {
    return new Date(dateTime).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount)
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800'
      case 'cancelled':
        return 'bg-red-100 text-red-800'
      case 'confirmed':
        return 'bg-blue-100 text-blue-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  if (loading) {
    return <div className="flex justify-center items-center h-64">Loading facilitator dashboard...</div>
  }

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Facilitator Dashboard</h1>
        <p className="text-gray-600 mt-2">Welcome back, {user?.name}! Manage your sessions and track your performance</p>
      </div>

      {/* Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Sessions</p>
              <p className="text-2xl font-bold text-gray-900">{metrics.total_sessions}</p>
            </div>
            <Calendar className="text-blue-600" size={24} />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Active Sessions</p>
              <p className="text-2xl font-bold text-gray-900">{metrics.active_sessions}</p>
            </div>
            <CheckCircle className="text-green-600" size={24} />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Bookings</p>
              <p className="text-2xl font-bold text-gray-900">{metrics.total_bookings}</p>
            </div>
            <Users className="text-purple-600" size={24} />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Revenue</p>
              <p className="text-2xl font-bold text-gray-900">{formatCurrency(metrics.total_revenue)}</p>
            </div>
            <DollarSign className="text-green-600" size={24} />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Upcoming</p>
              <p className="text-2xl font-bold text-gray-900">{metrics.upcoming_sessions}</p>
            </div>
            <Clock className="text-orange-600" size={24} />
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="mb-6">
        <nav className="flex space-x-8" aria-label="Tabs">
          <button
            onClick={() => setActiveTab('overview')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'overview'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            Overview
          </button>
          <button
            onClick={() => setActiveTab('sessions')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'sessions'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            My Sessions
          </button>
          <button
            onClick={() => setActiveTab('bookings')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'bookings'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            Recent Bookings
          </button>
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Quick Actions */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
            <div className="space-y-3">
              <Link
                to="/sessions/create"
                className="flex items-center w-full bg-blue-600 text-white py-3 px-4 rounded-md hover:bg-blue-700"
              >
                <Plus size={20} className="mr-2" />
                Create New Session
              </Link>
              <button
                onClick={() => setActiveTab('sessions')}
                className="flex items-center w-full border border-blue-600 text-blue-600 py-3 px-4 rounded-md hover:bg-blue-50"
              >
                <Edit3 size={20} className="mr-2" />
                Manage Sessions
              </button>
              <button
                onClick={() => setActiveTab('bookings')}
                className="flex items-center w-full border border-green-600 text-green-600 py-3 px-4 rounded-md hover:bg-green-50"
              >
                <Eye size={20} className="mr-2" />
                View All Bookings
              </button>
            </div>
          </div>

          {/* Recent Bookings Panel */}
          <div className="lg:col-span-2 bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold">Latest Bookings</h2>
              <Bell className="text-gray-400" size={20} />
            </div>
            {recentBookings.length === 0 ? (
              <p className="text-gray-500 text-center py-8">No recent bookings</p>
            ) : (
              <div className="space-y-4 max-h-96 overflow-y-auto">
                {recentBookings.map((booking) => (
                  <div key={booking.id} className="border border-gray-200 rounded-md p-4 hover:bg-gray-50">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex items-center mb-2">
                          <Users size={16} className="text-gray-400 mr-2" />
                          <span className="font-medium">{booking.user.name}</span>
                        </div>
                        <div className="flex items-center mb-2">
                          <Calendar size={16} className="text-gray-400 mr-2" />
                          <span className="text-sm text-gray-600">{booking.session.title}</span>
                        </div>
                        <div className="flex items-center">
                          <Clock size={16} className="text-gray-400 mr-2" />
                          <span className="text-sm text-gray-500">
                            Booked on {formatDateTime(booking.booking_date)}
                          </span>
                        </div>
                      </div>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(booking.status)}`}>
                        {booking.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {activeTab === 'sessions' && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-semibold">My Sessions</h2>
            <Link
              to="/sessions/create"
              className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 flex items-center"
            >
              <Plus size={20} className="mr-2" />
              Create Session
            </Link>
          </div>
          
          {sessions.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No sessions created yet</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Session
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Schedule
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Bookings
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Revenue
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {sessions.map((session) => (
                    <tr key={session.id}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div>
                          <div className="text-sm font-medium text-gray-900">{session.title}</div>
                          <div className="text-sm text-gray-500">{session.description}</div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="capitalize text-sm text-gray-900">{session.session_type}</span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {formatDateTime(session.start_time)}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {session.bookings_count} / {session.capacity}
                        </div>
                        <div className="text-sm text-gray-500">
                          {session.available_spots} spots left
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {formatCurrency(session.price * session.bookings_count)}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(session.status)}`}>
                          {session.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <div className="flex space-x-2">
                          <button 
                            onClick={() => handleEditSession(session)}
                            className="text-blue-600 hover:text-blue-900"
                          >
                            <Edit3 size={16} />
                          </button>
                          <button 
                            onClick={() => handleDeleteSession(session.id)}
                            className="text-red-600 hover:text-red-900"
                          >
                            <Trash2 size={16} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {activeTab === 'bookings' && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-6">All Bookings</h2>
          {recentBookings.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No bookings yet</p>
          ) : (
            <div className="space-y-4">
              {recentBookings.map((booking) => (
                <div key={booking.id} className="border border-gray-200 rounded-md p-4">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center mb-2">
                        <Users size={16} className="text-gray-400 mr-2" />
                        <span className="font-medium">{booking.user.name}</span>
                        <span className="text-sm text-gray-500 ml-2">({booking.user.email})</span>
                      </div>
                      <div className="flex items-center mb-2">
                        <Calendar size={16} className="text-gray-400 mr-2" />
                        <span className="text-sm text-gray-600">{booking.session.title}</span>
                      </div>
                      <div className="flex items-center mb-2">
                        <Clock size={16} className="text-gray-400 mr-2" />
                        <span className="text-sm text-gray-500">
                          Session: {formatDateTime(booking.session.start_time)}
                        </span>
                      </div>
                      <div className="flex items-center">
                        <Bell size={16} className="text-gray-400 mr-2" />
                        <span className="text-sm text-gray-500">
                          Booked: {formatDateTime(booking.booking_date)}
                        </span>
                      </div>
                    </div>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(booking.status)}`}>
                      {booking.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Edit Session Modal */}
      {isEditModalOpen && (
        <div className="fixed inset-0 flex items-center justify-center z-50">
          <div className="bg-black bg-opacity-50 absolute inset-0" onClick={handleCloseEditModal}></div>
          <div className="bg-white rounded-lg shadow-md p-6 max-w-lg w-full z-10">
            <h2 className="text-xl font-semibold mb-4">Edit Session</h2>
            <form onSubmit={handleUpdateSession}>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Title</label>
                  <input
                    type="text"
                    value={editFormData.title}
                    onChange={(e) => setEditFormData({ ...editFormData, title: e.target.value })}
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:ring focus:ring-blue-500 focus:border-blue-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Description</label>
                  <textarea
                    value={editFormData.description}
                    onChange={(e) => setEditFormData({ ...editFormData, description: e.target.value })}
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:ring focus:ring-blue-500 focus:border-blue-500"
                    rows={3}
                    required
                  ></textarea>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Session Type</label>
                  <select
                    value={editFormData.session_type}
                    onChange={(e) => setEditFormData({ ...editFormData, session_type: e.target.value })}
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:ring focus:ring-blue-500 focus:border-blue-500"
                    required
                  >
                    <option value="">Select Session Type</option>
                    <option value="session">Session</option>
                    <option value="retreat">Retreat</option>
                  </select>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Start Time</label>
                    <input
                      type="datetime-local"
                      value={editFormData.start_time}
                      onChange={(e) => setEditFormData({ ...editFormData, start_time: e.target.value })}
                      className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:ring focus:ring-blue-500 focus:border-blue-500"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">End Time</label>
                    <input
                      type="datetime-local"
                      value={editFormData.end_time}
                      onChange={(e) => setEditFormData({ ...editFormData, end_time: e.target.value })}
                      className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:ring focus:ring-blue-500 focus:border-blue-500"
                      required
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Capacity</label>
                    <input
                      type="number"
                      value={editFormData.capacity}
                      onChange={(e) => setEditFormData({ ...editFormData, capacity: Number(e.target.value) })}
                      className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:ring focus:ring-blue-500 focus:border-blue-500"
                      min={1}
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Price</label>
                    <input
                      type="number"
                      value={editFormData.price}
                      onChange={(e) => setEditFormData({ ...editFormData, price: Number(e.target.value) })}
                      className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:ring focus:ring-blue-500 focus:border-blue-500"
                      min={0}
                      step={0.01}
                      required
                    />
                  </div>
                </div>
                <div className="flex justify-end space-x-2">
                  <button
                    type="button"
                    onClick={handleCloseEditModal}
                    className="px-4 py-2 bg-gray-200 rounded-md hover:bg-gray-300"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                  >
                    Update Session
                  </button>
                </div>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default FacilitatorDashboard
