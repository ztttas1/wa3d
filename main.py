# by ztttas1
from flask import Flask, request, render_template_string, Response
import requests
import base64
import os
app = Flask(__name__)
ver = "1.0"
# Invidious APIのベースURL（公開インスタンスを使用）
INVIDIOUS_API_URL = "https://" + os.environ.get('INVIDIOUS',) + "/api/v1"
SERVER_LIST = ['https://natural-voltaic-titanium.glitch.me','https://wtserver3.glitch.me','https://wtserver1.glitch.me','https://wtserver2.glitch.me','https://watawata8.glitch.me','https://watawata7.glitch.me','https://watawata37.glitch.me','https://wataamee.glitch.me','https://watawatawata.glitch.me','https://amenable-charm-lute.glitch.me','https://battle-deciduous-bear.glitch.me','https://productive-noon-van.glitch.me','https://balsam-secret-fine.glitch.me']
# BASIC認証のユーザー名とパスワード
USERNAME = os.environ.get('USERNAME', 'ztttas1')
PASSWORD = os.environ.get('PASSWORD', 'pas')
def check_auth(username, password):
    """認証情報を確認する関数"""
    return username == USERNAME and password == PASSWORD

def authenticate():
    """認証失敗時に401レスポンスを返す関数"""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )

@app.before_request
def require_auth():
    """すべてのリクエストに対して認証を要求"""
    auth = request.authorization
    if not auth or not check_auth(auth.username, auth.password):
        return authenticate()

