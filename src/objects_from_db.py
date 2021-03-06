#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import numpy as np
import pandas as pd
from db_interface import DataBase
import rospy
import rosparam
import math
DIS = 0.15
NAME="./data_frames/data_frame_crest.csv"
# visualization
#import roslib; roslib.load_manifest('visualization_marker_tutorials')
from visualization_msgs.msg import Marker
from visualization_msgs.msg import MarkerArray
import matplotlib.cm as cm
color = [cm.gist_rainbow(i / float(1000))for i in range(1000)]
GET_DATA=False

def primary_function(x1, y1, x2, y2):
    """
    a = (y2- y1) / (x2 -x1)
    b = y1 - ax1
    Return
    y = ax + b
    ----------
    a: float
    b: float
    """
    a = (y2 -y1) / ((x2 -x1))
    b = y1 - a * x1

    return [a, b]

class Objects(object):

    u"""
    物体検出・認識に関する処理を扱うオーダークラス
    """
    def __init__(self,):
        u"""
        Paramaters
        -----
        robot : class instance
            hsrb_interface robot.py Robot
        """
        db_name = "hsr_db"
        host = "192.168.1.70"
        user = "administrator"
        password = "password"
#        db_name = rosparam.get_param("/db_param/dbname")
#        host = rosparam.get_param("/db_param/host")
#        user = rosparam.get_param("/db_param/user")
#        password = rosparam.get_param("/db_param/password")        
#        db_name = "hsr_db"
#        host = "192.168.1.70"
#        user = "administrator"
#        password = "password"
        self.df = None
        if not GET_DATA:
            self.df = pd.read_csv(NAME)
            self.df.sort("ros_timestamp")
        else:
            self.db = DataBase(db_name, host, user, password)
#        self.df = db.get_objects_info_filtered_time(ts,te)
#        self.df.to_csv("data_frame.csv")
        self.pub_marker = rospy.Publisher("visualization_objects", MarkerArray, queue_size=1)
        self.parent_frame = "map"

        rospy.loginfo("object class create success")

    def _visulaize_marker(self, sql_data):
        """
        可視化用
        """
        # rospy.sleep(0.1)
        None
