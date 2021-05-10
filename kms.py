from datetime import datetime
import flask
import json
# import bder as bd
from flask import request, jsonify
from flask_sqlalchemy import SQLAlchemy
import hashlib



app = flask.Flask(__name__)
app.config["DEBUG"] = True

app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///databases/DB.db'
db=SQLAlchemy(app)

def hash(hash_string):
    sha_signature = hashlib.sha256(hash_string.encode()).hexdigest()
    return sha_signature


class User(db.Model):

	user_id=db.Column(db.Integer, primary_key=True, autoincrement=True,unique=True)
	username=db.Column(db.String(25), nullable=False, unique=True)
	password=db.Column(db.String(25), nullable=False)
	email=db.Column(db.String(25), nullable=False, unique=True)
	profile_picture=db.Column(db.String(25), nullable=False,  default="dafault_p.jpg")
	icon = db.Column(db.String(25), nullable=False, default="dafault_i.jpg")
	cover = db.Column(db.String(25), nullable=False, default="dafault_c.jpg")
	
	
	
	posts=db.relationship("Post",backref="author",lazy=True)
	comments=db.relationship("Comment", backref="author", lazy=True)
	likes=db.relationship("Like", backref="author", lazy=True)
	followers=db.relationship("Follow", lazy=True,primaryjoin="Follow.followed_id== User.user_id", backref="followed")
	following=db.relationship("Follow",  lazy=True,primaryjoin = "Follow.follower_id == User.user_id",backref="follower")



class Post(db.Model):

	post_id=db.Column(db.Integer, primary_key=True, autoincrement=True,unique=True)
	user_id=db.Column(db.Integer,db.ForeignKey("user.user_id"), nullable=False)
	date_posted=db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	content=db.Column(db.Text, nullable=False)
	image=db.Column(db.Text )

	comments=db.relationship("Comment", backref="master", lazy=True)
	likes=db.relationship("Like", backref="master", lazy=True)


class Comment(db.Model):
	comment_id=db.Column(db.Integer, primary_key=True, autoincrement=True,unique=True)
	date_posted=db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	content=db.Column(db.Text, nullable=False)
	user_id=db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)
	post_id=db.Column(db.Integer, db.ForeignKey("post.post_id"), nullable=False)

class Like(db.Model):
	like_id=db.Column(db.Integer, primary_key=True, autoincrement=True,unique=True)

	date_posted=db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

	user_id=db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)
	post_id=db.Column(db.Integer, db.ForeignKey("post.post_id"), nullable=False)

class Follow(db.Model):
	follow_id=db.Column(db.Integer, primary_key=True, autoincrement=True,unique=True)

	date_followed=db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

	follower_id=db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)
	followed_id=db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)






def login(username,password):
	user=User.query.filter_by(username=username,password=password).first()
	if user:
		return(user.user_id )
	else:
		return False


@app.route('/api/get/user', methods=['GET'])
def get_user():

	if ("user_id") in request.args:
		user=User.query.filter_by(user_id=	request.args["user_id"]).first()
		if not(user):
			return jsonify({
				"success": False,
				"error": "user not found"
				})


		mini={

		"username":user.username,
		"email":user.email,
		"profile_picture":user.profile_picture,


			}

		return jsonify(mini)

	return jsonify({
		"success":False,
		"error":"user_id not found"
		})






@app.route('/api/get/followers', methods=['GET'])
def get_followers():
	comments=[]
	if ("user_id") in request.args:
		user=User.query.filter_by(user_id=	request.args["user_id"]).first()
		for follower in user.followers:
			mini={
				"user_id": follower.follower.user_id,
				"icon":follower.follower.icon,
				"follow_id":follower.follow_id,
				"username_id":follower.follower.username,
				}
			comments.append(mini)
	return jsonify(comments)


@app.route('/api/get/following', methods=['GET'])
def get_following():
	comments=[]
	if ("user_id") in request.args:
		user=User.query.filter_by(user_id=	request.args["user_id"]).first()
		for follower in user.following:
			mini={
				"user_id": follower.followed_id,

				}
			comments.append(mini)
	return jsonify(comments)


@app.route('/api/get/comments', methods=['GET'])
def get_comments():
	comments=[]
	if ("post_id") in request.args:
		posts=Post.query.filter_by(user_id=	request.args["post_id"]).first()
		for comment in posts.comments:
			mini={
				"comment_id": comment.comment_id,
				"date_posted": comment.date_posted,
				"content" : comment.content,
				"user_id": comment.user_id
				}
			comments.append(mini)
	return jsonify(comments)

@app.route('/api/get/posts', methods=['GET'])
def get_posts():
	posts=[]
	if ("user_id") in request.args:
		user=User.query.filter_by(user_id=	request.args["user_id"]).first()
		for post in user.posts:
			mini={
				"date_posted": post.date_posted,
				"content": post.content,
				"image":post.image,
				"post_id":post.post_id,

				}
			posts.append(mini)
	return jsonify(posts)


@app.route('/api/get/profile', methods=['GET'])
def get_profile():

	f_posts=[]
	if ("user_id") in request.args:
		user=User.query.filter_by(user_id=	request.args["user_id"]).first()
		posts=user.posts

		for post in posts:
			comments = post.comments
			comments_filter = []
			mini = {}
			for comment in comments:
				mini = {
					"commentor_username": comment.author.username,
					"content": comment.content,
					"date": comment.date_posted,
					"commenter_icon": comment.author.icon

				}
				comments_filter.append(mini)
			mini = {
				"comments": comments_filter,
				"date_posted": post.date_posted,
				"content": post.content,
				"image": post.image,
				"poster_icon": user.icon,
				"post_id": post.post_id,
				"poster_username": user.username,
				"n_likes": len(post.likes)
			}
			f_posts.append(mini)
	return jsonify(f_posts)




