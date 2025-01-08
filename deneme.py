import pandas as pd
import random

# Dosya adları
basics_file = "title.basics.tsv"
ratings_file = "title.ratings.tsv"

# Tüm desteklenen türler
SUPPORTED_GENRES = [
    "Action", "Comedy", "Drama", "Sci-Fi", "Thriller", "Horror", "Fantasy", "Romance"
]

# Filmleri filtreleme fonksiyonu
def filter_and_select_movies(genres, num_movies=30):
    # Dosyaları yükle
    basics = pd.read_csv(basics_file, sep='\t', dtype=str, na_values='\\N')
    ratings = pd.read_csv(ratings_file, sep='\t', dtype=str, na_values='\\N')

    # Verileri uygun türlere dönüştür
    basics['startYear'] = pd.to_numeric(basics['startYear'], errors='coerce')
    ratings['averageRating'] = pd.to_numeric(ratings['averageRating'], errors='coerce')
    ratings['numVotes'] = pd.to_numeric(ratings['numVotes'], errors='coerce')

    # Filmleri birleştir
    merged = basics.merge(ratings, on='tconst')

    # Kriterlere göre filtreleme
    filtered = merged[
        (merged['titleType'] == 'movie') &  # Sadece filmler
        (merged['startYear'] > 1940) &  # 1940'tan sonra
        (merged['averageRating'] > 5) &  # IMDb puanı 5'in üstünde
        (merged['numVotes'] > 1000)  # Oylama sayısı 1000'den fazla
    ]

    # Seçilen türlere göre filtreleme (tüm türlerin bulunduğu filmleri seç)
    def contains_all_selected_genres(genre_list, selected_genres):
        genre_set = set(genre_list.split(","))
        return all(genre in genre_set for genre in selected_genres)

    filtered = filtered[filtered['genres'].apply(lambda x: contains_all_selected_genres(str(x), genres))]

    # Filtreleme sonrası kontrol
    num_filtered = len(filtered)
    print(f"Filtrelenmiş film sayısı: {num_filtered}")

    if num_filtered == 0:
        print("Belirtilen kriterlere uygun film bulunamadı. Lütfen farklı türler seçin.")
        exit()

    # Eğer filtrelenmiş film sayısı istenenden azsa, hepsini döndür
    if num_filtered < num_movies:
        print(f"Seçilecek film sayısı {num_movies}, ancak yalnızca {num_filtered} uygun film bulundu.")
        return filtered[['primaryTitle', 'startYear', 'averageRating', 'genres']]

    # Rastgele seçim
    selected_movies = filtered.sample(n=num_movies, random_state=random.randint(1, 100000))
    return selected_movies[['primaryTitle', 'startYear', 'averageRating', 'genres']]

# Kullanıcıdan türleri al
print("Desteklenen türler:")
print(", ".join(SUPPORTED_GENRES))
print("Lütfen istediğiniz türü veya türleri virgülle ayırarak tam girin (örnek: Action, Comedy, Drama):")
user_input = input("Türler: ")

# Kullanıcı girdisini kontrol et
selected_genres = [genre.strip() for genre in user_input.split(",")]
for genre in selected_genres:
    if genre not in SUPPORTED_GENRES:
        print(f"Hata: '{genre}' desteklenen türler arasında değil.")
        print("Lütfen yalnızca şu türlerden seçim yapın:")
        print(", ".join(SUPPORTED_GENRES))
        exit()

# Filmleri seç ve yazdır
num_movies_to_select = 30
movies = filter_and_select_movies(selected_genres, num_movies_to_select)

# Sonuçları göster
print("\nSeçilen Filmler:")
print(movies)
