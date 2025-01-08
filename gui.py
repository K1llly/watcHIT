import tkinter as tk
from tkinter import messagebox, Toplevel
import os
import pandas as pd

# Create or open the TSV file to store user data
USER_DATA_FILE = "users.tsv"
if not os.path.exists(USER_DATA_FILE):
    with open(USER_DATA_FILE, "w") as file:
        file.write("username\tpassword\n")  # Header for the TSV file

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# Variable to track the currently logged-in user
current_user = None

def register_user():
    username = entry_username.get()
    password = entry_password.get()

    if not username or not password:
        messagebox.showerror("Error", "Both username and password are required!")
        return

    # Load user data from the TSV file
    user_data = pd.read_csv(USER_DATA_FILE, sep="\t")
    if username in user_data["username"].values:
        messagebox.showerror("Error", "Username already exists!")
        return

    # Append new user
    new_user = pd.DataFrame([[username, password]], columns=["username", "password"])
    new_user.to_csv(USER_DATA_FILE, sep="\t", mode="a", header=False, index=False)

    messagebox.showinfo("Success", "User registered successfully!")
    entry_username.delete(0, tk.END)
    entry_password.delete(0, tk.END)

def login_user():
    global current_user
    username = entry_username.get().strip()  # Boşlukları temizle
    password = entry_password.get().strip()  # Boşlukları temizle

    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        current_user = username
        show_admin_panel()
        return

    if not username or not password:
        messagebox.showerror("Error", "Both username and password are required!")
        return

    try:
        # Load user data from the TSV file
        user_data = pd.read_csv(USER_DATA_FILE, sep="\t", dtype=str)  # Tüm verileri string olarak yükle
        user = user_data[(user_data["username"].str.strip() == username) & (user_data["password"].str.strip() == password)]

        if not user.empty:
            current_user = username
            messagebox.showinfo("Success", "Login successful!")
            show_main_app()
            return

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while processing login: {e}")
        return

    messagebox.showerror("Error", "Invalid username or password!")


def show_admin_panel():
    clear_main_window()

    def delete_user():
        username_to_delete = entry_delete_username.get()

        if not username_to_delete:
            messagebox.showerror("Error", "Username is required to delete!")
            return

        # Load user data
        user_data = pd.read_csv(USER_DATA_FILE, sep="\t")

        if username_to_delete in user_data["username"].values:
            user_data = user_data[user_data["username"] != username_to_delete]
            user_data.to_csv(USER_DATA_FILE, sep="\t", index=False)
            messagebox.showinfo("Success", "User deleted successfully!")
        else:
            messagebox.showerror("Error", "User not found!")

    def view_users():
        user_data = pd.read_csv(USER_DATA_FILE, sep="\t")
        users_list = user_data["username"].tolist()

        users_display.configure(state="normal")
        users_display.delete(1.0, tk.END)
        if users_list:
            users_display.insert(tk.END, "\n".join(users_list))
        else:
            users_display.insert(tk.END, "No users found.")
        users_display.configure(state="disabled")

    def logout():
        show_login_screen()

    label_delete_username = tk.Label(app, text="Enter username to delete:")
    label_delete_username.pack(pady=5)
    entry_delete_username = tk.Entry(app)
    entry_delete_username.pack(pady=5)
    button_delete_user = tk.Button(app, text="Delete User", command=delete_user)
    button_delete_user.pack(pady=5)

    button_view_users = tk.Button(app, text="View Users", command=view_users)
    button_view_users.pack(pady=5)

    users_display = tk.Text(app, height=10, width=40, state="disabled")
    users_display.pack(pady=5)

    button_logout = tk.Button(app, text="Back to Login Screen", command=logout)
    button_logout.pack(pady=10)

# Define the UI components for the main app and login screen
# (show_login_screen, show_main_app, clear_main_window should be implemented similarly)


def filter_and_select_movies(genres, num_movies=30):
    try:
        basics_file = "title.basics.tsv"
        ratings_file = "title.ratings.tsv"

        basics = pd.read_csv(basics_file, sep='\t', dtype=str, na_values='\\N')
        ratings = pd.read_csv(ratings_file, sep='\t', dtype=str, na_values='\\N')

        basics['startYear'] = pd.to_numeric(basics['startYear'], errors='coerce')
        ratings['averageRating'] = pd.to_numeric(ratings['averageRating'], errors='coerce')
        ratings['numVotes'] = pd.to_numeric(ratings['numVotes'], errors='coerce')

        merged = basics.merge(ratings, on='tconst')

        filtered = merged[
            (merged['titleType'] == 'movie') &
            (merged['genres'].notna()) &
            (merged['genres'].apply(lambda g: isinstance(g, str) and any(genre in g.split(',') for genre in genres))) &
            (merged['averageRating'] > 5)
        ]

        selected_movies = filtered.sample(n=min(num_movies, len(filtered)))

        return selected_movies[['primaryTitle', 'genres', 'averageRating', 'startYear']]
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")
        return None

def save_selected_movies(movies):
    if current_user:
        user_movies_file = f"{current_user}_movies.tsv"
        movies.to_csv(user_movies_file, sep='\t', index=False, mode='a', header=not os.path.exists(user_movies_file))

def show_user_movies():
    if current_user:
        user_movies_file = f"{current_user}_movies.tsv"
        if os.path.exists(user_movies_file):
            movies = pd.read_csv(user_movies_file, sep='\t')
            if not movies.empty:
                display_movies_window(movies)
            else:
                messagebox.showinfo("Info", "You haven't picked any movies yet.")
        else:
            messagebox.showinfo("Info", "You haven't picked any movies yet.")
    else:
        messagebox.showerror("Error", "Giriş yapmanız gerekiyor!")

