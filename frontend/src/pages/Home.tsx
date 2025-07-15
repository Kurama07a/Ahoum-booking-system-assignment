"use client"

import type React from "react"
import { Link } from "react-router-dom"
import { useAuth } from "../contexts/AuthContext"
import { Calendar, Users, Shield, Star } from "lucide-react"

const Home: React.FC = () => {
  const { user } = useAuth()

  return (
    <div className="max-w-6xl mx-auto">
      {/* Hero Section */}
      <div className="text-center py-16">
        <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
          Book Your Perfect
          <span className="text-blue-600"> Wellness Session</span>
        </h1>
        <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
          Connect with certified facilitators and join transformative sessions and retreats designed to enhance your
          well-being and personal growth.
        </p>

        {!user ? (
          <div className="flex justify-center space-x-4">
            <Link
              to="/register"
              className="bg-blue-600 text-white px-8 py-3 rounded-md hover:bg-blue-700 font-semibold"
            >
              Get Started
            </Link>
            <Link
              to="/login"
              className="border border-blue-600 text-blue-600 px-8 py-3 rounded-md hover:bg-blue-50 font-semibold"
            >
              Login
            </Link>
          </div>
        ) : (
          <div className="flex justify-center space-x-4">
            <Link
              to="/sessions"
              className="bg-blue-600 text-white px-8 py-3 rounded-md hover:bg-blue-700 font-semibold"
            >
              Browse Sessions
            </Link>
            <Link
              to="/dashboard"
              className="border border-blue-600 text-blue-600 px-8 py-3 rounded-md hover:bg-blue-50 font-semibold"
            >
              Dashboard
            </Link>
          </div>
        )}
      </div>

      {/* Features Section */}
      <div className="py-16">
        <h2 className="text-3xl font-bold text-center mb-12">Why Choose Our Platform?</h2>

        <div className="grid md:grid-cols-4 gap-8">
          <div className="text-center">
            <div className="bg-blue-100 rounded-full p-6 w-20 h-20 mx-auto mb-4 flex items-center justify-center">
              <Calendar className="text-blue-600" size={32} />
            </div>
            <h3 className="text-xl font-semibold mb-2">Easy Booking</h3>
            <p className="text-gray-600">Simple and intuitive booking process for all sessions and retreats.</p>
          </div>

          <div className="text-center">
            <div className="bg-green-100 rounded-full p-6 w-20 h-20 mx-auto mb-4 flex items-center justify-center">
              <Users className="text-green-600" size={32} />
            </div>
            <h3 className="text-xl font-semibold mb-2">Expert Facilitators</h3>
            <p className="text-gray-600">Connect with certified and experienced wellness professionals.</p>
          </div>

          <div className="text-center">
            <div className="bg-purple-100 rounded-full p-6 w-20 h-20 mx-auto mb-4 flex items-center justify-center">
              <Shield className="text-purple-600" size={32} />
            </div>
            <h3 className="text-xl font-semibold mb-2">Secure Platform</h3>
            <p className="text-gray-600">Your data and payments are protected with industry-standard security.</p>
          </div>

          <div className="text-center">
            <div className="bg-yellow-100 rounded-full p-6 w-20 h-20 mx-auto mb-4 flex items-center justify-center">
              <Star className="text-yellow-600" size={32} />
            </div>
            <h3 className="text-xl font-semibold mb-2">Quality Sessions</h3>
            <p className="text-gray-600">Carefully curated sessions and retreats for your personal growth.</p>
          </div>
        </div>
      </div>

      {/* How It Works Section */}
      <div className="py-16 bg-gray-50 rounded-lg">
        <h2 className="text-3xl font-bold text-center mb-12">How It Works</h2>

        <div className="grid md:grid-cols-3 gap-8">
          <div className="text-center">
            <div className="bg-blue-600 text-white rounded-full w-12 h-12 mx-auto mb-4 flex items-center justify-center text-xl font-bold">
              1
            </div>
            <h3 className="text-xl font-semibold mb-2">Browse Sessions</h3>
            <p className="text-gray-600">Explore our wide variety of wellness sessions and retreats available.</p>
          </div>

          <div className="text-center">
            <div className="bg-blue-600 text-white rounded-full w-12 h-12 mx-auto mb-4 flex items-center justify-center text-xl font-bold">
              2
            </div>
            <h3 className="text-xl font-semibold mb-2">Book Your Spot</h3>
            <p className="text-gray-600">Choose your preferred session and secure your spot with easy booking.</p>
          </div>

          <div className="text-center">
            <div className="bg-blue-600 text-white rounded-full w-12 h-12 mx-auto mb-4 flex items-center justify-center text-xl font-bold">
              3
            </div>
            <h3 className="text-xl font-semibold mb-2">Enjoy & Grow</h3>
            <p className="text-gray-600">Attend your session and embark on your wellness journey.</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Home
