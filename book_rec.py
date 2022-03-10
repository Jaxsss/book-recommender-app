# import
import pandas as pd
import numpy as np
import streamlit as st
from isbntools.app import *
import string

# functions

#get isbn by bookname
def get_isbn(bookname):
    isbn = isbn_from_words(bookname)
    return isbn

# find author in dataset by book title
def find_author(bookname):
    author = books.loc[books['Book-Title'] == str(bookname), 'Book-Author'].iloc[0]
    author = string.capwords(author)
    return author

# get published year
def get_year(bookname):
    year = books.loc[books['Book-Title'] == str(bookname), 'Year-Of-Publication'].iloc[0]
    return year

# create css style for button
def button(isbn):
    link = "<form action='https://isbnsearch.org/isbn/" + str(
        isbn) + ') ' + "method='get' target='_blank'><button style='display: inline-flex; -webkit-box-align: center; align-items: center;" \
                       "-webkit-box-pack: center; justify-content: center; font-weight: 400; padding: 0.25rem 0.75rem; border-radius: 0.25rem; " \
                       "margin: 0px; line-height: 1.6; color: inherit; width: auto; user-select: none; " \
                       "background-color: rgb(19, 23, 32); border: 1px solid rgba(250, 250, 250, 0.2);' type='submit'>View the book</button></form>"
    return link

# load ratings
ratings = pd.read_csv('./BX-Book-Ratings.csv', encoding='cp1251', sep=';')
ratings = ratings[ratings['Book-Rating']!=0]

# load books
books = pd.read_csv('./BX-Books.csv',  encoding='cp1251', sep=';', on_bad_lines='skip', low_memory=False)
# apply lower to search authors
books = books.apply(lambda x: x.str.lower() if(x.dtype == 'object') else x)

# merge dataset
dataset = pd.merge(ratings, books, on=['ISBN'])
dataset_lowercase=dataset.apply(lambda x: x.str.lower() if(x.dtype == 'object') else x)

# Streamlit Page
st.set_page_config(page_title="Book Recommender App", page_icon=':notebook:')
st.title('Book Recommender App')
st.caption("This app gives you ability to find the best book based on your latest reading. "
           "Recommendations are based on our qualified reviewers and calculated by simply the best algorithm. We dare you to try it! :)")
st.caption('Be sure to put in both title and author!')
form = st.form(key='my_form')
selected_book_title = form.text_input(label='Enter your book title:')
selected_book_author = form.text_input(label="Enter the book's author:")
submit = form.form_submit_button('Get recommendations!')

# find the book title and author in dataset
tolkien_readers = dataset_lowercase['User-ID'][(dataset_lowercase['Book-Title'].str.contains(selected_book_title.lower())) & (
            dataset_lowercase['Book-Author'].str.contains(selected_book_author.lower()))]
tolkien_readers = tolkien_readers.tolist()
tolkien_readers = np.unique(tolkien_readers)

# final dataset
books_of_tolkien_readers = dataset_lowercase[(dataset_lowercase['User-ID'].isin(tolkien_readers))]

# Number of ratings per other books in dataset
number_of_rating_per_book = books_of_tolkien_readers.groupby(['Book-Title']).agg('count').reset_index()

# select only books which have actually higher number of ratings than threshold
books_to_compare = number_of_rating_per_book['Book-Title'][number_of_rating_per_book['User-ID'] >= 8]
books_to_compare = books_to_compare.tolist()
ratings_data_raw = books_of_tolkien_readers[['User-ID', 'Book-Rating', 'Book-Title']][books_of_tolkien_readers['Book-Title'].isin(books_to_compare)]

# group by User and Book and compute mean
ratings_data_raw_nodup = ratings_data_raw.groupby(['User-ID', 'Book-Title'])['Book-Rating'].mean()

# reset index to see User-ID in every row
ratings_data_raw_nodup = ratings_data_raw_nodup.to_frame().reset_index()
dataset_for_corr = ratings_data_raw_nodup.pivot(index='User-ID', columns='Book-Title', values='Book-Rating')

# lists
LoR_list = [selected_book_title.lower()]
result_list = []
worst_list = []
book_titles = []
book_names = []
book_correlations = []
book_rating = []

