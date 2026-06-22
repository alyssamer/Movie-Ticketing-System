import tkinter as tk
from tkinter import *
from PIL import Image, ImageTk
from httpx import options
import database


###############################################
######### register & login

### enters new user to database
def register_info(name_entry, email_entry, password_entry, interests, rewards, label):
    ### getting entries 
    name = name_entry.get()
    email = email_entry.get()
    password = password_entry.get()
    # get selected items, seperate w commas
    selected_indices = interests.curselection()  
    selected_interests = [interests.get(i) for i in selected_indices]  
    interests_string = ",".join(selected_interests)  
    reward_info = rewards.get()

    ### check not empty before insertion
    if not name or not email or not password or not reward_info:
        label.config(text = "please fill in all required fields")
        return
    
    ### validity 
   

    ### insert into database
    registration = database.create_client_account(name, email, password, interests_string, reward_info)

    # if succees auto log in
    if registration:
        register_info.destroy()
    else:
        label.config(text = "registration failed")
    

    return 


### register new client for the website
def client_register_screen(root):
    register = tk.Toplevel(root)
    register.geometry("400x400")
    register.title("registration screen")

    ### close out registration page
    close = tk.Button(register, text = "close", command = register.destroy)
    close.pack()

    ### labels for users
    name_text = tk.Label(register, text = "name*")
    email_text = tk.Label(register, text = "email*")
    pass_text = tk.Label(register, text = "password*")
    address_text = tk.Label(register, text = "address")
    rewards_text = tk.Label(register, text = "want to be in our rewards program?*")
    interests_text = tk.Label(register, text = "movie interests")

    ### user input
    ### name, email, password, rewards required
    ### address and interests optional
    name_entry = tk.Entry(register)
    email_entry = tk.Entry(register)
    password_entry = tk.Entry(register)
    address_entry = tk.Entry(register)

    rewards_check = tk.Checkbutton(register, text = "yes", onvalue = "yes", offvalue = "no")

    ### able to choose multiple interests
    interest_list = tk.Listbox(register, height = 40, selectmode=tk.MULTIPLE)
    interest_list.insert(tk.END, "Action")
    interest_list.insert(tk.END, "Family")
    interest_list.insert(tk.END, "Thriller")
    interest_list.insert(tk.END, "Horror")
    interest_list.insert(tk.END, "Sci-Fi")

    ### pack in order
    name_text.pack()
    name_entry.pack()
    email_text.pack()
    email_entry.pack()
    pass_text.pack()
    password_entry.pack()
    address_text.pack()
    address_entry.pack()
    rewards_text.pack()
    rewards_check.pack()
    interests_text.pack()
    interest_list.pack()

    ### label for login validity information
    label = tk.Label(register, text = "") 
    label.pack()
    
    ### goes to registration func submits to databse
    register_button = tk.Button(register, text = "Login", 
                          command = lambda: register_info(name_entry, email_entry, password_entry, 
                                                          interest_list, rewards_check, label),
                          width=15, height=2, bg="#859bc4")
    register_button.pack()

    register.update()
    return 


### checks validity of login info
def login_info(root, email_entry, password_entry, label, user):
    email = email_entry.get()
    password = password_entry.get()

    ### different login checking based on user
    if user == "client":
        valid_user = database.check_client_login(email, password)
    else:
        valid_user = database.check_admin_login(email, password)


    ### change label
    if valid_user:
        root.logged_in_user = email
        root.user_type = user

        if user == "client":
            show_user_info(root, user)
            label.config(text = "successful login")
            load_movies(root)
        else:
            show_user_info(root, user)
            label.config(text = "successful admin login")
            load_admin_dashboard(root)
    else:
        label.config(text = "email or password is incorrect")
    
    return


### remove buttns, replace with user info
def show_user_info(root, user):
    root.button_frame.place_forget()  # hide the login/register buttons
    
    ### create user info frame
    user_frame = tk.Frame(root, bg="#060c28")
    root.user_info_frame = user_frame
    user_frame.place(x=900, y=42)
    
    # user email
    email_label = tk.Label(user_frame, text=f"{root.logged_in_user}", 
                          fg="#d9e4f7", bg="#060c28", font=("Arial", 10))
    email_label.pack()
    
    # clients have num movies at the end
    if user == "client":
        # num movies watched
        movies_watched = database.get_movies_watched(root.logged_in_user)
        watched_label = tk.Label(user_frame, text=f"Movies: {movies_watched}/10", 
                                fg="#d9e4f7", bg="#060c28", font=("Arial", 9))
        watched_label.pack()


