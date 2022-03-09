from flask import Flask, request, render_template
app = Flask(__name__)

@app.route('/index.html', methods=["GET", "POST"])

def get_book():
    if request.method == "POST":
       # getting input with name = fname in HTML form
       book_title = request.form.get("book-title")
       # getting input with name = lname in HTML form
       book_author = request.form.get("book-author")
       return "Your book is" + book_title + book_author
    return render_template("index.html")

if __name__=='__main__':
   app.run()