from flask import Flask, render_template, request, session, Blueprint, redirect, url_for, flash, current_app, send_file
from datetime import datetime, timedelta
import requests
import os, time

render = Blueprint('render', __name__)

@render.route('/', methods=['GET', 'POST'])
def index():
    if 'username' in session:
        logged_in = True
        username = session['username'][0]
        is_admin = session['username'][1]
        if is_admin:
            return redirect('/admin')
        else:
            if request.method == 'POST':
                title = request.form.get('title')
                print("title: ", title)
                return render_template('readbook.html', filename=title)
            response = requests.get(f'http://127.0.0.1:5000/api/books/borrowed/{username}')
            borrowed_books = response.json()
            print("borrowed_books: ", borrowed_books)
            return render_template('home.html', logged_in=logged_in, username=username, borrowed_books=borrowed_books)
    else:
        return redirect('/login')


@render.route('/login', methods=['GET', 'POST'])
def render_login_page():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        response = requests.post('http://127.0.0.1:5000/api/login', json={'username': username, 'password': password})

        if response.status_code == 200:
            isadmin = response.json()['isAdmin']
            session['username'] = username, isadmin
            return redirect('/')
        else:
            # Show toast message with login failure
            if response.status_code == 401:
                login_failed_toast = 'Invalid username or password. Please try again.'
                
            elif response.status_code == 404:
                login_failed_toast = 'User not found. Please register.'
            elif response.status_code == 500:
                login_failed_toast = 'Internal server error. Please try again later.'
            return render_template('login.html', toast_message=login_failed_toast)
    else:
        return render_template('login.html', toast_message=None)

@render.route('/register', methods=['GET', 'POST'])
def render_register_page():
    if request.method == 'POST':
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        isAdmin = request.form.get('isAdmin')

        response = requests.post('http://127.0.0.1:5000/api/register', json={'username': username, 'name':name, 'password': password, 'isAdmin': isAdmin})
        
        print("response: ", response.status_code)
        if response.status_code == 200:
            return redirect('/login')
        else:
            if response.status_code == 409:
                toast_message = 'Username already exists. Please try again with a different username.'
            elif response.status_code == 500:
                toast_message = 'Internal server error. Please try again later.'
                
            print('toast_message: ', toast_message)
            return render_template('register.html', toast_message=toast_message)
    else:
        return render_template('register.html', toast_message=None)
    
@render.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')

@render.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'username' in session:
        username = session['username'][0]
        if request.method == 'POST':
            name = request.form.get('name')
            email = request.form.get('email')
            bio = request.form.get('bio')

            print("Data to be updated:", username, name, email, bio)
            
            response = requests.post('http://127.0.0.1:5000/api/profile/update', json={'username': username, 'name': name, 'email': email, 'bio': bio})

            if response.status_code == 200:
                flash('Profile updated successfully.', 'success')
                toast_message = 'Profile updated successfully.'
                return render_template('profile.html', username=username, name=name, email=email, bio=bio, toast_message=toast_message)
            else:
                if response.status_code == 404:
                    toast_message = 'User not found. Please try again.'
                elif response.status_code == 500:
                    toast_message = 'Internal server error. Please try again later.'
                return render_template('profile.html', username=username, name=name, email=email, bio=bio, toast_message=toast_message)

        # Send a GET request to fetch user data
        response = requests.post('http://127.0.0.1:5000/api/profile', json={'username': username})

        if response.status_code == 200:
            user_data = response.json()
            print("data from API: ", user_data)
            name = user_data[1]
            email = user_data[3]
            bio = user_data[4]
            
            return render_template('profile.html', username=username, name=name, email=email, bio=bio, toast_message=None)
        else:
            flash('Failed to fetch user data.', 'error')
            return render_template('profile.html', username=username, toast_message=None)  
        
    flash('Please log in to view your profile.', 'error')
    return redirect('/login')

@render.route('/admin')
def admin():
    if 'username' in session and session['username'][1]:
        username = session['username'][0]
        response = requests.post('http://127.0.0.1:5000/api/profile', json={'username': username})

        if response.status_code == 200:
            user_data = response.json()
            name = user_data[0]
        return render_template('adminhome.html', name=name)
    else:
        return redirect('/login')

