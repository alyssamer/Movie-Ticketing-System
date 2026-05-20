#include <iostream>
#include <libpq-fe.h>
#include <string>

using namespace std;

PGconn* connectDB() // Connects to our database
{
    PGconn* conn = PQconnectdb("dbname=movietix user=postgres password=mercado6 host = localhost");
    return conn;
}



//User login functions, amdmin/client login, client account registration
void registerUser(PGconn* conn) //Function that allows user to create a new accound
{
    string name;
    string email;
    string password;
    string interests;
    string rewardInput;

    cout << "Please enter your first and last name: ";
    cin.ignore();
    getline(cin, name);

    cout << "Please enter your email: ";
    getline(cin, email);

    cout << "Please enter your password: ";
    getline(cin, password);

    cout << "What is your favorite movie genre?: ";
    getline(cin, interests);

    cout << "Would you like to register to our rewards program? (yes/no): ";
    getline(cin, rewardInput);

    bool isRewardMember;

    if (rewardInput == "yes" || rewardInput == "Yes") 
    {
        isRewardMember = true;
    } 
    else 
    {
        isRewardMember = false;
    }

    string rewardVal;
    if (isRewardMember) {
        rewardVal = "TRUE";
    } 
    else 
    {
        rewardVal = "FALSE";
    }

    string query =
        "INSERT INTO client (name, email, password, interests, reward_member) VALUES ('" +
        name + "', '" + email + "', '" + password + "', '" + interests + "', " + rewardVal + ");";

    PGresult* res = PQexec(conn, query.c_str());

    cout << "Registration successful!\n";
    PQclear(res);
}




bool loginUser(PGconn* conn, string& emailKey) //Client login portal
{
    while(true) //Keeps prompting user until they input a valid combo of email and password
    {

    
        string email;
        string password;
        
        cout << "Please enter your email: ";
        cin >> email;

        cout << "Please enter the password assoicated with your email: ";
        cin >> password;


        string query = "SELECT email FROM client WHERE email = '" + email + "' AND password = '" + password + "';";
        PGresult* res = PQexec(conn, query.c_str());
        if(PQntuples(res) > 0) 
        {
            cout << "Successfully logged in!\n";
            emailKey = email;
            PQclear(res);
            return true;
        }
        else
        {
            cout << "Invalid Email/Password. Please try again.\n";
            PQclear(res);
        }
    }
}






bool adminLogin(PGconn* conn) //Admin only login portal
{
    while(true) //Keeps prompting user until they input a valid combo of email and password
    {

    
        string email;
        string password;
        
        cout << "Please enter your admin email: ";
        cin >> email;

        cout << "Please enter the password associated with this admin account: ";
        cin >> password;


        string query = "SELECT email FROM administration WHERE email = '" + email + "' AND password = '" + password + "';";
        PGresult* res = PQexec(conn, query.c_str());
        if(PQntuples(res) > 0) 
        {
            cout << "Successfully logged in as an admin!\n";
            PQclear(res);
            return true;
        }
        else //Not in DB
        {
            cout << "Invalid admin login. Please try again.\n";
            PQclear(res);
        }
    }
}



/// admin only add screenings view capacity 

