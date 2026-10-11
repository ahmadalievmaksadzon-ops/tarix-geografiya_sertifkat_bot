import os
import random
import string
from flask import Flask, render_template_string, request, jsonify
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

BOT_TOKEN = os.getenv("BOT_TOKEN", "SIZNING_BOT_TOKENINGIZ")
WEB_URL = os.getenv("WEB_URL", "https://sizning-sayt.onrender.com")

app = Flask(__name__)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

tests_db = {}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Milliy Sertifikat Test Tizimi</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f4f7f6; margin: 0; padding: 15px; }
        .card { background: white; border-radius: 12px; padding: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }
        h3 { color: #2c3e50; text-align: center; }
        .welcome { background: #e8f4f8; padding: 15px; border-radius: 8px; font-weight: bold; color: #1a5276; text-align: center; }
        .btn { display: block; width: 100%; padding: 12px; margin: 10px 0; border: none; background: #27ae60; color: white; border-radius: 6px; font-size: 16px; cursor: pointer; }
        .btn-secondary { background: #2980b9; }
        .option-btn { padding: 8px 12px; border: 1px solid #ccc; background: white; border-radius: 4px; cursor: pointer; margin: 2px; }
        .option-btn.selected { background: #3498db; color: white; border-color: #2980b9; }
        .hidden { display: none; }
        .certificate { border: 10px double #c5a059; padding: 20px; background: #fffdf9; text-align: center; font-family: Georgia, serif; margin-top: 20px; }
    </style>
</head>
<body>
<div class="card">
    <div class="welcome">
        {{ user_name }}, tarix fanidan milliy sertifikat testlarini yechish uchun xush kelibsiz!
    </div>
    <div style="margin-top: 20px;">
        <button class="btn" onclick="showSection('createSection')">📝 Test Tuzish</button>
        <button class="btn btn-secondary" onclick="showSection('solveSection')">✏️ Test Ishlash</button>
    </div>
</div>

<div id="createSection" class="card hidden">
    <h3>Yangi Test Tuzish</h3>
    <label>Fanni tanlang:</label>
    <select id="subjectSelect" style="width:100%; padding: 10px; margin-bottom: 15px;">
        <option value="Tarix">Tarix</option>
        <option value="Geografiya">Geografiya</option>
    </select>
    <div id="createQuestionsContainer"></div>
    <button class="btn" onclick="submitCreatedTest()">Tasdiqlash va Kod Olish</button>
</div>

<div id="solveSection" class="card hidden">
    <h3>Testni Ishlash</h3>
    <input type="text" id="testCodeInput" placeholder="6 xonali kodni kiriting" style="width: 90%; padding: 10px; margin-bottom: 10px;">
    <button class="btn btn-secondary" onclick="loadTest()">Testni Boshlash</button>
    <div id="solveQuestionsContainer" class="hidden">
        <div id="questionsList"></div>
        <button class="btn" onclick="submitAnswers()">Testni Yakunlash</button>
    </div>
</div>

<div id="certResult" class="hidden"></div>

<script>
let createdAnswers = {};
let solveAnswers = {};
const userName = "{{ user_name }}";

function showSection(id) {
    document.getElementById('createSection').classList.add('hidden');
    document.getElementById('solveSection').classList.add('hidden');
    document.getElementById(id).classList.remove('hidden');
    if(id === 'createSection') renderCreateQuestions();
}

function renderCreateQuestions() {
    let container = document.getElementById('createQuestionsContainer');
    container.innerHTML = '';
    for(let i = 1; i <= 35; i++) {
        let opts = (i <= 32 ? ['A','B','C','D'] : ['A','B','C','D','E','F']).map(o => `<button class="option-btn" onclick="selectOpt(this, '${i}', '${o}')">${o}</button>`).join(' ');
        container.innerHTML += `<div style="margin: 8px 0;"><b>${i}.</b> ${opts}</div>`;
    }
    for(let i = 36; i <= 45; i++) {
        container.innerHTML += `<div style="margin: 10px 0;"><b>${i}-savol (Yopiq):</b><br><input type="text" onchange="createdAnswers['${i}'] = this.value" style="width:90%; padding:5px;"></div>`;
    }
}

function selectOpt(btn, qNum, val) {
    btn.parentElement.querySelectorAll('.option-btn').forEach(b => b.classList.remove('selected'));
    btn.classList.add('selected');
    createdAnswers[qNum] = val;
}

function submitCreatedTest() {
    let subject = document.getElementById('subjectSelect').value;
    fetch('/create_test', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ subject: subject, answers: createdAnswers })
    }).then(res => res.json()).then(data => {
        alert("Test tuzildi! Maxfiy kod: " + data.code);
        location.reload();
    });
}

function loadTest() {
    let code = document.getElementById('testCodeInput').value;
    fetch('/get_test?code=' + code).then(res => res.json()).then(data => {
        if(data.status === 'ok') {
            document.getElementById('solveQuestionsContainer').classList.remove('hidden');
            let container = document.getElementById('questionsList');
            container.innerHTML = '';
            for(let i = 1; i <= 35; i++) {
                let opts = (i <= 32 ? ['A','B','C','D'] : ['A','B','C','D','E','F']).map(o => `<button class="option-btn" onclick="selectSolveOpt(this, '${i}', '${o}')">${o}</button>`).join(' ');
                container.innerHTML += `<div style="margin: 8px 0;"><b>${i}.</b> ${opts}</div>`;
            }
            for(let i = 36; i <= 45; i++) {
                container.innerHTML += `<div style="margin: 10px 0;"><b>${i}-savol javobi:</b><br><input type="text" onchange="solveAnswers['${i}'] = this.value" style="width:90%; padding:5px;"></div>`;
            }
        } else { alert(data.message); }
    });
}

function selectSolveOpt(btn, qNum, val) {
    btn.parentElement.querySelectorAll('.option-btn').forEach(b => b.classList.remove('selected'));
    btn.classList.add('selected');
    solveAnswers[qNum] = val;
}

function submitAnswers() {
    let code = document.getElementById('testCodeInput').value;
    fetch('/submit_test', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ code: code, answers: solveAnswers, user_name: userName })
    }).then(res => res.json()).then(data => {
        if(data.status === 'ok') {
            let c = data.result;
            document.getElementById('certResult').innerHTML = `
                <div class="certificate">
                    <h4>AHMADALIYEV MAQSADJONNING ONLINE KURSLARI</h4>
                    <h3>UMUMTA'LIM FANINI BILISH DARAJASI TO'G'RISIDA SERTIFIKAT</h3>
                    <p><b>Ism:</b> ${c.user_name}</p>
                    <p><b>Fan:</b> ${c.subject}</p>
                    <p><b>To'plagan ball:</b> ${c.score} (${c.percentage})</p>
                    <p><b>Daraja:</b> ${c.grade}</p>
                    <p><b>Berilgan sana:</b> ${c.date} | <b>Amal qilish muddati:</b> ${c.expire_date}</p>
                    <p><b>O'qituvchi:</b> ${c.teacher}</p>
                </div>`;
            document.getElementById('certResult').classList.remove('hidden');
        } else { alert(data.message); }
    });
}
</script>
</body>
</html>
"""

class Registration(StatesGroup):
    waiting_for_fullname = State()

@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer("Assalomu alaykum! Ism va Familiyangizni kiriting (Masalan: Ndirbek Xolboyev):")
    await state.set_state(Registration.waiting_for_fullname)

@dp.message(Registration.waiting_for_fullname)
async def process_name(message: types.Message, state: FSMContext):
    fullname = message.text.strip()
    await state.clear()
    web_app_url = f"{WEB_URL}/?name={fullname}"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎓 Test Tizimiga Kirish", web_app=WebAppInfo(url=web_app_url))]
    ])
    await message.answer(f"Rahmat, **{fullname}**! Quyidagi tugmani bosing:", reply_markup=kb, parse_mode="Markdown")

@app.route('/')
def index():
    user_name = request.args.get('name', 'Talabgor')
    return render_template_string(HTML_TEMPLATE, user_name=user_name)

@app.route('/create_test', methods=['POST'])
def create_test():
    data = request.json
    code = ''.join(random.choices(string.digits, k=6))
    tests_db[code] = {"subject": data.get("subject"), "answers": data.get("answers")}
    return jsonify({"status": "ok", "code": code})

@app.route('/get_test', methods=['GET'])
def get_test():
    code = request.args.get('code')
    if code in tests_db:
        return jsonify({"status": "ok"})
    return jsonify({"status": "error", "message": "Kod topilmadi!"})

@app.route('/submit_test', methods=['POST'])
def submit_test():
    data = request.json
    code = data.get("code")
    user_answers = data.get("answers")
    user_name = data.get("user_name", "Noma'lum")
    
    if code not in tests_db:
        return jsonify({"status": "error", "message": "Xato kod!"})
    
    correct_answers = tests_db[code]["answers"]
    score = sum(1.5 for k, v in user_answers.items() if correct_answers.get(str(k)) == v)
    
    grade = "C" if score >= 46 else None
    if score >= 70: grade = "A+"
    elif score >= 65: grade = "A"
    elif score >= 60: grade = "B+"
    elif score >= 55: grade = "B"
    elif score >= 50: grade = "C+"

    if not grade:
        return jsonify({"status": "error", "message": f"Siz {score} ball oldingiz. Sertifikat uchun minimal 46 ball kerak!"})

    return jsonify({
        "status": "ok",
        "result": {
            "user_name": user_name, "subject": tests_db[code]["subject"],
            "score": score, "percentage": f"{round((score/90)*100, 1)}%", "grade": grade,
            "date": "11.10.2026", "expire_date": "11.10.2029", "teacher": "AHMADALIYEV M."
        }
    })

if __name__ == '__main__':
    import threading
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000)).start()
    import asyncio
    asyncio.run(dp.start_polling(bot))
