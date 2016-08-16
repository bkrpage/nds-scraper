from flask import Flask, render_template
import scraper

app = Flask(__name__)

@app.route("/")
def hello():
    return render_template('game_list_template.html', game_list = scraper.get_games())


if __name__ == "__main__":
    app.run()