#        m = MarkerArray()
#        marker = Marker()
#        marker.action = 3 # alls marker deleate
#        m.markers.append(marker)
#        self.pub_marker.publish(m)
#        markerArray = MarkerArray()
#        marker = Marker()
#        for i, _ in sql_data.iterrows():
#            marker = Marker()
#            objects_pos = list(sql_data.ix[i, ["position_x", "position_y", "position_z", "generic_id_0", "generic_score_0"]])
#            marker.id = i #"object_{0}".format(i)
#            marker.header.frame_id = "/map"
#            marker.type = marker.SPHERE
#            marker.action = marker.ADD
#            marker.scale.x = 0.08 # objects_pos[4] / 10.0
#            marker.scale.y = 0.08 # objects_pos[4] / 10.0
#            marker.scale.z = 0.08 # objects_pos[4] / 10.0
#            marker.color.a = 1 #objects_pos[4]
#            marker.color.r = color[objects_pos[3]][0]
#            marker.color.g = color[objects_pos[3]][1]
#            marker.color.b = color[objects_pos[3]][2]
#            marker.pose.orientation.w = 1.0
#            marker.pose.position.x = objects_pos[0]
#            marker.pose.position.y = objects_pos[1]
#            marker.pose.position.z = objects_pos[2]
#            markerArray.markers.append(marker)
#        self.pub_marker.publish(markerArray)

        

    def _calc_area_point(self, minx, maxx, miny, maxy, base_tf):
        u"""
        | データベースから入手した座標をbase_tfから見たエリアで区切る為に
        | エリアの必要な点の座標変換を行う
        Params
        -----
        minx : float
            base_tfから見たxの最小値、base_footprint基準ではどれだけ手前かを表す(負だと背後)
        maxx : float
            base_tfから見たxの最大値、base_footprint基準ではどれだけ奥かを表す
        miny : float
            base_tfから見たyの最小値、base_footprint基準ではどれだけ右かを表す（負右正左）
        maxy : float
            base_tfから見たyの最大値、base_footprint基準ではどれだけ左かを表す（負右正左）
        base_tf : string
            エリアの基準と成るtf
        Returns
        -----
        min_x : list of float
            base_tf基準の座標点をmap基準に変換したもの、その中におけるx最小となる[x,y]
        min_y : list of float
            base_tf基準の座標点をmap基準に変換したもの、その中におけるy最小となる[x,y]
        max_y : list of float
            base_tf基準の座標点をmap基準に変換したもの、その中におけるy最大となる[x,y]
        max_x : list of float
            base_tf基準の座標点をmap基準に変換したもの、その中におけるx最大となる[x,y]
        """
        xy_list = []
        while not rospy.is_shutdown():
            xyz= self._tf_utils.calcpos_base2child(minx, miny, 0.0, base_tf, "map")
            if xyz != []:
                break
            rospy.logwarn("can not look tf")
        xy_list.append(xyz)

        while not rospy.is_shutdown():
            xyz= self._tf_utils.calcpos_base2child(minx, maxy, 0.0, base_tf, "map")
            if xyz != []:
                break
            rospy.logwarn("can not look tf")
        xy_list.append(xyz)

        while not rospy.is_shutdown():
            xyz= self._tf_utils.calcpos_base2child(maxx, miny, 0.0, base_tf, "map")
            if xyz != []:
                break
            rospy.logwarn("can not look tf")
        xy_list.append(xyz)

        while not rospy.is_shutdown():
            xyz= self._tf_utils.calcpos_base2child(maxx, maxy, 0.0, base_tf, "map")
            if xyz != []:
                break
            rospy.logwarn("can not look tf")
        xy_list.append(xyz)
        array = np.array(xy_list)
        max_x = array[array[:,0].argmax()]
        min_x = array[array[:,0].argmin()]
        max_y = array[array[:,1].argmax()]
        min_y = array[array[:,1].argmin()]

        return min_x, min_y, max_y, max_x

    def _near_point_deleate(self, data_frame, score_type=True):
        u"""
        | データフレームの座標を閾値以上の距離にあるものを削除し、同一と思われるものを排除するメソッド
        |
        Params
        -----
        data_frame : DataFrame
            座標点の削減を行うためのDataFrame
        score_type : bool
            削除するにあたりscoreによるソートを行うが、Trueならば特定物体認識、Falseならば一般物体認識のスコアを用いる
        Returns
        -----
        data_frame : DataFrame
            座標点の削減を行ったDataFrame
        """
        if score_type:
            score_name = "specific_score_0"
        else:
            score_name = "generic_score_0"
        data_frame = data_frame.sort(score_name)
        N = len(data_frame)
        if N == 0:
            return data_frame
        df = data_frame[0:1]
        x = df.position_x.values[-1]
        y = df.position_y.values[-1]
        z = df.position_z.values[-1]
        for i in range(N):
            data_frame = data_frame.loc[(((data_frame.position_x -x)**2 + (data_frame.position_y -y) **2 +(data_frame.position_z -z) **2 ) > DIS**2 )]
            if len(data_frame) == 0:
                break
            ddf = data_frame[0:1]
            df = pd.concat([df, ddf])
            if len(data_frame) == 1:
                break
            x = ddf.position_x.values[-1]
            y = ddf.position_y.values[-1]
            z = ddf.position_z.values[-1]
        df = df.sort_values(by=score_name,ascending=False)
#        self._visulaize_marker(df)
        return df

    def _extraction_time(self, data_frame, tstart, tend):
        df = data_frame.loc[((data_frame.ros_timestamp > int(tstart)) & (data_frame.ros_timestamp < int(tend)))]
        return df
        
    def _extraction_threshold_score(self, data_frame, threshold_score, score_type=True):
        u"""
        | DataFrameからスコアで情報を取得するメソッド
        Params
        -----
        data_frame : DataFrame
            座標点の検索を行うためのDataFrame

        threshold_score : float
            スコアの閾値
        score_type : bool
            Trueならば特定物体認識、Falseならば一般物体認識のスコアを用いる
        Returns
        -----
        data_frame :
            データベースから獲得した情報
        """
        if score_type:
            data_frame = data_frame.loc[(data_frame.specific_score_0 > threshold_score)]
        else:
            data_frame = data_frame.loc[(data_frame.generic_score_0 > threshold_score)]

        return data_frame

    def _select_data_from_object_position(self, data_frame, minx, maxx, miny, maxy, minz, maxz, base_tf):
        u"""
        | DataFrameからエリアで情報を取得するメソッド
        Params
        -----
        data_frame : DataFrame
            座標点の検索を行うためのDataFrame
        minx : float
            base_tfから見たxの最小値、base_footprint基準ではどれだけ手前かを表す(負だと背後)
        maxx : float
            base_tfから見たxの最大値、base_footprint基準ではどれだけ奥かを表す
        miny : float
            base_tfから見たyの最小値、base_footprint基準ではどれだけ右かを表す（負右正左）
        maxy : float
            base_tfから見たyの最大値、base_footprint基準ではどれだけ左かを表す（負右正左）
        minz : float
            mapから見たzの最小値、高さをあらわす
        maxz : float
            mapから見たzの最大値、高さをあらわす
        base_tf : string
            エリアの基準と成るtf
        Returns
        -----
        data_frame :
            データベースから獲得した情報
        """
