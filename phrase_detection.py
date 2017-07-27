#coding:utf-8

"""
@Description: Phrase extraction.
@Author     : wangxingjun778@163.com
@Date       : 2017-5-9
@Last modified by: wangxingjun778@163.com  2017-5-26
"""

import os, sys, math, re, copy
import jieba
reload(sys)
sys.setdefaultencoding('utf-8')
cur_dir = os.path.dirname( os.path.abspath(__file__)) or os.getcwd()
sys.path.append(cur_dir)
from config import Config    
import Levenshtein as lv


class Phrase_Detection(object):
    def __init__(self):
        jieba.initialize()
        config_obj = Config()
        self.stopwords   = self.load_stop_file(config_obj.stop_file)
        self.phrase_dict = self.load_model(config_obj.phrase_file)
        self.idf_dict    = self.load_model(config_obj.idf_file)

    def load_stop_file(self, file_path):
        """ 
        Brief: For loading the input stopwords file.
        Input:
            file_path <string>: The path of the stopwords file.
        Output:
            res <set>: The stopwords set.
        """
        res = set()
        with open(file_path, 'r') as fp:
            for line in fp.readlines():
                line = line.strip()
                if not line:
                    continue
                res.add(line)
        return res

    def load_model(self, file_path):
        """ 
        Brief: For loading the model file.
        Input:
            file_path <string>: The path of the model file.
        Output:
            d_res       <dict>: The dict of the model.
        """
        d_res = {}
        with open(file_path, 'r') as fp:
            for line in fp.readlines():
                line = line.strip()
                if not line:
                    continue
                line = line.split('\t')
                if not len(line)==2:
                    continue
                d_res[line[0].strip()] = float(line[1])
        return d_res

    def full2half(self, string):
        """ 
        Brief: Full-width to half-width for input text.
        Input:
            string  <string>: Input text.
        Output:
            res_str <string>: Output half-width text.
        """
        res_str = ""
        if not isinstance(string, (unicode)):
            string = unicode(string, 'utf-8')
        for char in string:
            encode_char = ord(char)
            if encode_char == 12288:
                encode_char = 32
            elif encode_char >= 65281 and encode_char <= 65374:
                encode_char -= 65248
            res_str += unichr(encode_char)
        return res_str

    def compute_pmi(self, x1, x2):
        """ 
        Brief: To compute the PMI(Pointwise Mutual Information) for the input data.
        Input:
            x1 <string>: Input word1.
            x2 <string>: Input word2.
        Output:
            pmi <float>: Output value of pmi.
        """
        joint_proba = float(self.phrase_dict.get(x1+x2, 0))
        p_x1 = float(self.phrase_dict.get(x1, 0))
        p_x2 = float(self.phrase_dict.get(x2, 0))
        if joint_proba * p_x1 * p_x2 == 0:
            return 0.0
        pmi = math.log( joint_proba / (p_x1 * p_x2) )  
        return -1.0/pmi

    def bigram_detect(self, l_words):
        """ 
        Brief: To find the bigram phrase.
        Input:
            l_words <list>: The list of words after segmenting.
        Output:
            d_res   <dict>: The dict of the bigram-phrase.  key==>bigram-phrase, value==>pmi
        """
        d_res = {}
        lens = len(l_words)
        if lens < 2:
            return {}
        for i in range(lens-1):
            cur_word  = str(l_words[i].strip())
            next_word = str(l_words[i+1].strip())
            if (not cur_word) or (not next_word):
                continue
            pmi = self.compute_pmi(cur_word, next_word)
            d_res[cur_word + next_word] = pmi
        return d_res

    def trigram_detect(self, l_words):
        """ 
        Brief: To find the trigram phrase.
        Input:
            l_words <list>: The list of words after segmenting.
        Output:
            d_res   <dict>: The dict of the trigram-phrase.  key==>trigram-phrase, value==>pmi*idf
        """
        d_res = {}
        lens = len(l_words)
        if lens < 3:
            return {}
        for i in range(lens-2):
            word1 = str(l_words[i].strip())
            word2 = str(l_words[i+1].strip())
            word3 = str(l_words[i+2].strip())
            if (not word1) or (not word2) or (not word3):
                continue
            pmi = self.compute_pmi(word1+word2, word3)
            if pmi == 0:
                pmi = self.compute_pmi(word1, word2)
                idf1 = self.idf_dict.get(word1, 1.0)
                idf2 = self.idf_dict.get(word2, 1.0)
                d_res[word1 + word2] = pmi * (idf1+idf2)/2.0
            else:
                idf1 = self.idf_dict.get(word1, 1.0)
                idf2 = self.idf_dict.get(word2, 1.0)
                idf3 = self.idf_dict.get(word3, 1.0)
                d_res[word1 + word2 + word3] = pmi * (idf1+idf2+idf3)/3.0
        return d_res

    def deduplication(self, d_data, thres=0.75):
        """
        Brief: deduplication by using Levenshtein distance.
        Input:
            d_data <dict>: input dict data. Ex: {word1:weight1, word2:weight2, ...}
            thres <float>: threshold of the Levenshtein distance.
        Output:
            d_data_res <dict>: output dict data after deduplicating. Ex: {word1:weight1, word2:weight2, ...} 
        """
        d_data_res = copy.deepcopy(d_data)
        record = set()
        for text,score in d_data.items():
            record.add(text)
            for another_text,score in d_data.items():
                if another_text in record:
                    continue
                if text in another_text:
                    if d_data_res.get(text, False):
                        d_data_res.pop(text)
                        record.add(text)
                if another_text in text:
                    if d_data_res.get(another_text, False):
                        d_data_res.pop(another_text)
                        record.add(another_text)
                if lv.ratio(text, another_text)>=thres:
                    if len(text)==len(another_text):
                        continue
                    temp = text if len(text)<len(another_text) else another_text
                    if d_data_res.get(temp, False):
                        d_data_res.pop(temp)
                    record.add(another_text)
        return d_data_res

    def process(self, text, topN=7, thres=0.01):
        """ 
        Brief: Main function for processing the input text.
        Input:
            text <string>: Input text.
            topN    <int>: The number of the result.
            thres <float>: The threshold of the pmi.
        Output:
            l_res_all <dict>: The dict of the trigram-phrase.  key==>trigram-phrase, value==>weight
        """
        d_res_all = {}
        if topN > 15:
            topN = 15
        if topN < 0:
            topN = 0
        text = self.full2half(text)
        text = re.split(r"，|。|、|“|”|？|,|\?", text)
        ll_words = []
        for term in text:
            term = term.strip()
            if not term:
                continue
            ll_words.append( [i.strip() for i in jieba.cut(term) if i.strip()] )
        for l_words in ll_words:
            #d_res = self.bigram_detect(l_words)
            d_res = self.trigram_detect(l_words)
            for k,v in d_res.items():
                if v < thres:
                    continue
                if k in d_res_all:
                    d_res_all[k] += round(v, 3) 
                else:
                    d_res_all[k] = round(v, 3)
        d_res_all = self.deduplication(d_res_all)    
        l_res_all = sorted(d_res_all.items(), lambda x, y: cmp(x[1], y[1]), reverse=True)
        ## l_res_all <list>: [(k1,v1), (k2,v2), ...]
        l_res_all = l_res_all[:topN]                           
        return l_res_all


