import psycopg2
from datetime import datetime

def get_connection():
    return psycopg2.connect(
        host = "localhost",
        database = "movietix",
        user = "postgres",
        password = "mercado6"
    )


###############################################
#########  accounts #########

### register by adding client to database
def create_client_account(name, email, password, interests, rewards):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO client (name, email, password, movie_interests, reward_program) 
            VALUES (%s, %s, %s, %s, %s)""", (name, email, password, interests, rewards))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"error: {e}")
        return False



### login by finding existing client
def check_client_login(email, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM client WHERE email = %s AND password = %s", (email, password))
    valid = cursor.fetchone()
    cursor.close()
    conn.close()
    return valid

### login existing administrator 
def check_admin_login(email, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM administration WHERE email = %s AND password = %s", (email, password))
    valid = cursor.fetchone()
    cursor.close()
    conn.close()
    return valid


###############################################
#########  client functions #########

### all available movies by day 
def get_available_movies():
    conn = get_connection()
    cursor = conn.cursor()

    now = datetime.now()
    curr_date = now.date()
    cursor.execute("SELECT DISTINCT movie_id, title, release_date FROM movies NATURAL JOIN screening_schedule WHERE date = '2026-05-01'")

    movies = cursor.fetchall()
    cursor.close()
    conn.close()
    return movies



###############################################
######### admin functions #########

### add a movie screening to the schedule
def add_movie_screening(movie_id, date, time, theater):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO screening_schedule (movie_id, date, time, theater) 
            VALUES (%s, %s, %s, %s)""", (movie_id, date, time, theater))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"error: {e}")
        return False
    

### delete customer account
def delete_client_account(email):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM client WHERE email = %s", (email,))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"error: {e}")
        return False


###### various analytics functions for admin dashboard ######

### view remaining seat capacity for a screening
def get_seat_capacity(screening_id):
    conn = get_connection()
    cursor = conn.cursor()

    return 

### revenue grouped by movie
def get_revenue_by_movie():
    conn = get_connection()
    cursor = conn.cursor()

    return

### revenue grouped by day
def get_revenue_by_day():
    conn = get_connection()
    cursor = conn.cursor()

    return

### average occupancy rate by theater
def get_occupancy_by_theater():
    conn = get_connection()
    cursor = conn.cursor()

    return

### average occupancy rate by movie
def get_occupancy_by_movie():
    conn = get_connection()
    cursor = conn.cursor()

    return
