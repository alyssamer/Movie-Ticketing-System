import psycopg2
from datetime import datetime
from tkinter import messagebox

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


### payment method functions
def add_payment_method(email, card_number):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO payment_method (email, card_number) 
            VALUES (%s, %s)""", (email, card_number))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"error: {e}")
        return False
    

def get_payment_methods(email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT card_number FROM payment_method WHERE client_email = %s", (email,))
    methods = cursor.fetchall()
    cursor.close()
    conn.close()
    return methods

###############################################
#########  client functions #########

### all available movies by day 
def get_available_movies():
    conn = get_connection()
    cursor = conn.cursor()

    now = datetime.now()
    curr_date = now.date()
    cursor.execute("SELECT DISTINCT movie_id, title, release_date FROM movies NATURAL JOIN screening_schedule WHERE date = '2026-05-12'")

    movies = cursor.fetchall()
    cursor.close()
    conn.close()
    return movies

### movies watched for rewards program
def get_movies_watched(email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT movies_watched FROM client WHERE email = %s", (email,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result[0] if result else 0

# times for movie
def get_showtimes(movie_id, date): ### placeholder date in python code
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""SELECT screening_id, theater_id, date, time FROM screening_schedule 
                   WHERE movie_id = %s AND date = %s""", (movie_id, date))
    showtimes = cursor.fetchall()
    cursor.close()
    conn.close()
    return showtimes



###### booking screen functions ######

### movie title for booking screen
def get_movie_title(movie_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT title FROM movies WHERE movie_id = %s", (movie_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result[0] if result else "Unknown Movie"

### theater information for tickets
def get_theater_info(theater_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT is_3d, has_fancy_sound 
        FROM theater 
        WHERE theater_id = %s
    """, (theater_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result if result else (False, False)

### movie information for ticket price calculation
def get_movie_info(movie_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT is_major_studio, release_date 
        FROM movies 
        WHERE movie_id = %s
    """, (movie_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result if result else (False, None)


### calculate ticket price
def calculate_ticket_price(screening_id, movie_id, theater_id):
    base_price = 15.00
    
    #  info
    is_3d, has_fancy_sound = get_theater_info(theater_id)
    is_major_studio, release_date = get_movie_info(movie_id)
    
    price = base_price
    if is_3d:
        price += 5.00
    if has_fancy_sound:
        price += 3.00
    if is_major_studio:
        price += 2.00

    ### discount for older movies
    
    return price

### insert client ticket sale
def book_ticket(num_tickets, price, email, card_number, screening_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
  
        cursor.execute("""
            INSERT INTO ticket_sales (quantity_sold, ticket_price, client_email, card_number, screening_id) 
            VALUES (%s, %s, %s, %s, %s)""", (num_tickets, price, email, card_number, screening_id))
        
        ### increment movies watched for rewards program! 
        ### later keep track of specific movies watched for personalized recs
        cursor.execute("""
            UPDATE client 
            SET movies_watched = movies_watched + %s 
            WHERE email = %s
        """, (num_tickets, email))

        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"error: {e}")
        return False



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
