from datetime import datetime
import flask
import uuid
from flask import request, jsonify
from flask_sqlalchemy import SQLAlchemy
import hashlib
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os


app = flask.Flask(__name__)
app.config["DEBUG"] = True
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['UPLOAD_FOLDER'] = "/tmp/web/assets/"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///databases/DB.db'
CORS(app)

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


db = SQLAlchemy(app)

password_salt = "n69@@yes"
secret_salt = "bruh_wtf@@@6969"

(bad_secret) = ({
    "success": False,
    "error": "bad secret"
})
(missing_args) = ({
    "success": False,
    "error": "misisng arguments"
})
not_found = ({
    "success": False,
    "error": "not found"
})


def hash(hash_string, is_password=True):
    if is_password:
        salt = password_salt
    else:
        salt = secret_salt
    hash_string_salted = hash_string + salt
    sha_signature = hashlib.sha256(hash_string_salted.encode()).hexdigest()
    return sha_signature


class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    username = db.Column(db.String(25), nullable=False, unique=True)
    password = db.Column(db.String(25), nullable=False)
    email = db.Column(db.String(25), nullable=False, unique=True)
    profile_picture = db.Column(db.String(25), nullable=False, default="dafault_p.jpg")
    icon = db.Column(db.String(25), nullable=False, default="dafault_i.jpg")
    cover = db.Column(db.String(25), nullable=False, default="dafault_c.jpg")
    secret_user = db.Column(db.String(50))
    secret_hash = db.Column(db.String(50))

    posts = db.relationship("Post", backref="author", lazy=True)
    comments = db.relationship("Comment", backref="author", lazy=True)
    likes = db.relationship("Like", backref="author", lazy=True)
    followers = db.relationship("Follow", lazy=True, primaryjoin="Follow.followed_id== User.user_id",
                                backref="followed")
    following = db.relationship("Follow", lazy=True, primaryjoin="Follow.follower_id == User.user_id",
                                backref="follower")


class Post(db.Model):
    post_id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.Text)

    comments = db.relationship("Comment", backref="master", lazy=True)
    likes = db.relationship("Like", backref="master", lazy=True)


class Comment(db.Model):
    comment_id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("post.post_id"), nullable=False)

 
class Like(db.Model):
    like_id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)

    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("post.post_id"), nullable=False)

    
class Follow(db.Model):
    follow_id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)

    date_followed = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    follower_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)
    followed_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)


def login(username, password):
    user = User.query.filter_by(username=username, password=password).first()
    if user:
        return (user.user_id)
    else:
        return False


def check_secret(secret_user, secret_hash, id=False):
    user = User.query.filter_by(secret_user=secret_user, secret_hash=secret_hash).first()
    if not user:
        return False
    if id:
        return user.user_id
    return user


@app.route('/api/get/user', methods=['GET'])
def get_user():
    requirements = ["secret_user", "secret_hash", "user_id"]
    if all(r in request.args for r in requirements):
        if not check_secret(request.args["secret_user"], request.args["secret_hash"]):
            return jsonify(bad_secret)
        user = User.query.filter_by(user_id=request.args["user_id"]).first()
        if not (user):
            return jsonify(not_found)

        mini = {

            "username": user.username,
            "email": user.email,
            "profile_picture": user.profile_picture,

        }

        return jsonify(mini)

    return jsonify(missing_args)


@app.route('/api/get/followers', methods=['GET'])
def get_followers():
    comments = []
    requirements = ["secret_user", "secret_hash", "user_id"]
    if all(r in request.args for r in requirements):
        if not check_secret(request.args["secret_user"], request.args["secret_hash"]):
            return jsonify(bad_secret)
        user = User.query.filter_by(user_id=request.args["user_id"]).first()
        if user:
            for follower in user.followers:
                mini = {
                    "user_id": follower.follower.user_id,
                    "icon": follower.follower.icon,
                    "follow_id": follower.follow_id,
                    "username": follower.follower.username,
                }
                comments.append(mini)
        else:
            return jsonify(not_found)
        return jsonify(comments)

    else:
        return jsonify(missing_args)