# if user clicks button, the script will run
if submit:
    # for each of the trilogy book compute:
    for LoR_book in LoR_list:
        #Take out the Lord of the Rings selected book from correlation dataframe
        dataset_of_other_books = dataset_for_corr.copy(deep=False)

        try:
            dataset_of_other_books.drop([LoR_book], axis=1, inplace=True)
        except:
            pass

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
        corr_fellowship = pd.DataFrame(list(zip(book_titles, correlations, avgrating)), columns=['book', 'corr','avg_rating'])
        corr_fellowship.head()

        # top 10 books with highest corr
        result = corr_fellowship.sort_values('corr', ascending=False).head(10)

        # add book information to the lists
        for name in result.itertuples(index=True, name="Pandas"):
            book_names.append(name.book)
            book_correlations.append(name.corr)
            book_rating.append(name.avg_rating)

        # finish result list
        result_list.append(corr_fellowship.sort_values('corr', ascending = False).head(10))

        #worst 10 books
        worst_list.append(corr_fellowship.sort_values('corr', ascending = False).tail(10))

    print(result_list[0])
    # make rating in percents up to 100%
    book_correlations = [int(x * 100) for x in book_correlations]

    # try statement to make sure no syntax error pops up during recommendation
    try:
        # main book 1
        isbn = get_isbn(str(book_names[0]))
        st.header('Best alternative book by reviewers')
        st.subheader('1. ')
        st.markdown(string.capwords(str(book_names[0])) + ' by ' + str(find_author(book_names[0])))
        st.image('https://covers.openlibrary.org/b/isbn/' + str(isbn) + '-L.jpg', width=250)
        st.markdown('Match: ' + str(book_correlations[0]) + '%')
        st.markdown('Average rating: ' + str(round(book_rating[0], 2)))
        st.markdown('Year: ' + str(get_year(book_names[0])))
        st.markdown(button(isbn), unsafe_allow_html=True)
        st.write("_____________________________")

        # try statement if there is not enough recommended books to show
        try:
            # all if statements to make sure rating is higher than zero
            if book_correlations[1] > 0:
                st.subheader('2. ')
                isbn = get_isbn(str(book_names[1]))
                st.markdown(string.capwords(str(book_names[1])) + ' by ' + str(find_author(book_names[1])))
                st.image('https://covers.openlibrary.org/b/isbn/' + str(isbn) + '-L.jpg', width=150)
                st.markdown('Match: ' + str(book_correlations[1]) + '%')
                st.markdown('Average rating: ' + str(round(book_rating[1], 2)))
                st.markdown('Year: ' + str(get_year(book_names[1])))
                st.markdown(button(isbn), unsafe_allow_html=True)
                st.write("_____________________________")
            else:
                pass
            if book_correlations[2] > 0:
                st.subheader('3. ')
                isbn = get_isbn(str(book_names[2]))
                st.markdown(string.capwords(str(book_names[2])) + ' by ' + str(find_author(book_names[2])))
                st.image('https://covers.openlibrary.org/b/isbn/' + str(isbn) + '-L.jpg', width=150)
                st.markdown('Match: ' + str(book_correlations[2]) + '%')
                st.markdown('Average rating: ' + str(round(book_rating[2], 2)))
                st.markdown('Year: ' + str(get_year(book_names[2])))
                st.markdown(button(isbn), unsafe_allow_html=True)
                st.write("_____________________________")
            else:
                pass
            if book_correlations[3] > 0:
                st.subheader('4. ')
                isbn = get_isbn(str(book_names[3]))
                st.markdown(string.capwords(str(book_names[3])) + ' by ' + str(find_author(book_names[3])))
                st.image('https://covers.openlibrary.org/b/isbn/' + str(isbn) + '-L.jpg', width=150)
                st.markdown('Match: ' + str(book_correlations[3]) + '%')
                st.markdown('Average rating: ' + str(round(book_rating[3], 2)))
                st.markdown('Year: ' + str(get_year(book_names[3])))
                st.markdown(button(isbn), unsafe_allow_html=True)
                st.write("_____________________________")
            else:
                pass

            if book_correlations[4] > 0:
                st.subheader('5. ')
                isbn = get_isbn(str(book_names[4]))
                st.markdown(string.capwords(str(book_names[4])) + ' by ' + str(find_author(book_names[4])))
                st.image('https://covers.openlibrary.org/b/isbn/' + str(isbn) + '-L.jpg', width=150)
                st.markdown('Match: ' + str(book_correlations[4]) + '%')
                st.markdown('Average rating: ' + str(round(book_rating[4], 2)))
                st.markdown('Year: ' + str(get_year(book_names[4])))
                st.markdown(button(isbn), unsafe_allow_html=True)
                st.write("_____________________________")
            else:
                pass
            if book_correlations[5] > 0:
                st.subheader('6. ')
                isbn = get_isbn(str(book_names[5]))
                st.markdown(string.capwords(str(book_names[5])) + ' by ' + str(find_author(book_names[5])))
                st.image('https://covers.openlibrary.org/b/isbn/' + str(isbn) + '-L.jpg', width=150)
                st.markdown('Match: ' + str(book_correlations[5]) + '%')
                st.markdown('Average rating: ' + str(round(book_rating[5], 2)))
                st.markdown('Year: ' + str(get_year(book_names[5])))
                st.markdown(button(isbn), unsafe_allow_html=True)
                st.write("_____________________________")
            else:
                pass
            if book_correlations[6] > 0:
                st.subheader('7. ')
                isbn = get_isbn(str(book_names[6]))
                st.markdown(string.capwords(str(book_names[6])) + ' by ' + str(find_author(book_names[6])))
                st.image('https://covers.openlibrary.org/b/isbn/' + str(isbn) + '-L.jpg', width=150)
                st.markdown('Match: ' + str(book_correlations[6]) + '%')
                st.markdown('Average rating: ' + str(round(book_rating[6], 2)))
                st.markdown('Year: ' + str(get_year(book_names[6])))
                st.markdown(button(isbn), unsafe_allow_html=True)
                st.write("_____________________________")
            else:
                pass

            if book_correlations[7] > 0:
                st.subheader('8. ')
                isbn = get_isbn(str(book_names[7]))
                st.markdown(string.capwords(str(book_names[7])) + ' by ' + str(find_author(book_names[7])))
                st.image('https://covers.openlibrary.org/b/isbn/' + str(isbn) + '-L.jpg', width=150)
                st.markdown('Match: ' + str(book_correlations[7]) + '%')
                st.markdown('Average rating: ' + str(round(book_rating[7], 2)))
                st.markdown('Year: ' + str(get_year(book_names[7])))
                st.markdown(button(isbn), unsafe_allow_html=True)
                st.write("_____________________________")
            else:
                pass
            if book_correlations[8] > 0:
                st.subheader('9. ')
                isbn = get_isbn(str(book_names[8]))
                st.markdown(string.capwords(str(book_names[8])) + ' by ' + str(find_author(book_names[8])))
                st.image('https://covers.openlibrary.org/b/isbn/' + str(isbn) + '-L.jpg', width=150)
                st.markdown('Match: ' + str(book_correlations[8]) + '%')
                st.markdown('Average rating: ' + str(round(book_rating[8], 2)))
                st.markdown('Year: ' + str(get_year(book_names[8])))
                st.markdown(button(isbn), unsafe_allow_html=True)
                st.write("_____________________________")
            else:
                pass
            if book_correlations[9] > 0:
                st.subheader('10. ')
                isbn = get_isbn(str(book_names[9]))
                st.markdown(string.capwords(str(book_names[9])) + ' by ' + str(find_author(book_names[9])))
                st.image('https://covers.openlibrary.org/b/isbn/' + str(isbn) + '-L.jpg', width=150)
                st.markdown('Match: ' + str(book_correlations[9]) + '%')
                st.markdown('Average rating: ' + str(round(book_rating[9], 2)))
                st.markdown('Year: ' + str(get_year(book_names[9])))
                st.markdown(button(isbn), unsafe_allow_html=True)
            else:
                pass
        except:
            pass
    except:
        st.error("This book might not be in the database, try checking the name and make sure you've typed full name of the book.")
else:
    pass