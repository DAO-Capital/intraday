# WARNING: This script assumes PostgreSQL is already installed.
# It will start the service, create a database, and a user if they do not already exist.

# TO RUN THIS SCRIPT:
# 1. Save this script as postgres_setup_windows.ps1.
# 2. Open PowerShell as Administrator.
# 3. Change the execution policy to allow script running (if needed): Set-ExecutionPolicy RemoteSigned
# 4. Run the script: .\postgres_setup_windows.ps1
# 5. Verify the setup by connecting to PostgreSQL: psql -U postgres -d intraday_db

Write-Output "Starting PostgreSQL setup..."

# Set PostgreSQL credentials
$DB_NAME = "intraday_db"
$DB_USER = "postgres"
$DB_PASSWORD = "your_password"

# Function to check PostgreSQL status
function Check-Postgres {
    $service = Get-Service -Name postgresql-x64-14 -ErrorAction SilentlyContinue
    if ($service.Status -eq 'Running') {
        Write-Output "PostgreSQL is running."
    } else {
        Write-Output "PostgreSQL is not running. Starting PostgreSQL..."
        Start-Service -Name postgresql-x64-14
        
        # Wait a bit for PostgreSQL to start
        Start-Sleep -Seconds 10

        # Check again
        $service = Get-Service -Name postgresql-x64-14 -ErrorAction SilentlyContinue
        if ($service.Status -eq 'Running') {
            Write-Output "PostgreSQL started successfully."
        } else {
            Write-Output "Failed to start PostgreSQL. Please start it manually and run the script again."
            exit 1
        }
    }
}

# Function to check if the database exists
function Check-DatabaseExists {
    $dbExists = & psql -U postgres -tAc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'"
    if ($dbExists -eq "1") {
        Write-Output "Database $DB_NAME already exists."
        return $true
    } else {
        return $false
    }
}

# Function to check if the user exists
function Check-UserExists {
    $userExists = & psql -U postgres -tAc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'"
    if ($userExists -eq "1") {
        Write-Output "User $DB_USER already exists."
        return $true
    } else {
        return $false
    }
}

# Check PostgreSQL and start if necessary
Check-Postgres

# Create a PostgreSQL user and database
Write-Output "Creating PostgreSQL user and database..."

# Check if the database already exists
if (-not (Check-DatabaseExists)) {
    & psql -U postgres -c "CREATE DATABASE $DB_NAME;"
    Write-Output "Database $DB_NAME created."
} else {
    Write-Output "Skipping database creation."
}

# Check if the user already exists
if (-not (Check-UserExists)) {
    & psql -U postgres -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
    & psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
    Write-Output "User $DB_USER created and granted privileges."
} else {
    Write-Output "Skipping user creation and privilege assignment."
}

# Instructions for the user
Write-Output "To connect to your PostgreSQL database, use the following command:"
Write-Output "psql -U $DB_USER -d $DB_NAME"
