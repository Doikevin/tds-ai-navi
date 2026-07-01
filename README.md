# TDS AI ナビ

東京ディズニーシーのアトラクション待ち時間を記録・予測し、最適な巡回ルートを提案する
アプリの開発プロジェクトです。

> データ提供: **Powered by [Queue-Times.com](https://queue-times.com/)**
> （このプロジェクトは Disney / オリエンタルランドの公式サービスではありません）

---

## いま何ができるか（Phase 0：データ収集）

- `logger.py` … 待ち時間（Queue-Times）と天気（Open-Meteo）を取得し `data/` に CSV で追記
- `.github/workflows/logger.yml` … GitHub のクラウドで **15分ごとに自動実行**する設定

自分のPCは電源オフでOK。GitHub がクラウドで勝手にデータを貯めてくれます。

---

## セットアップ手順（初心者向け・GitHub Actions）

### 1. GitHub アカウントを作る（無料）
https://github.com/ で Sign up。すでに持っていればスキップ。

### 2. GitHub Desktop を入れる（GUIで簡単）
https://desktop.github.com/ からインストールし、作ったアカウントでサインイン。

### 3. このフォルダをリポジトリにして公開する
1. GitHub Desktop で **File → Add local repository** → このフォルダ（`tds-ai-navi`）を選ぶ
   - 「これはgitリポジトリではない」と出たら **create a repository** を押す
2. 左下で最初のコミット（Summaryに `first commit` などと入れて **Commit**）
3. 右上の **Publish repository** を押す
   - **Keep this code private のチェックを外す（＝公開リポジトリ）を推奨**
     → 公開リポジトリなら GitHub Actions が **無料で無制限**に使えます。
     待ち時間データは公開情報なので公開で問題ありません。
   - 非公開にしたい場合は月2000分の無料枠内（この設定なら収まります）

### 4. Actions に書き込み権限を与える（重要）
ブラウザで自分のリポジトリを開き、
**Settings → Actions → General → Workflow permissions** で
**「Read and write permissions」を選んで Save**。
（これをしないと、集めたデータを保存できません）

### 5. 動作テスト
リポジトリの **Actions** タブ → 左の **Wait Time Logger** → 右の **Run workflow** を押す。
1〜2分で緑のチェックが付き、`data/` フォルダに CSV が追加されればOK。

以降は **15分ごと（日本時間9:00〜23:00）に自動実行**され、データが貯まり続けます。

---

## うまくいかないときの確認
- Actions が赤（失敗）→ 手順4の書き込み権限を確認
- スケジュールが動かない → 初回は少し遅れることがある。手順5の手動実行で確認
- 長期間コミットが無いと GitHub がスケジュールを止めることがあるが、
  このロガーは毎回コミットするので基本的に止まりません

---

## ローカルでの手動テスト（任意）
```powershell
pip install -r requirements.txt
python logger.py
```
`data/` に CSV が作られます。

---

## 今後の予定
- Phase 1: ルート最適化エンジン（アトラクションはUUIDで管理）
- Phase 2: Web画面（行きたい施設を選ぶ→ルート提案）
- Phase 3: 貯めたデータで待ち時間予測（LightGBM）