// view remaining seat capacity for every screening
void viewSeatCapacity(PGconn* conn) {
    string query =
        "SELECT s.screening_id, m.title, t.theatre_id, t.max_occupancy, " 
        "COALESCE(SUM(ts.quantity_sold), 0) AS sold, "
        "t.max_occupancy - COALESCE(SUM(ts.quantity_sold), 0) AS available " // all viewable informatin
        "FROM screening_schedule s "
        "JOIN movies m ON s.movie_id = m.movie_id "
        "JOIN theatre t ON s.theatre_id = t.theatre_id " // inner join, need valid movie or theatre
        "LEFT JOIN occurs_in oi ON s.screening_id = oi.screening_id " 
        "LEFT JOIN ticket_sales ts ON oi.sale_id = ts.sale_id " // left join, just need every screening
        "GROUP BY s.screening_id, m.title, t.theatre_id, t.max_occupancy "
        "ORDER BY s.screening_id;";

    PGresult* res = PQexec(conn, query.c_str());
    if (PQresultStatus(res) != PGRES_TUPLES_OK) {
        cout << "Could not get capacity: " << PQerrorMessage(conn) << endl;
        PQclear(res);
        return;
    }

    if (PQntuples(res) == 0) {
        cout << "No screenings found.\n";
    } else {
        cout << "\n--- Screening Capacity ---\n";
        for (int i = 0; i < PQntuples(res); i++) {
            cout << "Screening ID: " << PQgetvalue(res, i, 0)
                 << " | Movie: " << PQgetvalue(res, i, 1)
                 << " | Theatre: " << PQgetvalue(res, i, 2)
                 << " | Max: " << PQgetvalue(res, i, 3)
                 << " | Sold: " << PQgetvalue(res, i, 4)
                 << " | Available: " << PQgetvalue(res, i, 5)
                 << endl;
        }
    }
    PQclear(res);
}


// schedule a new screening
void addScreening(PGconn* conn) {
    int movie_id, theatre_id;
    string date, time;

    cout << "Enter movie ID: ";
    cin >> movie_id;
    cout << "Enter theatre ID: ";
    cin >> theatre_id;
    cout << "Enter screening date (MM/DD/YYYY): ";
    cin >> date;
    cout << "Enter screening time (HH:MM): ";
    cin >> time;

    // check for valid movie and theatre
    string checkMovie = "SELECT 1 FROM movies WHERE movie_id = " + to_string(movie_id) + ";";
    PGresult* res = PQexec(conn, checkMovie.c_str());
    if (PQntuples(res) == 0) {
        cout << "Error: movie ID does not exist!\n";
        PQclear(res);
        return;
    }
    PQclear(res);

    string checkTheatre = "SELECT 1 FROM theatre WHERE theatre_id = " + to_string(theatre_id) + ";";
    res = PQexec(conn, checkTheatre.c_str());
    if (PQntuples(res) == 0) {
        cout << "Error: Theatre ID does not exist!\n";
        PQclear(res);
        return;
    }
    PQclear(res);

    //  new screening_id (max + 1)
    string getMax = "SELECT COALESCE(MAX(screening_id), 0) + 1 FROM screening_schedule;";
    res = PQexec(conn, getMax.c_str());
    int new_id = stoi(PQgetvalue(res, 0, 0));
    PQclear(res);

    // add it into the schedule table
    string insert = "INSERT INTO screening_schedule (screening_id, movie_id, theatre_id, date, time) VALUES (" +
                    to_string(new_id) + ", " +
                    to_string(movie_id) + ", " +
                    to_string(theatre_id) + ", '" +
                    date + "', '" + time + "');";

    res = PQexec(conn, insert.c_str());
    if (PQresultStatus(res) == PGRES_COMMAND_OK) {
        cout << "Screening added successfully! (ID: " << new_id << ").\n";
    } else {
        cout << "Could not add screening: " << PQerrorMessage(conn) << endl;
    }
    PQclear(res);
}


// revenue grouped by movie
void viewRevenueByMovie(PGconn* conn) {
    string query =
        "SELECT m.title, COALESCE(SUM(ts.quantity_sold * ts.ticket_price), 0) AS revenue "
        "FROM movies m "
        "LEFT JOIN screening_schedule s ON m.movie_id = s.movie_id "
        "LEFT JOIN occurs_in oi ON s.screening_id = oi.screening_id "
        "LEFT JOIN ticket_sales ts ON oi.sale_id = ts.sale_id "  // all left joins, needs a valid movie
        "GROUP BY m.title " 
        "ORDER BY revenue DESC;";

    PGresult* res = PQexec(conn, query.c_str());
    if (PQresultStatus(res) != PGRES_TUPLES_OK) {
        cout << "Error: " << PQerrorMessage(conn) << endl;
        PQclear(res);
        return;
    }

    cout << "\n--- Revenue by movie ---\n";
    if (PQntuples(res) == 0) {
        cout << "No ticket sales yet.\n";
    } else {
        for (int i = 0; i < PQntuples(res); i++) {
            cout << PQgetvalue(res, i, 0) << " : $" << PQgetvalue(res, i, 1) << endl;
        }
    }
    PQclear(res);
}

