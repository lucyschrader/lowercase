from flask import Flask, render_template, request, flash, redirect, url_for, jsonify, Markup
import os, pymongo, re, arrow
from pymongo import MongoClient
from flask.ext.login import LoginManager
from classes import newPost
from unidecode import unidecode

application = app = Flask('lowercase')
app.config.from_object('config')

# Set connection to mongodb
#COMPOSE_URL = os.environ.get('COMPOSE_URL')
#client = MongoClient(COMPOSE_URL)
#db = client.lowercase_db
#content = db.lowercase

# Local connection
connection = pymongo.Connection()
db = connection["personal_db"]
content = db["content"]

# For making url slugs
_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')

# Page type options
page_types = ['Blog', 'Making']

@app.route('/')
def home():
    posts = content.find().limit(5)
    return render_template('main.html',
        posts = posts
        )

@app.route('/blog')
def blog():
    posts = content.find({'page_type': 'blog'})
    return render_template('blog.html',
        posts = posts
        )

@app.route('/makings')
def makings():
    posts = content.find({'page_type': 'making'})
    return render_template('making.html',
        posts = posts
        )

@app.route('/post/<url_slug>')
def single_post(url_slug):
    for i in content.find({'url_slug': url_slug}):
        post = i
        if post['page_type'] == 'Blog':
            return render_template('blogpost.html', post = post)
        elif post['page_type'] == 'Making':
            return render_template('makingpost.html', post = post)

@app.route('/cms')
def cms():
    pages = content.find()
    return render_template('cms.html',
        pages = pages
        )

# TODO - make saving as draft work, and save and continue editing
@app.route('/newpost', methods=['GET', 'POST'], defaults={'url_slug': None})
@app.route('/post/<url_slug>/edit', methods=['GET', 'POST'])
def new(url_slug):
    if url_slug:
        for i in content.find({'url_slug': url_slug}):
            post = i
        publication_time = arrow.get(post["publication_time"])
    else:
        post = None
        publication_time = arrow.now()
    if request.method == 'POST':
        request.get_data()
        form = request.form
        updates = handle_new_data(form, post)
        if post:
            content.update(
                {'_id': post["_id"]},
                {"$set":updates},
                upsert=True
                )
        else:
            content.insert(updates)
        return redirect(url_for('cms'))
    return render_template("newpost.html",
        post = post,
        page_types = page_types,
        publication_time = publication_time
        )

def handle_new_data(form_data, post):
    updates = {}
    for k in form_data:
        if "datestamp" in k:
            pass
        else:
            field_data = form_data[k]
            updates[str(k)] = field_data
    publication_time = arrow.get(int(form_data["datestamp_year"]), int(form_data["datestamp_month"]), int(form_data["datestamp_day"]))
    publication_time = publication_time.datetime
    print publication_time
    updates['publication_time'] = publication_time
    if post:
        pass
    else:
        url_slug = slugify(form_data['title'])
        updates['url_slug'] = url_slug
    return updates

def slugify(text, delim=u'-'):
    """Generates an ASCII-only slug. Thanks Armin Ronacher!"""
    result = []
    for word in _punct_re.split(text.lower()):
        result.extend(unidecode(word).split())
    return unicode(delim.join(result))

@app.route('/testform', methods=['GET', 'POST'], defaults={'url_slug': None})
@app.route('/post/<url_slug>/testedit', methods=['GET', 'POST'])
def testform(url_slug):
    if url_slug:
        for i in content.find({'url_slug': url_slug}):
            post = i
    else:
        post = None
    updates = {}
    request.get_data()
    form = request.form
#    title = request.form['title']
    print form
    for k in form:
        print k
        field_data = form[k]
        updates[str(k)] = field_data
    print updates
    return render_template("testform.html",
        post = post,
        page_types = page_types
        )

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, port=port, host='0.0.0.0')