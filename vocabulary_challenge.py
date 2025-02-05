from flask import Flask, request, render_template, redirect, url_for, session
import time
import csv
import os
import random
import json
import uuid
from datetime import datetime
import pytz

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "default_secret_key")

# 单词库（保持不变）
word_database = [
    {"english": "traveller", "chinese": "旅行者"},
    {"english": "come true", "chinese": "实现"},
    {"english": "pianist", "chinese": "钢琴家"},
    {"english": "football player", "chinese": "足球运动员"},
    {"english": "World Cup", "chinese": "世界杯"},
    {"english": "go into", "chinese": "进入"},
    {"english": "get out", "chinese": "出去"},
    {"english": "lover", "chinese": "爱人"},
    {"english": "zebra crossing", "chinese": "斑马线"},
    {"english": "cheer", "chinese": "欢呼"},
    {"english": "sleepy", "chinese": "困倦的"},
    {"english": "a little", "chinese": "一点点"},
    {"english": "safety", "chinese": "安全"},
    {"english": "koala", "chinese": "考拉"},
    {"english": "care about", "chinese": "关心"},
    {"english": "Disneyland", "chinese": "迪士尼乐园"},
    {"english": "Taipei", "chinese": "台北"},
    {"english": "Oxford", "chinese": "牛津"},
    {"english": "at a time", "chinese": "一次"},
    {"english": "Children's Day", "chinese": "儿童节"},
    {"english": "look out for", "chinese": "留意"},
    {"english": "go back to", "chinese": "回去"},
    {"english": "last night", "chinese": "昨晚"},
    {"english": "pour into", "chinese": "倒入"},
    {"english": "summer holiday", "chinese": "暑假"},
    {"english": "how long", "chinese": "多久"},
    {"english": "put in order", "chinese": "整理"},
    {"english": "just then", "chinese": "就在那时"},
    {"english": "Moon", "chinese": "月亮"},
    {"english": "London Eye", "chinese": "伦敦眼"},
    {"english": "Ocean Park", "chinese": "海洋公园"},
    {"english": "some day", "chinese": "某一天"},
    {"english": "the next day", "chinese": "第二天"},
    {"english": "walk by", "chinese": "走过"},
    {"english": "wake...up", "chinese": "唤醒"},
    {"english": "too much", "chinese": "太多"},
    {"english": "next week", "chinese": "下周"},
    {"english": "like", "chinese": "喜欢"},
    {"english": "London", "chinese": "伦敦"},
    {"english": "about", "chinese": "关于"},
    {"english": "from then on", "chinese": "从那时起"},
    {"english": "Sydney", "chinese": "悉尼"},
    {"english": "Big Ben", "chinese": "大本钟"},
    {"english": "a few", "chinese": "几个"},
    {"english": "Tower Bridge", "chinese": "塔桥"},
    {"english": "future", "chinese": "未来"},
    {"english": "dream", "chinese": "梦想"},
    {"english": "reach", "chinese": "到达"},
    {"english": "net", "chinese": "网"},
    {"english": "magazine", "chinese": "杂志"},
    {"english": "exciting", "chinese": "令人兴奋的"},
    {"english": "diet", "chinese": "饮食"},
    {"english": "appear", "chinese": "出现"},
    {"english": "bite", "chinese": "咬"},
    {"english": "spaceship", "chinese": "飞船"},
    {"english": "pavement", "chinese": "人行道"},
    {"english": "clown", "chinese": "小丑"},
    {"english": "artist", "chinese": "艺术家"},
    {"english": "rule", "chinese": "规则"},
    {"english": "cross", "chinese": "穿过"},
    {"english": "sharp", "chinese": "锋利的"},
    {"english": "astronaut", "chinese": "宇航员"},
    {"english": "tidy", "chinese": "整洁的"},
    {"english": "ground", "chinese": "地面"},
    {"english": "light", "chinese": "光"},
    {"english": "paint", "chinese": "画"},
    {"english": "healthy", "chinese": "健康的"},
    {"english": "safe", "chinese": "安全"},
    {"english": "finish", "chinese": "完成"},
    {"english": "travel", "chinese": "旅行"},
    {"english": "welcome", "chinese": "欢迎"},
    {"english": "weak", "chinese": "虚弱的"},
    {"english": "mouse", "chinese": "鼠标"},
    {"english": "need", "chinese": "需要"},
    {"english": "never", "chinese": "从未"},
    {"english": "strong", "chinese": "强壮的"},
    {"english": "stay", "chinese": "停留"},
    {"english": "late", "chinese": "迟到"},
    {"english": "follow", "chinese": "跟随"},
    {"english": "deep", "chinese": "深的"},
    {"english": "begin", "chinese": "开始"},
    {"english": "scientist", "chinese": "科学家"},
    {"english": "country", "chinese": "国家"},
    {"english": "will", "chinese": "将"},
    {"english": "put on", "chinese": "穿上"},
    {"english": "hit", "chinese": "击打"},
    {"english": "fast", "chinese": "快速的"},
    {"english": "find out", "chinese": "发现"},
    {"english": "large", "chinese": "大的"},
    {"english": "sound", "chinese": "声音"},
    {"english": "learn", "chinese": "学习"},
    {"english": "habit", "chinese": "习惯"},
    {"english": "balloon", "chinese": "气球"},
    {"english": "kangaroo", "chinese": "袋鼠"},
    {"english": "soon", "chinese": "很快"},
    {"english": "child", "chinese": "孩子"},
    {"english": "bad", "chinese": "坏的"},
    {"english": "visitor", "chinese": "访客"},
    {"english": "ask", "chinese": "询问"},
    {"english": "road", "chinese": "道路"},
    {"english": "must", "chinese": "必须"},
    {"english": "cola", "chinese": "可乐"},
    {"english": "dancer", "chinese": "舞者"},
    {"english": "happily", "chinese": "愉快地"},
    {"english": "loudly", "chinese": "大声地"},
    {"english": "quietly", "chinese": "安静地"},
    {"english": "safely", "chinese": "安全地"},
    {"english": "take care of", "chinese": "照顾"}
]

