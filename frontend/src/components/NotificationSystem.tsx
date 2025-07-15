"use client"

import React from "react"
import { useState, useEffect, useRef, useCallback } from "react"
import { useAuth } from "../contexts/AuthContext"
import { toast } from "react-hot-toast"
import { Bell, X, Check } from "lucide-react"
import { io, type Socket } from "socket.io-client"
import { API_CONFIG } from "../config/api"

interface Notification {
  notification_id?: number
  type: string
  booking_id: number
  user: {
    id: number
    name: string
    email: string
  }
  session: {
    id: number
    title: string
    start_time: string
  }
  timestamp: string
  message: string
  stored_at?: string
}

const NotificationSystem: React.FC = () => {
  const { user, token } = useAuth()
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [unreadCount, setUnreadCount] = useState(0)
  const [showNotifications, setShowNotifications] = useState(false)
  const [connected, setConnected] = useState(false)
  const socketRef = useRef<Socket | null>(null)

  const playNotificationSound = () => {
    // Create a simple notification sound
    const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)()
    const oscillator = audioContext.createOscillator()
    const gainNode = audioContext.createGain()

    oscillator.connect(gainNode)
    gainNode.connect(audioContext.destination)

    oscillator.frequency.value = 800
    gainNode.gain.value = 0.1

    oscillator.start()
    oscillator.stop(audioContext.currentTime + 0.2)
  }

  const initializeWebSocket = useCallback(() => {
    const socket = io(API_CONFIG.NOTIFICATION_URL, {
      transports: ["websocket"],
    })

    socketRef.current = socket

    socket.on("connect", () => {
      console.log("Connected to notification service")
      // Authenticate as facilitator
      socket.emit("facilitator_connect", {
        facilitator_id: user?.id, // In production, get facilitator ID from user profile
        token: token,
      })
    })

    socket.on("disconnect", () => {
      console.log("Disconnected from notification service")
      setConnected(false)
    })

    socket.on("facilitator_auth_success", (data) => {
      console.log("Facilitator authenticated:", data)
      setConnected(true)
      toast.success("Connected to real-time notifications")

      // Request pending notifications
      socket.emit("get_pending_notifications", {
        facilitator_id: user?.id,
      })
    })

    socket.on("auth_error", (data) => {
      console.error("Authentication error:", data)
      toast.error("Failed to connect to notifications")
    })

    socket.on("new_booking_notification", (notification: Notification) => {
      console.log("New booking notification:", notification)
      setNotifications((prev) => [notification, ...prev])
      setUnreadCount((prev) => prev + 1)
      toast.success(`New booking: ${notification.user.name}`)

      // Play notification sound (optional)
      playNotificationSound()
    })

    socket.on("pending_notifications", (data) => {
      console.log("Pending notifications:", data)
      if (data.notifications && data.notifications.length > 0) {
        setNotifications((prev) => [...data.notifications, ...prev])
        setUnreadCount((prev) => prev + data.count)
        toast(`You have ${data.count} pending notifications`)
      }
    })

    socket.on("notification_marked_read", (data) => {
      console.log("Notification marked as read:", data)
    })

    socket.on("error", (data) => {
      console.error("Socket error:", data)
      toast.error("Notification system error")
    })
  }, [user?.id, token])

  useEffect(() => {
    if (user?.role === "facilitator" && token) {
      initializeWebSocket()
    }

    return () => {
      if (socketRef.current) {
        socketRef.current.disconnect()
      }
    }
  }, [user, token, initializeWebSocket])

  const markAsRead = (notification: Notification) => {
    if (notification.notification_id && socketRef.current) {
      socketRef.current.emit("mark_notification_read", {
        facilitator_id: user?.id,
        notification_id: notification.notification_id,
      })
    }

    // Remove from local state
    setNotifications((prev) => prev.filter((n) => n.booking_id !== notification.booking_id))
    setUnreadCount((prev) => Math.max(0, prev - 1))
  }

  const clearAllNotifications = () => {
    setNotifications([])
    setUnreadCount(0)
  }

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleString()
  }

  // Don't render for non-facilitators
  if (user?.role !== "facilitator") {
    return null
  }

  return (
    <div className="relative">
      {/* Notification Bell */}
      <button
        onClick={() => setShowNotifications(!showNotifications)}
        className="relative p-2 text-gray-600 hover:text-gray-800 focus:outline-none"
      >
        <Bell size={24} />
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
            {unreadCount > 99 ? "99+" : unreadCount}
          </span>
        )}
        {connected && (
          <span className="absolute -bottom-1 -right-1 bg-green-500 rounded-full h-3 w-3 border-2 border-white"></span>
        )}
      </button>

      {/* Notifications Panel */}
      {showNotifications && (
        <div className="absolute right-0 top-12 w-96 bg-white rounded-lg shadow-lg border z-50 max-h-96 overflow-hidden">
          <div className="p-4 border-b flex justify-between items-center">
            <h3 className="font-semibold">Notifications</h3>
            <div className="flex space-x-2">
              {notifications.length > 0 && (
                <button onClick={clearAllNotifications} className="text-sm text-gray-500 hover:text-gray-700">
                  Clear All
                </button>
              )}
              <button onClick={() => setShowNotifications(false)} className="text-gray-500 hover:text-gray-700">
                <X size={20} />
              </button>
            </div>
          </div>

          <div className="max-h-80 overflow-y-auto">
            {notifications.length === 0 ? (
              <div className="p-4 text-center text-gray-500">No notifications</div>
            ) : (
              notifications.map((notification, index) => (
                <div key={`${notification.booking_id}-${index}`} className="p-4 border-b hover:bg-gray-50">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-1">
                        <span className="font-medium text-blue-600">{notification.type.replace("_", " ")}</span>
                        {notification.stored_at && (
                          <span className="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded">Offline</span>
                        )}
                      </div>
                      <p className="text-sm text-gray-800 mb-2">{notification.message}</p>
                      <div className="text-xs text-gray-500 space-y-1">
                        <p>
                          User: {notification.user.name} ({notification.user.email})
                        </p>
                        <p>Session: {notification.session.title}</p>
                        <p>Time: {formatTime(notification.timestamp)}</p>
                      </div>
                    </div>
                    <button
                      onClick={() => markAsRead(notification)}
                      className="ml-2 p-1 text-green-600 hover:text-green-800"
                      title="Mark as read"
                    >
                      <Check size={16} />
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>

          {!connected && (
            <div className="p-3 bg-yellow-50 border-t">
              <p className="text-sm text-yellow-800">⚠️ Not connected to real-time notifications</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default NotificationSystem
