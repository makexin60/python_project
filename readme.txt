1.appinfo_****
记录爬虫APP数据，里面的successful.json是已经成功跑完label和privacy的app

google:（volume:5000）
只有app_id
"beatmaker.edm.musicgames.PianoGames"

appstore:（volume:55000）
{
    "id": 1349856274,
    "name": "uTRAC",
    "url": "https://apps.apple.com/ie/app/utrac/id1349856274?uo=4"
}

2.Label_****
记录的是Label数据，里面都是json,现有的全部APP都已经跑完了

3.Policy_****
记录的是privacy数据，里面就是纯文本，内容包含隐私的原页面和原因面中带有privacy文本的可视化a标签的body的内容，里面都过滤了header和footer标签和包含header和footer class名的任何元素。
现在数据量没跑完 大约都是1000左右

4.Logger
****_warning.log 里面是完整的app信息记录

google:(GooglePlayPrivacy_warning.log)
2025-03-02 20:15:28,829 - WARNING - {'title': 'Western Union Send Money Now', 'app_id': 'com.westernunion.android.mtapp', 'installs': '10,000,000+', 'score': 4.595993, 'ratings': 313168, 'reviews': 135620, 'privacyPolicy': 'https://www.westernunion.com/us/privacy-statement', 'developerEmail': 'customerservice@westernunion.com', 'developerWebsite': 'https://www.westernunion.com/us/en/home.html', 'app_url': 'https://play.google.com/store/apps/datasafety?id=com.westernunion.android.mtapp&hl=en', 'sub-section_urls': ['https://www.westernunion.com/global/en/us-consumer-privacy-notice.html', 'https://www.westernunion.com/global/en/privacy-statement.html']}

appstore:(AppStorePrivacy_warning.log)
2025-03-03 04:10:58,805 - WARNING - {'id': 724241430, 'name': 'Naukrigulf Job Search App', 'app_url': 'https://apps.apple.com/ie/app/naukrigulf-job-search-app/id724241430?uo=4', 'privacy_url': '', 'filtered_urls': ['http://www.naukrigulf.com/ni/nilinks/nkr_links.php?open=privacy', 'https://www.apple.com/legal/privacy/data/en/app-store/']}

****_error.log 里面是错误信息记录
有可能是404等，有可能是页面打不开，有可能是元素获取不到.......


google categories reference:
https://support.google.com/googleplay/android-developer/answer/9859673?hl=en


2025-03-17 00:11:17,806---8：45之后的error find_privacy_cards:都不要了


