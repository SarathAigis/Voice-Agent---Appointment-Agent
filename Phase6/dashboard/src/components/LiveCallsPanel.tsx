'use client'

import { useEffect, useState } from 'react'
import { Phone, Clock, User, MapPin } from 'lucide-react'

interface LiveCall {
  call_sid: string
  driver_name: string
  status: string
  duration: number
  facility?: string
}

export default function LiveCallsPanel() {
  const [liveCalls, setLiveCalls] = useState<LiveCall[]>([])

  useEffect(() => {
    const fetchLiveCalls = async () => {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/dashboard/live-calls`)
        const data = await response.json()
        setLiveCalls(data.calls || [])
      } catch (error) {
        console.error('Failed to fetch live calls:', error)
      }
    }

    fetchLiveCalls()
    const interval = setInterval(fetchLiveCalls, 2000) // Refresh every 2 seconds

    return () => clearInterval(interval)
  }, [])

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold text-gray-900 flex items-center">
            <Phone className="w-5 h-5 mr-2 text-blue-500" />
            Live Calls
          </h2>
          <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
            {liveCalls.length} Active
          </span>
        </div>
      </div>

      <div className="divide-y divide-gray-200">
        {liveCalls.length === 0 ? (
          <div className="px-6 py-12 text-center">
            <Phone className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No active calls</h3>
            <p className="mt-1 text-sm text-gray-500">
              When calls are in progress, they'll appear here
            </p>
          </div>
        ) : (
          liveCalls.map((call) => (
            <LiveCallCard key={call.call_sid} call={call} />
          ))
        )}
      </div>
    </div>
  )
}

function LiveCallCard({ call }: { call: LiveCall }) {
  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const statusColors = {
    'in-progress': 'bg-green-100 text-green-800',
    ringing: 'bg-yellow-100 text-yellow-800',
    initiated: 'bg-blue-100 text-blue-800',
  }

  return (
    <div className="px-6 py-4 hover:bg-gray-50 transition-colors">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4 flex-1">
          <div className="flex-shrink-0">
            <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
              <User className="w-5 h-5 text-blue-600" />
            </div>
          </div>

          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-900 truncate">
              {call.driver_name}
            </p>
            {call.facility && (
              <p className="text-sm text-gray-500 flex items-center mt-1">
                <MapPin className="w-4 h-4 mr-1" />
                {call.facility}
              </p>
            )}
          </div>
        </div>

        <div className="flex items-center space-x-4">
          <div className="flex items-center text-sm text-gray-500">
            <Clock className="w-4 h-4 mr-1" />
            {formatDuration(call.duration)}
          </div>

          <span
            className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
              statusColors[call.status as keyof typeof statusColors] || 'bg-gray-100 text-gray-800'
            }`}
          >
            <span className="w-1.5 h-1.5 bg-current rounded-full mr-1.5 animate-pulse"></span>
            {call.status}
          </span>

          <button className="text-blue-600 hover:text-blue-800 text-sm font-medium">
            View
          </button>
        </div>
      </div>
    </div>
  )
}