// average occupancy rate per theater
void viewOccupancyByTheater(PGconn* conn) {
    string query =
        "SELECT t.theatre_id, "
        "ROUND(AVG((COALESCE(sold.total_sold,0)::decimal / t.max_occupancy) * 100), 2) AS avg_occ " // avg occupancy as percentage! 
        "FROM theatre t "
        "LEFT JOIN screening_schedule s ON t.theatre_id = s.theatre_id "
        "LEFT JOIN ( "
        "  SELECT oi.screening_id, SUM(ts.quantity_sold) AS total_sold "
        "  FROM occurs_in oi "
        "  JOIN ticket_sales ts ON oi.sale_id = ts.sale_id " 
        "  GROUP BY oi.screening_id "
        ") sold ON s.screening_id = sold.screening_id "
        "GROUP BY t.theatre_id "
        "ORDER BY t.theatre_id;";

    PGresult* res = PQexec(conn, query.c_str());
    if (PQresultStatus(res) != PGRES_TUPLES_OK) {
        cout << "Error: " << PQerrorMessage(conn) << endl;
        PQclear(res);
        return;
    }

    cout << "\n--- Average occupancy rate by theater ---\n";
    if (PQntuples(res) == 0) {
        cout << "No screenings found.\n";
    } else {
        for (int i = 0; i < PQntuples(res); i++) {
            cout << "Theater " << PQgetvalue(res, i, 0)
                 << " : " << PQgetvalue(res, i, 1) << "%\n";
        }
    }
    PQclear(res);
}





void bookTickets(PGconn* conn, int screening_id, string emailKey) //Ticket booking function
{
    int quantity;
    cout << "How many tickets would you like? ";
    cin >> quantity;

    string checkQuery =
    "SELECT t.max_occupancy - COALESCE(SUM(ts.quantity_sold),0) "
    "FROM screening_schedule s "
    "JOIN theatre t ON s.theatre_id = t.theatre_id "
    "LEFT JOIN occurs_in oi ON s.screening_id = oi.screening_id "
    "LEFT JOIN ticket_sales ts ON oi.sale_id = ts.sale_id "
    "WHERE s.screening_id = " + to_string(screening_id) +
    " GROUP BY t.max_occupancy;";

    PGresult* res = PQexec(conn, checkQuery.c_str());

    if(PQntuples(res) == 0)
    {
        cout << "Invalid screening.\n";
        PQclear(res);
        return;
    }

    int available = stoi(PQgetvalue(res, 0, 0));
    PQclear(res);

    if(quantity > available) //Fails if user tries to buy more seays than there are
    {
        cout << "Not enough seats available.\n";
        return;
    }
    //THis is whay actually track the sale in our DB, buy 2 tickets, available tickets goes down by 2 etc.
    string insertSale =
    "INSERT INTO ticket_sales (sale_id, quantity_sold, ticket_price, client_email) \n    VALUES ((SELECT COALESCE(MAX(sale_id),0)+1 FROM ticket_sales), " + to_string(quantity) + ", 10, '" + emailKey + "') \n    RETURNING sale_id;";

    PGresult* res2 = PQexec(conn, insertSale.c_str());

    if (PQresultStatus(res2) != PGRES_TUPLES_OK || PQntuples(res2) == 0)
    {
        cout << "Error creating ticket sale: " << PQerrorMessage(conn) << endl;
        PQclear(res2);
        return;
    }

    int sale_id = stoi(PQgetvalue(res2, 0, 0));
    PQclear(res2);
    //Assigns a sale ID into the DB
    string insertOccurs =
    "INSERT INTO occurs_in (sale_id, theatre_id, screening_id) "
    "VALUES (" + to_string(sale_id) + ", "
    "(SELECT theatre_id FROM screening_schedule WHERE screening_id = "
    + to_string(screening_id) + "), "
    + to_string(screening_id) + ");";

    PGresult* res3 = PQexec(conn, insertOccurs.c_str());

    if(PQresultStatus(res3) == PGRES_COMMAND_OK) //Makes sure query is valid
    {
        cout << "Booking successful!\n";
    }
    else
    {
        cout << "Booking failed.\n";
    }

    PQclear(res3);
}



