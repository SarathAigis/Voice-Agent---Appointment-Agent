#!/bin/bash

# Test call script
# Usage: ./test_call.sh +1YOUR_PHONE_NUMBER

PHONE_NUMBER=${1:-"+1234567890"}

echo "🚛 Making test call to: $PHONE_NUMBER"
echo ""

curl -X POST http://localhost:8000/api/calls/initiate \
  -H "Content-Type: application/json" \
  -d "{
    \"driver_id\": \"DRV-TEST-001\",
    \"driver_name\": \"Test Driver\",
    \"driver_phone\": \"$PHONE_NUMBER\",
    \"truck_number\": \"T-001\",
    \"call_purpose\": \"appointment scheduling test\"
  }" | jq .

echo ""
echo "✅ Call initiated! Your phone should ring in a few seconds..."
echo "📱 Check your phone for incoming call from Twilio number"
