from flask import Flask, render_template, request, jsonify
import yaml
import random
import threading
from jinja2 import Environment, FileSystemLoader

YAML_PATH = 'problems.yaml'

app = Flask(__name__)
lock = threading.Lock()  # ファイル同時書き込み対策

# ----------------------------------------------------------------------
# データ読み込み & ヘルパ
# ----------------------------------------------------------------------

def load_problems():
    """YAML から全問題を読み込む。空の場合は空リストを返す。"""
    try:
        with open(YAML_PATH, encoding='utf-8') as fp:
            data = yaml.safe_load(fp) or []
    except FileNotFoundError:
        data = []
    return data


def write_problems(problems):
    """問題リストを YAML に保存する。"""
    with open(YAML_PATH, 'w', encoding='utf-8') as fp:
        yaml.safe_dump(problems, fp, allow_unicode=True, sort_keys=False)


def refresh_sets():
    """subjects / categories / difficulties を問題リストから生成。"""
    global ALL_SUBJECTS, ALL_CATEGORIES, ALL_DIFFICULTIES
    ALL_SUBJECTS     = sorted({p['subject']    for p in ALL_PROBLEMS})
    ALL_CATEGORIES   = sorted({p['category']   for p in ALL_PROBLEMS})
    ALL_DIFFICULTIES = sorted({p.get('difficulty') for p in ALL_PROBLEMS if p.get('difficulty')})


# 初期ロード
ALL_PROBLEMS = load_problems()
refresh_sets()

DEFAULT_NUM  = 5
CHOICES_NUM  = [1, 3, 5]

# ----------------------------------------------------------------------
# ルーティング
# ----------------------------------------------------------------------

@app.route('/', methods=['GET'])
def index():
    """トップページ (フォーム表示 & 直前の生成結果)"""
    return render_template(
        'index.html',
        subjects      = ALL_SUBJECTS,
        categories    = ALL_CATEGORIES,
        difficulties  = ALL_DIFFICULTIES,
        num_choices   = CHOICES_NUM,
        selected_num  = DEFAULT_NUM,
        latex         = None,
        answers_latex = None,
        selected_subjects     = [],
        selected_categories   = [],
        selected_difficulties = []
    )


@app.route('/generate', methods=['POST'])
def generate():
    """条件に合うランダムな問題を選び、LaTeX を生成して画面へ返す。"""
    sel_subjs  = request.values.getlist('subject')
    sel_cats   = request.values.getlist('category')
    sel_diffs  = request.values.getlist('difficulty')
    sel_num    = int(request.values.get('num_questions', DEFAULT_NUM))

    # ---- フィルタリング ----
    filtered = [
        p for p in ALL_PROBLEMS
        if (not sel_subjs  or p['subject']        in sel_subjs)
        and (not sel_cats  or p['category']       in sel_cats)
        and (not sel_diffs or p.get('difficulty') in sel_diffs)
    ]

    k = min(sel_num, len(filtered))
    selected = random.sample(filtered, k=k) if k else []

    # ---- LaTeX 生成 ----
    env = Environment(loader=FileSystemLoader('.'), autoescape=False)
    prob_tpl = env.get_template('template.tex.j2')
    ans_tpl  = env.get_template('answers.tex.j2')
    latex_src   = prob_tpl.render(problems=selected)
    answers_src = ans_tpl.render(problems=selected)

    return render_template(
        'index.html',
        subjects      = ALL_SUBJECTS,
        categories    = ALL_CATEGORIES,
        difficulties  = ALL_DIFFICULTIES,
        num_choices   = CHOICES_NUM,
        selected_num  = sel_num,
        latex         = latex_src,
        answers_latex = answers_src,
        selected_subjects     = sel_subjs,
        selected_categories   = sel_cats,
        selected_difficulties = sel_diffs
    )


@app.route('/add_problem', methods=['POST'])
def add_problem():
    """フォームから受け取った 1 問を YAML に追記し、メモリ上の一覧も更新。"""
    new = {
        'subject'   : request.form.get('subject', '').strip(),
        'category'  : request.form.get('category', '').strip(),
        'difficulty': request.form.get('difficulty', '').strip(),
        'body'      : request.form.get('body', '').strip(),
        'answer'    : request.form.get('answer', '').strip()
    }

    # ---- バリデーション ----
    if not all(new.values()):
        return jsonify(ok=False, msg='全フィールド必須です'), 400

    # ---- 追記 (排他制御) ----
    with lock:
        ALL_PROBLEMS.append(new)
        write_problems(ALL_PROBLEMS)
        refresh_sets()

    return jsonify(ok=True)

# ----------------------------------------------------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)