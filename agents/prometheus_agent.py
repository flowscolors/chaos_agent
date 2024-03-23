import time

from agentscope.agents import AgentBase
from agentscope.message import Msg
from typing import Optional
from agentscope.prompt import PromptEngine, PromptType
from ChaosPlan import ChaosPlan
from tools import query_prometheus


class PrometheusAgent(AgentBase):
    def __init__(
            self,
            name: str,
            sys_prompt: Optional[str] = None,
            model_config_name: str = None,
            use_memory: bool = True,
            memory_config: Optional[dict] = None,
            prompt_type: Optional[PromptType] = PromptType.LIST,
    ) -> None:
        super().__init__(
            name=name,
            sys_prompt=sys_prompt,
            model_config_name=model_config_name,
            use_memory=use_memory,
            memory_config=memory_config,
        )

        # init prompt engine
        self.engine = PromptEngine(self.model, prompt_type=prompt_type)

    def reply(self, x: dict = None) -> dict:
        # 处理用户的输入，执行chaosPlan的Prometheus Query
        chaos_plan: ChaosPlan = x.get("chaosPlan")
        print(chaos_plan)
        print(chaos_plan.prometheus_query)

        # 添加10秒延迟
        print("等待10秒钟...")
        time.sleep(70)
        print("延迟结束,开始查询Prometheus")

        result = query_prometheus(chaos_plan.prometheus_url, chaos_plan.prometheus_query)
        print(result)

        # 输入程序执行的命令与结果，
        prompt = self.engine.join(
            self.sys_prompt,
            x["content"],
            f"根据以下信息 查询入口：{chaos_plan.prometheus_url}\n查询语句：{chaos_plan.prometheus_query}\n查询结果：{result}\n",
            "作为观察者，先描述Prometheus查询入口、查询语句和查询结果，并分析查询结果，"
        )
        print(prompt)

        response = self.model(prompt).text
        print(response)

        # 格式化输出LLM接口调用结果
        msg = Msg(self.name, response)
        return msg
