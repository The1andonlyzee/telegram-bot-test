from telegram.ext import ConversationHandler

# Conversation states
SELECT_LOCATION = 1
NAVIGATE = 2
CUSTOMER_SELECT_LOCATION = 3
CUSTOMER_SELECT_ODP = 4
CUSTOMER_NAVIGATE = 5

# Global user state storage
user_location = {}