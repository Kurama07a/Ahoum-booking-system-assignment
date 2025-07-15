"use client"

import type React from "react"
import { useState, useEffect } from "react"
import axios from "axios"
import { toast } from "react-hot-toast"
import { Calendar, Clock, User } from "lucide-react"
import { buildApiUrl, API_CONFIG } from "../config/api"

interface Booking {
  id: number
  session: {
    id: number
    title: string
    start_time: string
    end_time: string
    facilitator: string
  }
  booking_status: string
  booking_date: string
  notes: string
}

const Bookings: React.FC = () => {
  const [bookings, setBookings] = useState<Booking[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchBookings()
  }, [])

  const fetchBookings = async () => {
    try {
      const response = await axios.get(buildApiUrl(API_CONFIG.ENDPOINTS.bookings.my))
      setBookings(response.data)
    } catch (error) {
      toast.error("Failed to fetch bookings")
    } finally {
      setLoading(false)
    }
  }

  const formatDateTime = (dateTime: string) => {
    return new Date(dateTime).toLocaleString()
  }

  const isUpcoming = (startTime: string) => {
    return new Date(startTime) > new Date()
  }

  const upcomingBookings = bookings.filter(
    (booking) => isUpcoming(booking.session.start_time) && booking.booking_status === "confirmed",
  )

  const pastBookings = bookings.filter(
    (booking) => !isUpcoming(booking.session.start_time) || booking.booking_status !== "confirmed",
  )

  if (loading) {
    return <div className="flex justify-center items-center h-64">Loading bookings...</div>
  }

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-8">My Bookings</h1>

      {/* Upcoming Bookings */}
      <div className="mb-8">
        <h2 className="text-2xl font-semibold mb-4">Upcoming Sessions</h2>

        {upcomingBookings.length === 0 ? (
          <div className="bg-white rounded-lg shadow-md p-6 text-center">
            <p className="text-gray-500">No upcoming bookings.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {upcomingBookings.map((booking) => (
              <div key={booking.id} className="bg-white rounded-lg shadow-md p-6">
                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-xl font-semibold">{booking.session.title}</h3>
                  <span className="px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                    {booking.booking_status}
                  </span>
                </div>

                <div className="space-y-2 mb-4">
                  <div className="flex items-center text-gray-600">
                    <Calendar size={16} className="mr-2" />
                    <span className="text-sm">
                      {formatDateTime(booking.session.start_time)} - {formatDateTime(booking.session.end_time)}
                    </span>
                  </div>

                  <div className="flex items-center text-gray-600">
                    <User size={16} className="mr-2" />
                    <span className="text-sm">Facilitator: {booking.session.facilitator}</span>
                  </div>

                  <div className="flex items-center text-gray-600">
                    <Clock size={16} className="mr-2" />
                    <span className="text-sm">Booked on: {formatDateTime(booking.booking_date)}</span>
                  </div>
                </div>

                {booking.notes && (
                  <div className="bg-gray-50 rounded-md p-3">
                    <p className="text-sm text-gray-700">
                      <strong>Notes:</strong> {booking.notes}
                    </p>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Past Bookings */}
      <div>
        <h2 className="text-2xl font-semibold mb-4">Past Sessions</h2>

        {pastBookings.length === 0 ? (
          <div className="bg-white rounded-lg shadow-md p-6 text-center">
            <p className="text-gray-500">No past bookings.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {pastBookings.map((booking) => (
              <div key={booking.id} className="bg-white rounded-lg shadow-md p-6 opacity-75">
                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-xl font-semibold">{booking.session.title}</h3>
                  <span
                    className={`px-3 py-1 rounded-full text-sm font-medium ${
                      booking.booking_status === "confirmed" ? "bg-gray-100 text-gray-800" : "bg-red-100 text-red-800"
                    }`}
                  >
                    {booking.booking_status}
                  </span>
                </div>

                <div className="space-y-2 mb-4">
                  <div className="flex items-center text-gray-600">
                    <Calendar size={16} className="mr-2" />
                    <span className="text-sm">
                      {formatDateTime(booking.session.start_time)} - {formatDateTime(booking.session.end_time)}
                    </span>
                  </div>

                  <div className="flex items-center text-gray-600">
                    <User size={16} className="mr-2" />
                    <span className="text-sm">Facilitator: {booking.session.facilitator}</span>
                  </div>
                </div>

                {booking.notes && (
                  <div className="bg-gray-50 rounded-md p-3">
                    <p className="text-sm text-gray-700">
                      <strong>Notes:</strong> {booking.notes}
                    </p>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default Bookings
