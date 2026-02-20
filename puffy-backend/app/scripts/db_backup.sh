#!/bin/bash

# Database credentials (replace with your actual values)
DB_HOST="localhost"
DB_USER="your_username"
DB_PASSWORD="your_password"
DB_NAME="your_database_name"

# Backup directory (create it if it doesn't exist)
BACKUP_DIR="/path/to/backups"
mkdir -p "$BACKUP_DIR"

# Current date and time for filename
CURRENT_DATE_TIME=$(date +%Y-%m-%d_%H-%M-%S)

# Backup command with options
mysqldump \
    -h "$DB_HOST" \
    -u "$DB_USER" \
    -p"$DB_PASSWORD" \
    "$DB_NAME" > "$BACKUP_DIR/$CURRENT_DATE_TIME.sql"

echo "Database backup created: $BACKUP_DIR/$CURRENT_DATE_TIME.sql"