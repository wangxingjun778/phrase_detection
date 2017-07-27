#encoding=utf-8
import json
from gen.phrase.PhraseService import Client
from bfd.harpc.common import config
from bfd.harpc import client
import sys
import time

if __name__ == '__main__':
    branch=sys.argv[1]
    conf_path='etc/client.conf.'+branch
    conf = config.Config(conf_path)
    manager = client.Client(Client,conf)
    client_ = manager.create_proxy()


    text = """

    新房二手房共卖42万套 去年津城楼市创六年新高 受购房需求持续释放影响，去年楼市始终保持高位运行。记者从安居客、赶集网、我爱我家等平台了解到，2016年本市新建商品住宅和二手私产住宅分别成交234264套和188751套，分别比2015年增长75%和51%，成交量均创下六年来新高。后悔去年年初没买房谈及去年的房地产市场，市民李先生表示，特别后悔去年年初时没有买套房。李先生所言正好反映出去年楼市的运行情况。去年年初，在宽松的信贷政策条件下，刚需、改善型购房需求集中入市，尤其是“买一卖一”和“卖一买一”的改善型客户需求较高。从58同城搜索发现，中心城区90至140平方米的二室、三室房源供不应求，刺激卖方非理性上调价格，次中心区域的二手房价格同比涨幅甚至不低于70%。在这种情况下，投资客群也看好市中心区域，坚定出手，强势追涨。幸亏第四季度，随着限购限贷政策的落地执行，新房二手房市场活跃度有所下降。预计今年房价将回调元旦3天假期，本市新房二手房市场热度继续下滑，咨询量、带看量与上月同期相比下降10%以上，在梅江、奥城以及老城厢等高端片区内，跌幅甚至超过20%。今年楼市将会呈现怎样的走势呢？中国指数研究院天津分院分析师认为，今年房地产市场将呈现“销售量价回调，新开工小幅下降，投资低速增长”的特点。在需求方面，今年商品房销售面积受到政策、货币因素的影响，将出现回调，预计全年降幅将达到12.8%至14.8%。供应方面，鉴于销售回落，新开工意愿也不足，预计全年降幅在3%以内。在价格方面，需求回调将导致价格有所下跌，预计全年跌幅在1.9%到3.9%。

    """
    N = 1
    t1 = time.time()
    for i in range(N):
        result = client_.phrase_detect(text, 7)
    t2 = time.time()
    print result
    print "\nAverage time consuming: ", (t2-t1)/float(N)
    print "\nTotal time consuming: ", (t2-t1)
    
