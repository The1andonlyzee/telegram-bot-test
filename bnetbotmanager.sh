#!/bin/bash

# Bot Management Script for BNet ODP Management Bot
# This script checks if main.py is running and starts it if it's not

# Configuration
BOT_DIR="./"  # Change this to your actual bot directory
BOT_SCRIPT="main.py"
PYTHON_CMD="python3"  # or just "python" if that's your setup
# VENV_PATH="$BOT_DIR/venv"  # Path to virtual environment (optional)
LOG_FILE="$BOT_DIR/bot_manager.log"
PID_FILE="$BOT_DIR/bot.pid"

# Function to log messages with timestamp
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# Function to check if bot is running
is_bot_running() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            # Check if the process is actually our bot
            if ps -p "$pid" -o command= | grep -q "$BOT_SCRIPT"; then
                return 0  # Bot is running
            else
                # PID file exists but process is not our bot, remove stale PID file
                rm -f "$PID_FILE"
                return 1  # Bot is not running
            fi
        else
            # PID file exists but process is dead, remove stale PID file
            rm -f "$PID_FILE"
            return 1  # Bot is not running
        fi
    else
        return 1  # Bot is not running
    fi
}

# Function to start the bot
start_bot() {
    log_message "Starting BNet ODP Management Bot..."
    
    # Change to bot directory
    cd "$BOT_DIR" || {
        log_message "ERROR: Cannot change to bot directory: $BOT_DIR"
        exit 1
    }
    
    # # Activate virtual environment if it exists
    # if [ -d "$VENV_PATH" ]; then
    #     source "$VENV_PATH/bin/activate"
    #     log_message "Activated virtual environment: $VENV_PATH"
    # fi
    
    # Start the bot in background and save PID
    nohup $PYTHON_CMD "$BOT_SCRIPT" > "$BOT_DIR/bot_output.log" 2>&1 &
    local bot_pid=$!
    
    # Save PID to file
    echo "$bot_pid" > "$PID_FILE"
    
    # Wait a moment and check if bot started successfully
    sleep 3
    if ps -p "$bot_pid" > /dev/null 2>&1; then
        log_message "Bot started successfully with PID: $bot_pid"
    else
        log_message "ERROR: Bot failed to start"
        rm -f "$PID_FILE"
        exit 1
    fi
}

# Function to stop the bot
stop_bot() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            log_message "Stopping bot with PID: $pid"
            kill "$pid"
            sleep 2
            
            # Force kill if still running
            if ps -p "$pid" > /dev/null 2>&1; then
                log_message "Force killing bot with PID: $pid"
                kill -9 "$pid"
            fi
        fi
        rm -f "$PID_FILE"
        log_message "Bot stopped"
    else
        log_message "No PID file found, bot may not be running"
    fi
}

# Function to restart the bot
restart_bot() {
    log_message "Restarting bot..."
    stop_bot
    sleep 2
    start_bot
}

# Function to show bot status
show_status() {
    if is_bot_running; then
        local pid=$(cat "$PID_FILE")
        echo "Bot is running with PID: $pid"
        log_message "Status check: Bot is running with PID: $pid"
    else
        echo "Bot is not running"
        log_message "Status check: Bot is not running"
    fi
}

# Main script logic
case "${1:-check}" in
    "start")
        if is_bot_running; then
            echo "Bot is already running"
            log_message "Start attempt: Bot is already running"
        else
            start_bot
            echo "Bot started"
        fi
        ;;
    "stop")
        stop_bot
        echo "Bot stopped"
        ;;
    "restart")
        restart_bot
        echo "Bot restarted"
        ;;
    "status")
        show_status
        ;;
    "check"|*)
        # Default action: check if running and start if not
        if is_bot_running; then
            log_message "Check: Bot is running normally"
        else
            log_message "Check: Bot is not running, starting it..."
            start_bot
        fi
        ;;
esac