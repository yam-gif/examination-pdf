import random, yaml
from jinja2 import Environment, FileSystemLoader

# --- 1) 問題データを読み込む
with open("problems.yaml", encoding="utf-8") as f:
    problems = yaml.safe_load(f)        # :contentReference[oaicite:2]{index=2}:contentReference[oaicite:3]{index=3}

# --- 2) ランダムに最大5問を選択
selected = random.sample(problems, k=min(5, len(problems)))  # :contentReference[oaicite:4]{index=4}:contentReference[oaicite:5]{index=5}

# --- 3) Jinja2 環境をセットアップ
env = Environment(loader=FileSystemLoader("."), autoescape=False)

# --- 4) LaTeX テンプレートを読み込む
tpl = env.get_template("template.tex.j2")   # 修正済みのテンプレファイル名

# --- 5) レンダリングしてソースを文字列化
latex_source = tpl.render(problems=selected)

# --- 6) そのまま TXT として書き出し
with open("mock_test.txt", "w", encoding="utf-8") as fw:
    fw.write(latex_source)

print("mock_test.txt を生成しました。")
