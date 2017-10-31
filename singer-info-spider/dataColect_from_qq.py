import requests
from bs4 import BeautifulSoup
import re
import json
import oss2
import Insql

headers = {'Accept-Language': 'zh-CN,zh;q=0.8', 'Cache-Control': 'max-age=0',
           'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 '
                        '(KHTML, like Gecko) Chrome/59.0.3071.109 Safari/537.36'}

QQ_MUSIC_SINGER_URL = 'https://y.qq.com/portal/singer_list.html'

DETAIL_URL_START = 'https://c.y.qq.com/v8/fcg-bin/v8.fcg?channel=singer&page=list&'

DETAIL_URL_END = '&g_tk=1117285992&jsonpCallback=GetSingerListCallback&loginUin=1&hostUin=0&format=jsonp' \
                 '&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq&needNewCode=0'
PAGE_NUM = 1

IMAGE_URL_START = 'http://y.gtimg.cn/music/photo_new/'
IMAGE_NAME_BEG = 'T001R300x300M000'
IMAGE_NAME_END = '.jpg'
IMAGE_ART_PHOTO_FILE_PATH = 'http://source.edian66.com/prosingerphoto/'

OSS_PHOTO_FILE_PATH = 'prosingerphoto/'

IMAGE_NOT_FOUND = 'http://y.gtimg.cn/mediastyle/global/img/singer_300.png'
IMAGE_NOT_FOUND_FILE_PATE = 'http://source.edian66.com/prosingerphoto/img/singer_300.png'

# 设置oss
auth = oss2.Auth('LTAIgKpditaGe91a', '0IbKHUZFhz1rOGzXi76PWFjUdLxGT8')
bucket = oss2.Bucket(auth, 'http://oss-cn-shenzhen.aliyuncs.com/', 'shujustore')


# 下载图片
def get_file(file_name, r_content):
    try:
        bucket.put_object(file_name, r_content)
    except Exception as e:
        print(e)


# 取得所有歌手分类信息
def get_singer_classify_info():
    r = requests.get(QQ_MUSIC_SINGER_URL, headers=headers)

    soup = BeautifulSoup(r.content.decode('utf-8'), 'html5lib')

    singer_tag_group = soup.find_all('div', re.compile('singer_tag__list js_area'))[0].find_all('a')

    alphas_group = soup.find_all('div', re.compile('singer_tag__list js_letter'))[0].find_all('a')

    is_going = False
    is_open_file = False
    read_point_param = True
    for item in iter(singer_tag_group):
        singer_data_key_str = str(item.get('data-key'))
        if singer_data_key_str.startswith('eu'):
            break
        #     is_going = True
        # if not is_going:
        #     continue

        if singer_data_key_str.startswith('all'):
            continue

        singer_data_key_list = singer_data_key_str.split('_')
        singer_area = singer_data_key_list[0]
        singer_belong = singer_data_key_list[1]

        f = open('page-qq.txt', 'r')
        page_content = f.read().split('_')
        continue_singer_area = page_content[0]
        continue_singer_belong = page_content[1]
        continue_alphas = page_content[2]
        f.close()

        if singer_area == continue_singer_area and singer_belong == continue_singer_belong:
            is_going = True
            is_open_file = True

        if not is_going:
            continue

        singer_group = ''
        if singer_belong == 'man':
            singer_group = '男歌手'
        elif singer_belong == 'woman':
            singer_group = '女歌手'
        elif singer_belong == 'team':
            singer_group = '组合'

        singer_tag = item.string

        param_dict = {"singer_area": singer_area, "singer_belong": singer_belong, "singer_group": singer_group,
                      "singer_tag": singer_tag}

        for alp_item in iter(alphas_group):
            alphas_str = str(alp_item.get('data-key'))
            if alphas_str.islower():
                continue
            # if not alphas_str.isdigit():
            #     continue

            if ((ord(alphas_str) < ord(continue_alphas)) or
                    (continue_alphas == '9' and alphas_str != continue_alphas)) and read_point_param:
                continue

            read_point_param = False
            key_str = singer_data_key_str + '_' + alphas_str

            # special for some case
            # if key_str.startswith('eu_man') is False or (ord(alphas_str) >= ord('L')):
            #     continue
            # special for some case
            # if key_str.startswith('eu_man') is False or (ord(alphas_str) >= ord('O')):
            #     continue
            # special for some case
            # if key_str.startswith('eu_man') is False or (ord(alphas_str) >= ord('T')):
            #     continue
            # special for some case
            # if key_str != 'eu_man_T':
            #     continue

            detail_url = DETAIL_URL_START + 'key=%s&pagesize=100&pagenum=%d' % (key_str, PAGE_NUM) + DETAIL_URL_END
            req = requests.get(detail_url, headers=headers)
            # print(detail_url)

            beau_soup = BeautifulSoup(req.content.decode('utf-8'), 'html5lib')
            detail_content = str(beau_soup.find_all('body'))
            json_obj = json.loads(detail_content[detail_content.find('list') - 2: detail_content.rfind('message') - 2])
            total_page = json_obj['total_page']
            if total_page < 1:
                continue

            get_detail_info(alphas_str, total_page, key_str, singer_data_key_str, param_dict, is_open_file)