@app.route('/api/get/following', methods=['GET'])
def get_following():
    comments = []
    requirements = ["secret_user", "secret_hash", "user_id"]
    if all(r in request.args for r in requirements):
        if not check_secret(request.args["secret_user"], request.args["secret_hash"]):
            return jsonify(bad_secret)
        user = User.query.filter_by(user_id=request.args["user_id"]).first()
        if user:
            for follower in user.following:
                mini = {

                    "user_id": follower.followed.user_id,
                    "icon": follower.followed.icon,
                    "follow_id": follower.follow_id,
                    "username": follower.followed.username,
                }
                comments.append(mini)
            return jsonify(comments)
        else:
            return jsonify(not_found)
    else:
        return jsonify(missing_args)


@app.route('/api/get/comments', methods=['GET'])
def get_comments():
    comments = []
    requirements = ["secret_user", "secret_hash", "post_id"]
    if all(r in request.args for r in requirements):
        if not check_secret(request.args["secret_user"], request.args["secret_hash"]):
            return jsonify(bad_secret)
        posts = Post.query.filter_by(post_id=request.args["post_id"]).first()
        if posts:
            for comment in posts.comments:
                mini = {
                    "comment_id": comment.comment_id,
                    "date_posted": comment.date_posted,
                    "content": comment.content,
                    "user_id": comment.user_id
                }
                comments.append(mini)
            return jsonify(comments)
        else:
            return jsonify(not_found)
    else:
        return jsonify(missing_args)


@app.route('/api/get/posts', methods=['GET'])
def get_posts():
    posts = []
    requirements = ["secret_user", "secret_hash", "user_id"]
    if all(r in request.args for r in requirements):
        if not check_secret(request.args["secret_user"], request.args["secret_hash"]):
            return jsonify(bad_secret)
        user = User.query.filter_by(user_id=request.args["user_id"]).first()
        if user:
            for post in user.posts:
                mini = {
                    "date_posted": post.date_posted,
                    "content": post.content,
                    "image": post.image,
                    "post_id": post.post_id,

                }
                posts.append(mini)
            return jsonify(posts)
        else:
            return jsonify(not_found)
    else:
        return jsonify(missing_args)


@app.route('/api/get/profile', methods=['GET'])
def get_profile():
    f_posts = []
    requirements = ["secret_user", "secret_hash"]
    if all(r in request.args for r in requirements):
        user = check_secret(request.args["secret_user"], request.args["secret_hash"])
        if not user:
            return jsonify(bad_secret)

        posts = user.posts

        for post in posts:
            comments = post.comments
            comments_filter = []
            mini = {}
            for comment in comments:
                # mini = {
                # 	"commentor_username": comment.author.username,
                # 	"content": comment.content,
                # 	"date": comment.date_posted,
                # 	"commenter_icon": comment.author.icon
                #
                # }
                mini = [comment.author.username, comment.content, comment.date_posted, comment.author.icon]
                comments_filter.append(mini)
            mini = {
                "comments": comments_filter,
                "postDate": post.date_posted,
                "postText": post.content,
                # "postImgURL": post.image,
                "postImgURL": "/assets/images/resources/user-post6.jppg",

                # "userIconURL": following.followed.icon,
                "userIconURL": "/assets/images/resources/admin.jpg",
                "postID": post.post_id,
                "userName": user.username,
                "likesCount": len(post.likes),
                "liked": bool(Like.query.filter_by(user_id=user.user_id, post_id=post.post_id).first())
            }
            f_posts.append(mini)
        return jsonify(f_posts)

    else:
        return jsonify(missing_args)


