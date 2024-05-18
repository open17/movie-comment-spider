from libs.movie_comment import get_all_comments
from libs.tools import *

CONFIG_FILE = 'config.json'


def auto_get_comments():
    config = load_json(CONFIG_FILE)
    cookie_str = config.get('cookies', '')
    cookies=parse_cookies(cookie_str)
    tmp_path=config.get('tmp_path','./tmp')
    output=config.get('output_file','res.xlsx')
    douban_tasks=config.get("douban")
    maoyan_tasks=config.get("maoyan")
    for task in douban_tasks:
        get_all_comments(movie_id=task, platform="douban", cookies=cookies,save_dir=tmp_path)
    for task in maoyan_tasks:
        get_all_comments(movie_id=task, platform="maoyan", cookies=None,save_dir=tmp_path)
    merge_comment_excels(folder_path=tmp_path,output_path=output)
    
if __name__ == "__main__":
    auto_get_comments()