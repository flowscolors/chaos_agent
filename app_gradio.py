import os
import random
import hashlib
from PIL import Image
import gradio as gr
from gradio.components import Chatbot
import agentscope
from ChaosPlan import ChaosPlan
from agentscope.agents import DialogAgent
from agentscope.agents.user_agent import UserAgent
from agentscope.message import Msg

from agents.kubernetes_agent import KubernetesAgent
from agents.prometheus_agent import PrometheusAgent
from tools import *


def generate_image_from_name(name):
    hash_func = hashlib.md5()
    hash_func.update(name.encode('utf-8'))
    hash_value = hash_func.hexdigest()

    color_hex = '#' + hash_value[:6]
    color_rgb = Image.new('RGB', (1, 1), color_hex).getpixel((0, 0))

    image_filepath = f"./images/{name}_image.png"
    if os.path.exists(image_filepath):
        print(f"Image already exists at {image_filepath}")
        return image_filepath

    width, height = 200, 200
    image = Image.new('RGB', (width, height), color_rgb)
    image.save(image_filepath)
    return image_filepath


def format_cover_html():
    image_src = '//images.squarespace-cdn.com/content/v1/59fa11d312abd9aa31ecb788/1510605148101-A0XH8MG659FZ0LQ22ESX/ChaosMonkey_Logo.png'
    return f"""
<div class="bot_cover">
    <div class="bot_avatar">
        <img src={image_src} />
    </div>
    <div class="bot_name">{"ChaosAgent"}</div>
    <div class="bot_desp">{"基于AgentScope框架的混沌工程实验应用 Powered by AgentScope"}</div>
</div>
"""


# agents = agentscope.init(
#     model_configs="./model_configs.json",
#     agent_configs="./agent_configs_chaos.json",
# )
# commander_agent = agents[0]
# monkey_agent = agents[1]
# observer_agent = agents[2]
# analyzer_agent = agents[3]
# summarizer_agent = agents[4]
# 定义代理使用的模型配置
model_configs = [
    {
        "model_type": "dashscope_chat",
        "config_name": "qwen1.5-72b-chat",
        "model_name": "qwen1.5-72b-chat",
        "api_key": os.environ.get("DASHSCOPE_API_KEY"),
        "generate_args": {
            "temperature": 0.5,
        },
        "messages_key": "input",
    },
]

# 使用提供的模型配置初始化agentscope
agentscope.init(model_configs=model_configs)

# 创建程序所需的各个代理
commander_agent = DialogAgent(
        name="commander",
        sys_prompt="对现实工程中执行混沌实验需要多团队协作,现在你正在扮演混乱工程过程的协调者指挥官。你的任务是制定混沌实验计划,协调其他团队成员(ChaosMonkey、Observer、Analyzer)的工作,确保实验顺利进行。你可以利用提供的Kubernetes集群信息和Prometheus监控信息,对实验过程进行监督和调整。现在,请根据用户的输入,给出下一步的实验计划和指令。",
        model_config_name="qwen1.5-72b-chat",  # replace by your model config name
    )

monkey_agent = KubernetesAgent(
        name="ChaosMonkey",
        sys_prompt="对现实工程中执行混沌实验需要多团队协作,现在你正在扮演向Kubernetes集群注入故障的注入者ChaosMonkey。你的任务是根据指挥官制定的实验计划,使用提供的Kubernetes集群信息,通过创建ChaosBladeOperator的自定义资源(CR)来模拟各种故障场景,比如Pod故障、网络延迟、资源占用等。在故障注入后,请向Observer和Analyzer报告注入的故障类型和影响范围。现在,请根据指挥官的指令,执行故障注入操作。",
        model_config_name="qwen1.5-72b-chat",  # replace by your model config name
    )

observer_agent = PrometheusAgent(
        name="observer",
        sys_prompt="对现实工程中执行混沌实验需要多团队协作,现在你正在扮演监视Kubernetes集群的观察者。你的任务是利用提供的Prometheus监控信息,实时查询和分析集群的各项指标,包括Pod状态、资源使用情况、网络性能等。当发现异常情况时,请立即向Analyzer报告,并提供相关的监控数据和图表。同时,请随时向指挥官汇报集群的整体运行状态。现在,请根据指挥官的要求,开始监视集群。",
        model_config_name="qwen1.5-72b-chat",  # replace by your model config name
    )

analyzer_agent = DialogAgent(
        name="analyzer",
        sys_prompt="对现实工程中执行混沌实验需要多团队协作,现在你正在扮演分析故障注入和监控情况的分析者。你的任务是综合ChaosMonkey报告的故障注入情况和Observer提供的监控数据,分析故障对系统的影响,评估系统的稳定性和恢复能力。你需要识别潜在的风险和改进点,并向指挥官提出优化建议。同时,请与Summarizer协作,总结实验过程和结果。现在,请根据当前的故障注入和监控情况,开始进行分析。",
        model_config_name="qwen1.5-72b-chat",  # replace by your model config name
    )

