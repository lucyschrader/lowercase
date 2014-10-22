from flask import Flask, render_template, request, flash, redirect, url_for, jsonify, Markup
import os, pymongo, re
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

@app.route('/')
def home():
    posts = content.find()
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
        if post['page_type'] == 'blog':
            return render_template('blogpost.html', post = post)
        elif post['page_type'] == 'making':
            return render_template('makingpost.html', post = post)

@app.route('/cms')
def cms():
    pages = content.find()
    return render_template('cms.html',
        pages = pages
        )

@app.route('/newpost', methods=['GET', 'POST'], defaults={'url_slug': None})
@app.route('/post/<url_slug>/edit', methods=['GET', 'POST'])
def new(url_slug):
    form = newPost()
    if url_slug:
        for i in content.find({'url_slug': url_slug}):
            post = i
    else:
        post = None
    if form.validate_on_submit():
        updates = {}
        for k in form.data:
            field_name = k
            field_data = form.data[k]
            updates[str(field_name)] = field_data
        url_slug = slugify(form.title.data)
        updates['url_slug'] = url_slug
        content.insert(updates)
        return redirect(url_for('cms'))
    return render_template("newpost.html",
        form = form,
        post = post
        )

def slugify(text, delim=u'-'):
    """Generates an ASCII-only slug. Thanks Armin Ronacher!"""
    result = []
    for word in _punct_re.split(text.lower()):
        result.extend(unidecode(word).split())
    return unicode(delim.join(result))

# Got to figure out how to add stuff like this
def rel_links(rel_link):
    link_dict = {}
    rel_link.rstrip().split('\n')
    for link in rel_link:
        link.split(',')
        print link
#        url = link[0]
#        title = link[1]
#        link_dict[url] = link
    return link_dict

@app.route('/testform', methods=['GET', 'POST'])
def testform():
    form = newPost()
    updates = {}
    if form.validate_on_submit():
        for k in form.data:
            field_name = k
            field_data = form.data[k]
            updates[str(field_name)] = field_data
        url_slug = slugify(form.title.data)
        updates['url_slug'] = url_slug
    content.insert(updates)
    return render_template("newpost.html",
        form = form
        )

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, port=port, host='0.0.0.0')