##  ｚで切る
        data_frame = data_frame.loc[(data_frame.position_z >= minz) & (data_frame.position_z <= maxz)]

##  エリアで切る


        min_x, min_y, max_y, max_x = self._calc_area_point(minx, maxx, miny, maxy, base_tf)

        mix2miy = primary_function(min_x[0], min_x[1], min_y[0], min_y[1])
        mix2may = primary_function(min_x[0], min_x[1], max_y[0], max_y[1])
        miy2max = primary_function(min_y[0], min_y[1], max_x[0], max_x[1])
        may2max = primary_function(max_y[0], max_y[1], max_x[0], max_x[1])

        data = data_frame.loc[((mix2miy[0] * data_frame.position_x + mix2miy[1] - data_frame.position_y) <= 0.0) &
                              ((mix2may[0] * data_frame.position_x + mix2may[1] - data_frame.position_y) >= 0.0) &
                              ((miy2max[0] * data_frame.position_x + miy2max[1] - data_frame.position_y) <= 0.0) &
                              ((may2max[0] * data_frame.position_x + may2max[1] - data_frame.position_y) >= 0.0) ]
        return data

    def _get_object_info_all(self,):
        u"""
        | DataBaseからすべての情報を取得するメソッド
        Returns
        -----
        data_frame :
            データベースから獲得した情報
        """
        data_frame = self.df
        return data_frame

    def _get_object_info_from_time(self, tstart=5, tend=0):
        u"""
        | DataBaseから指定した時間の情報を取得するメソッド
        Params
        -----
        tstart : rospy.time、 default rospy.Time(0)
            情報を引き出すための開始時間
        tend : rospy.time、 default rospy.Time.now()
            情報を引き出すための終了時間
        Returns
        -----
        data_frame :
            データベースから獲得した情報
        """
        ts = rospy.Time.now() - rospy.Duration(tstart)
        ts = ts.to_nsec()
        te = rospy.Time.now().to_nsec()
        data_frame = self.db.get_objects_info_filtered_time(ts, te)
        return data_frame

    def _get_object_info_latest(self):
        u"""
        | 最新の物体情報をすべて取得するメソッド
        """
        data_frame = self.db.get_objects_info_latest()
        return data_frame

    def _get_plane_info_latest(self):
        u"""
        | 最新の平面情報をすべて取得するメソッド
        """
        data_frame = self.db.get_objects_info_latest()
        return data_frame

    def get_object_num_latest(self, threshold_score, score_type):
        """
        見つけた物体候補数を返すメソッド
        Params
        -----
        threshold_score : float
            スコアの閾値
        score_type : bool
            Trueならば特定物体認識、Falseならば一般物体認識のスコアを用いる
        Returns
        -----
        num_objects : int
            見つけた物体候補の数
        """
##     スコアによる物体の閾値が必要？
        data_frame = self._get_object_info_latest()
        if len(data_frame)==0:
            return 0
        data_frame = self._extraction_threshold_score(data_frame, threshold_score, score_type)
        if len(data_frame)==0:
            return 0
        data_frame = self._near_point_deleate(data_frame)
        num_objects = len(data_frame)
        rospy.loginfo("Num_Object:{}".format(num_objects))
        return num_objects

    def get_object_num_from_time(self, tstart, tend, threshold_score, score_type):
        """
        見つけた物体候補数を返すメソッド
        Params
        -----
        tstart : rospy.time、 default rospy.Time(0)
            情報を引き出すための開始時間
        tend : rospy.time、 default rospy.Time.now()
            情報を引き出すための終了時間
        threshold_score : float
            スコアの閾値
        score_type : bool
            Trueならば特定物体認識、Falseならば一般物体認識のスコアを用いる
        Returns
        -----
        num_objects : int
            見つけた物体候補の数
        """