LEADERBOARD_FILE = "leaderboard.csv"

@app.route("/")
def index():
    # 每次加载页面时生成新的 token 防重提交
    token = uuid.uuid4().hex
    session['token'] = token
    # 使用 templates/index.html 渲染首页
    return render_template('index.html', word_db=json.dumps(word_database), token=token)

@app.route("/save_score", methods=["POST"])
def save_score_route():
    token = request.form.get("token")
    if not token or 'token' not in session or token != session['token']:
        return redirect(url_for("leaderboard"))
    session.pop('token', None)
    
    action = request.form.get("action")
    score = request.form.get("score")
    if action == "save":
        name = request.form.get("name")
        school = request.form.get("school")
        class_info = request.form.get("class_info")
        if all([score, name, school, class_info]):
            tz = pytz.timezone('Asia/Shanghai')
            current_time = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

            record = [score, name, school, class_info, current_time]
            records = []
            if os.path.exists(LEADERBOARD_FILE):
                with open(LEADERBOARD_FILE, "r", newline='', encoding="utf-8") as csvfile:
                    reader = csv.reader(csvfile)
                    for row in reader:
                        if row:
                            records.append(row)
            records.append(record)
            records.sort(key=lambda x: int(x[0]), reverse=True)
            records = records[:50]
            with open(LEADERBOARD_FILE, "w", newline='', encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(records)
    return redirect(url_for("leaderboard"))

@app.route("/leaderboard")
def leaderboard():
    records = []
    if os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, "r", newline='', encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if row:
                    records.append(row)
    # 使用 templates/leaderboard.html 渲染排行榜页面
    return render_template('leaderboard.html', records=records)

if __name__ == "__main__":
    app.run(debug=True)
