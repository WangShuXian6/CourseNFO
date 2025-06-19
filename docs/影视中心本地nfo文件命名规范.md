# 影视中心本地nfo文件命名规范



原始地址：https://support.ugnas.com/knowledgecenter/#/detail/eyJpZCI6NDA4MCwidHlwZSI6InRhZzAwMiIsImxhbmd1YWdlIjoiemgtQ04iLCJjbGllbnRUeXBlIjoiUEMiLCJhcnRpY2xlSW5mb0lkIjo2NjUsImFydGljbGVWZXJzaW9uIjoiIiwicGF0aENvZGUiOiIifQ==

绿联 NAS 的 UGOS Pro 影视中心当前有三种影视刮削方式：

1、TMDB：通过 The Movie Database (TMDB) 抓取元数据，包括影片名称、演员、简介和海报等。

2、智能识别：系统通过算法自动识别文件名和属性，从数据库中选取最佳匹配信息。

3、优先读取本地信息：通过自行配置资源nfo本地文件刮削，在勾选该项后，获取到配置文件的基本信息、封面、海报等数据信息。



【刮削顺序逻辑参考】

影视中心的 NFO 刮削、TMDB 刮削、智能刮削优先顺序是什么？

本文档介绍nfo文件的使用，对于无法通过TMDB或智能识别获取的资源的视频文件（如课程、综艺等），可参考以下信息自行编辑创建基本nfo文件信息

编写电影nfo文件
1、电影nfo文件的格式按照以下格式起名：
```
<movie>
中间为电影基本信息内容
</movie>
```
其中电影基本信息内容部分包括：
-|-
所需内容 | 编辑案例

指定电影名字 | <title>电影标题</title>

指定年份 | <year>2002</year>

指定简介 |<plot>简介</plot>

指定tmdbid|<tmdbid>79</tmdbid>

指定豆瓣 id|<doubanid>79</doubanid>

指定播出年月日|<releasedate>2006-01-02</releasedate>

指定评分|<rating>7.2</rating>

指定演员|<actor> <name>演员名字</name>< role>饰演角色</ role><tmdbid>演员的tmdbid</tmdbid></actor>

国家/地区（待1月上线）|<country>iso3166-1填写三位的国家数字码</country>，如 <country>156</country> 即中国

风格（待1月上线）|风格需要使用标准命名或者id。建议使用id，如<genre>战争</genre> 或 <genre>10752</genre>

分级（待1月上线）|<mpaa>PG-13</mpaa>




2、可以通过在视频文件同级目录放置图片文件，以指定展示所需海报图

海报封面推荐尺寸：1080x1920

海报剧照推荐尺寸：1920x1080

海报logo推荐尺寸：800x310

类型|命名规范&格式
-|-

竖版海报|视频文件名-poster.jpg

横板海报|视频文件名-background.jpg，视频文件名-backdrop.jpg，视频文件名-fanart.jpg





编写剧集nfo文件
1、剧集nfo文件的格式按照以下格式起名：

剧集nfo有三种，与视频文件同名.nfo、season.nfo、tvshow.nfo

(1)与视频文件同名.nfo ，放在跟播放视频文件一起，作为单集的信息

文件的格式需按照以下格式起名：
```
<episodedetails>
后续内容
</episodedetails>
```
其中视频同名文件基本信息内容部分包括：

所需内容|编辑案例
-|-
指定集标题|<title>第1集</title>

指定集简介|<plot>简介</plot>

指定季|<season>1</season>

指定集|<episode>1</episode>

如：剧集 怪奇物语-第1集



文件存放路径跟视频一致：



(2) season.nfo、tvshow.nfo 放在对应的季文件夹，或整部剧的文件夹下，作为本剧季信息及同剧多季自动合集信息来源。

season.nfo 文件的格式需按照以下格式起名：
```
<season>
后续内容
</season>
```

tvshow.nfo 文件的格式需按照以下格式起名：
```
<tvshow> 
后续内容 
</tvshow> 
```
其中season、和tvshow 文件基本信息内容部分包括：

所需内容|编辑案例

季标题|<title>季 1</title>

指定季|<seasonnumber>1</seasonnumber>

指定剧集名字|<title>剧集标题</title>

指定年份|<year>2002</year>

指定简介|<plot>简介</plot>

指定tmdbid|<tmdbid>79</tmdbid>

指定豆瓣 id|<doubanid>79</doubanid>

指定播出年月日|<releasedate>2006-01-02</releasedate>

指定评分|<rating>7.2</rating>

指定演员|<actor><name>演员名字</name>< role>饰演角色</ role><tmdbid>演员的tmdbid</tmdbid></actor>





备注： 如果tvshow和season都有title会拼接为 ”剧集标题 季标题“

如：剧集 怪奇物语-第2季



文件存放路径如：



2、可以通过在视频文件同级目录、季文件夹同集目录 放置图片文件，以指定展示所需海报图

海报封面推荐尺寸：1080x1920

海报剧照推荐尺寸：1920x1080

剧集封面推荐尺寸：1920x1080


类型|命名规范&格式
-|-
竖版海报|剧海报：poster.jpg,季海报：season01-poster.jpg

横板海报|视频文件名-background.jpg,视频文件名-backdrop.jp,视频文件名-fanart.jpg

剧集的集封面海报|视频文件名.jpg