@app.route('/', methods=['GET', 'POST'])
def search_videos():
    if request.method == 'POST':
        query = request.form.get('query')
        page = request.form.get('page', '1')  # Default to page 1
        if not query:
            return "検索キーワードを入力してください", 400

        try:
            page = int(page)
            if page < 1:
                page = 1
        except ValueError:
            page = 1

        # Invidious APIで動画とチャンネルを検索（type=allで両方を含む）
        search_url = f"{INVIDIOUS_API_URL}/search?q={query}&type=all&page={page}"
        try:
            response = requests.get(search_url)
            response.raise_for_status()
            results = response.json()

            # 検索結果をHTMLで表示
            html_content = """
            <!DOCTYPE html>
            <html lang="ja">
            <head>
                <meta charset="UTF-8">
                <title>Search</title>
                <style>
                    body { font-family: sans-serif; text-align: center; margin: 10px; }
                    .result { margin: 10px; text-align: left; }
                    img { width: 80px; height: auto; float: left; margin-right: 5px; }
                    p { font-size: 12px; margin: 5px 0; }
                    input, button { font-size: 12px; padding: 5px; }
                    form { margin: 10px 0; }
                </style>
            </head>
            <body>
                <h1>Search</h1>
                <form method="post">
                    <input type="text" name="query" value="{{query}}">
                    <input type="submit" value="検索">
                </form>
                <h2>検索結果</h2>
            """.replace("{{query}}", query)

            for item in results[:40]:  # 最大40件表示
                item_type = item.get('type')
                
                if item_type == 'video':
                    # 動画の場合
                    video_id = item.get('videoId')
                    title = item.get('title')
                    thumbnails = item.get('videoThumbnails')
                    if thumbnails and len(thumbnails) > 0:
                        thumbnail_url = f"https://img.youtube.com/vi/{video_id}/0.jpg"
                    else:
                        thumbnail_url = "https://via.placeholder.com/80"  # デフォルト画像
                    html_content += f"""
                    <div class="result">
                        <a href="/w?id={video_id}">
                            <img src="{thumbnail_url}" alt="thumbnail">
                            <p>{title}</p>
                        </a>
                    </div>
                    """
                elif item_type == 'channel':
                    # チャンネルの場合
                    channel_id = item.get('authorId')
                    channel_name = item.get('author')
                    thumbnails = item.get('authorThumbnails')
                    if thumbnails and len(thumbnails) > 0:
                        thumbnail_url = thumbnails[-1].get('url', 'https://via.placeholder.com/80')
                    else:
                        thumbnail_url = "https://via.placeholder.com/80"  # デフォルト画像
                    html_content += f"""
                    <div class="result">
                        <a href="/c?id={channel_id}">
                            <img src="{thumbnail_url}" alt="channel thumbnail">
                            <p>{channel_name}</p>
                        </a>
                    </div>
                    """

            # ページネーション用のボタンを追加
            html_content += """
            <div>
                <form method="post" style="display:inline;">
                    <input type="hidden" name="query" value="{{query}}">
                    <input type="hidden" name="page" value="{{prev_page}}">
                    <input type="submit" value="前のページ" {{prev_disabled}}>
                </form>
                <span>ページ {{current_page}}</span>
                <form method="post" style="display:inline;">
                    <input type="hidden" name="query" value="{{query}}">
                    <input type="hidden" name="page" value="{{next_page}}">
                    <input type="submit" value="次のページ">
                </form>
            </div>
            </body>
            </html>
            """.replace("{{query}}", query)\
               .replace("{{prev_page}}", str(page - 1))\
               .replace("{{next_page}}", str(page + 1))\
               .replace("{{current_page}}", str(page))\
               .replace("{{prev_disabled}}", 'disabled' if page == 1 else '')

            return render_template_string(html_content)

        except requests.exceptions.RequestException as e:
            return f"検索エラー: {str(e)}", 500

    # GETリクエストの場合は検索フォームのみ表示
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <title>Home</title>
        <style>
            body { font-family: sans-serif; text-align: center; margin: 10px; }
            h1 { font-size: 16px; }
            input { font-size: 12px; padding: 5px; }
            p { font-size: 12px; }
        </style>
    </head>
    <body>
        <h1>YouTubeViewer Search</h1>
        <form method="post">
            <input type="text" name="query" placeholder="Search word">
            <input type="submit" value="検索">
        </form>
        <p>製作:ztttas1<br>動画:わかめtube<br>検索:Invidious<br>Version:{ver}</p>
    </body>
    </html>
    """
    return render_template_string(html_content)

@app.route('/w', methods=['GET', 'POST'])
def get_stream_url():
    param_id = request.args.get('id')

    if not param_id:
        return "id parameter is required", 400

    if request.method == 'POST':
        server_index = request.form.get('server_index')
        try:
            server_index = int(server_index)
            if 0 <= server_index < len(SERVER_LIST):
                selected_server = SERVER_LIST[server_index]
            else:
                return "Invalid server index", 400
        except (ValueError, TypeError):
            return "Server index must be a number", 400

        api_url = f"{selected_server}/api/{param_id}"

        try:
            response = requests.get(api_url)
            response.raise_for_status()

            data = response.json()

            stream_url = data.get('stream_url')
            channel_image = data.get('channelImage')
            channel_name = data.get('channelName')
            video_des = data.get('videoDes')
            video_title = data.get('videoTitle')

            html_content = f"""
            <!DOCTYPE html>
            <html lang="ja">
            <head>
                <meta charset="UTF-8">
                <title>Video</title>
                <style>
                    body {{ font-family: sans-serif; text-align: center; margin: 10px; }}
                    img {{ width: 80px; height: auto; float: left; margin-right: 5px; }}
                    p {{ font-size: 12px; margin: 5px 0; }}
                    select, input {{ font-size: 12px; padding: 5px; }}
                    h3 {{ font-size: 14px; }}
                </style>
            </head>
            <body>
                <h1>{video_title}</h1>
                <p><a href="{stream_url}"><img src="https://img.youtube.com/vi/{param_id}/0.jpg" alt="Video Thumbnail"></a></p>
                <p>{channel_name}</p>
                <p>{video_des}</p>
                <h3>サーバー選択</h3>
                <form method="post">
                    <select name="server_index">
                        {''.join(f'<option value="{i}">{i}: {server}</option>' for i, server in enumerate(SERVER_LIST))}
                    </select>
                    <input type="hidden" name="id" value="{param_id}">
                    <input type="submit" value="サーバー変更">
                </form>
            </body>
            </html>
            """
            return render_template_string(html_content)

        except requests.exceptions.RequestException as e:
            er = f'''
            <form method="post">
                <select name="server_index">
                    {''.join(f'<option value="{i}">{i}: {server}</option>' for i, server in enumerate(SERVER_LIST))}
                </select>
                <input type="hidden" name="id" value="{param_id}">
                <input type="submit" value="サーバー変更">
            </form>
            '''
            return f'Error: {str(e)}<br>{er}', 500

    # GETリクエストの場合はデフォルトサーバー（0番目）を使用
    api_url = f"{SERVER_LIST[0]}/api/{param_id}"

    try:
        response = requests.get(api_url)
        response.raise_for_status()

        data = response.json()

        stream_url = data.get('stream_url')
        channel_image = data.get('channelImage')
        channel_name = data.get('channelName')
        video_des = data.get('videoDes')
        video_title = data.get('videoTitle')

        html_content = f"""
        <!DOCTYPE html>
        <html lang="ja">
        <head>
            <meta charset="UTF-8">
            <title>Video</title>
            <style>
                body {{ font-family: sans-serif; text-align: center; margin: 10px; }}
                img {{ width: 80px; height: auto; float: left; margin-right: 5px; }}
                p {{ font-size: 12px; margin: 5px 0; }}
                select, input {{ font-size: 12px; padding: 5px; }}
                h3 {{ font-size: 14px; }}
            </style>
        </head>
        <body>
            <h1>{video_title}</h1>
            <p><a href="{stream_url}"><img src="https://img.youtube.com/vi/{param_id}/0.jpg" alt="Video Thumbnail"></a></p>
            <p>{channel_name}</p>
            <p>{video_des}</p>
            <h3>サーバー選択</h3>
            <form method="post">
                <select name="server_index">
                    {''.join(f'<option value="{i}">{i}: {server}</option>' for i, server in enumerate(SERVER_LIST))}
                </select>
                <input type="hidden" name="id" value="{param_id}">
                <input type="submit" value="サーバー変更">
            </form>
        </body>
        </html>
        """
        return render_template_string(html_content)

    except requests.exceptions.RequestException as e:
        er = f'''
        <form method="post">
            <select name="server_index">
                {''.join(f'<option value="{i}">{i}: {server}</option>' for i, server in enumerate(SERVER_LIST))}
            </select>
            <input type="hidden" name="id" value="{param_id}">
            <input type="submit" value="サーバー変更">
        </form>
        '''
        return f'Error: {str(e)}<br>{er}', 500

@app.route('/c', methods=['GET'])
def get_channel_info():
    channel_id = request.args.get('id')
    page = request.args.get('page', '1')  # ページネーション用のパラメータ

    if not channel_id:
        return "Channel ID is required", 400

    try:
        page = int(page)
        if page < 1:
            page = 1
    except ValueError:
        page = 1

    # Invidious APIでチャンネル情報を取得
    channel_url = f"{INVIDIOUS_API_URL}/channels/{channel_id}"
    videos_url = f"{INVIDIOUS_API_URL}/channels/{channel_id}/videos?page={page}"

    try:
        # チャンネル情報の取得
        channel_response = requests.get(channel_url)
        channel_response.raise_for_status()
        channel_data = channel_response.json()

        # チャンネル動画の取得
        videos_response = requests.get(videos_url)
        videos_response.raise_for_status()
        videos_data = videos_response.json()

        # チャンネル情報の抽出
        channel_name = channel_data.get('author', 'Unknown Channel')
        channel_description = channel_data.get('description', 'No description available')
        banner_url = channel_data.get('authorBanners', [{}])[0].get('url', 'https://via.placeholder.com/320x80')
        thumbnail_url = channel_data.get('authorThumbnails', [{}])[-1].get('url', 'https://via.placeholder.com/80')

        # HTMLテンプレート
        html_content = f"""
        <!DOCTYPE html>
        <html lang="ja">
        <head>
            <meta charset="UTF-8">
            <title>{channel_name}</title>
            <style>
                body {{ font-family: sans-serif; text-align: center; margin: 10px; }}
                img {{ width: 80px; height: auto; margin-right: 5px; }}
                p {{ font-size: 12px; margin: 5px 0; }}
                .banner {{ width: 100%; max-width: 320px; height: auto; }}
                .video {{ margin: 10px 0; text-align: left; }}
                input, button {{ font-size: 12px; padding: 5px; }}
                h1 {{ font-size: 16px; }}
                h2 {{ font-size: 14px; }}
            </style>
        </head>
        <body>
            <img src="{banner_url}" alt="Channel Banner" class="banner">
            <h1>{channel_name}</h1>
            <p><img src="{thumbnail_url}" alt="Channel Thumbnail">{channel_description}</p>
            <h2>動画</h2>
        """

        # 動画リストの追加
        for video in videos_data.get('videos', [])[:40]:  # 最大40件表示
            video_id = video.get('videoId')
            title = video.get('title', 'No Title')
            thumbnail_url = f"https://img.youtube.com/vi/{video_id}/0.jpg"
            html_content += f"""
            <div class="video">
                <a href="/w?id={video_id}">
                    <img src="{thumbnail_url}" alt="Video Thumbnail">
                    <p>{title}</p>
                </a>
            </div>
            """

        # ページネーション
        html_content += f"""
            <div>
                <form method="get" style="display:inline;">
                    <input type="hidden" name="id" value="{channel_id}">
                    <input type="hidden" name="page" value="{page - 1}">
                    <input type="submit" value="前のページ" {"disabled" if page == 1 else ""}>
                </form>
                <span>ページ {page}</span>
                <form method="get" style="display:inline;">
                    <input type="hidden" name="id" value="{channel_id}">
                    <input type="hidden" name="page" value="{page + 1}">
                    <input type="submit" value="次のページ">
                </form>
            </div>
        </body>
        </html>
        """

        return render_template_string(html_content)

    except requests.exceptions.RequestException as e:
        return f"Error fetching channel data: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
