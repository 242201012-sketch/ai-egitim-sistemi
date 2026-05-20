from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return """
    <h1>AI Eğitim Sistemi Çalışıyor 🚀</h1>
    <p>Render deploy başarılı.</p>
    """

if __name__ == "__main__":
    app.run(debug=True)