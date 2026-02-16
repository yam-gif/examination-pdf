import random, yaml, os
from jinja2 import Environment, FileSystemLoader

# --- [追加] !include を処理するためのクラス ---
class YamlIncludeLoader(yaml.SafeLoader):
    def __init__(self, stream):
        self._root = os.path.split(stream.name)[0]
        super(YamlIncludeLoader, self).__init__(stream)

    def include(self, node):
        filename = os.path.join(self._root, self.construct_scalar(node))
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()

# !include タグを登録
YamlIncludeLoader.add_constructor('!include', YamlIncludeLoader.include)

# --- 1) 問題データを読み込む (ここを修正) ---
with open("problems.yaml", encoding="utf-8") as f:
    # safe_load の代わりに、作成した Loader を指定する
    problems = yaml.load(f, Loader=YamlIncludeLoader)

# --- あとは全く同じ ---
selected = random.sample(problems, k=min(5, len(problems)))
env = Environment(loader=FileSystemLoader("."), autoescape=False)
tpl = env.get_template("template.tex.j2")
latex_source = tpl.render(problems=selected)

with open("mock_test.txt", "w", encoding="utf-8") as fw:
    fw.write(latex_source)

print("mock_test.txt を生成しました。")
