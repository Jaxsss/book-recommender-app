# import
import pandas as pd
import numpy as np
import streamlit as st
from isbntools.app import *
import string

def get_isbn(bookname):
    isbn = isbn_from_words(bookname)
    return isbn

# load ratings
ratings = pd.read_csv('./BX-Book-Ratings.csv', encoding='cp1251', sep=';')
ratings = ratings[ratings['Book-Rating']!=0]

# load books
<<<<<<< Updated upstream
books = pd.read_csv('./BX-Books.csv',  encoding='cp1251', sep=';', on_bad_lines='skip', low_memory=False)
=======
books = pd.read_csv('./BX-Books.csv', encoding='cp1251', sep=';', on_bad_lines='skip', low_memory=False)
>>>>>>> Stashed changes

#users_ratings = pd.merge(ratings, users, on=['User-ID'])
dataset = pd.merge(ratings, books, on=['ISBN'])
dataset_lowercase=dataset.apply(lambda x: x.str.lower() if(x.dtype == 'object') else x)

# Streamlit Page
st.title('Book Recommender App')
st.caption("This app gives you ability to find the best book based on your latest reading. Recommendations are based on our qualified reviewers and calculated by simply the best algorithm. We dare you to try it! :)")
form = st.form(key='my_form')
selected_book_title = form.text_input(label='Enter your book title:')
selected_book_author = form.text_input(label="Enter the book's author:")
submit = form.form_submit_button('Get recommendations!')

# find the book title and author in dataset
tolkien_readers = dataset_lowercase['User-ID'][(dataset_lowercase['Book-Title'] == selected_book_title.lower()) & (
            dataset_lowercase['Book-Author'].str.contains(selected_book_author.lower()))]
tolkien_readers = tolkien_readers.tolist()
tolkien_readers = np.unique(tolkien_readers)

# final dataset
books_of_tolkien_readers = dataset_lowercase[(dataset_lowercase['User-ID'].isin(tolkien_readers))]

# Number of ratings per other books in dataset
number_of_rating_per_book = books_of_tolkien_readers.groupby(['Book-Title']).agg('count').reset_index()

#select only books which have actually higher number of ratings than threshold
books_to_compare = number_of_rating_per_book['Book-Title'][number_of_rating_per_book['User-ID'] >= 8]
books_to_compare = books_to_compare.tolist()

ratings_data_raw = books_of_tolkien_readers[['User-ID', 'Book-Rating', 'Book-Title']][books_of_tolkien_readers['Book-Title'].isin(books_to_compare)]

# group by User and Book and compute mean
ratings_data_raw_nodup = ratings_data_raw.groupby(['User-ID', 'Book-Title'])['Book-Rating'].mean()

# reset index to see User-ID in every row
ratings_data_raw_nodup = ratings_data_raw_nodup.to_frame().reset_index()

dataset_for_corr = ratings_data_raw_nodup.pivot(index='User-ID', columns='Book-Title', values='Book-Rating')

LoR_list = [selected_book_title.lower()]

result_list = []
worst_list = []

<<<<<<< Updated upstream
book_names = []
book_correlations = []
book_rating = []

if submit:
    # for each of the trilogy book compute:
    for LoR_book in LoR_list:
        #Take out the Lord of the Rings selected book from correlation dataframe
        dataset_of_other_books = dataset_for_corr.copy(deep=False)

        try:
            dataset_of_other_books.drop([LoR_book], axis=1, inplace=True)
        except:
            print("This book might not be in the database, try check the name and make sure you've typed full name of the book")

        # empty lists
        book_titles = []
        correlations = []
        avgrating = []

        # corr computation
        for book_title in list(dataset_of_other_books.columns.values):
            book_titles.append(book_title)
            correlations.append(dataset_for_corr[LoR_book].corr(dataset_of_other_books[book_title]))
            tab=(ratings_data_raw[ratings_data_raw['Book-Title']==book_title].groupby(ratings_data_raw['Book-Title']).mean())
            avgrating.append(tab['Book-Rating'].min())

        # final dataframe of all correlation of each book
        corr_fellowship = pd.DataFrame(list(zip(book_titles, correlations, avgrating)), columns=['book','corr','avg_rating'])
        corr_fellowship.head()

        # top 10 books with highest corr
        result = corr_fellowship.sort_values('corr', ascending=False).head(10)

        for name in result.itertuples(index=True, name="Pandas"):
            book_names.append(name.book)
            book_correlations.append(name.corr)
            book_rating.append(name.avg_rating)

        result_list.append(corr_fellowship.sort_values('corr', ascending = False).head(10))

        #worst 10 books
        worst_list.append(corr_fellowship.sort_values('corr', ascending = False).tail(10))



    print("Correlation for book:", LoR_list[0])
    #print("Average rating of LOR:", ratings_data_raw[ratings_data_raw['Book-Title']=='the fellowship of the ring (the lord of the rings, part 1'].groupby(ratings_data_raw['Book-Title']).mean())
    rslt = result_list[0]
    print(rslt, book_names[0], book_correlations[0], book_rating[0])

    st.subheader('Best alternative book by reviewers')
    isbn = get_isbn(str(book_names[0]))
    st.markdown(string.capwords(str(book_names[0])))
    st.image('https://covers.openlibrary.org/b/isbn/' + str(isbn) + '-L.jpg', width=200)
    link = '[Show the book](https://isbnsearch.org/isbn/' + str(isbn) + ')'
    st.markdown(link, unsafe_allow_html=True)
else:
    pass

=======
# for each of the trilogy book compute:
for LoR_book in LoR_list:
    
    #Take out the Lord of the Rings selected book from correlation dataframe
    dataset_of_other_books = dataset_for_corr.copy(deep=False)
    dataset_of_other_books.drop([LoR_book], axis=1, inplace=True)
      
    # empty lists
    book_titles = []
    correlations = []
    avgrating = []

    # corr computation
    for book_title in list(dataset_of_other_books.columns.values):
        book_titles.append(book_title)
        correlations.append(dataset_for_corr[LoR_book].corr(dataset_of_other_books[book_title]))
        tab=(ratings_data_raw[ratings_data_raw['Book-Title']==book_title].groupby(ratings_data_raw['Book-Title']).mean())
        avgrating.append(tab['Book-Rating'].min())
    # final dataframe of all correlation of each book   
    corr_fellowship = pd.DataFrame(list(zip(book_titles, correlations, avgrating)), columns=['book','corr','avg_rating'])
    corr_fellowship.head()

    # top 10 books with highest corr
    result_list.append(corr_fellowship.sort_values('corr', ascending = False).head(10))
    
    #worst 10 books
    worst_list.append(corr_fellowship.sort_values('corr', ascending = False).tail(10))

print(LoR_list)
print("Correlation for book:", LoR_list[0])
#print("Average rating of LOR:", ratings_data_raw[ratings_data_raw['Book-Title']=='the fellowship of the ring (the lord of the rings, part 1'].groupby(ratings_data_raw['Book-Title']).mean())
rslt = result_list[0]
print(rslt)
>>>>>>> Stashed changes
