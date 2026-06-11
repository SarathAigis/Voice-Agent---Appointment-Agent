'use client'

import { useEffect, useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts'

interface MetricsData {
  hourly: { hour: string; calls: number; successful: number }[]
  outcomes: { name: string; value: number }[]
}

export default function MetricsOverview() {
  const [metrics, setMetrics] = useState<MetricsData>({
    hourly: [],
    outcomes: [],
  })
  const [timeRange, setTimeRange] = useState<'today' | 'week' | 'month'>('today')

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/api/dashboard/metrics?range=${timeRange}`
        )
        const data = await response.json()
        setMetrics(data)
      } catch (error) {
        console.error('Failed to fetch metrics:', error)
      }
    }

    fetchMetrics()
    const interval = setInterval(fetchMetrics, 30000) // Refresh every 30 seconds

    return () => clearInterval(interval)
  }, [timeRange])

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold text-gray-900">Call Metrics</h2>

          <div className="flex space-x-2">
            {(['today', 'week', 'month'] as const).map((range) => (
              <button
                key={range}
                onClick={() => setTimeRange(range)}
                className={`px-3 py-1 text-sm font-medium rounded-md ${
                  timeRange === range
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                {range.charAt(0).toUpperCase() + range.slice(1)}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="p-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Hourly Call Volume */}
          <div>
            <h3 className="text-sm font-medium text-gray-700 mb-4">Call Volume</h3>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={metrics.hourly}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="hour" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="calls" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Success Rate Trend */}
          <div>
            <h3 className="text-sm font-medium text-gray-700 mb-4">Success Rate</h3>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={metrics.hourly}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="hour" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="successful" stroke="#10b981" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Call Outcomes */}
        <div className="mt-6">
          <h3 className="text-sm font-medium text-gray-700 mb-4">Call Outcomes</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {metrics.outcomes.map((outcome) => (
              <div key={outcome.name} className="bg-gray-50 rounded-lg p-4">
                <p className="text-2xl font-semibold text-gray-900">{outcome.value}</p>
                <p className="text-sm text-gray-600 mt-1 capitalize">{outcome.name}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
