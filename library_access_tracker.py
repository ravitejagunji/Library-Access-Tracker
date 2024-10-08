import mysql.connector
import datetime
import re

# Database configuration
db_config = {
    'user': 'root',
    'password': '####',
    'host': 'localhost',
    'database': 'library'
}

# Function to connect to MySQL
def mysql_connect():
    return mysql.connector.connect(**db_config)

# Function to create the students table
def create_table():
    try:
        conn = mysql_connect()
        cursor = conn.cursor()
        
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS students (
            si_no INT AUTO_INCREMENT PRIMARY KEY,
            roll_number VARCHAR(7) UNIQUE NOT NULL,
            branch VARCHAR(50),
            date_in DATE,
            in_time TIME,
            out_time TIME,
            total_time_spent TIME
        );
        '''
        
        cursor.execute(create_table_query)
        conn.commit()
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Function to get the branch from roll number
def get_branch(roll_number):
    branch_codes = {
        'ME': 'Mechanical',
        'CS': 'Computer Science',
        'EE': 'Electrical and Electronics',
        'EC': 'Electronics and Communication',
        'IT': 'Information Technology',
        'CV': 'Civil',
        'AM': 'Artificial Intelligence and Machine Learning'
    }
    code = roll_number[2:4]  # Extract branch code
    return branch_codes.get(code, 'Unknown')

# Function to handle student entry
def student_entry(roll_number):
    try:
        conn = mysql_connect()
        cursor = conn.cursor()
        
        branch = get_branch(roll_number)
        now = datetime.datetime.now()
        
        insert_query = '''
        INSERT INTO students (roll_number, branch, date_in, in_time)
        VALUES (%s, %s, %s, %s)
        '''
        
        cursor.execute(insert_query, (roll_number, branch, now.date(), now.time()))
        conn.commit()
        print("Entry recorded successfully.")
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Function to handle student exit
def student_exit(roll_number):
    try:
        conn = mysql_connect()
        cursor = conn.cursor()

        # Retrieve the in_time from the database
        query = "SELECT in_time FROM students WHERE roll_number = %s AND out_time IS NULL"
        cursor.execute(query, (roll_number,))
        result = cursor.fetchone()

        if result:
            in_time = result[0]

            # Convert timedelta to time if necessary
            if isinstance(in_time, datetime.timedelta):
                # Convert timedelta to seconds, then create a time object
                total_seconds = in_time.total_seconds()
                hours = int(total_seconds // 3600)
                minutes = int((total_seconds % 3600) // 60)
                seconds = int(total_seconds % 60)
                in_time = datetime.time(hours, minutes, seconds)
            elif isinstance(in_time, datetime.datetime):
                in_time = in_time.time()

            # Calculate the current time as out_time
            out_time = datetime.datetime.now().time()

            # Calculate the total time spent in the library
            in_datetime = datetime.datetime.combine(datetime.date.today(), in_time)
            out_datetime = datetime.datetime.combine(datetime.date.today(), out_time)
            total_time_spent = out_datetime - in_datetime

            # Update the record with the out_time and total_time_spent
            update_query = """
            UPDATE students
            SET out_time = %s, total_time_spent = %s
            WHERE roll_number = %s AND out_time IS NULL
            """
            cursor.execute(update_query, (out_time, total_time_spent, roll_number))
            conn.commit()
            print("Exit recorded successfully.")
        else:
            print("No entry found for this roll number.")
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Main function to demonstrate usage
def main():
    create_table()
    
    while True:
        action = input("Enter 'in' to check in or 'out' to check out (or 'exit' to quit): ").strip().lower()
        if action == 'exit':
            break
        
        roll_number = input("Enter roll number: ").strip().upper()
        if not re.match(r'^\d{2}[A-Z]{2}0\d{3}$', roll_number):  # Updated pattern
            print("Invalid roll number format.")
            continue
        
        if action == 'in':
            student_entry(roll_number)
        elif action == 'out':
            student_exit(roll_number)
        else:
            print("Invalid action. Please enter 'in' or 'out'.")

if __name__ == "__main__":
    main()