# 取得字母A-Z的歌手详情
def get_detail_info(alphas, total_page, key_str, singer_data_key_str, param_dict, is_open_file):
    for page_num in range(total_page):
        page_num_reset = 'T'
        if is_open_file:
            f = open('page-qq.txt', 'r')
            page_content = f.read().split('_')
            continue_page_num = int(page_content[3])
            page_num_reset = page_content[4]
            f.close()

        if page_num < continue_page_num - 1:
            continue

        if page_num_reset == 'T' and page_num < continue_page_num - 1:
            continue

        # if singer_data_key_str.startswith('eu_man') and alphas.startswith('O') and page_num < 75:
        #     continue   key=cn_woman_9&pagesize=100&pagenum=1

        detail_url = DETAIL_URL_START + 'key=%s&pagesize=100&pagenum=%d' % (key_str, page_num + 1) + DETAIL_URL_END
        # r = requests.get(detail_url, headers=headers)
        page_num_val = str(page_num + 1)
        try:
            r = requests.get(detail_url, headers=headers)
        except Exception as e:
            print(detail_url)
            f = open('page-qq.txt', 'w')
            f.write(key_str + '_' + page_num_val + '_T')
            f.close()
            print(e)

        # print(detail_url)

        soup = BeautifulSoup(r.content.decode('utf-8'), 'html5lib')
        detail_content = str(soup.find_all('body'))
        if detail_content.find('list') <= 2 or detail_content.rfind('message') <= 2:
            continue

        json_obj = json.loads(detail_content[detail_content.find('list') - 2: detail_content.rfind('message') - 2])
        # print(json_obj)
        detail_info_list = json_obj['list']

        f = open('page-qq.txt', 'w')
        f.write(key_str + '_' + page_num_val + '_F')
        f.close()

        singer_classify_info = {'singer_tag': param_dict.get('singer_tag')}
        singer_classify_info['singer_alpha'] = alphas
        singer_classify_info['singer_area'] = param_dict.get('singer_area')
        singer_classify_info['singer_group'] = param_dict.get('singer_group')
        singer_classify_info['singer_belong'] = param_dict.get('singer_belong')

        per_page_exec_num = 0
        ff = open('per-page-exec-size.txt', 'r')
        page_size = ff.read()

        page_executed_num = int(page_size)
        for info_item in detail_info_list:
            if per_page_exec_num < page_executed_num:
                per_page_exec_num += 1
                continue

            singer_name = info_item['Fsinger_name']
            if singer_name is None:
                continue

            s_singer_id = int(info_item['Fsinger_id'])
            s_singer_mid = info_item['Fsinger_mid']

            image_name = IMAGE_NAME_BEG + s_singer_mid + IMAGE_NAME_END

            singer_path = str(s_singer_id) + "/" + image_name

            singer_photo_url = IMAGE_ART_PHOTO_FILE_PATH + singer_path

            art_photo_download_url = IMAGE_URL_START + image_name
            oss_singer_photo_url = OSS_PHOTO_FILE_PATH + singer_path

            singer_classify_info['singer_name'] = singer_name
            singer_classify_info['s_singer_id'] = s_singer_id
            singer_classify_info['s_singer_mid'] = s_singer_mid
            singer_classify_info['singer_photo_url'] = singer_photo_url

            try:
                req = requests.get(art_photo_download_url, headers=headers)
                status_code = req.status_code
            except Exception as e:
                status_code = 404

            if status_code == 200:
                get_file(oss_singer_photo_url, req.content)
            else:
                singer_classify_info['singer_photo_url'] = IMAGE_NOT_FOUND_FILE_PATE

            try:
                Insql.insertDb(singer_classify_info, 'singerclassify')
            except Exception as e:
                print(detail_url)
                f = open('page-qq.txt', 'w')
                f.write(key_str + '_' + page_num_val + '_T')
                f.close()
                print(e)

            f = open('per-page-exec-size.txt', 'w')
            f.write(str(per_page_exec_num))
            f.close()

            per_page_exec_num += 1

        if per_page_exec_num == detail_info_list.__len__():
            f = open('per-page-exec-size.txt', 'w')
            f.write('0')
            f.close()

        if (total_page > 1 and continue_page_num == total_page - 1) or (total_page == 1):
            f = open('page-qq.txt', 'w')
            f.write(key_str + '_1_F')
            f.close()


if __name__ == "__main__":
    get_singer_classify_info()
