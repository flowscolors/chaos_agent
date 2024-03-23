# -*- coding: utf-8 -*-
"""一个用于Kubernetes集群的混沌代理，可以对指定的应用进行故障注入."""

# 导入所需的库和模块
import agentscope
from agentscope.agents import DialogAgent, UserAgent
from agentscope.message import Msg

# 定义代理使用的模型配置
model_configs = [
    {
        "model_type": "dashscope_chat",
        "config_name": "qwen1.5-72b-chat",
        "model_name": "qwen1.5-72b-chat",
        "api_key": "sk-69094d3516b149a78104652e924f6706",
        "generate_args": {
            "temperature": 0.5,
        },
        "messages_key": "input",
    },
]

# 使用提供的模型配置初始化agentscope
agentscope.init(model_configs=model_configs)

# 定义代理角色和系统提示
# def create_agent(role: str, characteristic: str) -> DialogAgent:
#     return DialogAgent(
#         name=role,
#         sys_prompt=f"对现实工程中执行混沌实验需要多团队协作，现在你正在扮演 {characteristic} {role}.现在简洁的请向用户提问注入Kubernetes集群的信息，格式如下“请输入注入Kubernetes集群的信息”",
#         model_config_name="qwen1.5-72b-chat",  # 替换为你的模型配置名称
#     )

# commander = create_agent("指挥官", "混乱工程过程的协调者")
# injector = create_agent("ChaosMonkey", "向Kubernetes集群注入故障的注入者") #需要替换成自定义的Agent 调用Chaos
# observer = create_agent("观察者", "监视Kubernetes集群的观察者")            #需要替换成自定义的Agent 调用Pro
# analyzer = create_agent("分析者", "分析故障注入和监控情况的分析者")
# summarizer = create_agent("分析者", "对混沌工程实验过程进行总结汇报")

# 创建程序所需的各个代理
commander = DialogAgent(
        name="指挥官",
        sys_prompt="对现实工程中执行混沌实验需要多团队协作，现在你正在扮演 混乱工程过程的协调者 指挥官.现在简洁的请向用户提问注入Kubernetes集群的信息，格式如下“请输入注入Kubernetes集群的信息”",
        model_config_name="qwen1.5-72b-chat",  # replace by your model config name
    )

injector = DialogAgent(
        name="ChaosMonkey",
        sys_prompt="对现实工程中执行混沌实验需要多团队协作，现在你正在扮演 向Kubernetes集群注入故障的注入者 ChaosMonkey.现在简洁的请向用户提问注入Kubernetes集群的信息，格式如下“请输入注入Kubernetes集群的信息”",
        model_config_name="qwen1.5-72b-chat",  # replace by your model config name
    )

observer = DialogAgent(
        name="观察者",
        sys_prompt="对现实工程中执行混沌实验需要多团队协作，现在你正在扮演 监视Kubernetes集群的观察者.现在简洁的请向用户提问注入Kubernetes集群的信息，格式如下“请输入注入Kubernetes集群的信息”",
        model_config_name="qwen1.5-72b-chat",  # replace by your model config name
    )

analyzer = DialogAgent(
        name="分析者",
        sys_prompt="对现实工程中执行混沌实验需要多团队协作，现在你正在扮演 分析故障注入和监控情况的分析者.现在简洁的请向用户提问注入Kubernetes集群的信息，格式如下“请输入注入Kubernetes集群的信息”",
        model_config_name="qwen1.5-72b-chat",  # replace by your model config name
    )

summarizer = DialogAgent(
        name="分析者",
        sys_prompt="对现实工程中执行混沌实验需要多团队协作，现在你正在扮演 对混沌工程实验过程进行总结汇报 分析者.现在简洁的请向用户提问注入Kubernetes集群的信息，格式如下“请输入注入Kubernetes集群的信息”",
        model_config_name="qwen1.5-72b-chat",  # replace by your model config name
    )


user_agent = UserAgent()

#代理列表
agents = [commander, injector, observer, analyzer, summarizer]


# 定义主交互循环
def main():
    # 初始化消息
    input = Msg(name="commander", content="现在简洁的请向用户提问注入Kubernetes集群的信息，格式如下“请输入注入Kubernetes集群的信息”")
    print(input.get("content"))
    while True:
        plan = commander(input)
        x = user_agent(plan)

        # 如果用户输入"exit"，则终止对话
        if x.content == "exit":
            print("Exiting the conversation.")
            break

        # 如果用户输入"yes"，则确认执行计划，进行混沌工程执行
        if x.content == "yes":
            print("ChaosMonkey Go ! ! !")
            chaos_result = injector(plan)
            prometheus_result = observer(plan)
            all_things = chaos_result.get("content") + prometheus_result.get("content")
            all_things_msg = Msg(name="analyzer", content=all_things+"bak")
            analyzer_result = analyzer(all_things_msg)
            summary = summarizer(analyzer_result)
            print(summary)


if __name__ == "__main__":
    main()