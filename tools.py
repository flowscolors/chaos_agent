# -*- coding: utf-8 -*-
"""some utils of chaos_agent"""
import re
import requests
from kubernetes import client
import yaml



# 检查Kubernetes、Prometheus联通性
def check_connectivity(k8s_api_url, k8s_token, prometheus_url):
    try:
        # 设置 Kubernetes 连接配置
        configuration = client.Configuration()
        #configuration.host = "https://"+k8s_api_url
        configuration.host = k8s_api_url
        configuration.verify_ssl = False
        configuration.debug = False
        configuration.api_key['authorization'] = f'Bearer {k8s_token}'
        client.Configuration.set_default(configuration)

        # 创建 Kubernetes API 实例
        v1 = client.CoreV1Api()
        ret = v1.list_namespaced_pod("kube-system")
        if len(ret.items) > 0:
            k8s_connected = True
        else:
            k8s_connected = False

        # 检测 Prometheus 地址的联通性
        # response = requests.get("http://"+prometheus_url, timeout=5)
        response = requests.get(prometheus_url, timeout=5)
        if response.status_code == 200:
            prometheus_connected = True
        else:
            prometheus_connected = False

        return k8s_connected, prometheus_connected

    except requests.exceptions.RequestException:
        return False, False


# 创建混沌故障的 CR 方法
def create_chaos_cr(k8s_api_url, k8s_token, chaosblade_resource):
    try:
        # 设置 Kubernetes 连接配置
        configuration = client.Configuration()
        configuration.host = k8s_api_url
        configuration.verify_ssl = False
        configuration.debug = False
        configuration.api_key['authorization'] = f'Bearer {k8s_token}'
        client.Configuration.set_default(configuration)

        # 创建 Kubernetes API 实例
        api_instance = client.CustomObjectsApi()

        # 解析 YAML 格式的 ChaosBlade 资源
        chaos_blade = yaml.safe_load(chaosblade_resource)

        # 创建 ChaosBlade 资源
        api_response = api_instance.create_cluster_custom_object(
            group="chaosblade.io",
            version="v1alpha1",
            plural="chaosblades",
            body=chaos_blade,
        )

        return str(api_response)

    except client.rest.ApiException as e:
        print("Exception when calling CustomObjectsApi->create_cluster_custom_object: %s\n" % e)
        return None

# Prometheus Query 查询方法
def query_prometheus(prometheus_url, prometheus_query):
    try:
        # 构建 Prometheus 查询 URL
        query_url = f"{prometheus_url}/api/v1/query"

        # 设置查询参数
        params = {"query": prometheus_query}

        # 发送 GET 请求到 Prometheus 查询接口
        response = requests.get(query_url, params=params)

        # 检查响应状态码
        if response.status_code == 200:
            result = response.json()
            return str(result)
        else:
            print(f"Prometheus query failed with status code: {response.status_code}")
            return None

    except requests.exceptions.RequestException as e:
        print("Exception when sending request to Prometheus: %s\n" % e)
        return None

# 删除混沌故障的 CR 方法
def delete_chaos_cr(k8s_api_url, k8s_token, chaosblade_resource):
    try:
        # 设置 Kubernetes 连接配置
        configuration = client.Configuration()
        configuration.host = k8s_api_url
        configuration.verify_ssl = False
        configuration.debug = False
        configuration.api_key['authorization'] = f'Bearer {k8s_token}'
        client.Configuration.set_default(configuration)

        # 创建 Kubernetes API 实例
        api_instance = client.CustomObjectsApi()

        # 解析 YAML 格式的 ChaosBlade 资源
        chaos_blade = yaml.safe_load(chaosblade_resource)

        chaos_blade_name = chaos_blade['metadata']['name']

        # 删除 ChaosBlade 资源
        api_response = api_instance.delete_cluster_custom_object(
            group="chaosblade.io",
            version="v1alpha1",
            plural="chaosblades",
            name=chaos_blade_name,
        )

        return str(api_response)

    except client.rest.ApiException as e:
        print("Exception when calling CustomObjectsApi->delete_cluster_custom_object: %s\n" % e)
        return None