@render.route('/admin/manage/section', methods=['GET', 'POST'])
def manage_section():
    if 'username' in session:
        username = session['username'][0]

        if request.method == 'POST':
            method = request.form.get('_method', '').upper()  # Get the value of _method hidden field
            print("method: ", method)
            if method == 'PUT':
                # Update section
                section_id = request.form.get('edit_section_id')
                section_name = request.form.get('edit_section_name')
                section_desc = request.form.get('edit_section_desc')
                print("section_id: ", section_id, "section_name: ", section_name, "section_desc: ", section_desc)
                response = requests.put('http://127.0.0.1:5000/api/manage/sections', json={'id': section_id, 'name': section_name, 'desc': section_desc, 'method': 'PUT'}) 
                if response.status_code == 200:
                    flash('Section updated successfully.', 'success')
                else:
                    flash('Failed to update section.', 'error')
            elif method == 'DELETE':
                # Delete section
                section_id = request.form.get('delete_section_id')
                print("section_id: ", section_id)
                response = requests.delete('http://127.0.0.1:5000/api/manage/sections', json={'id': section_id, 'method': 'DELETE'})  
                if response.status_code == 200:
                    flash('Section deleted successfully.', 'success')
                else:
                    flash('Failed to delete section.', 'error')
            elif method == 'POST':
                # Create section
                section_name = request.form.get('section_name')
                section_desc = request.form.get('section_desc')
                response = requests.post('http://127.0.0.1:5000/api/manage/sections', json={'name': section_name, 'desc': section_desc, 'method': 'POST'})  
                if response.status_code == 200:
                    flash('Section created successfully.', 'success')
                else:
                    flash('Failed to create section.', 'error')

        sections = requests.get('http://127.0.0.1:5000/api/sections').json()
        print(sections)
        return render_template('managesections.html', sections=sections, toast_message=None)
    else:
        return redirect('/login')
    
@render.route('/admin/manage/books', methods=['GET', 'POST'])
def manage_books():
    if 'username' in session:
        username = session['username'][0]

        if request.method == 'POST':
            method = request.form.get('_method', '').upper()  # Get the value of _method hidden field
            print("method: ", method)
            if method == 'PUT':
                # Update book
                book_id = request.form.get('edit_book_id')
                book_title = request.form.get('edit_book_title')
                book_author = request.form.get('edit_book_author')
                book_section = request.form.get('edit_book_section')
                book_desc = request.form.get('edit_book_desc')
                book_copies = request.form.get('edit_book_copies')

                response = requests.put('http://127.0.0.1:5000/api/manage/books', json={'id': book_id, 'title': book_title, 'author': book_author, 'section_id': book_section, 'desc': book_desc, 'copies': book_copies})

                if response.status_code == 200:
                    flash('Book updated successfully.', 'success')
                else:
                    flash('Failed to update book.', 'error')
            
            elif method == 'DELETE':
                # Delete book
                book_id = request.form.get('delete_book_id')
                print("book_id: ", book_id)
                response = requests.get(f'http://127.0.0.1:5000/api/books/{book_id}')
                book = response.json()
                print("book: ", book)
                file = book[1] + '.pdf'
                save_path = os.path.join(current_app.config.get('UPLOAD_FOLDER'),file)

                response = requests.delete('http://127.0.0.1:5000/api/manage/books', json={'id': book_id, 'method': 'DELETE'})

                if response.status_code == 200:
                    flash('Book deleted successfully.', 'success')
                    if os.path.exists(save_path):
                        os.remove(save_path)

                else:
                    flash('Failed to delete book.', 'error')
            
            elif method == 'POST':
                # Create book
                book_title = request.form.get('title')
                book_author = request.form.get('author')
                book_section = request.form.get('section_id')
                book_desc = request.form.get('desc')
                book_copies = request.form.get('copies')

                file = request.files['book']
                save_path = os.path.join(current_app.config.get('UPLOAD_FOLDER'),file.filename)

                print("book_title: ", file.filename, "book_author: ", book_author, "book_section: ", book_section, "book_desc: ", book_desc, "book_copies: ", book_copies)

                response = requests.post('http://127.0.0.1:5000/api/manage/books', json={'title': book_title, 'author': book_author, 'section_id': book_section, 'desc': book_desc, 'copies': book_copies, 'method': 'POST'})
                
                if response.status_code == 200:
                    file.save(save_path)
                    flash('Book created successfully.', 'success')
                else:
                    flash('Failed to create book.', 'error')
        
        sections = requests.get('http://127.0.0.1:5000/api/sections').json()
        books = requests.get('http://127.0.0.1:5000/api/books').json()
        print(sections)
        print(books)
        return render_template('managebooks.html', sections=sections, books=books)
    else:
        return redirect('/login')
    
@render.route('/admin/manage/users', methods=['GET', 'POST'])
def manage_users():
    if 'username' in session:
        username = session['username'][0]

        # Fetch users data
        response_users = requests.get('http://127.0.0.1:5000/api/manage/users')
        users = response_users.json()

        # Fetch borrowed books data for each user
        borrows_data = []
        for user in users:
            user_id = user[0]
            response_borrows = requests.get(f'http://127.0.0.1:5000/api/books/borrowed/{user_id}')
            try:
                borrows = response_borrows.json()
            except ValueError:
                print("Response is not in valid JSON format")
                borrows = []
            borrows_data.append((user_id, borrows))

        return render_template('manageusers.html', users=users, borrows_data=borrows_data)
    else:
        return redirect('/login')
    
