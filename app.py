from flask import Flask, request, jsonify

app = Flask(__name__)

HTML_PAGE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Eğitim Chatbot</title>

    <style>

        *{
            margin:0;
            padding:0;
            box-sizing:border-box;
            font-family:Arial;
        }

        body{
            background:#0f172a;
            color:white;
            height:100vh;
            display:flex;
            justify-content:center;
            align-items:center;
        }

        .container{
            width:90%;
            max-width:900px;
            height:90vh;
            background:#1e293b;
            border-radius:20px;
            display:flex;
            flex-direction:column;
            overflow:hidden;
            box-shadow:0 0 30px rgba(0,0,0,0.4);
        }

        .header{
            background:#38bdf8;
            padding:20px;
            font-size:28px;
            font-weight:bold;
            text-align:center;
        }

        .chat-box{
            flex:1;
            padding:20px;
            overflow-y:auto;
        }

        .message{
            margin-bottom:15px;
            padding:15px;
            border-radius:12px;
            max-width:80%;
        }

        .user{
            background:#2563eb;
            margin-left:auto;
        }

        .bot{
            background:#334155;
        }

        .input-area{
            display:flex;
            padding:20px;
            background:#111827;
        }

        input{
            flex:1;
            padding:15px;
            border:none;
            border-radius:10px;
            outline:none;
            font-size:16px;
        }

        button{
            margin-left:10px;
            padding:15px 25px;
            border:none;
            border-radius:10px;
            background:#38bdf8;
            color:white;
            font-size:16px;
            cursor:pointer;
        }

        button:hover{
            background:#0ea5e9;
        }

    </style>

</head>

<body>

<div class="container">

    <div class="header">
        🤖 AI Eğitim Chatbot
    </div>

    <div class="chat-box" id="chatBox">

        <div class="message bot">
            Merhaba 👋 Ben AI eğitim asistanıyım.
        </div>

    </div>

    <div class="input-area">

        <input type="text" id="userInput" placeholder="Mesaj yaz...">

        <button onclick="sendMessage()">
            Gönder
        </button>

    </div>

</div>

<script>

async function sendMessage(){

    let input = document.getElementById("userInput");
    let chatBox = document.getElementById("chatBox");

    let message = input.value;

    if(message.trim() === ""){
        return;
    }

    chatBox.innerHTML += `
        <div class="message user">
            ${message}
        </div>
    `;

    input.value = "";

    let response = await fetch("/chat",{
        method:"POST",
        headers:{
            "Content-Type":"application/json"
        },
        body:JSON.stringify({
            message:message
        })
    });

    let data = await response.json();

    chatBox.innerHTML += `
        <div class="message bot">
            ${data.reply}
        </div>
    `;

    chatBox.scrollTop = chatBox.scrollHeight;
}

</script>

</body>
</html>
"""

@app.route("/")
def home():
    return HTML_PAGE


@app.route("/chat", methods=["POST"])
def chat():

    user_message = request.json["message"].lower()

    if "python" in user_message:
        reply = "Python çok güçlü bir programlama dilidir 🐍"

    elif "merhaba" in user_message:
        reply = "Merhaba 👋 Sana nasıl yardımcı olabilirim?"

    elif "html" in user_message:
        reply = "HTML web sitelerinin iskeletidir 🌐"

    elif "css" in user_message:
        reply = "CSS web tasarımı için kullanılır 🎨"

    else:
        reply = "Mesajını aldım 🚀 AI sistemi geliştiriliyor."

    return jsonify({
        "reply": reply
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)