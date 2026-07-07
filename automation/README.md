# n8n による自動化

LLM（ネタ出し・台本）は **API を使わず、あなたが claude.ai にコピペ**します。
それ以外の機械的な工程を n8n が回します。人間の判断ポイントは
「台本の承認」と「完成動画の確認」の2箇所だけです。

```
 あなた                          n8n（自動）
─────────────────────────────────────────────────────────────
 claude.ai で台本生成
 script.yaml をレビュー
 ytf approve <slug>      ──→   15分ごとに .approved を検出
                                → ytf make（音声〜書き出し）
                                → Discord/Slackに完成通知
 動画をチェック
 ytf release <slug>      ──→   30分ごとに .release を検出
                                → YouTubeへ限定公開でアップロード
                                → .uploaded にマーク
 YouTube Studioで公開設定
```

状態は `ytf status` でいつでも一覧できます。マーカーはただのファイル
（`projects/<slug>/.approved` など）なので、n8n以外（cron、Keyboard Maestro等）
からも同じ仕組みが使えます。

## セットアップ

### 1. n8n を Mac でセルフホスト（無料）

```bash
# Node.js があれば
npx n8n
# → http://localhost:5678
```

セルフホスト版（Community Edition）は無料です。n8n Cloud（月額課金）は不要。
常駐させるなら `brew services` や Docker で。

### 2. 自動ビルドワークフロー

1. n8n の Workflows → Import from File → `automation/n8n/auto_build.json`
2. 「承認済みをビルド」ノードのコマンド内 2箇所を書き換え:
   - リポジトリの絶対パス
   - Discord/Slack の Webhook URL（通知不要なら export ごと削除）
3. Activate

※ n8n をDockerで動かす場合、コンテナ内から `ytf` やリポジトリが見える必要が
あるため、Macでは `npx n8n`（ホスト実行）が一番簡単です。

### 3. YouTube アップロードワークフロー

1. Import from File → `automation/n8n/upload_youtube.json`
2. リポジトリ絶対パス（2箇所）を書き換え
3. YouTube ノードに OAuth 認証を設定:
   - [Google Cloud Console](https://console.cloud.google.com/) でプロジェクト作成
   - 「YouTube Data API v3」を有効化
   - OAuth クライアントID（Webアプリ）を作成し、n8n が表示するリダイレクトURLを登録
   - n8n の Credentials で接続
4. Activate

アップロードは安全のため **private（非公開）** で行う設定にしてあります。
最終確認して YouTube Studio で公開してください（サムネイル設定もそのとき手動で。
自動化したくなったら `thumbnails.set` APIを叩くノードを足せます）。

## YouTube Data API の費用について

- **金銭的コストはゼロ**（無料。従量課金は存在しない）
- 代わりに「クォータ」制: 既定で 10,000 ユニット/日、動画アップロードは
  1回 1,600 ユニット → **1日6本まで無料枠内**。increase申請も無料
- 注意点が1つ: 新しいAPIプロジェクトは Google の審査（無料）を通すまで、
  APIでアップロードした動画が **非公開ロック** になる場合があります。
  どうせ最終確認して手動公開する運用なので実害はほぼありませんが、
  完全自動公開をやりたくなったら審査フォームを出してください
- 面倒なら、アップロードだけ YouTube Studio に手動ドラッグ（1本2分）でもOK。
  `out/metadata.txt` をコピペするだけの状態にはなっています
