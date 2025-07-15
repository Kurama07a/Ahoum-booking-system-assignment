"use client"

import type React from "react"
import { useState, useEffect } from "react"
import axios from "axios"
import { toast } from "react-hot-toast"
import { Calendar, Users, DollarSign } from "lucide-react"
import { buildApiUrl, API_CONFIG } from "../config/api"

interface Session {
  id: number
  title: string
  description: string
  facilitator: string
  session_type: string
  start_time: string
  end_time: string
  capacity: number
  price: number
  available_spots: number
}

const Sessions: React.FC = () => {
  const [sessions, setSessions] = useState<Session[]>([])
  const [loading, setLoading] = useState(true)
  const [bookingLoading, setBookingLoading] = useState<number | null>(null)

  useEffect(() => {
    fetchSessions()
  }, [])

  const fetchSessions = async () => {
    try {
      const response = await axios.get(buildApiUrl(API_CONFIG.ENDPOINTS.sessions))
      setSessions(response.data)
    } catch (error) {
      toast.error("Failed to fetch sessions")
    } finally {
      setLoading(false)
    }
  }

  const handleBookSession = async (sessionId: number) => {
    setBookingLoading(sessionId)
    try {
      await axios.post(buildApiUrl(API_CONFIG.ENDPOINTS.bookings.create), {
        session_id: sessionId,
      })
      toast.success("Session booked successfully!")
      fetchSessions() // Refresh to update available spots
    } catch (error: any) {
      toast.error(error.response?.data?.error || "Booking failed")
    } finally {
      setBookingLoading(null)
    }
  }

  const formatDateTime = (dateTime: string) => {
    return new Date(dateTime).toLocaleString()
  }

  if (loading) {
    return <div className="flex justify-center items-center h-64">Loading sessions...</div>
  }

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-8">Available Sessions & Retreats</h1>

      <div className="grid gap-6 md:grid-cols-2">
        {sessions.map((session) => (
          <div key={session.id} className="bg-white rounded-lg shadow-md p-6">
            <div className="flex justify-between items-start mb-4">
              <h3 className="text-xl font-semibold">{session.title}</h3>
              <span
                className={`px-3 py-1 rounded-full text-sm font-medium ${
                  session.session_type === "retreat" ? "bg-purple-100 text-purple-800" : "bg-blue-100 text-blue-800"
                }`}
              >
                {session.session_type}
              </span>
            </div>

            <p className="text-gray-600 mb-4">{session.description}</p>

            <div className="space-y-2 mb-4">
              <div className="flex items-center text-gray-600">
                <Calendar size={16} className="mr-2" />
                <span className="text-sm">
                  {formatDateTime(session.start_time)} - {formatDateTime(session.end_time)}
                </span>
              </div>

              <div className="flex items-center text-gray-600">
                <Users size={16} className="mr-2" />
                <span className="text-sm">
                  {session.available_spots} of {session.capacity} spots available
                </span>
              </div>

              <div className="flex items-center text-gray-600">
                <DollarSign size={16} className="mr-2" />
                <span className="text-sm font-medium">${session.price}</span>
              </div>
            </div>

            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-500">Facilitator: {session.facilitator}</span>

              <button
                onClick={() => handleBookSession(session.id)}
                disabled={session.available_spots === 0 || bookingLoading === session.id}
                className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {bookingLoading === session.id ? "Booking..." : session.available_spots === 0 ? "Full" : "Book Now"}
              </button>
            </div>
          </div>
        ))}
      </div>

      {sessions.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500">No sessions available at the moment.</p>
        </div>
      )}
    </div>
  )
}

export default Sessions