//Client menu functions searching, booking, updating payment methods etc.
void searchByTitle(PGconn* conn, string emailKey)
{
    string title;
    cout << "Please enter the name of the movie you want to watch: ";
    cin.ignore();
    getline(cin, title);

    string query =
    "SELECT m.title, s.screening_id, s.date, s.time, t.theatre_id, "
    "t.is_3d, t.has_fancy_sound, t.max_occupancy, "
    "(SELECT COALESCE(SUM(ts.quantity_sold),0) "
    " FROM ticket_sales ts "
    " JOIN occurs_in oi ON ts.sale_id = oi.sale_id "
    " WHERE oi.screening_id = s.screening_id), "
    "("                                             //Handles pricing depending on 3d, fancy, date, etc
    "(15 "
    "+ CASE WHEN t.is_3d THEN 5 ELSE 0 END "
    "+ CASE WHEN t.has_fancy_sound THEN 3 ELSE 0 END "
    "+ CASE WHEN m.is_major_studio THEN 3 ELSE 0 END "
    " ) "
    " * "
    " CASE "
    " WHEN m.release_date <= CURRENT_DATE - INTERVAL '2 years' THEN 0.6 "
    " WHEN m.release_date <= CURRENT_DATE - INTERVAL '2 months' THEN 0.8 "
    " ELSE 1 "
    " END "
    ") AS price "
    "FROM movies m "
    "JOIN screening_schedule s ON m.movie_id = s.movie_id "
    "JOIN theatre t ON s.theatre_id = t.theatre_id "
    "WHERE m.title ILIKE '%" + title + "%';";
    PGresult* res = PQexec(conn, query.c_str());

    cout << "\n--- Available Screenings ---\n";
    for(int i = 0; i < PQntuples(res); i++)
    {
        int capacity = stoi(PQgetvalue(res, i, 7));
        int sold = stoi(PQgetvalue(res, i, 8));
        int available = capacity - sold;

        cout << "Title: " << PQgetvalue(res, i, 0)
        << " | Screening ID: " << PQgetvalue(res, i, 1)
        << " | Date: " << PQgetvalue(res, i, 2)
        << " | Time: " << PQgetvalue(res, i, 3)
        << " | Theatre: " << PQgetvalue(res, i, 4)
        << " | 3D: " << PQgetvalue(res, i, 5)
        << " | Sound: " << PQgetvalue(res, i, 6)
        << " | Seats Available: " << available
        << " | Price: $" << PQgetvalue(res, i, 9)
        << endl;
    }

    int screening_id;
    cout << "\nEnter screening ID to book (0 to cancel): ";
    cin >> screening_id;

    if(screening_id != 0)
    {
        bookTickets(conn, screening_id, emailKey);
    }

    PQclear(res);
}