##     スコアによる物体の閾値が必要？
        data_frame = self._get_object_info_from_time(tstart, tend)
        if len(data_frame)==0:
            return 0
        data_frame = self._extraction_threshold_score(data_frame, threshold_score, score_type)
        if len(data_frame)==0:
            return 0
        data_frame = self._near_point_deleate(data_frame)
        num_objects = len(data_frame)
        rospy.loginfo("Num_Object:{}".format(num_objects))
        return num_objects

    def get_object_pos_filterd_time_and_specific_score(self, tstart, tend,threshold_score, wear_flag=True):
        """
        特定物体認識のスコアが一定以上のものかつ
        指定された時刻に発見された物体の位置とidを返すメソッド
        Params
        -----
        tstart : rospy.time、 default rospy.Time(0)
            情報を引き出すための開始時間
        tend : rospy.time、 default rospy.Time.now()
            情報を引き出すための終了時間
        threshold_score : float
            スコアの閾値
        score_type : bool
            Trueならば特定物体認識、Falseならば一般物体認識のスコアを用いる
        Returns
        -----
        obj_pos : list of float
            見つけた物体位置
        obj_id : list of int
            見つけた物体id
        """
        data = self._get_object_info_from_time(tstart, tend)
        if len(data) == 0:
            return [], []
        data = self._extraction_threshold_score(data, threshold_score, True)
        if wear_flag:
            data = self._near_point_deleate(data)
        data = data.sort_values(by="specific_score_0",ascending=False)
        N = len(data)
        obj_pos = []
        obj_id = []
        for i in range(N):
            obj_pos.append([data.position_x.values[i], data.position_y.values[i], data.position_z.values[i]])
            obj_id.append(data.specific_id_0.values[i])
        return obj_pos, obj_id

    def get_object_pos_filterd_time_and_generic_score(self, tstart, tend, threshold_score, wear_flag=True):
        """
        特定物体認識のスコアが一定以上のものかつ
        指定された時刻に発見された物体の位置とidを返すメソッド
        Params
        -----
        tstart : rospy.time、 default rospy.Time(0)
            情報を引き出すための開始時間
        tend : rospy.time、 default rospy.Time.now()
            情報を引き出すための終了時間
        threshold_score : float
            スコアの閾値
        score_type : bool
            Trueならば特定物体認識、Falseならば一般物体認識のスコアを用いる
        Returns
        -----
        obj_pos : list of float
            見つけた物体位置
        obj_id : list of int
            見つけた物体id
        """
        data = self._get_object_info_from_time(tstart, tend)
        if len(data) == 0:
            return [], []
        data = self._extraction_threshold_score(data, threshold_score, False)
        if wear_flag:
            data = self._near_point_deleate(data, False)
        data = data.sort_values(by="generic_score_0",ascending=False)
        N = len(data)
        obj_pos = []
        obj_id = []
        for i in range(N):
            obj_pos.append([data.position_x.values[i], data.position_y.values[i], data.position_z.values[i]])
            obj_id.append(data.specific_id_0.values[i])
        return obj_pos, obj_id



    def get_object_pos_filterd_time_and_specific_id(self, tstart, tend, specific_id, threshold_score, wear_flag=True):
        """
        特定物体認識のスコアが一定以上のものかつ
        指定された時刻に発見されたものかつ
        特定の物体Idのものの位置を返すメソッド
        Params
        -----
        tstart : rospy.time、 default rospy.Time(0)
            情報を引き出すための開始時間
        tend : rospy.time、 default rospy.Time.now()
            情報を引き出すための終了時間
        specific_id： int or list int
            特定物体Id
        threshold_score : float
            スコアの閾値
        score_type : bool
            Trueならば特定物体認識、Falseならば一般物体認識のスコアを用いる
        Returns
        -----
        obj_pos : list of float
            見つけた物体位置
        """
        data = self._get_object_info_from_time(tstart, tend)
        if len(data) == 0:
            return []
        data = data.loc[(data.specific_id_0 == specific_id)]
        if len(data) == 0:
            return []
        data = self._extraction_threshold_score(data, threshold_score, True)
        if wear_flag:
            data = self._near_point_deleate(data)
        data = data.sort_values(by="specific_score_0",ascending=False)
        N = len(data)
        obj_pos = []
        for i in range(N):
            obj_pos.append([data.position_x.values[i], data.position_y.values[i], data.position_z.values[i]])
        return obj_pos

    def get_object_pos_filterd_time_and_generic_name(self, tstart, tend, generic_name, threshold_score, wear_flag=True):
        """
        特定物体認識のスコアが一定以上のものかつ
        指定された時刻に発見されたものかつ
        特定の物体Idのものの位置を返すメソッド
        Params
        -----
        tstart : rospy.time、 default rospy.Time(0)
            情報を引き出すための開始時間
        tend : rospy.time、 default rospy.Time.now()
            情報を引き出すための終了時間
        specific_id： int
            特定物体Id
        threshold_score : float
            スコアの閾値
        score_type : bool
            Trueならば特定物体認識、Falseならば一般物体認識のスコアを用いる
        Returns
        -----
        obj_pos : list of float
            見つけた物体位置
        """
        data = self._get_object_info_from_time(tstart, tend)
        if len(data) == 0:
            return []
        data = data.loc[(data.generic_name_0 ==  generic_name)]
        if len(data) == 0:
            return None
        data = self._extraction_threshold_score(data, threshold_score, True)
        if wear_flag:
            data = self._near_point_deleate(data)
        data = data.sort_values(by="specific_score_0",ascending=False)
        N = len(data)
        obj_pos = []
        for i in range(N):
            obj_pos.append([data.position_x.values[i], data.position_y.values[i], data.position_z.values[i]])
        return obj_pos

    def get_object_info_filterd_time_and_area(self, tstart, tend,  minx, maxx, miny, maxy, minz, maxz, base_tf, score_type=True, wear_flag=True):
        """
        指定された範囲内で発見されたものの位置とIDを返すメソッド
        Params
        -----
        tstart : rospy.time、 default rospy.Time(0)
            情報を引き出すための開始時間
        tend : rospy.time、 default rospy.Time.now()
            情報を引き出すための終了時間
        minx : float
            base_tfから見たxの最小値、base_footprint基準ではどれだけ手前かを表す(負だと背後)
        maxx : float
            base_tfから見たxの最大値、base_footprint基準ではどれだけ奥かを表す
        miny : float
            base_tfから見たyの最小値、base_footprint基準ではどれだけ右かを表す（負右正左）
        maxy : float
            base_tfから見たyの最大値、base_footprint基準ではどれだけ左かを表す（負右正左）
        minz : float
            mapから見たzの最小値、高さをあらわす
        maxz : float
            mapから見たzの最大値、高さをあらわす
        base_tf : string
            エリアの基準と成るtf
        score_type : bool
            Trueならば特定物体認識、Falseならば一般物体認識のスコアを用いる
        Returns
        -----
        obj_pos : list of float
            見つけた物体位置
        obj_rgb : list of string
            見つけた物体の色
        obj_id : list of int
            見つけた物体id
        """
        data = self._get_object_info_from_time(tstart, tend)
        if len(data) == 0:
            return [], [], []
        data = self._select_data_from_object_position(data,  minx, maxx, miny, maxy, minz, maxz, base_tf)
        if wear_flag:
            data = self._near_point_deleate(data, score_type)
        data = data.sort_values(by="ros_timestamp",ascending=False)
        N = len(data)
        obj_pos = []
        obj_id = []
        obj_color = []
        for i in range(N):
            obj_pos.append([data.position_x.values[i], data.position_y.values[i], data.position_z.values[i]])
            obj_id.append(data.specific_id_0.values[i])
            obj_color.append(data.color.values[i])
        return obj_pos, obj_id, obj_color



    def get_object_pos_filterd_time_and_area(self, tstart, tend,  minx, maxx, miny, maxy, minz, maxz, base_tf, score_type=True, wear_flag=True):
        """
        指定された範囲内で発見されたものの位置とIDを返すメソッド
        Params
        -----
        tstart : rospy.time、 default rospy.Time(0)
            情報を引き出すための開始時間
        tend : rospy.time、 default rospy.Time.now()
            情報を引き出すための終了時間
        minx : float
            base_tfから見たxの最小値、base_footprint基準ではどれだけ手前かを表す(負だと背後)
        maxx : float
            base_tfから見たxの最大値、base_footprint基準ではどれだけ奥かを表す
        miny : float
            base_tfから見たyの最小値、base_footprint基準ではどれだけ右かを表す（負右正左）
        maxy : float
            base_tfから見たyの最大値、base_footprint基準ではどれだけ左かを表す（負右正左）
        minz : float
            mapから見たzの最小値、高さをあらわす
        maxz : float
            mapから見たzの最大値、高さをあらわす
        base_tf : string
            エリアの基準と成るtf
        score_type : bool
            Trueならば特定物体認識、Falseならば一般物体認識のスコアを用いる
        Returns
        -----
        obj_pos : list of float
            見つけた物体位置
        obj_id : list of int
            見つけた物体id
        """
        data = self._get_object_info_from_time(tstart, tend)
        if len(data) == 0:
            return [], []
        data = self._select_data_from_object_position(data,  minx, maxx, miny, maxy, minz, maxz, base_tf)
        if wear_flag:
            data = self._near_point_deleate(data, score_type)
        data = data.sort_values(by="ros_timestamp",ascending=False)
        N = len(data)
        obj_pos = []
        obj_id = []
        for i in range(N):
            obj_pos.append([data.position_x.values[i], data.position_y.values[i], data.position_z.values[i]])
            obj_id.append(data.specific_id_0.values[i])
        return obj_pos, obj_id


    def get_object_pos_filterd_time_and_area_and_specific_score(self, tstart, tend,  minx, maxx, miny, maxy, minz, maxz, base_tf, threshold_score, score_type=True, wear_flag=True):
        """
        指定された範囲内で発見されたものの位置とIDを返すメソッド
        Params
        -----
        tstart : rospy.time、 default rospy.Time(0)
            情報を引き出すための開始時間
        tend : rospy.time、 default rospy.Time.now()
            情報を引き出すための終了時間
        minx : float
            base_tfから見たxの最小値、base_footprint基準ではどれだけ手前かを表す(負だと背後)
        maxx : float
            base_tfから見たxの最大値、base_footprint基準ではどれだけ奥かを表す
        miny : float
            base_tfから見たyの最小値、base_footprint基準ではどれだけ右かを表す（負右正左）
        maxy : float
            base_tfから見たyの最大値、base_footprint基準ではどれだけ左かを表す（負右正左）
        minz : float
            mapから見たzの最小値、高さをあらわす
        maxz : float
            mapから見たzの最大値、高さをあらわす
        base_tf : string
            エリアの基準と成るtf
        score_type : bool
            Trueならば特定物体認識、Falseならば一般物体認識のスコアを用いる
        Returns
        -----
        obj_pos : list of float
            見つけた物体位置
        obj_id : list of int
            見つけた物体id
        """
        data = self._get_object_info_from_time(tstart, tend)
        if len(data) == 0:
            return [], []
        data = self._select_data_from_object_position(data,  minx, maxx, miny, maxy, minz, maxz, base_tf)
        if len(data) == 0:
            return [], []
        data = self._extraction_threshold_score(data, threshold_score, True)
        if wear_flag:
            data = self._near_point_deleate(data, score_type)
        N = len(data)
        obj_pos = []
        obj_id = []
        for i in range(N):
            obj_pos.append([data.position_x.values[i], data.position_y.values[i], data.position_z.values[i]])
            obj_id.append(data.specific_id_0.values[i])
        return obj_pos, obj_id

    def get_object_pos_filterd_time_and_area_and_generic_score(self, tstart, tend,  minx, maxx, miny, maxy, minz, maxz, base_tf, threshold_score, wear_flag=True):
        """
        指定された範囲内で発見されたものの位置とIDを返すメソッド
        Params
        -----
        tstart : rospy.time、 default rospy.Time(0)
            情報を引き出すための開始時間
        tend : rospy.time、 default rospy.Time.now()
            情報を引き出すための終了時間
        minx : float
            base_tfから見たxの最小値、base_footprint基準ではどれだけ手前かを表す(負だと背後)
        maxx : float
            base_tfから見たxの最大値、base_footprint基準ではどれだけ奥かを表す
        miny : float
            base_tfから見たyの最小値、base_footprint基準ではどれだけ右かを表す（負右正左）
        maxy : float
            base_tfから見たyの最大値、base_footprint基準ではどれだけ左かを表す（負右正左）
        minz : float
            mapから見たzの最小値、高さをあらわす
        maxz : float
            mapから見たzの最大値、高さをあらわす
        base_tf : string
            エリアの基準と成るtf
        score_type : bool
            Trueならば特定物体認識、Falseならば一般物体認識のスコアを用いる
        Returns
        -----
        obj_pos : list of float
            見つけた物体位置
        obj_id : list of int
            見つけた物体id
        """
        data = self._get_object_info_from_time(tstart, tend)
        if len(data) == 0:
            return [], []
        data = self._select_data_from_object_position(data,  minx, maxx, miny, maxy, minz, maxz, base_tf)
        if len(data) == 0:
            return [], []
        data = self._extraction_threshold_score(data, threshold_score, False)
        if wear_flag:
            data = self._near_point_deleate(data, False)
        N = len(data)
        obj_pos = []
        obj_id = []
        for i in range(N):
            obj_pos.append([data.position_x.values[i], data.position_y.values[i], data.position_z.values[i]])
            obj_id.append(data.generic_name_0.values[i])
        return obj_pos, obj_id

    def get_object_pos_filterd_time_and_area_and_specific_id(self, tstart, tend,  minx, maxx, miny, maxy, minz, maxz, base_tf, specific_id, threshold_score, score_type=True, wear_flag=True):
        """
        指定された範囲内で発見されたものの位置とIDを返すメソッド
        Params
        -----
        tstart : rospy.time、 default rospy.Time(0)
            情報を引き出すための開始時間
        tend : rospy.time、 default rospy.Time.now()
            情報を引き出すための終了時間
        minx : float
            base_tfから見たxの最小値、base_footprint基準ではどれだけ手前かを表す(負だと背後)
        maxx : float
            base_tfから見たxの最大値、base_footprint基準ではどれだけ奥かを表す
        miny : float
            base_tfから見たyの最小値、base_footprint基準ではどれだけ右かを表す（負右正左）
        maxy : float
            base_tfから見たyの最大値、base_footprint基準ではどれだけ左かを表す（負右正左）
        minz : float
            mapから見たzの最小値、高さをあらわす
        maxz : float
            mapから見たzの最大値、高さをあらわす
        base_tf : string
            エリアの基準と成るtf
        score_type : bool
            Trueならば特定物体認識、Falseならば一般物体認識のスコアを用いる
        Returns
        -----
        obj_pos : list of float
            見つけた物体位置
        obj_id : list of int
            見つけた物体id
        """
        data = self._get_object_info_from_time(tstart, tend)
        if len(data) == 0:
            return [], []
        data = data.loc[(data.specific_id_0 == specific_id)]
        if len(data) == 0:
            return [], []
        data = self._select_data_from_object_position(data,  minx, maxx, miny, maxy, minz, maxz, base_tf)
        if len(data) == 0:
            return [], []
        data = self._extraction_threshold_score(data, threshold_score, True)
        if wear_flag:
            data = self._near_point_deleate(data, score_type)
        N = len(data)
        obj_pos = []
        obj_id = []
        for i in range(N):
            obj_pos.append([data.position_x.values[i], data.position_y.values[i], data.position_z.values[i]])
            obj_id.append(data.specific_id_0.values[i])
        return obj_pos, obj_id


    def get_object_pos_filterd_time_and_area_and_generic_name(self, tstart, tend,  minx, maxx, miny, maxy, minz, maxz, base_tf, generic_name, threshold_score, wear_flag=True):
        """
        指定された範囲内で発見されたものの位置とIDを返すメソッド
        Params
        -----
        tstart : rospy.time、 default rospy.Time(0)
            情報を引き出すための開始時間
        tend : rospy.time、 default rospy.Time.now()
            情報を引き出すための終了時間
        minx : float
            base_tfから見たxの最小値、base_footprint基準ではどれだけ手前かを表す(負だと背後)
        maxx : float
            base_tfから見たxの最大値、base_footprint基準ではどれだけ奥かを表す
        miny : float
            base_tfから見たyの最小値、base_footprint基準ではどれだけ右かを表す（負右正左）
        maxy : float
            base_tfから見たyの最大値、base_footprint基準ではどれだけ左かを表す（負右正左）
        minz : float
            mapから見たzの最小値、高さをあらわす
        maxz : float
            mapから見たzの最大値、高さをあらわす
        base_tf : string
            エリアの基準と成るtf
        score_type : bool
            Trueならば特定物体認識、Falseならば一般物体認識のスコアを用いる
        Returns
        -----
        obj_pos : list of float
            見つけた物体位置
        obj_id : list of int
            見つけた物体id
        """
        data = self._get_object_info_from_time(tstart, tend)
        if len(data) == 0:
            return []
        data = data.loc[(data.generic_name_0 == generic_name)]
        if len(data) == 0:
            return []
        data = self._select_data_from_object_position(data,  minx, maxx, miny, maxy, minz, maxz, base_tf)
        if len(data) == 0:
            return []
        data = self._extraction_threshold_score(data, threshold_score, True)
        if wear_flag:
            data = self._near_point_deleate(data, False)
        N = len(data)
        obj_pos = []
        for i in range(N):
            obj_pos.append([data.position_x.values[i], data.position_y.values[i], data.position_z.values[i]])
        return obj_pos
        
    def get_landmark_list(self, tstart, tend):
        if type(self.df) != type(None):
            df = self.df
        else:
            df = self.db.get_objects_info_filtered_time(tstart, tend)
        df = self._extraction_time(df, tstart, tend)
        if len(df) == 0:
            return []
