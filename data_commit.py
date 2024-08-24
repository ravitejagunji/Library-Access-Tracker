import mysql.connector
import datetime
import library_access_tracker as l

def student_exit(roll_number):
    conn = l.mysql_connect()
    cursor = conn.cursor()

    # Retrieve the in_time from the database
    query = "SELECT in_time FROM students WHERE roll_number = %s AND out_time IS NULL"
    cursor.execute(query, (roll_number,))
    result = cursor.fetchone()

    if result:
        in_time = result[0]

        # Ensure in_time is a datetime.time object
        if isinstance(in_time, datetime.datetime):
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

    cursor.close()
    conn.close()

# Test the function
student_exit(roll_number='22ME0338')
