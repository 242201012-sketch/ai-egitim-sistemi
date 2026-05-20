from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return """
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Eğitim Sistemi</title>

        <style>
            *{
                margin:0;
                padding:0;
                box-sizing:border-box;
                font-family:Arial, sans-serif;
            }

            body{
                background: linear-gradient(135deg,#0f172a,#1e293b);
                color:white;
                min-height:100vh;
            }

            nav{
                display:flex;
                justify-content:space-between;
                align-items:center;
                padding:20px 60px;
                background:rgba(255,255,255,0.05);
                backdrop-filter:blur(10px);
            }

            .logo{
                font-size:28px;
                font-weight:bold;
                color:#38bdf8;
            }

            .menu a{
                color:white;
                text-decoration:none;
                margin-left:25px;
                transition:0.3s;
            }

            .menu a:hover{
                color:#38bdf8;
            }

            .hero{
                display:flex;
                flex-direction:column;
                justify-content:center;
                align-items:center;
                text-align:center;
                height:85vh;
                padding:20px;
            }

            .hero h1{
                font-size:64px;
                margin-bottom:20px;
            }

            .hero p{
                font-size:22px;
                max-width:700px;
                color:#cbd5e1;
                margin-bottom:35px;
            }

            .btn{
                padding:15px 35px;
                background:#38bdf8;
                color:white;
                border:none;
                border-radius:12px;
                font-size:18px;
                cursor:pointer;
                transition:0.3s;
                text-decoration:none;
            }

            .btn:hover{
                background:#0ea5e9;
                transform:scale(1.05);
            }

            .cards{
                display:flex;
                justify-content:center;
                gap:25px;
                padding:50px;
                flex-wrap:wrap;
            }

            .card{
                width:300px;
                background:rgba(255,255,255,0.05);
                padding:30px;
                border-radius:20px;
                backdrop-filter:blur(10px);
                transition:0.3s;
            }

            .card:hover{
                transform:translateY(-10px);
            }

            .card h2{
                margin-bottom:15px;
                color:#38bdf8;
            }

            footer{
                text-align:center;
                padding:25px;
                color:#94a3b8;
            }
        </style>
    </head>

    <body>

        <nav>
            <div class="logo">AI Eğitim</div>

            <div class="menu">
                <a href="#">Ana Sayfa</a>
                <a href="#">Dersler</a>
                <a href="#">Quiz</a>
                <a href="#">İletişim</a>
            </div>
        </nav>

        <section class="hero">
            <h1>Geleceğin AI Eğitim Platformu 🚀</h1>

            <p>
                Yapay zeka destekli modern eğitim sistemi ile
                ders çalış, quiz çöz ve kendini geliştir.
            </p>

            <a href="#" class="btn">Hemen Başla</a>
        </section>

        <section class="cards">

            <div class="card">
                <h2>🤖 AI Destekli</h2>
                <p>
                    Yapay zeka ile kişiselleştirilmiş öğrenme deneyimi.
                </p>
            </div>

            <div class="card">
                <h2>📚 Modern Dersler</h2>
                <p>
                    Güncel teknoloji ve yazılım eğitimleri.
                </p>
            </div>

            <div class="card">
                <h2>📝 Quiz Sistemi</h2>
                <p>
                    İnteraktif testler ve gelişim analizi.
                </p>
            </div>

        </section>

        <footer>
            © 2026 AI Eğitim Sistemi | Tüm Hakları Saklıdır
        </footer>

    </body>
    </html>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)