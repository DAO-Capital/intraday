#!/bin/bash

# WARNING: This script assumes PostgreSQL is already installed on your system.
# It will start the service if necessary, create a database, a user, and grant all privileges.

# TO RUN THIS SCRIPT:
# chmod +x postgres_setup_linux.sh
# ./postgres_setup_linux.sh

# TO VERIFY THE DATABASE AND USER:
# psql -U postgres -d intraday_db

echo "Starting PostgreSQL setup..."

# Set PostgreSQL credentials
DB_NAME="intraday_db"
DB_USER="postgres"
DB_PASSWORD="your_password"

# Function to check PostgreSQL status
check_postgres() {
    if systemctl is-active --quiet postgresql; then
        echo "PostgreSQL is running."
    else
        echo "PostgreSQL is not running. Starting PostgreSQL..."
        sudo systemctl start postgresql
        
        # Wait a bit for PostgreSQL to start
        sleep 10

        # Check again
        if systemctl is-active --quiet postgresql; then
            echo "PostgreSQL started successfully."
        else
            echo "Failed to start PostgreSQL. Please start it manually and run the script again."
            exit 1
        fi
    fi
}

# Check PostgreSQL and start if necessary
check_postgres

# Create a PostgreSQL user and database
echo "Creating PostgreSQL user and database..."

# Use `psql` to create the database and user
sudo -u postgres psql <<EOF
-- Create the database if it does not exist
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_database WHERE datname = '$DB_NAME') THEN
        CREATE DATABASE $DB_NAME;
    END IF;
END
\$\$;

-- Create the user if it does not exist
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '$DB_USER') THEN
        CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';
    END IF;
END
\$\$;

-- Grant all privileges on the database to the user
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;

-- Connect to the database to grant privileges on all tables
\c $DB_NAME

-- Grant all privileges on all tables to the user
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $DB_USER;

-- Grant all privileges on all sequences to the user
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO $DB_USER;

-- Grant all privileges on all functions to the user
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO $DB_USER;
EOF

if [ $? -eq 0 ]; then
    echo "PostgreSQL setup completed. Database and user have been created with all privileges."
else
    echo "There was an error creating the database, user, and granting privileges."
    exit 1
fi

# Instructions for the user
echo "To connect to your PostgreSQL database, use the following command:"
echo "psql -U $DB_USER -d $DB_NAME"