def display_movies_window(movies):
    movie_window = Toplevel(app)
    movie_window.title("My Movie History")

    tk.Label(movie_window, text="Your Movie History", font=("Arial", 16)).pack(pady=10)

    movie_text = tk.Text(movie_window, wrap=tk.WORD, height=20, width=80)
    movie_text.pack(pady=10)

    user_ratings_file = f"{current_user}_ratings.tsv"
    user_reviews_file = f"{current_user}_reviews.tsv"

    if os.path.exists(user_ratings_file):
        user_ratings = pd.read_csv(user_ratings_file, sep='\t', index_col=0)
    else:
        user_ratings = pd.DataFrame(columns=['rating'])

    if os.path.exists(user_reviews_file):
        user_reviews = pd.read_csv(user_reviews_file, sep='\t', index_col=0)
    else:
        user_reviews = pd.DataFrame(columns=['review'])

    def rate_and_review_movie():
        try:
            movie_idx = int(entry_movie_idx.get()) - 1
            rating = int(entry_rating.get())
            review = entry_review.get()

            if rating < 1 or rating > 5:
                messagebox.showerror("Error", "Please pick your rating from 1 - 5")
                return

            if 0 <= movie_idx < len(movies):
                movie_title = movies.iloc[movie_idx]['primaryTitle']
                user_ratings.loc[movie_idx, 'rating'] = rating
                user_reviews.loc[movie_idx, 'review'] = review
                user_ratings.to_csv(user_ratings_file, sep='\t')
                user_reviews.to_csv(user_reviews_file, sep='\t')
                messagebox.showinfo("Success", f"For the movie '{movie_title}' you gave a rating of {rating} and you have commented.")
            else:
                messagebox.showerror("Error", "Please enter a valid movie number.")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number.")

    for idx, row in movies.iterrows():
        rating_display = ""
        review_display = ""
        if idx in user_ratings.index:
            rating_display = f" (My rating for this movie: {user_ratings.loc[idx, 'rating']})"
        if idx in user_reviews.index:
            review_display = f"\nMy opinions about this movie: {user_reviews.loc[idx, 'review']}"
        movie_text.insert(tk.END, f"{idx + 1}. Movie Name: {row['primaryTitle']}{rating_display}{review_display}\n")
        movie_text.insert(tk.END, f"Genres: {row['genres']}\n")
        movie_text.insert(tk.END, f"IMDb Score: {row['averageRating']}\n")
        movie_text.insert(tk.END, f"Production Year: {row['startYear']}\n\n")

    tk.Label(movie_window, text="Movie Number:").pack(pady=5)
    entry_movie_idx = tk.Entry(movie_window)
    entry_movie_idx.pack(pady=5)

    tk.Label(movie_window, text="Your Rating (1-5):").pack(pady=5)
    entry_rating = tk.Entry(movie_window)
    entry_rating.pack(pady=5)

    tk.Label(movie_window, text="Your Comment:").pack(pady=5)
    entry_review = tk.Entry(movie_window)
    entry_review.pack(pady=5)

    tk.Button(movie_window, text="Submit Rating and Comment", command=rate_and_review_movie).pack(pady=10)
    tk.Button(movie_window, text="Close", command=movie_window.destroy).pack(pady=10)

def show_main_app():
    clear_main_window()

    tk.Label(app, text=f"Hello, {current_user}!", font=("Arial", 20)).pack(pady=10)

    def execute_filter():
        selected_genres = [genre for genre, var in genre_vars.items() if var.get()]

        if not selected_genres:
            messagebox.showerror("Error", "Please select at least one genre.")
           
            return

        movies = filter_and_select_movies(selected_genres)
        if movies is not None:
            save_selected_movies(movies)
            output_text.delete(1.0, tk.END)
            for idx, (index, row) in enumerate(movies.iterrows(), start=1):
                output_text.insert(tk.END, f"{idx}. Movie Name: {row['primaryTitle']}\n")
                output_text.insert(tk.END, f"Genres: {row['genres']}\n")
                output_text.insert(tk.END, f"IMDb Score: {row['averageRating']}\n")
                output_text.insert(tk.END, f"Production Year: {row['startYear']}\n\n")

    tk.Label(app, text="Genres:").pack(anchor="w")
    genre_vars = {}
    genres = ["Action", "Comedy", "Drama", "Sci-Fi", "Thriller", "Horror", "Fantasy", "Romance"]

    for genre in genres:
        var = tk.BooleanVar()
        tk.Checkbutton(app, text=genre, variable=var).pack(anchor="w")
        genre_vars[genre] = var

    tk.Button(app, text="Filter and Find", command=execute_filter).pack(pady=10)
    tk.Button(app, text="Movie History", command=show_user_movies).pack(pady=10)

    global output_text
    output_text = tk.Text(app, wrap=tk.WORD, height=20, width=80)
    output_text.pack(pady=10)

def clear_main_window():
    for widget in app.winfo_children():
        widget.destroy()

# Create the main application window
app = tk.Tk()
app.title("watcHIT")

def show_login_screen():
    clear_main_window()

    tk.Label(app, text="Username:").pack(pady=5)
    global entry_username
    entry_username = tk.Entry(app)
    entry_username.pack(pady=5)

    tk.Label(app, text="Password:").pack(pady=5)
    global entry_password
    entry_password = tk.Entry(app, show="*")
    entry_password.pack(pady=5)

    tk.Button(app, text="Register", command=register_user).pack(pady=5)
    tk.Button(app, text="Login", command=login_user).pack(pady=5)

show_login_screen()
app.mainloop()