@render.route('/requests', methods=['GET', 'POST'])
def requests_page():
    if 'username' in session:
        username = session['username'][0]

        if request.method == 'POST':
            request_action = request.form.get('action')

            if request_action == 'ISSUE':
                request_id = request.form.get('request_id')

                response = requests.post('http://127.0.0.1:5000/api/issue', json={'request_id': request_id})
            elif request_action == 'REVOKE':
                username = request.form.get('username')
                book_id = request.form.get('book_id')

                response = requests.post(f'http://127.0.0.1:5000/api/revoke/{username}/{book_id}')

        # Fetch requests data
        response = requests.get('http://127.0.0.1:5000/api/requests', json={'username': username})
        requests_data = response.json()
        print("requests_data: ", requests_data)
    
        if response.status_code == 200:
            flash('Requests fetched successfully.', 'success')
        else:
            flash('Failed to fetch requests.', 'error')

        return render_template('requests.html', requests=requests_data)
    else:
        return redirect('/login')


    
@render.route('/books', methods=['GET', 'POST'])
def books():
    if 'username' in session:
        flag = 0
        if request.method == 'POST':
            # Ensure the user is logged in
            if 'username' not in session:
                flash('Please log in to request books.', 'error')
                return redirect('/login')

            book_id = request.form.get('book_id')
            username = session['username'][0]
            current_date = datetime.now().strftime('%d-%m-%Y')
            till_date = (datetime.now() + timedelta(days=14)).strftime('%d-%m-%Y')

            print("book_id: ", book_id, "username: ", username, "start_date: ", current_date, "end_date: ", till_date)

            check_count = requests.get('http://127.0.0.1:5000/api/request/getcount', json={'username': username})
            print("check_count: ", check_count.json())
            if check_count.json()['count'][0] >= 5:
                flag = -1

            check_already_requested = requests.get(f'http://127.0.0.1:5000/api/books/requests/{username}').json()
            print("check_already_requested: ", check_already_requested)
            for book in check_already_requested:
                if book[0] == int(book_id):
                    flag = -2
                    print("Book already requested")
                    break
                    
            if flag == 0:
                response = requests.post('http://127.0.0.1:5000/api/books/request', json={'book_id': book_id, 'username': username, 'start_date': current_date, 'end_date': till_date})

                if response.status_code == 200:
                    flash('Book requested successfully.', 'success')
                else:
                    flash('Failed to request book.', 'error')

        current_date = datetime.now().strftime('%d-%m-%Y')
        till_date = (datetime.now() + timedelta(days=14)).strftime('%d-%m-%Y')

        response = requests.get('http://127.0.0.1:5000/api/books')

        if response.status_code != 200:
            flash('Failed to fetch books data.', 'error')
            return redirect('/')

        books = response.json()
        if flag == -1:
            toast_message = 'You have already borrowed 5 books. Please return some books to borrow more.'
        elif flag == -2:
            toast_message = 'You have already requested this book. Please wait for approval.'
        else:
            toast_message = None
        return render_template('books.html', books=books, current_date=current_date, till_date=till_date, toast_message=toast_message)
    else:
        flash('Please log in to view books.', 'error')
        return redirect('/login')
    
@render.route('/viewBook/<string:filename>', methods=['GET', 'POST'])
def viewBook(filename):
    print("filename: ", filename)
    filename = filename + '.pdf'
    save_path = os.path.join(current_app.config.get('UPLOAD_FOLDER'),filename)
    if not os.path.exists(save_path):
        return "File not found", 404
    
    if not filename.lower().endswith('.pdf'):
        return "Invalid file format", 400
    
    response = send_file(save_path, as_attachment=False)
    response.headers['Content-Type'] = 'application/pdf'
    
    return response

@render.route('/search', methods=['GET', 'POST'])
def search():
    if 'username' in session:
        if request.method == 'POST':
            # Get the search criteria from the form
            title = request.form.get('title')
            author = request.form.get('author')
            section = request.form.get('section')

            response = requests.get('http://127.0.0.1:5000/api/search', json=({'title': title, 'author': author, 'section': section}))

            # Check if the request was successful
            if response.status_code == 200:
                books = response.json()['books']
                print('search books: ', books)
                return render_template('search.html', books=books)
            else:
                return render_template('search.html', books=None)
        else:
            books = requests.get('http://127.0.0.1:5000/api/books').json()
            return render_template('search.html', books=books)
    else:
        # If the user is not logged in, redirect to the login page
        return redirect('/login')
if __name__ == '__main__':
    render.run(debug=True)