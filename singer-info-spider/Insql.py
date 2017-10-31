# -*- coding: gbk -*-
from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# 建立链接
engine = create_engine('mysql+pymysql://music_pro_root:!QAZ2wsx#EDC@rm-wz9ig417esevyu3yio.mysql.rds.aliyuncs.com'
                       '/music-test?charset=utf8', echo=False, pool_size=20)
# 建立会话
DBSession = sessionmaker(bind=engine)
session = DBSession()
Base = declarative_base()


# 歌手分类表
class singerclassify(Base):
    __tablename__ = 'singerclassify'
    singer_id = Column(Integer, primary_key=True)
    singer_tag = Column(String(20))
    singer_alpha = Column(String(10))
    singer_name = Column(String(50))
    singer_belong = Column(String(20))
    singer_group = Column(String(20))
    singer_area = Column(String(20))
    singer_photo_url = Column(String(200))
    s_singer_id = Column(Integer)
    s_singer_mid = Column(String(50))

Base.metadata.create_all(engine)


# 爬虫--入库功能
def insertDb(dict_value, type='artist'):
    engine = create_engine(
        'mysql+pymysql://music_pro_root:!QAZ2wsx#EDC@rm-wz9ig417esevyu3yio.mysql.rds.aliyuncs.com/music-test?'
        'charset=utf8', echo=False, pool_size=20)
    # 建立会话
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    Base = declarative_base()

    # 歌手信息
    if type == 'singerclassify' and dict_value:
        singer_classify_add = singerclassify(singer_tag=dict_value['singer_tag'],
                                             singer_alpha=dict_value['singer_alpha'],
                                             singer_name=dict_value['singer_name'],
                                             singer_belong=dict_value['singer_belong'],
                                             singer_group=dict_value['singer_group'],
                                             singer_area=dict_value['singer_area'],
                                             singer_photo_url=dict_value['singer_photo_url'],
                                             s_singer_id=dict_value['s_singer_id'],
                                             s_singer_mid=dict_value['s_singer_mid'])
        session.add(singer_classify_add)
        session.commit()
    session.close()