### user login input
def client_login_screen(root):
    ### window
    client_login = tk.Toplevel(root)
    client_login.geometry("400x250")
    client_login.title("client login screen")

    ### switch to admin login
    switch_login = tk.Button(client_login, text = "admin login?", command = lambda:admin_login_screen(root))
    switch_login.pack()

    ### closing and entering 
    close = tk.Button(client_login, text = "close", command = client_login.destroy)
    close.pack()
    enter_email = tk.Label(client_login, text = "enter email")
    enter_pass = tk.Label(client_login, text = "enter password")

    ### user input
    email_entry = tk.Entry(client_login)
    password_entry = tk.Entry(client_login)

    ### pack in order
    enter_email.pack()
    email_entry.pack()
    enter_pass.pack()
    password_entry.pack()

    ### label for login validity information
    label = tk.Label(client_login, text = "") 
    label.pack()

    ### goes to login func
    login_button = tk.Button(client_login, text = "Login", 
                          command = lambda: login_info(root, email_entry, password_entry, label, "client"),
                          width=15, height=2, bg="#859bc4")
    login_button.pack()

    client_login.update()

    return 


## admin login input
def admin_login_screen(root):
    ### window
    admin_login = tk.Toplevel(root)
    admin_login.geometry("400x250")
    admin_login.title("administrator login screen")

    ### closing and entering buttons
    close = tk.Button(admin_login, text = "close", command = admin_login.destroy)
    close.pack()
    enter_email = tk.Label(admin_login, text = "enter email")
    enter_pass = tk.Label(admin_login, text = "enter password")

    ### user input
    email_entry = tk.Entry(admin_login)
    password_entry = tk.Entry(admin_login)

    ### pack in order
    enter_email.pack()
    email_entry.pack()
    enter_pass.pack()
    password_entry.pack()

    ### label for login validity information
    label = tk.Label(admin_login, text = "") 
    label.pack()

    ### goes to login func
    login_button = tk.Button(admin_login, text = "Login", 
                          command = lambda: login_info(root, email_entry, password_entry, label, "admin"),
                          width=15, height=2, bg="#859bc4")
    login_button.pack()

    admin_login.update()


    return 



###############################################
######### load current movies screen 

def load_movies(root):
    ### currently showing movies from database
    movies = database.get_available_movies()

    ### destroy admin dashboard if it exists
    if hasattr(root, 'admin_frame') and root.admin_frame:
        root.admin_frame.destroy()

    ### frame to hold them
    movies_frame = tk.Frame(root, background = "#859bc4")
    root.movies_frame = movies_frame
    movies_frame.place(x = 200, y = 140, width = 800, height = 500)

    ### vertical scrolling
    canvas = tk.Canvas(movies_frame, background = "#859bc4", highlightthickness = 0)

    movie_scroll = tk.Scrollbar(movies_frame, orient = "vertical", command = canvas.yview, background = "#859bc4")
    scroll_frame = tk.Frame(canvas, background = "#859bc4")
    scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

    canvas.create_window((0,0), window = scroll_frame, anchor = "nw")
    canvas.config(yscrollcommand = movie_scroll.set)

    ### movie tuple stuff
    for movie in movies:
        movie_id, title, release_date = movie
        movie_card(scroll_frame, movie_id, title, release_date, root)


    canvas.pack(side = "left", fill = "both", expand = True)
    movie_scroll.pack(side = "right", fill = "y")
    return


### creates movie "card" in scroll list
def movie_card(scroll, movie_id, title, release_date, root):
    ### image on the left, title and times on the right
    card = tk.Frame(scroll, height = 150, bg = "#859bc4", highlightthickness = 0)
    card.pack(fill = "x", padx = 15, pady = 15)

    ### left - movie image
    image_filename = title + ".jpg"

    try:
        img = Image.open(f"images/{image_filename}").resize((190, 250))
        photo = ImageTk.PhotoImage(img)
        img_label = tk.Label(card, image = photo)
        img_label.image = photo
        img_label.pack(side = "left", padx = 20, pady = 15)

    except: # default if no image avail
        img_label = tk.Label(card, text = "no poster!", background = "#859bc4")
        img_label.pack(side = "left")

    ##### right side 
    right_frame = tk.Frame(card, background = "#859bc4")
    right_frame.pack(side = "left", fill = "both", padx = 20, expand = True)

    ### title and showing times
    title_label = tk.Label(right_frame, text = title, font = ("Arial", 18, "bold"), fg = "#d9e4f7", background = "#859bc4")
    title_label.pack(pady = 15)

    showtimes_frame = tk.Frame(right_frame)
    showtimes_frame.pack(pady = 10)

    ### showtimes for movie for example date
    showtime = database.get_showtimes(movie_id, date ='2026-05-12')

    for data in showtime:
        screening_id, theater_id, date, time = data

        time_formatted = str(time)[:5]  # takes first 5 chars: "14:30"
    
        time_button = tk.Button(showtimes_frame, text = time_formatted, bg = "#859bc4", width = 10, height = 2, padx = 10, pady = 10,
                                command = lambda s = screening_id, th = theater_id, d = date, t = time: booking_screen(root, movie_id, s, th, d, t))
        time_button.pack(side = "left", padx = 5, pady = 5)

    return




