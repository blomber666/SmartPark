from flask import Flask, render_template, request

app = Flask(__name__, template_folder='templates', static_folder='static')

@app.route("/login")
def home():
    return render_template('login.html')


@app.get("/home")
def login():
    usr=request.args.get('email')
    pwd=request.args.get('pswd')
    print(usr,pwd, end="\n\n")
    if usr == "luca@fontana.it" and pwd == "123":
        return render_template('home.html'), 200
    else:
        return render_template('home.html'), 401

@app.route("/signed")
def signed_up():
    return render_template('signed-up.html'), 200


if __name__ == "__main__":
    app.run(debug=True)

#GET /?email=lcua%40kdnvkna.it&pswd=fsjdbnvin HTTP/1.1" 200 -