#        df = self._extraction_threshold_score(df, 0.1, False)
        df = self._near_point_deleate(df, True)
        if len(df) == 0:
            return []
        return df

    def divid_df(self,ts,te):
        if type(self.df) == type(None):
            self.df = self.db.get_objects_info_filtered_time(ts, te)
        self.df = self._extraction_time(self.df, ts, te)        
        
    def get_all(self):
        db_name = "hsr_db"
        host = "192.168.1.70"
        user = "administrator"
        password = "password"
        try:
            db = DataBase(db_name, host, user, password)
            self.df = db.get_objects_info()
            self.df.to_csv("data_frame.csv")
        except:
            import pandas as pd
            self.df = pd.read_csv("data_frame.csv")        
        return self.df

    def sparse_df(self,sparse):
        if type(self.df) != type(None):
            self.df = self.df[::sparse]

    def get_df_raw_data(self):
        df = self.df
        df = df.loc[(df.specific_score_0 >= 0.75)]        
        x = df.position_x.values
        y = df.position_y.values
        z = df.position_z.values
        sx = df.szwht_x.values
        sy = df.szwht_y.values
        sz = df.szwht_z.values
        ix = df.id.values
        names = df.generic_name_0.values
        times = df.ros_timestamp.values
        data = np.array([x,y,z,sx,sy,sz,ix]).T
        times = np.array(times)
        names = np.array(names)
        return data, times, np.array(ix), names
    
    def get_df_raw_data_extract_recogobj(self, extract_param, score):
        if type(extract_param)==type([]):
            print extract_param
            if len(extract_param) > 1:
                if type(extract_param[0]) == type(int(1)):
                    minp = min(extract_param)
                    maxp = max(extract_param)
                    df = self.df.loc[((self.df.specific_id_0 >= minp) & (self.df.specific_id_0 <= maxp))]