void searchByGenreTime(PGconn* conn, string emailKey)
{
    string genre;
    string time;
    cout << "What genre are you feeling like watching today?: ";
    cin.ignore();
    getline(cin, genre);
    cout << "Enter your earliest available time (HH:MM): ";
    getline(cin, time);

    string query =
    "SELECT m.title, s.screening_id, s.date, s.time, t.theatre_id, "
    "t.is_3d, t.has_fancy_sound, t.max_occupancy, "
    "(SELECT COALESCE(SUM(ts.quantity_sold),0) "
    " FROM ticket_sales ts "
    " JOIN occurs_in oi ON ts.sale_id = oi.sale_id "
    " WHERE oi.screening_id = s.screening_id), "
    "("                                         //Again, this is the dynamic pricing
    "(15 "
    "+ CASE WHEN t.is_3d THEN 5 ELSE 0 END "
    "+ CASE WHEN t.has_fancy_sound THEN 3 ELSE 0 END "
    "+ CASE WHEN m.is_major_studio THEN 3 ELSE 0 END "
    ") "
    "* "
    "CASE "
    "WHEN m.release_date <= CURRENT_DATE - INTERVAL '2 years' THEN 0.6 "
    " WHEN m.release_date <= CURRENT_DATE - INTERVAL '2 months' THEN 0.8 "
    " ELSE 1 "
    " END "
    ") AS price "
    "FROM movies m "
    "JOIN screening_schedule s ON m.movie_id = s.movie_id "
    "JOIN theatre t ON s.theatre_id = t.theatre_id "
    "WHERE m.genre ILIKE '%" + genre + "%' " //ILIKE helps with case sensitivity
    "AND s.time >= '" + time + "';";

    PGresult* res = PQexec(conn, query.c_str());
    cout << "\n--- Here's what's available ---\n";
    for(int i = 0; i < PQntuples(res); i++)
    {
        int capacity = stoi(PQgetvalue(res, i, 7));
        int sold = stoi(PQgetvalue(res, i, 8));
        int available = capacity - sold;

        cout << "Title: " << PQgetvalue(res, i, 0)
            << " | Screening ID: " << PQgetvalue(res, i, 1)
            << " | Date: " << PQgetvalue(res, i, 2)
            << " | Time: " << PQgetvalue(res, i, 3)
            << " | Theatre: " << PQgetvalue(res, i, 4)
            << " | 3D: " << PQgetvalue(res, i, 5)
            << " | Sound: " << PQgetvalue(res, i, 6)
            << " | Seats Available: " << available
            << " | Price: $" << PQgetvalue(res, i, 9)
            << endl;
    }
    int screening_id;
    cout << "\nEnter screening ID to book (0 to cancel): ";
    cin >> screening_id;

    if(screening_id != 0)
    {
        bookTickets(conn, screening_id, emailKey);
    }

    PQclear(res);

}



//Payment methods, view and add payment methods functions
void viewPaymentMethods(PGconn* conn, string emailKey) // allows user to view what cards they have on file
{
    string query = "SELECT type, card_number, billing_address FROM payment_method WHERE client_email = '" + emailKey + "';";
    PGresult* res = PQexec(conn, query.c_str());
    cout << "\n ---- Your Payment Methods ----\n";
    for(int i = 0; i < PQntuples(res);i++)
    {
        cout << "Type: " << PQgetvalue(res, i, 0) << " | Card: " << PQgetvalue(res, i, 1) << " | Address: " << PQgetvalue(res, i, 2) << endl; 
    }
    PQclear(res);
}

void addPaymentMethod(PGconn* conn, string emailKey)
{
    string type;
    string card;
    string address;

    cout << "Please enter card type (debit/credit): ";
    cin >> type;
    cout << "Please enter card number: ";
    cin >> card;
    cout << "Please enter the billing address assoicated with the card: ";
    cin.ignore();
    getline(cin, address);
    //Updates payment method with new one
    string query = "INSERT INTO payment_method (client_email, type, card_number, billing_address) VALUES ('" + emailKey + "', '" + type + "', '" + card + "', '" + address + "');";

    PGresult* res = PQexec(conn, query.c_str());
    cout << "Payment method saved!\n";
    PQclear(res);
}