###############################################
#########  booking tickets screen

def booking_screen(root, movie_id, screening_id, theater_id, date, time):
    ### remove existing screen
    if hasattr(root, 'movies_frame') and root.movies_frame:
        root.movies_frame.destroy()

    ### must be logged in to book tickets
    if not hasattr(root, 'logged_in_user'):
        tk.messagebox.showerror("Error", "Please log in first")
        load_movies(root)
        return

    booking_frame = tk.Frame(root, background="#859bc4")
    root.booking_frame = booking_frame
    booking_frame.place(x = 200, y = 140, width = 800, height = 500) 
    


    ### back button to movies
    back_button = tk.Button(booking_frame, text = "back to movies", command = lambda: load_movies(root), bg = "#859bc4")
    back_button.grid(row=0, column=0, padx=10, pady=10)

    ### movie title - date, time 
    title = database.get_movie_title(movie_id)
    title_label = tk.Label(booking_frame, text = title, font = ("Arial", 18, "bold"), bg = "#859bc4", fg = "#d9e4f7")
    title_label.grid(row=0, column=1, padx=10, pady=10)

    ### screening info  
    info_text = f"Date: {date}    Time: {str(time)[:5]}    Theater: {theater_id}"
    info_label = tk.Label(booking_frame, text = info_text, font = ("Arial", 12), bg = "#859bc4", fg = "#d9e4f7")
    info_label.grid(row=0, column=2, padx=10, pady=10)



    ### choose or add payment method
    payment_methods = database.get_payment_methods(root.logged_in_user)
    card_list = [method[0] for method in payment_methods]  # extract card numbers from tuples

    payment_label = tk.Label(booking_frame, text = "Choose Payment Method:", font = ("Arial", 12), bg = "#859bc4", fg = "#d9e4f7")
    payment_label.grid(row = 1, column = 1, padx=10, pady=10)

    payment_var = tk.StringVar(value = card_list[0] if card_list else "")  # default to first card if exists


    if card_list:
        for i, card in enumerate(card_list): ### goes thru list of cards 
            card_button = tk.Radiobutton(booking_frame, text=f"Card ending in {card[-4:]}", variable=payment_var, value=card, 
                             bg="#859bc4", fg="#d9e4f7")
            card_button.grid(row=2+i, column=0, columnspan=2, sticky="w", padx=40, pady=5)
    else:
        no_card_label = tk.Label(booking_frame, text = "No payment methods saved. Please add a card.", bg = "#859bc4", fg = "#d9e4f7")
        no_card_label.grid(row = 2, column=2, padx=10, pady=5)

    ### add card button
    add_card_button = tk.Button(booking_frame, text = "Add Payment Method", bg = "#859bc4", width = 20, 
                                command = lambda: add_card_popup(root, root.logged_in_user))
    add_card_button.grid(row = 4, column = 1, pady = 10)


    ### choose number of tickets
    tickets_label = tk.Label(booking_frame, text = "Number of Tickets:", font = ("Arial", 12), bg = "#859bc4", fg = "#d9e4f7")
    tickets_label.grid(row = 5, column = 1, pady = 10)

    tickets_select = tk.Spinbox(booking_frame, from_= 1, to = 10, width = 5)
    tickets_select.grid(row = 5, column = 2, pady = 10)

    ### price for tickets
    price = database.calculate_ticket_price(screening_id, movie_id, theater_id)
    price_label = tk.Label(booking_frame, text = f"Price per Ticket: ${price:.2f}", font = ("Arial", 12), bg = "#859bc4", fg = "#d9e4f7")
    price_label.grid(row = 6, column = 1, pady = 10)

    ### label if not successful booking
    booking_label = tk.Label(booking_frame, text = "", font = ("Arial", 12), bg = "#859bc4", fg = "#d9e4f7")
    booking_label.grid(row = 7, column = 1, pady = 10)

    ### confirm booking button
    confirm_button = tk.Button(booking_frame, text = "Confirm Booking", bg = "#859bc4", width = 15, height = 2,
                                command = lambda: confirm_booking(root, tickets_select.get(), price, root.logged_in_user, payment_var.get(), screening_id, booking_label))
    confirm_button.grid(row = 8, column = 1, pady = 20)

    return



