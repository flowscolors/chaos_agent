import re
import uuid
from kubernetes import client, config

class ChaosPlan:
    k8s_api_url = ''
    k8s_token = ''
    prometheus_url = ''
    chaos_type = ''
    namespace_name = ''
    app_name = ''
    node_name = ''
    pod_name = ''
    chaosblade_resource = ''
    prometheus_query = ''

    def __init__(self, k8s_api_url, k8s_token, prometheus_url):
        self.k8s_api_url = str(k8s_api_url)
        self.k8s_token = str(k8s_token)
        self.prometheus_url = str(prometheus_url)

    def extract_fields_from_text(self, text):
        # 使用正则表达式从文本中提取字段值
        chaos_type_pattern = r"故障类型:\s*([\w-]+)"
        namespace_name_pattern = r"租户名称:\s*([\w-]+)"
        app_name_pattern = r"应用名称:\s*([\w-]+)"
        node_name_pattern = r"Node名称:\s*([\w-]+)"


        # 提取 chaos_type
        chaos_type_match = re.search(chaos_type_pattern, text)
        namespace_name_match = re.search(namespace_name_pattern, text)
        app_name_match = re.search(app_name_pattern, text)
        node_name_match = re.search(node_name_pattern, text)


        self.chaos_type = chaos_type_match.group(1) if chaos_type_match else None
        self.namespace_name = namespace_name_match.group(1) if namespace_name_match else None
        self.app_name = app_name_match.group(1) if app_name_match else None
        self.node_name = node_name_match.group(1) if node_name_match else None


    def generate_pod_name(self):
        if self.k8s_api_url != '':
            # 设置 Kubernetes 连接配置
            configuration = client.Configuration()
            configuration.host = self.k8s_api_url
            configuration.verify_ssl = False
            configuration.debug = False
            configuration.api_key['authorization'] = f'Bearer {self.k8s_token}'
            client.Configuration.set_default(configuration)

            # 创建 Kubernetes API 实例
            v1 = client.CoreV1Api()
            pod_list = v1.list_namespaced_pod(
                namespace=self.namespace_name,
                label_selector=f"app={self.app_name}"
            )
            if len(pod_list.items) > 0:
                self.pod_name = pod_list.items[0].metadata.name
            else:
                self.pod_name = None


    def generate_chaosblade_resource(self):
        # 生成一个唯一标识符 (UID)
        uid = str(uuid.uuid4())[:8]
            # 根据故障类型、Pod名称和节点名称生成ChaosBlade资源
        if self.chaos_type == "Pod-Reboot":
            self.chaosblade_resource = f"""
    apiVersion: chaosblade.io/v1alpha1
    kind: ChaosBlade
    metadata:
      name: pod-reboot-experiment-{uid}
    spec:
      experiments:
      - scope: pod
        target: pod
        action: delete
        desc: "Reboot pod {self.pod_name} in {self.namespace_name} namespace"
        matchers:
        - name: namespaces
          value:
          - {self.namespace_name}
        - name: names
          value:
          - {self.pod_name}
    """
        elif self.chaos_type == "Pod-CPU-Load":
            self.chaosblade_resource = f"""
    apiVersion: chaosblade.io/v1alpha1
    kind: ChaosBlade
    metadata:
      name: pod-cpu-load-experiment-{uid}
    spec:
      experiments:
      - scope: pod
        target: cpu
        action: fullload
        desc: "Increase CPU load on pod {self.pod_name} in {self.namespace_name} namespace"
        matchers:
        - name: names
          value:
          - {self.pod_name}
        - name: cpu-percent
          value:
          - "80"
    """
        elif self.chaos_type == "Node-CPU-Load":
            self.chaosblade_resource = f"""
    apiVersion: chaosblade.io/v1alpha1
    kind: ChaosBlade
    metadata:
      name: node-cpu-load-experiment-{uid}
    spec:
      experiments:
      - scope: node
        target: cpu
        action: fullload
        desc: "Increase CPU load on node {self.node_name}"
        matchers:
        - name: names
          value:
          - {self.node_name}
        - name: cpu-percent
          value:
          - "50"
    """
        else:
            self.chaosblade_resource = None

    def generate_prometheus_query(self):
        # 根据故障类型、Pod名称和节点名称生成Prometheus查询语句
        if self.chaos_type == "Pod-Reboot":
            self.prometheus_query = f'kube_pod_container_status_restarts_total{{pod="{self.pod_name}",namespace="{self.namespace_name}"}}'
        elif self.chaos_type == "Pod-CPU-Load":
            self.prometheus_query = f'sum(node_namespace_pod_container:container_cpu_usage_seconds_total:sum_irate{{pod="{self.pod_name}",namespace="{self.namespace_name}"}}) by (container)'
        elif self.chaos_type == "Node-CPU-Load":
            self.prometheus_query = f'sum(rate(node_cpu_seconds_total{{mode!="idle",instance=~"{self.node_name}:.*"}}[1m]))'
        else:
            self.prometheus_query = None

    def format_output(self):
        # 将ChaosPlan的字段内容格式化输出
        output = f"""
故障类型: {self.chaos_type}
租户名称: {self.namespace_name}
应用名称: {self.app_name}
节点名称: {self.node_name}
Pod名称: {self.pod_name}
ChaosBlade资源:
{self.chaosblade_resource}
Prometheus查询语句: {self.prometheus_query}
"""
        return output