void deletePayment(PGconn* conn, string emailKey) //Allows user to get rid of a payment method
{
    string card;
    cout << "Please enter the card number you would like to delete: ";
    cin >> card;
    string query = "DELETE FROM payment_method WHERE client_email = '" + emailKey + "' AND card_number = '" + card + "';";
    PGresult* res = PQexec(conn, query.c_str());
    cout << "Payment method deleted.\n";
    PQclear(res);
}

void paymentMenu(PGconn* conn, string emailKey) //Visual menu that allows user input
{
    int choice;
    while(true)
    {
        cout << "\n==== Payment Menu ====\n";
        cout << "1. View Payment Methods\n";
        cout << "2. Add Payment Method\n";
        cout << "3. Delete Payment Method\n";
        cout << "4. Back\n";
        cout << "Choice: ";
        cin >> choice;
        if(choice == 1)
        {
            viewPaymentMethods(conn, emailKey);
        }
        else if(choice == 2)
        {
            addPaymentMethod(conn, emailKey);
        }
        else if(choice == 3)
        {
            deletePayment(conn, emailKey);
        }
        else if(choice == 4)
        {
            break;
        }
        else
        {
            cout << "Invalid Choice, please try again.\n";
        }

    }
}

void clientMenu(PGconn* conn, string emailKey) //Similar to login screen, menu with different options specifically only for clients
{
    int choice;
    while(true)
    {
        cout << "\n==== Client Menu ====\n";
        cout << "Welcome, what would you like to do?\n";
        cout << "1. Search by movie name. I have a free schedule and a movie you need to watch\n";
        cout << "2. Search by genre and time. I have a strict schedule but I need to watch a movie\n";
        cout << "3. Manage Payment Methods\n";
        cout << "4. Close.\n";

        cout << "Choice: ";
        cin >> choice;
        if(choice == 1)
        {
            searchByTitle(conn, emailKey);
        }
        else if(choice == 2)
        {
            searchByGenreTime(conn, emailKey);
        }
        else if(choice == 3)
        {
            paymentMenu(conn, emailKey);
        }
        else if(choice == 4)
        {
            break;
        }
        else
        {
            cout << "Invalid Choice, please try again.\n";
        }
    }
}

// admin menu 
void adminMenu(PGconn* conn) {
    int choice;
    while (true) {
        cout << "\n==== ADMIN MENU ====\n";
        cout << "1. View Screening Seat Capacity\n";
        cout << "2. Add Movie Screening\n";
        cout << "3. Revenue by Movie\n";
        cout << "4. Occupancy Rate by Theater\n";
        cout << "5. Close\n";
        cout << "Choice: ";
        cin >> choice;

        if (choice == 1) {
            viewSeatCapacity(conn);
        } else if (choice == 2) {
            addScreening(conn);
        } else if (choice == 3) {
            viewRevenueByMovie(conn);
        } else if (choice == 4) {
            viewOccupancyByTheater(conn);
        } else if (choice == 5) {
            cout << "Closing out of admin menu.\n";
            break;
        } else {
            cout << "Invalid choice.\n";
        }
    }
}



int main() 
{
    PGconn* conn = connectDB();

    int choice;
    string currentUser;

    while (true) 
    {
        cout << "\n==== MAIN MENU ====\n";
        cout << "1. Register (Client)\n";
        cout << "2. Login (Client)\n";
        cout << "3. Login (Admin)\n";
        cout << "4. Exit\n";
        cout << "Choice: ";
        cin >> choice;

        if (choice == 1) 
        {
            registerUser(conn);
        } 
        else if(choice == 2)
        {
            loginUser(conn, currentUser);
            clientMenu(conn, currentUser);
        }
        else if(choice == 3)
        {
            if (adminLogin(conn)) {
                adminMenu(conn);
            }
        }
        else if (choice == 4)//Ends program. Like closing out a tab on a browser
        {
            break;
        }
        else 
        {
            cout << "Invalid input. Please try again.\n";
        }
       
    }
    PQfinish(conn);
    return 0;
}