@app.route('/api/get/home', methods=['GET'])
def get_home():
    requirements = ["secret_user", "secret_hash"]
    if all(r in request.args for r in requirements):
        user = check_secret(request.args["secret_user"], request.args["secret_hash"])
        if not bool(user):
            return jsonify(bad_secret)
        posts = []
        followings = user.following
        for following in followings:
            f_posts = following.followed.posts
            for post in f_posts:
                comments = post.comments
                comments_filter = []
                mini = {}
                for comment in comments:
                    mini = [comment.author.username, comment.content, comment.date_posted, comment.author.icon]
                    comments_filter.append(mini)
                mini = {
                    "comments": comments_filter,
                    "postDate": post.date_posted,
                    "postText": post.content,
                    # "postImgURL": post.image,
                    "postImgURL": "/assets/images/resources/user-post6.jppg",

                    # "userIconURL": following.followed.icon,
                    "userIconURL": "/assets/images/resources/admin.jpg",
                    "postID": post.post_id,
                    "userName": following.followed.username,
                    "likesCount": len(post.likes),
                    "liked": bool(Like.query.filter_by(user_id=user.user_id, post_id=post.post_id).first())
                }
                posts.append(mini)

        return jsonify(posts)


@app.route('/api/reset', methods=['GET'])
def reset():
    db.drop_all()
    db.create_all()

    ex = [
        User(username="python", password=hash("python"), email="ppp@69.com",
             profile_picture="assets/images/resources/user-avatar.jpg", cover="assets/images/resources/timeline-1.jpg",
             icon="/assets/images/resources/nearly1.jpg'"),
        User(username="fag", password=hash("python"), email="nyes@669.com"),
        User(username="sean", password=hash("python"), email="ssss@669.com"),
        Post(user_id=1, content="by user 1 post1"),
        Post(user_id=2, content="by user 2 post1"),
        Post(user_id=2, content="by user 2 post2"),
        Post(user_id=2, content="by user 2 post3"),
        Post(user_id=2, content="by user 2 post4"),
        Post(user_id=3, content="by user 3 post1"),
        Post(user_id=3, content="by user 3 post2"),
        Post(user_id=3, content="by user 3 post3"),
        Post(user_id=3, content="hby user 3 post4"),

        Comment(content="by user 1 on post 1", user_id=1, post_id=1),
        Comment(content="by user 1 on post 2", user_id=1, post_id=5),
        Comment(content="hhhby user 3 on post 5", user_id=3, post_id=5),
        Like(user_id=2, post_id=1),
        Like(user_id=2, post_id=5),
        Like(user_id=1, post_id=3),
        Like(user_id=2, post_id=3),
        Like(user_id=3, post_id=1),

        Follow(follower_id=1, followed_id=2),
        Follow(follower_id=1, followed_id=3),
        Follow(follower_id=2, followed_id=1)

    ]

    for x in ex:
        db.session.add(x)
    db.session.commit()

    return jsonify({"success": True})


@app.route('/api/add/like', methods=['GET'])  # here!!!
def add_like():
    requirements = ["secret_user", "secret_hash", "post_id"]
    if all(r in request.args for r in requirements):
        user_id = check_secret(request.args["secret_user"], request.args["secret_hash"], True)

        if not user_id:
            return jsonify(bad_secret)
        post = Post.query.filter_by(post_id=request.args["post_id"]).first()
        if not (post):
            return jsonify({
                "success": False,
                "error": "post  not found"
            })
        followed_id = post.author.user_id
        if not (followed_id == user_id or Follow.query.filter_by(follower_id=user_id, followed_id=followed_id).first()):
            return jsonify({
                "success": False,
                "error": "follow them first"
            })

        if (Like.query.filter_by(user_id=user_id, post_id=request.args["post_id"]).first()):
            return jsonify({
                "success": False,
                "error": "like already exists"
            })

        like = Like(user_id=user_id, post_id=request.args["post_id"])
        db.session.add(like)
        db.session.commit()

        return jsonify({
            "success": True
        })
    return jsonify(missing_args)


