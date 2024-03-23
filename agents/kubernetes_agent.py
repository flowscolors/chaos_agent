from agentscope.agents import AgentBase
from agentscope.message import Msg
from typing import Optional
from agentscope.prompt import PromptEngine, PromptType

from ChaosPlan import ChaosPlan
from tools import create_chaos_cr


class KubernetesAgent(AgentBase):
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
        # 处理用户的输入，执行chaosPlan的故障注入方法
        chaos_plan: ChaosPlan = x.get("chaosPlan")
        print(chaos_plan)
        print(chaos_plan.chaosblade_resource)
        result = create_chaos_cr(chaos_plan.k8s_api_url, chaos_plan.k8s_token, chaos_plan.chaosblade_resource)
        print(result)

        # 输入程序执行的命令与结果，
        prompt = self.engine.join(
            self.sys_prompt,
            x["content"],
            f"根据以下信息 Kubernetes集群入口：{chaos_plan.k8s_api_url}\nchaosblade cr：{chaos_plan.chaosblade_resource}\n创建结果：{result}\n",
            "作为ChaosMonkey，先描述Kubernetes集群入口、chaosblade内容和创建结果，并分析查询结果分析混沌注入执行情况"
        )
        print(prompt)

        response = self.model(prompt).text
        print(response)

        # 格式化输出LLM接口调用结果
        msg = Msg(self.name, response)
        return msg
