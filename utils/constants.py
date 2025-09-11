from telegram.ext import ConversationHandler

# Conversation states
SELECT_LOCATION = 1
NAVIGATE = 2
CUSTOMER_SELECT_LOCATION = 3
CUSTOMER_SELECT_ODP = 4
CUSTOMER_NAVIGATE = 5
CUSTOMER_NAME_SEARCH = 6
WAITING_USERNAME = 10
WAITING_PASSWORD = 11
# Global user state storage
user_location = {}  