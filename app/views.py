# import modules from standart python librarry
import os, random, string

# import modules from python packages
from flask          import render_template, request, url_for, redirect, flash, send_file
from flask_login    import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename

# import instances after initialization
from app            import app, lm, db, bc, csrf, logging
from app.models     import User, File
from app.forms      import LoginForm, RegistrationForm, FileUploadForm

# Callback for loading user from db by id 
@lm.user_loader
def load_user(user_id):
    try:
        return User.query.get(user_id)
    except:
        return None
    
# If not loggined on login required pages redirect to login page 
lm.login_view = 'login'

# home page
@app.route('/')
def index():
    # if user logged in return home page with list of files for downloading 
    if current_user.is_authenticated:
        files = File.query.filter_by(public = True).all()
        # gather all info about public files 
        files_list = []
        for file in files:
            files_list.append({"name":file.file_name,
                                "generated":file.generated_name,
                                "format":file.format,
                                "size":file.size,
                                "download_count":file.download_count})
        return render_template('index-loged.html',  files_list = files_list, csrf = csrf)
    # if user is not logged in return empty home page
    else:
        return render_template('index.html')

# register page
@app.route('/register', methods = ["GET", "POST"])
def register():
    # reset error message
    error = ''
    # get registration wtform
    form = RegistrationForm(request.form)
    # return register page
    if request.method == "GET":
        return render_template('register.html', form = form, error = error, csrf = csrf)
    # if method is post and if form is valid at the same time
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        found_user = User.query.filter_by(username = username).first()
        if found_user:
            error = "User Exist!"
        else:
            # create new user, log in and redirect to home
            password_hash = bc.generate_password_hash(password).decode("utf-8")
            user = User(username, password_hash, False)
            user.save()
            login_user(user)
            return redirect(url_for('index'))
    else:
        error = 'Input Error'

    return render_template('register.html', form = form, error = error , csrf = csrf)

@app.route('/login', methods=["GET","POST"])
def login():
    # reset error message
    error = ''
    flash('')
    # get login wtform
    form = LoginForm(request.form)
    # return login page
    if request.method == "GET":
        return render_template('login.html', form=form, error = error, csrf = csrf)
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        found_user = User.query.filter_by(username = username).first()
        # check if user exist, if exist check if password is correct
        if found_user:
            if bc.check_password_hash(found_user.password_hash, password):
                login_user(found_user)
                return redirect(url_for('index'))
            else:
                error = 'Wrong password'
        else:
            error = 'Unknown User'
        return render_template('login.html', form=form, error = error, csrf = csrf)
    else:
        return render_template('login.html', form=form, error = error, csrf = csrf)
    
@app.route('/logout', methods=["GET", "POST"])
def logout():
    logout_user()
    return redirect(url_for('index'))

# create admin role for test
@app.route("/admin/register")
def register_admin():
    found_user = User.query.filter_by(username = 'admin').first()
    if not found_user:
        admin_password_hash = bc.generate_password_hash('admin').decode("utf-8")
        admin = User('admin',admin_password_hash, True)
        admin.save()
    return redirect(url_for('login'))

# admin page for 
@app.route('/admin/uploads', methods = ["GET"])
@login_required
def admin_uploads():
    # if user is admin
    if current_user.admin_role:
        files = File.query.all()
        # get wtform for files uploading  
        form = FileUploadForm()
        if request.method == 'GET':
            # gather all info about files 
            files_list = []
            for file in files:
                files_list.append({"name":file.file_name,
                                   "generated":file.generated_name,
                                   "public":file.public,
                                   "format":file.format,
                                   "size":file.size,
                                   "download_count":file.download_count})
            # pass form, files info, csrf token to template and render 
            return render_template("admin-uploads.html", form = form, files_list = files_list, csrf = csrf)
    else:
        return redirect(url_for('index'))

@app.route('/admin/uploads/new', methods = ["POST"])
@login_required
def admin_uploads_new():
    # if user is admin
    if current_user.admin_role:
        # get wtform for files uploading  
        form = FileUploadForm()
        # if form valid
        if form.validate_on_submit():
            # get files list
            files = form.file.data
            # is files need to upload public
            public = form.check_public.data
            for f in files:
                filename = secure_filename(f.filename)
                name, format = os.path.splitext(filename)
                # generate new name for file to prevent overwriting
                generated_name = ''.join(random.choices(string.ascii_letters + string.digits, k=50))
                # construct path for file
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], generated_name+format)
                f.save(file_path)
                # if saved successfuly write file info into db
                if os.path.isfile(file_path):
                    size = float(os.path.getsize(file_path))/1000 # KB
                    file = File(name, generated_name, public, format, size)
                    file.save()
                else:
                    flash("Error Occured. Some files was not uploaded")
            return redirect(url_for('admin_uploads'))
    else:
        return redirect(url_for('index'))

# delete files by names
@app.route('/admin/uploads/delete/', methods = ["POST"])
@login_required
def file_delete():
    if current_user.admin_role:
        # files that was checked
        files = request.form.getlist('names')
        # delete files from db and file system
        for file_name in files:
            found_file = File.query.filter_by(generated_name = file_name).first()
            if found_file == None:
                return redirect(url_for('admin_uploads'))
            # construct path to file in file system
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], found_file.generated_name+found_file.format)
            # delete file
            if os.path.exists(file_path):
                os.remove(file_path)
            # if file not exist delete from db
            if not os.path.exists(file_path):
                File.query.filter_by(generated_name = file_name).delete()
        db.session.commit()
    return redirect(url_for('admin_uploads'))

# change public files status by links to protected or backwards
@app.route('/admin/uploads/public-change/', methods = ['POST'])
@login_required
def file_public_change():
    if current_user.admin_role:
        # files that was checked
        files = request.form.getlist('names')
        # change public file to protected or backwards
        for file_name in files:
            found_file = File.query.filter_by(generated_name = file_name).first()
            if found_file == None:
                return redirect(url_for('admin_uploads'))
            found_file.public = not found_file.public
        db.session.commit()
    return redirect(url_for('admin_uploads'))

# download file by link
@app.route('/uploads/<file_name>', methods = ['POST', 'GET'])
@login_required
def download_file(file_name):
    found_file = File.query.filter_by(generated_name = file_name).first()
    if found_file == None:
        return redirect(url_for('index'))
    # if file public or current user is admin 
    if current_user.admin_role or found_file.public:
        # construct path to file in file system
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], found_file.generated_name+found_file.format)
        # increment download count
        found_file.download_count += 1
        db.session.commit()
        # logging
        logging.info(f"User {current_user.username} downloaded file {found_file.generated_name} with name {found_file.file_name+found_file.format}")
        # download file with normal file name
        return send_file(file_path, download_name = found_file.file_name+found_file.format)
