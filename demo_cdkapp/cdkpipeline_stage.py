#!/usr/env/python 3
from aws_cdk import core
from demo_cdkapp.demo_cdkapp_stack import DemoCdkappStack

class CdkPipelineStage(core.Stage):

    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        service = DemoCdkappStack(self, 'DeploymentLambda')