@app.route('/api/remove/like', methods=['GET'])
def remove_like():
    requirements = ["secret_user", "secret_hash", "post_id"]
    if all(r in request.args for r in requirements):
        user_id = check_secret(request.args["secret_user"], request.args["secret_hash"], True)

        if not user_id:
            return jsonify(bad_secret)
        like = Like.query.filter_by(post_id=request.args["post_id"], user_id=user_id).first()
        if not like:
            return jsonify({
                "success": False,
                "error": "like does not exist"
            })
        db.session.delete(like)
        db.session.commit()

        return jsonify({
            "success": True
        })


    else:
        return jsonify(missing_args)


@app.route('/api/add/follow', methods=['GET'])
def add_follow():
    requirements = ["secret_user", "secret_hash", "followed_id"]

    if all(r in request.args for r in requirements):
        user_id = check_secret(request.args["secret_user"], request.args["secret_hash"], True)
        if not user_id:
            return jsonify(bad_secret)

        if (str(user_id) == request.args["followed_id"]):
            return jsonify({
                "success": False,
                "error": "you can't follow yourself"
            })

        if not (User.query.filter_by(user_id=request.args["followed_id"]).first()):
            return jsonify({
                "success": False,
                "error": "user not found"
            })

        if (Follow.query.filter_by(follower_id=user_id, followed_id=request.args["followed_id"]).first()):
            return jsonify({
                "success": False,
                "error": "follow already exists"
            })

        follow = Follow(follower_id=user_id, followed_id=request.args["followed_id"])
        db.session.add(follow)
        db.session.commit()

        return jsonify({
            "success": True
        })
    else:
        return jsonify(missing_args)


@app.route('/api/remove/follow', methods=['GET'])
def remove_follow():
    requirements = ["secret_user", "secret_hash", "followed_id"]

    if all(r in request.args for r in requirements):
        user_id = check_secret(request.args["secret_user"], request.args["secret_hash"], True)
        if not user_id:
            return jsonify(bad_secret)
        follow = Follow.query.filter_by(followed_id=request.args["followed_id"], follower_id=user_id).first()
        if not follow:
            return jsonify({
                "success": False,
                "error": "follow does not exist"
            })
        db.session.delete(follow)
        db.session.commit()

        return jsonify({
            "success": True
        })

    return jsonify(missing_args)


@app.route('/api/add/post', methods=['POST'])
def add_post():
    requirements = ["secret_user", "secret_hash", "text"]

    if all(r in request.form for r in requirements):
        user_id = check_secret(request.form["secret_user"], request.form["secret_hash"], True)
        if not user_id:
            return jsonify(bad_secret)
        path = None

        if 'picture' in request.files:

            file = request.files['picture']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                path = os.path.join(app.config['UPLOAD_FOLDER'] + "posts/", filename)
                file.save(path)

        post = Post(user_id=user_id, content=request.form["text"], image=path)
        db.session.add(post)
        db.session.commit()

        return jsonify({
            "success": True,
            "postID": post.post_id,
            "postImgURL": path
        })
    else:
        return jsonify(missing_args)


@app.route('/api/add/comment', methods=['GET'])  # here!!!
def add_comment():
    requirements = ["secret_user", "secret_hash", "post_id", "content"]
    if all(r in request.args for r in requirements):
        user_id = check_secret(request.args["secret_user"], request.args["secret_hash"], True)

        if not user_id:
            return jsonify(bad_secret)
        post = Post.query.filter_by(post_id=request.args["post_id"]).first()
        if not (post):
            return jsonify({
                "success": False,
                "error": "post  not found"
            })
        followed_id = post.author.user_id
        if not (followed_id == user_id or Follow.query.filter_by(follower_id=user_id, followed_id=followed_id).first()):
            return jsonify({
                "success": False,
                "error": "follow them first"
            })

        comment = Comment(user_id=user_id, post_id=request.args["post_id"], content=request.args["content"])
        db.session.add(comment)
        db.session.commit()

        return jsonify({
            "success": True
        })
    return jsonify(missing_args)