#                    df = df.loc[(df.specific_id_0 != 4)]
                elif type(extract_param[0]) == type("1"):
                    df = None
                    for i in range(len(extract_param)):
                        dfs = self.df.loc[(self.df.generic_name_0 == extract_param[i])]
                        if i == 0:
                            df = dfs
                        else:
                            df = pd.concat([df,dfs])
                    df.sort("ros_timestamp")
            elif len(extract_param) == 1:
                df = self.df.loc[(self.df.generic_id_0 == extract_param[0])]
            else:
                rospy.loginfo("bad param")
                return [], [], [], []                
        elif type(extract_param)==type("name"):
            df = self.df.loc[(self.df.generic_name_0 == extract_param)]
        else:
            rospy.loginfo("bad param")
            return [], [], [], []
        df = df.loc[(df.generic_score_0 >= score)]
        if len(df)== 0:
            rospy.loginfo("no object")
            return [], [], [], []                
                
        x = df.position_x.values
        y = df.position_y.values
        z = df.position_z.values
        sx = df.szwht_x.values
        sy = df.szwht_y.values
        sz = df.szwht_z.values
        ix = df.id.values
        names = df.generic_name_0.values
        times = df.ros_timestamp.values
        data = np.array([x,y,z,sx,sy,sz,ix]).T
        times = np.array(times/(10.**9))
        names = np.array(names)
        return data, times, np.array(ix), names



    def save(self,name):
        self.df.to_csv(name)

if __name__ == '__main__':
    rospy.init_node("vision_test")
    obj = Objects()
    while not rospy.is_shutdown():
        obj.get_object_num_from_time(10,0,-1,False)
