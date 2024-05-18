# 电影评论自动化爬虫

## 安装环境

```shell
git clone https://github.com/BiliVista/movie-comment-spider.git
cd movie-comment-spider
pip install -r requirements.txt
```

## 配置任务

你需要在config.json中配置相关任务信息:

```json
{
    "cookies":"XXXX",  // 豆瓣cookies(豆瓣不登录评论仅限前200多条)
    "tmp_path":"./tmp",  //电影临时评论的输出文件夹,默认为tmp
    "output_file":"res.xlsx", //最终的全部数据文件,默认为res
    "douban":[36208094,34951373], // 要爬取的豆瓣电影id
    "maoyan":[43] // 同理的猫眼电影id
}
```

其中电影id为对应的网站的浏览器链接最后部分,比如下面这步电影的猫眼id即为`1446323`
![alt text](https://cdn.jsdelivr.net/gh/open17/Pic/img/202405160015105.png)


## 运行爬虫

```shell
python main.py
```

该脚本会自动爬取一系列电影的豆瓣和猫眼评论信息(带评分标签)

