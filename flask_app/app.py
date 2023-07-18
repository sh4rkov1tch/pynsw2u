from flask import Flask, render_template, request
import scraped_data
app = Flask(__name__)

@app.route("/search", methods=['GET'])
def search():
    data = scraped_data.load(request.args.get('search'))
    return render_template('results.html', data=data)

@app.route("/", methods=['GET'])
def home_page():
    return(render_template('index.html'))