summarizer_agent = DialogAgent(
        name="summarizer",
        sys_prompt="对现实工程中执行混沌实验需要多团队协作,现在你正在扮演对混沌工程实验过程进行总结汇报的总结者。你的任务是在实验完成后,与Analyzer协作,汇总实验过程中的关键事件、监控数据、分析结果和优化建议,形成一份完整的混沌实验报告。报告需要包括实验目的、实验场景、故障注入和影响范围、系统响应和恢复情况、识别出的风险和改进措施等内容。现在,请根据Analyzer提供的信息,开始撰写实验总结报告。",
        model_config_name="qwen1.5-72b-chat",  # replace by your model config name
    )



user_agent = UserAgent()

commander_avatar = generate_image_from_name(commander_agent.name)
monkey_avatar = generate_image_from_name(monkey_agent.name)
observer_avatar = generate_image_from_name(observer_agent.name)
analyzer_avatar = generate_image_from_name(analyzer_agent.name)
summarizer_avatar = generate_image_from_name(summarizer_agent.name)
user_avatar = generate_image_from_name('user')

chaos_types = {
    "Pod-Reboot": "Pod 重启",
    "Pod-CPU-Load": "Pod CPU飙升",
    "Node-CPU-Load": "Node CPU飙升"
}
def init_user(state):
    user_agent = UserAgent()
    state['user_agent'] = user_agent
    return state


customTheme = gr.themes.Default(primary_hue=gr.themes.utils.colors.blue, radius_size=gr.themes.utils.sizes.radius_none)