# app routing 
@app.route('/api/remove/comment', methods=['GET'])
def remove_comment():
    requirements = ["secret_user", "secret_hash", "comment_id"]
    if all(r in request.args for r in requirements):
        user_id = check_secret(request.args["secret_user"], request.args["secret_hash"], True)

        if not user_id:
            return jsonify(bad_secret)
        comment = Comment.query.filter_by(comment_id=request.args["comment_id"]).first()
        if not comment:
            return jsonify({
                "success": False,
                "error": "like does not exist"
            })
        db.session.delete(comment)
        db.session.commit()

        return jsonify({
            "success": True
        })


    else:
        return jsonify(missing_args)


@app.route('/api/add/user', methods=['GET'])
def add_user():
    if ("username" and "email" and "password") in request.args:
        if (User.query.filter_by(email=request.args["email"]).first()):
            return jsonify({
                "success": False,
                "error": "email already exists"
            })
        if (User.query.filter_by(username=request.args["username"]).first()):
            return jsonify({
                "success": False,
                "error": "username already exists"
            })

        user = User(email=request.args["email"], username=request.args["username"],
                    password=hash(request.args["password"]))
        db.session.add(user)
        db.session.commit()

        return jsonify({
            "success": True
        })
    return jsonify(missing_args)


@app.route('/api/change/profile_picture', methods=['POST'])
def change_profile_picture():
    requirements = ["secret_user", "secret_hash"]
    if all(r in request.form for r in requirements):
        user = check_secret(request.form["secret_user"], request.form["secret_hash"])
        if not user:
            return jsonify(bad_secret)

        if 'profile_picture' not in request.files:
            return jsonify(missing_args)
        file = request.files['profile_picture']
        if file.filename == '':
            return jsonify(missing_args)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'] + "profiles_pictures/", filename)
            file.save(path)

            user.profile_picture = path
            user.icon = user.profile_picture

            db.session.commit()

            return jsonify({
                "success": True,
                "porfile_picture": path,
                "icon": path
            })
    return jsonify(missing_args)


@app.route('/api/change/cover', methods=['POST'])
def change_cover():
    requirements = ["secret_user", "secret_hash"]
    if all(r in request.form for r in requirements):
        user = check_secret(request.form["secret_user"], request.form["secret_hash"])
        if not user:
            return jsonify(bad_secret)

        if 'cover' not in request.files:
            return jsonify(missing_args)
        file = request.files['cover']
        if file.filename == '':
            return jsonify(missing_args)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'] + "covers/", filename)
            file.save(path)

            user.cover = path

            db.session.commit()

            return jsonify({
                "success": True,
                "cover": path
            })
    return jsonify(missing_args)


@app.route('/api/authentication', methods=['GET'])
def api_all():
    reply = {
        "error": "bad request",
        "success": False,
    }
    if "password" in request.args and "username" in request.args:
        reply["error"] = False
        username = request.args["username"]
        password = request.args["password"]

        user = User.query.filter_by(username=username, password=hash(password)).first()

        if user:
            secret_user = str(uuid.uuid4())
            secret_hash = hash(str(uuid.uuid4()), False)

            secret_user = "a"
            secret_hash = "a"

            user.secret_user = secret_user
            user.secret_hash = secret_hash
            db.session.commit()

            reply["success"] = True
            reply["id"] = user.user_id
            reply["success"] = True
            reply["profile_picture"] = user.profile_picture
            reply["icon"] = user.icon
            reply["username"] = user.username
            reply["secret_user"] = secret_user
            reply["secret_hash"] = secret_hash
            reply["cover"] = user.cover
            reply.pop("error")
        else:
            reply["error"] = "bad login"

    return jsonify(reply)


# app.run()
app.run(host='0.0.0.0', port=5000, threaded=True)