### add credit or debit card to payment methods
def add_card_popup(root, email):
    card_window = tk.Toplevel(root)
    card_window.geometry("400x250")
    card_window.title("Add Payment Method")

    ### card type 
    card_type_label = tk.Label(card_window, text = "*Card Type: ", font = ("Arial", 12))
    card_type_label.pack(pady = 10)

    card_type_var = tk.StringVar()
    card_type_dropdown = tk.OptionMenu(card_window, card_type_var, "Credit", "Debit")
    card_type_dropdown.pack(pady = 10)

    ### card number
    card_label = tk.Label(card_window, text = "*Card Number: ", font = ("Arial", 12))
    card_label.pack(pady = 10)
    
    card_entry = tk.Entry(card_window, width=30)
    card_entry.pack(pady=10)

    ### billing address
    address_label = tk.Label(card_window, text = "Billing Address: ", font = ("Arial", 12))
    address_label.pack(pady = 10)
    address_entry = tk.Entry(card_window, width=30)
    address_entry.pack(pady=10)

    ### label for card saving status
    card_status_label = tk.Label(card_window, text = "", font = ("Arial", 12), bg = "#859bc4", fg = "#d9e4f7")
    card_status_label.pack(pady = 10)

    ### save card button
    save_button = tk.Button(card_window, text = "Save Card", bg = "#859bc4", width = 15, height = 2,
                             command = lambda: save_card(card_window, email, card_entry, card_status_label))
    save_button.pack(pady = 20)


### save card to database
def save_card(card_window, email, card_entry, card_status_label):
    card_num = card_entry.get()
    
    if len(card_num) < 4:
        card_status_label.config(text = "Invalid card number")
        return
        
    if database.add_payment_method(email, card_num):
        card_status_label.config(text = "Card added successfully!")
    else:
        card_status_label.config(text = "Failed to add card")
    



### confirm booking and insSert into database
def confirm_booking(root, num_tickets, price, email, card_number, screening_id, booking_label):
    email = root.logged_in_user
    total_price = float(num_tickets) * price

    if not card_number:
        booking_label.config(text="Please select a payment method", fg="#FF6B6B")
        return
    
    if num_tickets > 10 or num_tickets == 0:
        booking_label.config(text="Select valid ticket number", fg="#FF6B6B")
        return

    if database.book_ticket(num_tickets, total_price, email, card_number, screening_id):
        booking_label.config(text = "Booking confirmed!")
        ### refresh user info with new num movies watched?
        if hasattr(root, 'user_info_frame') and root.user_info_frame:
            root.user_info_frame.destroy()
        show_user_info(root, root.user_type)

        root.after(1500, lambda: load_movies(root)) # return to movies after 1.5 seconds!
    else:
        booking_label.config(text = "Failed to book tickets")


###############################################
######### load administration dashboard screen

def load_admin_dashboard(root):

    # destroy movie frame if it exists
    if hasattr(root, 'movies_frame') and root.movies_frame:
        root.movies_frame.destroy()

    admin_frame = tk.Frame(root, background="#859bc4")
    root.admin_frame = admin_frame
    admin_frame.place(x = 200, y = 140, width = 800, height = 500)

    ### top spacers
    top_spacer = tk.Label(admin_frame, height = 3, bg = "#859bc4")
    top_spacer.grid(row = 0, column = 1)

    ### left spacers
    left_spacer = tk.Label(admin_frame, width = 10, bg = "#859bc4")
    left_spacer.grid(row = 0, column = 0)



    # top text
    title = tk.Label(admin_frame, text="Admin Dashboard", font=("Arial", 20, "bold"), bg="#859bc4", fg="#d9e4f7")
    title.grid(row = 0, column = 2, padx = 10, pady = 15)

    ### buttons for admin functions
    add_movie_button = tk.Button(admin_frame, text = "Add Movie", width=20, command = lambda: admin_screening(root))
    add_movie_button.grid(row = 1, column = 1, padx = 10, pady = 10)
    delete_account_button = tk.Button(admin_frame, text = "Delete Customer Account", width = 20, command = lambda: delete_account_screen(root))
    delete_account_button.grid(row = 2, column = 1, padx = 10, pady = 10)


    ### view analytics - revenue, remaining capacity, average occupancy 
    view_capacity_button = tk.Button(admin_frame, text = "View Remaining Seat Capacity", width = 30, command = lambda: view_seat_capacity(root))
    view_capacity_button.grid(row = 1, column = 3, padx = 10)

    view_revenue_button = tk.Button(admin_frame, text = "View Revenue", width = 20, command = lambda: view_revenue(root))
    view_revenue_button.grid(row = 2, column = 3, padx = 10, pady = 10)

    return


