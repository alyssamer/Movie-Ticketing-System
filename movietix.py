import tkinter as tk
from tkinter import *
from PIL import Image, ImageTk
import database


###############################################
######### register & login

### enters new user to database
def register_info(name_entry, email_entry, password_entry, interests, rewards, label):
    ### getting entries 
    name = name_entry.get()
    email = email_entry.get()
    password = password_entry.get()
    interest = interests.get()
    reward_info = rewards.get()

    ### insert into database
    registration = database.create_client_account(name, email, password, interest, reward_info)

    # if succees auto log in
    if registration:
        register_info.destroy()
    else:
        label.config(text = "registration failed")
    

    return 


### register new client for the website
def client_register_screen(root):
    register = tk.Toplevel(root)
    register.geometry("400x250")
    register.title("registration screen")

    ### close out registration page
    close = tk.Button(register, text = "close", command = register.destroy)
    close.pack()

    ### labels for users
    email_text = tk.Label(register, text = "email")
    pass_text = tk.Label(register, text = "password")


    ### user input
    email_entry = tk.Entry(register)
    password_entry = tk.Entry(register)


    ### pack in order
    email_text.pack()
    pass_text.pack()

    email_entry.pack()
    password_entry.pack()

    ### label for login validity information
    label = tk.Label(register, text = "") 
    label.pack()
    
    ### goes to registration func submits to databse
    register_button = tk.Button(register, text = "Login", 
                          command = lambda: register_info(email_entry, password_entry, label),
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
        if user == "client":
            label.config(text = "successful login")
            load_movies(root)
        else:
            label.config(text = "successful admin login")
            load_admin_dashboard(root)
    else:
        label.config(text = "email or password is incorrect")
    
    return


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
######### load current movies

def load_movies(root):
    ### currently showing movies from database
    movies = database.get_available_movies()

    ### destroy admin dashboard if it exists
    if hasattr(root, 'admin_frame') and root.admin_frame:
        root.admin_frame.destroy()

    ### frame to hold them
    movies_frame = tk.Frame(root, background = "#859bc4")
    root.movies_frame = movies_frame
    movies_frame.place(x = 200, y = 180, width = 800, height = 480)

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


### creates movie "card" 
def movie_card(scroll, movie_id, title, release_date, root):
    ### image on the left, title and times on the right
    card = tk.Frame(scroll, height = 150, bg = "#859bc4", highlightthickness = 0)
    card.pack(fill = "x", padx = 15, pady = 15)

    ### left - movie image
    image_filename = title + ".jpg"

    try:
        img = Image.open(f"images/{image_filename}").resize((170, 225))
        photo = ImageTk.PhotoImage(img)
        img_label = tk.Label(card, image = photo)
        img_label.image = photo
        img_label.pack(side = "left", padx = 15, pady = 15)

    except: # default if no image avail
        img_label = tk.Label(card, text = "no poster!", background = "#859bc4")
        img_label.pack(side = "left")

    ##### right side 
    right_frame = tk.Frame(card, background = "#859bc4")
    right_frame.pack(side = "left", fill = "both", expand = True)

    ### title and showing times
    title_label = tk.Label(right_frame, text = title, font = ("Arial", 12), fg = "#d9e4f7", background = "#859bc4")
    title_label.pack()

    # showtimes_frame = tk.Frame(right_frame)
    # showtimes_frame.pack()

    return



###############################################
######### load administration dashboard

def load_admin_dashboard(root):

    # destroy admin frame if it exists
    if hasattr(root, 'movies_frame') and root.movies_frame:
        root.movies_frame.destroy()
        
    admin_frame = tk.Frame(root, background="#859bc4")
    root.admin_frame = admin_frame
    admin_frame.place(x=200, y=180, width=800, height=400)
    
    # top text
    title = tk.Label(admin_frame, text="Admin Dashboard", font=("Arial", 16, "bold"),
                     bg="#859bc4", fg="#d9e4f7")
    title.pack(pady = 20)

    ### buttons for admin functions
    add_movie_button = tk.Button(admin_frame, text = "Add Movie", width=20, command = lambda: admin_screening(root))
    add_movie_button.pack(pady = 10)
    delete_account_button = tk.Button(admin_frame, text = "Delete Customer Account", width = 20, command = lambda: delete_account_screen(root))
    delete_account_button.pack(pady = 10)


    ### view analytics - revenue, remaining capacity, average occupancy 


    view_analytics_button = tk.Button(admin_frame, text = "View Analytics", width = 20, command = lambda: view_analytics(root))
    view_analytics_button.pack(pady = 10)

    return


### 
def delete_button(root, email_entry):
    email = email_entry.get()
    database.delete_client_account(email)
    return


### delete a customers account by email
def delete_account_screen(root):
    delete_account = tk.Toplevel(root)
    delete_account.geometry("400x250")
    delete_account.title("delete customer account")

    ### close out registration page
    close = tk.Button(delete_account, text = "close", command = delete_account.destroy)
    close.pack()

    ### labels for users
    email_text = tk.Label(delete_account, text = "email of account to delete")
    email_text.pack()

    ### user input
    email_entry = tk.Entry(delete_account)
    email_entry.pack()

    ### label for login validity information
    label = tk.Label(delete_account, text = "") 
    label.pack()
    
    ### goes to func submits to databse
    delete_button = tk.Button(delete_account, text = "Delete Account", 
                          command = lambda: delete_button(root, email_entry),
                          width=15, height=2, bg="#859bc4")
    delete_button.pack()

    delete_account.update()
    
    return


### send to database to add movie screening
def add_movie_screening(root, title_entry, date_entry, time_entry, theatre_entry):
    title = title_entry.get()
    date = date_entry.get()
    time = time_entry.get()
    theatre = theatre_entry.get()

    # add to database
    database.add_movie_screening(title, date, time, theatre)

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

    theater_label = tk.Label(add_movie, text = "Theater:")
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

    return




### view various analytics about movie sales and customers
def view_analytics(root):
    analytics = tk.Toplevel(root)
    analytics.geometry("600x450")
    analytics.title("Analytics")

    # close button
    close = tk.Button(analytics, text = "close", command = analytics.destroy)
    close.pack()


    # placeholder for now
    placeholder = tk.Label(analytics, text = "analytics coming soon!", font = ("Arial", 14), bg = "#859bc4", fg = "#d9e4f7")
    placeholder.pack(pady = 20)

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

    bg_image = Image.open("images/bg.jpg").resize((1200, 650)) # fit the screen
    bg = ImageTk.PhotoImage(bg_image)
    canvas.create_image(0, 0, image = bg, anchor = "nw")

    #####
    ##### top bar
    canvas.create_rectangle(0, 0, 1200, 120, fill = "#060c28", outline = "")

    # "logo"
    logo_image = Image.open("images/movietixtext.png").resize((300, 100))
    logo = ImageTk.PhotoImage(logo_image)
    canvas.create_image(27, 7, image = logo, anchor = "nw")

    canvas.bg = bg
    canvas.logo = logo

    # buttons
    button_frame = tk.Frame(master = root, relief = "raised", background = "#060c28")
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


