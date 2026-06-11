# Appointment Agent Dashboard

Next.js dashboard for monitoring voice agent calls and managing appointments.

## Features

- **Real-time Call Monitoring** - See active calls as they happen
- **Call History** - View past calls with transcripts
- **Metrics & Analytics** - Track performance and outcomes
- **Appointment Management** - View, reschedule, cancel appointments
- **Live Updates** - WebSocket connection for real-time data

## Getting Started

### Prerequisites

- Node.js 18+
- Running API server (Phase 5)

### Installation

```bash
# Install dependencies
npm install

# Copy environment file
cp .env.local.example .env.local

# Edit .env.local with your API URL
```

### Development

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

### Build for Production

```bash
npm run build
npm start
```

## Project Structure

```
dashboard/
├── src/
│   ├── app/              # Next.js app router pages
│   │   ├── page.tsx      # Dashboard home
│   │   ├── calls/        # Call detail pages
│   │   └── layout.tsx    # Root layout
│   ├── components/       # React components
│   │   ├── LiveCallsPanel.tsx
│   │   ├── MetricsOverview.tsx
│   │   └── RecentCallsTable.tsx
│   └── lib/              # Utilities
├── public/               # Static assets
└── package.json
```

## Components

### LiveCallsPanel
Displays currently active calls with:
- Driver information
- Call duration
- Status
- Quick actions

### MetricsOverview
Shows metrics charts:
- Call volume by hour
- Success rate trends
- Outcome distribution

### RecentCallsTable
Lists recent calls with:
- Driver details
- Call duration
- Outcome
- Appointment status
- Links to detailed view

## API Integration

Dashboard connects to FastAPI backend:

```
GET  /api/dashboard/stats           # Dashboard statistics
GET  /api/dashboard/live-calls      # Active calls
GET  /api/dashboard/metrics         # Metrics data
GET  /api/dashboard/recent-calls    # Call history
GET  /api/calls/{call_sid}          # Call details
WS   /ws/dashboard                  # Real-time updates
```

## Environment Variables

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

## Deployment

### Vercel (Recommended)

```bash
vercel deploy
```

### Docker

```bash
docker build -t appointment-dashboard .
docker run -p 3000:3000 appointment-dashboard
```

### Manual

```bash
npm run build
npm start
```

## Development

### Code Style

```bash
npm run lint
```

### Type Checking

```bash
npx tsc --noEmit
```

## Features by Page

### Dashboard (/)
- System status
- Active calls count
- Today's stats
- Live calls panel
- Metrics charts
- Recent calls table

### Call Detail (/calls/[id])
- Full transcript
- Audio playback
- Timeline
- Appointment details
- Actions (override, notes)

### Analytics (/analytics)
- Custom date ranges
- Export data
- Detailed metrics
- Driver performance

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **UI**: Tailwind CSS
- **Charts**: Recharts
- **Icons**: Lucide React
- **Date**: date-fns
- **API**: Axios
- **Real-time**: Socket.IO

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## License

MIT