### sends to database
def delete_button(root, email_entry, label):
    email = email_entry.get()

    ## check valid email formatkinda
    if "@" not in email or "." not in email:
        label.config(text = "Please enter a valid email address.")
        return

    ### check for existing email later
    database.delete_client_account(email)
    label.config(text="Account deleted successfully!")
    return


### delete a customers account by email
def delete_account_screen(root):
    delete_account = tk.Toplevel(root)
    delete_account.geometry("400x250")
    delete_account.title("delete customer account")

    ### close out page
    close = tk.Button(delete_account, text = "close", command = delete_account.destroy)
    close.pack()

    ### labels for users
    email_text = tk.Label(delete_account, text = "Account Email*")
    email_text.pack()

    ### user input
    email_entry = tk.Entry(delete_account)
    email_entry.pack()

    ### label for login validity information
    label = tk.Label(delete_account, text = "") 
    label.pack()
    
    ### goes to func submits to databse
    delete_button = tk.Button(delete_account, text = "Delete Account", 
                          command = lambda: delete_button(root, email_entry, label),
                          width=15, height=2, bg="#859bc4")
    delete_button.pack()

    delete_account.update()
    
    return


### send to database to add movie screening
def add_movie_screening(root, title_entry, date_entry, time_entry, theater_entry, valid_label):
    title = title_entry.get()
    date = date_entry.get()
    time = time_entry.get()
    theater = theater_entry.get()

    ### check valid entry
    if not title or not date or not time or not theater:
        valid_label.config(text="Please fill in all fields.")
        return

    ### check valid movie title
    movie_id = database.get_movie_id(title)
    if not movie_id:
        valid_label.config(text="Invalid movie title.")
        return
    
    ### check valid theater number
    if not theater.isdigit() or int(theater) < 1 or int(theater) > 4:
        valid_label.config(text="Please enter a valid theater number (1-4).")
        return
    
    ### check valid date and time format
    

    # add to database
    database.add_movie_screening(title, date, time, theater)

    valid_label.config(text="Screening added successfully!")
    return


### enter screening and check validity
def admin_screening(root):
    add_movie = tk.Toplevel(root)
    add_movie.geometry("600x450")
    add_movie.title("Add Movie Screening")

    # close button
    close = tk.Button(add_movie, text = "close", command = add_movie.destroy)
    close.pack()

    # movie title, date, time, theatre
    title_label = tk.Label(add_movie, text = "Movie Title:")
    title_label.pack()
    title_entry = tk.Entry(add_movie)
    title_entry.pack()

    theater_label = tk.Label(add_movie, text = "Theater (1-4):")
    theater_label.pack()
    theater_entry = tk.Entry(add_movie)
    theater_entry.pack()


    date_label = tk.Label(add_movie, text = "Date Showing (YYYY-MM-DD):")
    date_label.pack()
    date_entry = tk.Entry(add_movie)
    date_entry.pack()

    time_label = tk.Label(add_movie, text = "Time (HH:MM):")
    time_label.pack()
    time_entry = tk.Entry(add_movie)
    time_entry.pack()

    ### valid label
    valid_label = tk.Label(add_movie, text = "", font = ("Arial", 12), bg = "#859bc4", fg = "#d9e4f7")
    valid_label.pack(pady = 10)

    # submit button
    submit_button = tk.Button(add_movie, text = "Add Screening", bg = "#859bc4", width = 15, height = 2,
                              command = lambda: add_movie_screening(root, title_entry, date_entry, time_entry, theater_entry, valid_label))
    submit_button.pack(pady = 20)

    return



