"""
Setup script for NeuroHire Backend

This script helps with:
1. Creating the PostgreSQL database
2. Running migrations
3. Creating a superuser
4. Starting the server
"""

import os
import sys
import subprocess
import getpass
import time

def run_command(command):
    """Run a command and return its output"""
    process = subprocess.Popen(
        command, 
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = process.communicate()
    return process.returncode, stdout.decode('utf-8'), stderr.decode('utf-8')

def create_database():
    """Create PostgreSQL database"""
    print("\n=== Creating PostgreSQL Database ===")
    
    # Try to connect to PostgreSQL and create the database
    try:
        # Import environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        db_name = os.getenv('DB_NAME')
        db_user = os.getenv('DB_USER')
        db_password = os.getenv('DB_PASSWORD')
        
        # Check if database already exists
        check_cmd = f'psql -U {db_user} -c "SELECT 1 FROM pg_database WHERE datname=\'{db_name}\'"'
        returncode, stdout, stderr = run_command(check_cmd)
        
        if '1 row' in stdout:
            print(f"Database '{db_name}' already exists.")
            return True
        
        # Create the database
        create_cmd = f'psql -U {db_user} -c "CREATE DATABASE {db_name}"'
        returncode, stdout, stderr = run_command(create_cmd)
        
        if returncode == 0:
            print(f"Database '{db_name}' created successfully.")
            return True
        else:
            print(f"Error creating database: {stderr}")
            return False
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def run_migrations():
    """Run Django migrations"""
    print("\n=== Running Migrations ===")
    
    # Make migrations
    returncode, stdout, stderr = run_command('python manage.py makemigrations')
    if returncode != 0:
        print(f"Error making migrations: {stderr}")
        return False
    
    print("Migrations created successfully.")
    
    # Apply migrations
    returncode, stdout, stderr = run_command('python manage.py migrate')
    if returncode != 0:
        print(f"Error applying migrations: {stderr}")
        return False
    
    print("Migrations applied successfully.")
    return True

def create_superuser():
    """Create a Django superuser"""
    print("\n=== Creating Superuser ===")
    
    # Check if superuser already exists
    check_cmd = 'python manage.py shell -c "from django.contrib.auth.models import User; print(User.objects.filter(is_superuser=True).exists())"'
    returncode, stdout, stderr = run_command(check_cmd)
    
    if 'True' in stdout:
        print("Superuser already exists.")
        return True
    
    # Create superuser non-interactively
    username = input("Enter superuser username: ")
    email = input("Enter superuser email: ")
    password = getpass.getpass("Enter superuser password: ")
    
    create_cmd = f'python manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser(\'{username}\', \'{email}\', \'{password}\')"'
    returncode, stdout, stderr = run_command(create_cmd)
    
    if returncode == 0:
        print("Superuser created successfully.")
        return True
    else:
        print(f"Error creating superuser: {stderr}")
        return False

def run_server():
    """Run the Django development server"""
    print("\n=== Starting Django Server ===")
    print("Server will start at http://localhost:8000/")
    print("Admin interface is available at http://localhost:8000/admin/")
    print("API is available at http://localhost:8000/api/")
    print("Press Ctrl+C to stop the server")
    
    # Start the server
    os.system('python manage.py runserver')

def main():
    """Main function to run the setup"""
    print("=== NeuroHire Backend Setup ===")
    
    # Activate virtual environment if not already activated
    if 'VIRTUAL_ENV' not in os.environ:
        print("Virtual environment not activated. Please activate it first.")
        print("Run: .\\venv\\Scripts\\activate.ps1")
        return
    
    # Create database
    if not create_database():
        print("Failed to create database. Setup aborted.")
        return
    
    # Run migrations
    if not run_migrations():
        print("Failed to run migrations. Setup aborted.")
        return
    
    # Create superuser
    create_superuser()
    
    # Run server
    run_server()

if __name__ == "__main__":
    main()