def main(text):  
    ## Main function. For test.
    phraseDetect_obj = Phrase_Detection()
    t1 = time.time()
    l_res_all = phraseDetect_obj.process(text)
    t2 = time.time()
    print "Time consuming: ", t2-t1, '\n'
    res = '  '.join([k+'('+str(v)+')' for k,v in l_res_all])
    print res
    #print json.dumps(res, ensure_ascii=False)
    



import time
import json
if __name__ == '__main__':
    text = """

    受购房需求持续释放影响，去年楼市始终保持高位运行。记者从安居客、赶集网、我爱我家等平台了解到，2016年本市新建商品住宅和二手私产住宅分别成交234264套和188751套，分别比2015年增长75%和51%，成交量均创下六年来新高。后悔去年年初没买房谈及去年的房地产市场，市民李先生表示，特别后悔去年年初时没有买套房。李先生所言正好反映出去年楼市的运行情况。去年年初，在宽松的信贷政策条件下，刚需、改善型购房需求集中入市，尤其是“买一卖一”和“卖一买一”的改善型客户需求较高。从58同城搜索发现，中心城区90至140平方米的二室、三室房源供不应求，刺激卖方非理性上调价格，次中心区域的二手房价格同比涨幅甚至不低于70%。在这种情况下，投资客群也看好市中心区域，坚定出手，强势追涨。幸亏第四季度，随着限购限贷政策的落地执行，新房二手房市场活跃度有所下降。预计今年房价将回调元旦3天假期，本市新房二手房市场热度继续下滑，咨询量、带看量与上月同期相比下降10%以上，在梅江、奥城以及老城厢等高端片区内，跌幅甚至超过20%。今年楼市将会呈现怎样的走势呢？中国指数研究院天津分院分析师认为，今年房地产市场将呈现“销售量价回调，新开工小幅下降，投资低速增长”的特点。在需求方面，今年商品房销售面积受到政策、货币因素的影响，将出现回调，预计全年降幅将达到12.8%至14.8%。供应方面，鉴于销售回落，新开工意愿也不足，预计全年降幅在3%以内。在价格方面，需求回调将导致价格有所下跌，预计全年跌幅在1.9%到3.9%。

    """

    text = """
    近日,民航局发布信息称,自4月1日开始,开展为期9个月的2017年“民航服务质量规范”专项行动,进一步规范互联网机票销售平台经营行为,重点查处票务违规行为,着力改善消费者购票环境,规范退改签工作。不少人认为,民航局开展此次专项行动的背景,是目前互联网机票销售平台上出现的种种乱象。互联网机票销售存在哪些问题,需要民航局启动为期9个月的专项行动?对此,《法制日报》记者进行了深入调查。在移动互联网不断发展的今天,许多日常生活需求都可以通过手机App及支付平台的接入来完成,购买机票也是如此。互联网机票销售平台的出现,虽然方便了消费者,但其中的种种乱象也让消费者头疼不已。
    """
    
    main(text)

    """ 
    phraseDetect_obj = Phrase_Detection()
    d_data = {'邯郸市临漳县':1, '德州市平原县':1, '邯郸市永年县':1, '河北省邯郸市临漳县':1, '山东省德州市平原县':1, '擅自撕毁封条':1, '地区大气污染防治':1, '河北省邯郸市永年县':1, '北京市朝阳区金盏':1, '石家庄市晋州市':1}
    d_res = phraseDetect_obj.deduplication(d_data, 0.75)
    print '\n>>>>>:', json.dumps(d_data, ensure_ascii=False) 
    print '\n>>>>>:', json.dumps(d_res, ensure_ascii=False) 
    """