### view remaining seats for every screening
def view_seat_capacity(root):
    capacity_window = tk.Toplevel(root)
    capacity_window.geometry("400x300")
    capacity_window.title("Remaining Seat Capacity")

    # close button
    close = tk.Button(capacity_window, text = "close", command = capacity_window.destroy)
    close.pack()

    ### dropdown to choose screening
    options = database.get_screenings_by_day()  # get all screenings for the day from database
    screening_display = [f"Movie {s[1]} - Theater {s[2]} at {s[3]}" for s in options]
    
    screening_choice = tk.StringVar()
    screening_choice.set(screening_display[0] if screening_display else "")
    
    ### label to display remaining capacity
    capacity_label = tk.Label(capacity_window, text="", font=("Arial", 12))
    capacity_label.pack(pady=10)

    ### when screening selected, show remaining capacity
    def on_screening_select(*args):
        selected = screening_choice.get()
        index = screening_display.index(selected)
        screening_id = options[index][0]
        remaining = database.get_seat_capacity(screening_id)
        capacity_label.config(text=f"Remaining Capacity: {remaining} seats")
    
    ### dropdown does on_screening_select when changed
    screening_choice.trace_add("write", on_screening_select)

    screening_dropdown = tk.OptionMenu(capacity_window, screening_choice, *screening_display)
    screening_dropdown.pack(pady=10)

    return


### view revenue analytics
def view_revenue(root):
    revenue_window = tk.Toplevel(root)
    revenue_window.geometry("400x300")
    revenue_window.title("Revenue Analytics")

    # close button
    close = tk.Button(revenue_window, text = "close", command = revenue_window.destroy)
    close.pack()

    ### dropdown to choose revenue for day, movie, or theater
    revenue_choice = tk.StringVar()
    revenue_choice.set("Day")  # default value
    revenue_dropdown = tk.OptionMenu(revenue_window, revenue_choice, "Day", "Movie", "Theater")
    revenue_dropdown.pack(pady = 10)

    return


### view average occupancy analytics
def view_occupancy(root):
    occupancy_window = tk.Toplevel(root)
    occupancy_window.geometry("400x300")
    occupancy_window.title("Occupancy Analytics")

    # close button
    close = tk.Button(occupancy_window, text = "close", command = occupancy_window.destroy)
    close.pack()

    ### dropdown to choose occupancy for day, movie, or theater
    occupancy_choice = tk.StringVar()
    occupancy_choice.set("Theater")  # default value
    occupancy_dropdown = tk.OptionMenu(occupancy_window, occupancy_choice, "Day", "Movie", "Theater")
    occupancy_dropdown.pack(pady = 10)

    return



###############################################
#########  main screen

def main():
    #####
    ##### creating window and background 
    root = tk.Tk()
    root.geometry("1200x650")
    root.title("movietix ui")

    canvas = tk.Canvas(root, width = 1200, height = 200, highlightthickness = 0)
    canvas.pack(fill = "both", expand = True)

    bg_image = Image.open("images/bg2.png").resize((1200, 650)) # fit the screen
    bg = ImageTk.PhotoImage(bg_image)
    canvas.create_image(0, 0, image = bg, anchor = "nw")

    #####
    ##### top bar
    canvas.create_rectangle(0, 0, 1200, 120, fill = "#060c28", outline = "")

    # "logo"
    logo_image = Image.open("images/movietixtext.png").resize((330, 105))
    logo = ImageTk.PhotoImage(logo_image)
    canvas.create_image(27, 7, image = logo, anchor = "nw")

    canvas.bg = bg
    canvas.logo = logo

    # buttons
    button_frame = tk.Frame(master = root, relief = "raised", background = "#060c28")
    root.button_frame = button_frame
    button_frame.place(x = 900, y = 42)
    register = tk.Button(master = button_frame, text = "register", font = ("Arial", 12, "bold"), command = lambda: client_register_screen(root),
                      width = 12, height = 2, background = "#859bc4", fg = "#d9e4f7")
    register.pack(side = tk.LEFT)

    spacer = tk.Label(master = button_frame, width = 3, height = 3, bg = "#060c28")
    spacer.pack(side = tk.LEFT)

    login = tk.Button(master = button_frame, text = "log in",  font = ("Arial", 12, "bold"), fg = "#d9e4f7",
                      width = 12, height = 2, bg = "#859bc4", command = lambda: client_login_screen(root))
    login.pack(side = tk.LEFT)

    load_movies(root)

    root.mainloop()

if __name__ == "__main__":
    main()