@app.route('/api/get/home', methods=['GET'])
def get_home(user_id=None):
	posts=[]
	if ("user_id") in request.args or not(user_id is None) :
		if (user_id is None):
			user_id=request.args["user_id"]
		user=User.query.filter_by(user_id=user_id).first()
		followings=user.following
		for following in followings:
			f_posts=following.followed.posts
			for post in f_posts:
				comments=post.comments
				comments_filter=[]
				mini={}
				for comment in comments:




					mini={
						"commentor_username":comment.author.username,
						"content":comment.content,
						"date":comment.date_posted,
						"commenter_icon":comment.author.icon


					}
					comments_filter.append(mini)
				mini = {
					"comments":comments_filter,
					"date_posted": post.date_posted,
					"content": post.content,
					"image": post.image,
					"poster_icon": following.followed.icon,
					"post_id": post.post_id,
					"poster_username":following.followed.username,
					"n_likes":len(post.likes)
				}
				posts.append(mini)


	return jsonify(posts)






@app.route('/api/reset', methods=['GET'])
def reset():
	db.drop_all()
	db.create_all()

	ex=[
	User(username="python", password=hash("python"), email="ppp@69.com"),
	User(username="fag", password=hash("python"), email="nyes@669.com"),
	User(username="sean", password=hash("python"), email="ssss@669.com"),
	Post(user_id=1,  content="hi"),
	Post(user_id=2,  content="hi2"),
	Post(user_id=2,  content="hi2"),
	Post(user_id=2, content="hi2"),
	Post(user_id=2, content="hi2"),
	Post(user_id=3,  content="hi2"),
	Post(user_id=3,content="hi2"),
	Post(user_id=3,content="hi2"),
	Post(user_id=3,  content="hi2"),

	Comment(content="hhh",user_id=1,post_id=1),
	Comment(content="hhh",user_id=1,post_id=5),
	Comment(content="hhh2", user_id=3, post_id=5),
	Like(user_id=2,post_id=1),
	Like(user_id=2,post_id=5),
	Like(user_id=1,post_id=3),
	Like(user_id=2,post_id=3),


	Follow(follower_id=1, followed_id=2),
	Follow(follower_id=1, followed_id=3),
	Follow(follower_id=2,followed_id=3)


		]


	for x in ex:
		db.session.add(x)
	db.session.commit()

	return jsonify({"success":True})

@app.route('/api/add/like', methods=['GET'])
def add_like():
	if ("user_id" and "post_id") in request.args:
		if (Like.query.filter_by(user_id=request.args["user_id"],post_id=request.args["post_id"]).first()):
			return jsonify({
				"success": False,
				"error": "like already exists"
				})

		like=Like(user_id=request.args["user_id"],post_id=request.args["post_id"])
		db.session.add(like)
		db.session.commit()

		return jsonify({
						   "success": True
						   })
	return jsonify({
		"success": False,
		"error":"user_id or post_id not found"
		})

@app.route('/api/remove/like', methods=['GET'])
def remove_like():
	if ("like_id") in request.args:
		like=Like.query.filter_by(like_id=	request.args["like_id"]).first()
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

	return jsonify({
		"success": False,
		"error": "like_id not found"
		})


@app.route('/api/add/follow', methods=['GET'])
def add_follow():
	if ("follower_id" and "followed_id") in request.args:
		if (Follow.query.filter_by(follower_id=request.args["follower_id"],followed_id=request.args["followed_id"]).first()):
			return jsonify({
				"success": False,
				"error": "follow already exists"
				})

		follow=Follow(follower_id=request.args["follower_id"],followed_id=request.args["followed_id"])
		db.session.add(follow)
		db.session.commit()

		return jsonify({
						   "success": True
						   })
	return jsonify({
		"success": False,
		"error":"follower_id or followed_id not found"
		})

@app.route('/api/remove/follow', methods=['GET'])
def remove_follow():
	if ("follow_id") in request.args:
		follow=Follow.query.filter_by(follow_id=request.args["follow_id"]).first()
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

	return jsonify({
		"success": False,
		"error": "follow_id not found"
		})


@app.route('/api/add/user', methods=['GET'])
def add_user():
	if ("username" and "email" and "password" ) in request.args:
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


		user=User(email=request.args["email"],username=request.args["username"],password=hash(request.args["password"]))
		db.session.add(user)
		db.session.commit()

		return jsonify({
						   "success": True
						   })
	return jsonify({
		"success": False,
		"error":"username or email or password not found"
		})

@app.route('/api/change/profile_picture', methods=['GET'])
def change_profile_picture():
	if ("user_id","profile_picture") in request.args:
		user=User.query.filter_by(user_id=request.args["user_id"]).first()
		if not(user):
			return jsonify({
				"success": False,
				"error": "user not found"
				})
		user.profile_picture=request.args["profile_picture"]


		return jsonify({
						   "success": True
						   })
	return jsonify({
		"success": False,
		"error":"user_id not found"
		})






@app.route('/api/authentication', methods=['GET'])
def api_all():
	reply={
		"error":"bad request",
		"success":False,
		}
	if "password" in request.args and "username" in request.args:
		reply["error"] = False
		username=request.args["username"]
		password=request.args["password"]

		user = User.query.filter_by(username=username, password=hash(password)).first()



		if user:
			reply["success"]=True
			reply["id"]=user.user_id
			reply["success"]=True
			reply["profile_picture"]=user.profile_picture
			reply["icon"]=user.icon
			reply["username"]=user.username

			reply["cover"]=user.cover
			reply.pop("error")
		else:
			reply["error"]="bad login"





	return jsonify(reply)

app.run()
