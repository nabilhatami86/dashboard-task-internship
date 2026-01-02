#!/bin/bash

# Test Ticket Queue System Flow
# This script simulates the complete ticket queue workflow

API_URL="http://localhost:8000"

echo "========================================="
echo "🎫 TICKET QUEUE SYSTEM - FULL TEST"
echo "========================================="
echo ""

# Step 1: Login as Agent
echo "📝 Step 1: Login as Agent..."
LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"identifier": "agent", "password": "agent123"}')

TOKEN=$(echo $LOGIN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [ -z "$TOKEN" ]; then
    echo "❌ Login failed!"
    echo "$LOGIN_RESPONSE"
    exit 1
fi

echo "✅ Login successful!"
echo "Token: ${TOKEN:0:30}..."
echo ""

# Step 2: Check current chats (should only show assigned chats)
echo "📋 Step 2: Check agent's current chats..."
CURRENT_CHATS=$(curl -s "$API_URL/chats/" -H "Authorization: Bearer $TOKEN")
CHAT_COUNT=$(echo $CURRENT_CHATS | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null)

echo "✅ Agent has $CHAT_COUNT assigned chat(s)"
echo ""

# Step 3: View available tickets in queue
echo "🎯 Step 3: View available tickets in queue..."
AVAILABLE_TICKETS=$(curl -s "$API_URL/chats/queue/available")
TICKET_COUNT=$(echo $AVAILABLE_TICKETS | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null)

echo "✅ Found $TICKET_COUNT available ticket(s) in queue"

if [ "$TICKET_COUNT" -gt 0 ]; then
    echo ""
    echo "Available tickets:"
    echo $AVAILABLE_TICKETS | python3 -c "
import sys, json
tickets = json.load(sys.stdin)
for t in tickets[:3]:  # Show first 3
    print(f\"  - Ticket #{t['id']}: {t['name']} ({t['profile']['phone']})\")
"
fi
echo ""

# Step 4: Claim a ticket (if available)
if [ "$TICKET_COUNT" -gt 0 ]; then
    FIRST_TICKET_ID=$(echo $AVAILABLE_TICKETS | python3 -c "import sys, json; print(json.load(sys.stdin)[0]['id'])" 2>/dev/null)

    echo "🏃 Step 4: Claiming ticket #$FIRST_TICKET_ID..."
    CLAIM_RESPONSE=$(curl -s -X POST "$API_URL/chats/$FIRST_TICKET_ID/claim" \
      -H "Authorization: Bearer $TOKEN")

    CLAIM_SUCCESS=$(echo $CLAIM_RESPONSE | python3 -c "import sys, json; d = json.load(sys.stdin); print('success' if 'id' in d else 'failed')" 2>/dev/null)

    if [ "$CLAIM_SUCCESS" == "success" ]; then
        echo "✅ Ticket claimed successfully!"
        echo ""

        # Step 5: Verify chat now appears in agent's list
        echo "✔️  Step 5: Verify chat appears in agent's dashboard..."
        UPDATED_CHATS=$(curl -s "$API_URL/chats/" -H "Authorization: Bearer $TOKEN")
        NEW_CHAT_COUNT=$(echo $UPDATED_CHATS | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null)

        echo "✅ Agent now has $NEW_CHAT_COUNT assigned chat(s) (was $CHAT_COUNT)"

        if [ "$NEW_CHAT_COUNT" -gt "$CHAT_COUNT" ]; then
            echo "🎉 SUCCESS! Chat successfully added to agent's dashboard!"
        else
            echo "⚠️  Warning: Chat count didn't increase"
        fi
    else
        echo "❌ Failed to claim ticket"
        echo "$CLAIM_RESPONSE"
    fi
else
    echo "⚠️  Step 4: No tickets available to claim"
fi

echo ""
echo "========================================="
echo "✅ TEST COMPLETE"
echo "========================================="
