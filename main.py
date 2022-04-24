from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField.    ##In the html, the ckeditor should be placed in the <body> section
from datetime import datetime

now = datetime.now()
year = now.strftime("%Y")
month = now.strftime("%B")
date = now.strftime("%d")
written_on = f"{date} {month}, {year}"

app = Flask(__name__)
app.config['SECRET_KEY'] = ''
ckeditor = CKEditor(app)
Bootstrap(app)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

##CONFIGURE TABLE
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


##WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField('Blog Content', validators=[DataRequired()])
    submit = SubmitField("Submit Post")


@app.route('/')
def get_all_posts():
    posts = db.session.query(BlogPost).all()
    return render_template("index.html", all_posts=posts, year=year)


@app.route("/post/<int:index>")
def show_post(index):
    requested_post = None
    all_posts = db.session.query(BlogPost).all()
    for post in all_posts:
        if post.id == index:
            requested_post = post
    return render_template("post.html", post=requested_post)


@app.route("/edit-post/<post_id>", methods=["GET", "POST"])
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    # blog_to_update.title = "Harry Potter and the Goblet of Fire"
    # db.session.commit()
    create = CreatePostForm(request.form,
                            title=post.title,
                            subtitle=post.subtitle,
                            img_url=post.img_url,
                            author=post.author,
                            body=post.body
                            )
    if request.method == "POST" and create.validate():
        post.title = request.form["title"]
        post.subtitle = request.form["subtitle"]
        post.body = request.form["body"]
        post.author = request.form["author"]
        post.img_url = request.form["img_url"]
        db.session.commit()
        return redirect(url_for("show_post", index=post_id))
    return render_template("make-post.html", form=create, title="Edit Post")


@app.route("/new-post", methods=["GET", "POST"])
def add_post():
    create = CreatePostForm(request.form)
    if request.method == "POST" and create.validate():
        new_post = BlogPost(
                        title = request.form["title"],
                        subtitle = request.form["subtitle"],
                        date = written_on,
                        body = request.form["body"],
                        author =request.form["author"],
                        img_url = request.form["img_url"],
                    )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('get_all_posts'))
    return render_template("make-post.html", form=create, title="New Post")


@app.route("/delete-post/<int:index>", methods=["GET", "POST"])
def delete(index):
    post_to_delete = BlogPost.query.get(index)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for("get_all_posts"))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True)
