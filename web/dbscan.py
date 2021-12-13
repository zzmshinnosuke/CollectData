## 输入userdata，plt格式
## 输出聚类地图，异常指数
## 方法：将所有被聚类的点视为一个集合，统计经纬度的最小值和最大值，从而圈定一个活动范围，统计超出此活动范围的采样点数，并除以总数作为异常指数

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
import gmplot
from sklearn.cluster import DBSCAN
from sklearn import metrics
from shapely.geometry import MultiPoint
from geopy.distance import great_circle

# 进行DBScan聚类
def operate_dbscan(df_min):
    #print("df_min:",df_min)
    coords = df_min.as_matrix(columns=['lat', 'lng']) # 用（经度，纬度）表示GPS点
    kms_per_radian = 6371.0088
    epsilon = 0.5 / kms_per_radian # 定义DBScan的半径
    # print(df_min)
    # print(coords)
    db = DBSCAN(eps=epsilon, min_samples=50, algorithm='ball_tree', metric='haversine').fit(np.radians(coords))
    cluster_labels = db.labels_

    num_clusters = len(set(cluster_labels) - set([-1]))
    # print('将 ' + str(len(df_min)) + '个点分为' + str(num_clusters) + '类')

    clusters = pd.Series([coords[cluster_labels == n] for n in range(num_clusters)])
    return clusters, num_clusters

# 获取类中心点
def get_centermost_point(cluster):
    centroid = (MultiPoint(cluster).centroid.x, MultiPoint(cluster).centroid.y)
    centermost_point = min(cluster, key=lambda point: great_circle(point, centroid).m)
    return tuple(centermost_point)

# 绘制轨迹和聚类
def plot_trace(df_min, rep_points, num_clusters):
    fig, ax = plt.subplots(figsize=[10, 6])
    rs_scatter = ax.scatter(rep_points['lon'][0], rep_points['lat'][0], c='#99cc99', edgecolor='None', alpha=0.7, s=450)
    ax.scatter(rep_points['lon'][1], rep_points['lat'][1], c='#99cc99', edgecolor='None', alpha=0.7, s=250)
    ax.scatter(rep_points['lon'][2], rep_points['lat'][2], c='#99cc99', edgecolor='None', alpha=0.7, s=250)
    ax.scatter(rep_points['lon'][3], rep_points['lat'][3], c='#99cc99', edgecolor='None', alpha=0.7, s=150)
    df_scatter = ax.scatter(df_min['lng'], df_min['lat'], c='k', alpha=0.9, s=3)
    ax.set_title('Full GPS trace vs. DBSCAN clusters')
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.legend([df_scatter, rs_scatter], ['GPS points', 'Cluster centers'], loc='upper right')
    labels = ['cluster{0}'.format(i) for i in range(1, num_clusters+1)]
    for label, x, y in zip(labels, rep_points['lon'], rep_points['lat']):
        plt.annotate(
            label,
            xy = (x, y), xytext = (-25, -30),
            textcoords = 'offset points', ha = 'right', va = 'bottom',
            bbox = dict(boxstyle = 'round,pad=0.5', fc = 'white', alpha = 0.5),
            arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0'))

    plt.show()

# 保存googleMap
def save_gmap(df_min, rep_points, output_html):
    gmap = gmplot.GoogleMapPlotter(rep_points['lat'][0], rep_points['lon'][0], 11)
    gmap.plot(df_min.lat, df_min.lng)
    gmap.heatmap(rep_points['lat'][:4], rep_points['lon'][:4], radius=20)
    gmap.draw(output_html)

# 统计聚类点停留时间
def hour_plot(df_min, num_clusters, clusters):
    M = []
    def myfunc(row):
        t = df_min[(df_min['lat']==row[0]) & (df_min['lng']==row[1])]['time'].iloc[0]
        return t[:t.index(':')]
    for i in range(num_clusters):
        hours = np.apply_along_axis(myfunc, 1, clusters[i]).tolist()
        M.append(list(map(int, hours)))
    f, axarr = plt.subplots(num_clusters, sharex=True, figsize=(6,10))
    for i in range(num_clusters):
        # print(i)
        axarr[i].hist(M[i])
    axarr[num_clusters-1].set_xlabel("Hours of a day")
    plt.xticks(np.arange(0, 25, 2.0))
    f.text(0.04, 0.5, '# of GPS points', va='center', rotation='vertical')
    plt.show()

# 计算异常指数
def compute_anomaly(df_min, clusters, num_clusters, test_lat, test_lng):
    max_lng = 0
    max_lat = 0
    min_lng = 1000
    min_lat = 1000
    for i in range(num_clusters):
        max_lng = np.max(clusters[i][:, 0]) if np.max(clusters[i][:, 0]) > max_lng else max_lng
        min_lng = np.min(clusters[i][:, 0]) if np.min(clusters[i][:, 0]) < min_lng else min_lng
        max_lat = np.max(clusters[i][:, 1]) if np.max(clusters[i][:, 1]) > max_lat else max_lat
        min_lat = np.min(clusters[i][:, 1]) if np.min(clusters[i][:, 1]) < min_lat else min_lat
        # print(max_lng, max_lat, min_lng, min_lat)
    count = 0
    df_min = df_min.as_matrix(columns=['lat', 'lng'])
    for i in range(len(test_lat)):
        if test_lat[i]<min_lng or test_lat[i]>max_lng or test_lng[i]<min_lat or test_lng[i]>max_lat:
            count += 1
    anomaly = 100*(count/len(test_lat))
    # print(count, "{:.2f}".format(anomaly))
    return anomaly

def gps_anomaly(lat, lng, test_lat, test_lng):

    data = {'lat':lat, 'lng': lng}
    df_min = pd.DataFrame(data)
    clusters, num_clusters = operate_dbscan(df_min)
    centermost_points = clusters.map(get_centermost_point)
    lats, lons = zip(*centermost_points)
    rep_points = pd.DataFrame({'lon':lons, 'lat':lats})
    # plot_trace(df_min, rep_points, num_clusters)
    # output_html = str(id)+'map.html'
    # save_gmap(df_min, rep_points, output_html)
    anomaly = compute_anomaly(df_min, clusters, num_clusters, test_lat, test_lng)
    return anomaly