demo = gr.Blocks(css='assets/appBot.css', theme=customTheme)
with demo:
    state = gr.State({'session_seed': random.randint(0, 1000000000), 'k8s_api_url': '', 'k8s_token': '', 'prometheus_url': ''})
    with gr.Row(elem_classes='container'):
        with gr.Column(scale=4):
            with gr.Column():
                # 在此处设置谈话规则，提示用户该如何交互
                user_chatbot = Chatbot(
                    value=[[None, '欢迎使用ChaosAgent！我是指挥者，将协调整个混沌实验流程。请输入提示来让我帮你设计混沌实验，请输入"开始"来启动实验。']],
                    elem_id='user_chatbot',
                    elem_classes=['markdown-body'],
                    avatar_images=[user_avatar, commander_avatar],
                    height=600,
                    latex_delimiters=[],
                    show_label=False)
            with gr.Row():
                with gr.Column(scale=12):
                    chat_input = gr.Textbox(
                        show_label=False,
                        container=False,
                        placeholder='请输入指令...')
                with gr.Column(min_width=70, scale=1):
                    send_button = gr.Button('发送', variant='primary')

        with gr.Column(scale=1):
            user_chat_bot_cover = gr.HTML(format_cover_html())
            with gr.Accordion("环境设置", open=False):
                with gr.Row():
                    with gr.Column(scale=3):
                        k8s_api_url = gr.Textbox(label="Kubernetes API 地址")
                    with gr.Column(scale=3):
                        k8s_token = gr.Textbox(label="Kubernetes Token")
                    with gr.Column(scale=3):
                        prometheus_url = gr.Textbox(label="Prometheus 地址")
                with gr.Row():
                    with gr.Column(scale=1):
                        reset_button = gr.Button("Reset", variant='secondary', elem_classes=['red-button'])
                    with gr.Column(scale=1):
                        confirm_button = gr.Button("确定")
            with gr.Accordion("Example Prompts", open=True):
                prompt1 = gr.Button('帮我对default租户下的app应用进行一次Pod 重启的混沌实验')
                prompt2 = gr.Button('帮我对default租户下的nginx应用进行一次Pod CPU飙升的混沌实验')
                prompt3 = gr.Button('帮我对计算节点node-1进行一次Node CPU飙升的混沌实验')


    def save_settings(k8s_api_url, k8s_token, prometheus_url, state):
        state['k8s_api_url'] = k8s_api_url
        state['k8s_token'] = k8s_token
        state['prometheus_url'] = prometheus_url
        # 检查Kubernetes、Prometheus联通性
        k8s_connected, prometheus_connected = check_connectivity(k8s_api_url, k8s_token, prometheus_url)
        if k8s_connected and prometheus_connected:
            # 连接成功，显示绿色弹出框
            gr.Info("Kubernetes 和 Prometheus配置已保存，连接成功！")
        else:
            # 连接失败，显示红色弹出框
            gr.Warning("配置保存失败，请检查 Kubernetes 和 Prometheus 地址的正确性。")
        return state


    def reset_settings(state):
        state['k8s_api_url'] = ''
        state['k8s_token'] = ''
        state['prometheus_url'] = ''
        gr.Info("Kubernetes 和 Prometheus配置清理成功！")
        return state, '', '', ''


    confirm_button.click(save_settings, inputs=[k8s_api_url, k8s_token, prometheus_url, state], outputs=[state])
    reset_button.click(reset_settings, inputs=[state], outputs=[state, k8s_api_url, k8s_token, prometheus_url])


    def send_message(chatbot, input, _state):
        # 用户输入文本
        chatbot.append((input, None))
        yield {
            user_chatbot: chatbot,
            chat_input: '',
        }

        # 当用户输入开始时,检查是否已经生成了chaosPlan
        if input == '开始':
            if 'chaos_plan' not in _state or _state['chaos_plan'] is None:
                # 如果没有chaosPlan,提示用户先生成混沌计划
                chatbot.append((None, "请先根据提示生成混沌计划,然后再输入'开始'进行混沌实验。"))
                yield {
                    user_chatbot: chatbot,
                    chat_input: '',
                }
            else:
                # 如果已经生成了chaosPlan,则直接使用之前生成的chaosPlan进行后续操作
                chaos_plan = _state['chaos_plan']
                # 提示开始执行chaosPlan混沌计划
                msg = Msg(name="system", content="开始混沌实验,请Chaos Monkey对Kubernetes集群进行故障注入。", chaosPlan=chaos_plan)
                chatbot.append((None, msg.content))
                yield {
                    user_chatbot: chatbot,
                    chat_input: '',
                }

                # 调用Chaos Monkey Agent,并添加Chaos Monkey的回复到聊天框
                monkey_msg = monkey_agent(msg)
                chatbot.append((None, f"Chaos Monkey: {monkey_msg.content}"))
                yield {
                    user_chatbot: chatbot,
                    chat_input: '',
                }

                # 调用observer_agent,并添加回复到聊天框
                observer_msg = Msg(name='observer',
                                   content=f'请观察者通过Kubernetes API Server和监控系统获取相关数据,Chaos Monkey的行为是：{monkey_msg.content}',
                                   chaosPlan=chaos_plan)
                observer_result = observer_agent(observer_msg)
                chatbot.append((None, f"观察者: {observer_result.content}"))
                yield {
                    user_chatbot: chatbot,
                    chat_input: '',
                }

                # 调用analyzer_agent,并添加回复到聊天框
                analyzer_msg = Msg(name='analyzer',
                                   content=f'根据观察者提供的数据：{observer_result.content},请分析并生成故障报告。')
                analyzer_result = analyzer_agent(analyzer_msg)
                chatbot.append((None, f"分析者: {analyzer_result.content}"))
                yield {
                    user_chatbot: chatbot,
                    chat_input: '',
                }

                # summarizer_agent,并添加回复到聊天框
                summarizer_msg = Msg(name='summarizer',
                                     content=f'根据Chaos Monkey的行为：{monkey_msg.content},观察者的数据：{observer_result.content},以及分析者的报告：{analyzer_result.content},请总结此次混沌实验并生成最终报告。')
                summarizer_result = summarizer_agent(summarizer_msg)
                chatbot.append((None, f"总结者: {summarizer_result.content}"))
                yield {
                    user_chatbot: chatbot,
                    chat_input: '',
                }

                # 添加最终实验完成消息到聊天框
                chatbot.append((None, "混沌实验完成,感谢您的使用！"))
                yield {
                    user_chatbot: chatbot,
                    chat_input: '',
                }
        else:
            # commander_agent根据用户输入prompts,生成chaosPlan混沌计划,返回Msg
            msg = Msg(name="system",
                      content=f"请根据用户的输入,给出下一步的实验计划和指令。在你的输出中,请包含以下格式化的字段:故障类型: <string>、租户名称: <string>、应用名称: <string>、Node名称: <string> 、chaoslade_cr: <string> 、prometheus_query <string>.请确保你的输出包含这些字段,没有找到的值默认为null,故障类型仅有下面三种: 'Pod-Reboot': 'Pod 重启'、'Pod-CPU-Load': 'Pod CPU飙升'、 'Node-CPU-Load': 'Node CPU飙升'。现在,请根据用户的输入,给出下一步的实验计划和指令: " + input)
            plan = commander_agent(msg)

            # 创建ChaosPlan对象,根据Commander Agent的返回提取字段值
            chaos_plan = ChaosPlan(_state['k8s_api_url'], _state['k8s_token'], _state['prometheus_url'])
            chaos_plan.extract_fields_from_text(plan.get("content"))
            _state['chaos_plan'] = chaos_plan  # 将chaosPlan存储到state中

            print(chaos_plan.chaos_type)  # 输出: Pod-Reboot
            print(chaos_plan.namespace_name)  # 输出: default
            print(chaos_plan.app_name)  # 输出: app
            print(chaos_plan.node_name)  # 输出: None

            chaos_plan.generate_pod_name()
            chaos_plan.generate_chaosblade_resource()
            chaos_plan.generate_prometheus_query()
            chatbot.append((None, chaos_plan.format_output()))

            yield {
                user_chatbot: chatbot,
                chat_input: '',
            }


    def set_prompt(prompt):
        return gr.update(value=prompt)

    prompt1.click(set_prompt, inputs=[prompt1], outputs=[chat_input])
    prompt2.click(set_prompt, inputs=[prompt2], outputs=[chat_input])
    prompt3.click(set_prompt, inputs=[prompt3], outputs=[chat_input])

    send_button.click(
        send_message,
        inputs=[user_chatbot, chat_input, state],
        outputs=[user_chatbot, chat_input])

    demo.load(init_user, inputs=[state], outputs=[state])

demo.queue()
demo.launch(share=True)