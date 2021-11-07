#!/usr/env/python 3
from aws_cdk import (
    core,
    aws_lambda as _lambda,
    aws_sqs as sqs
)
class DemoCdkappStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        #this is the infrastructure as code or other app components deloyed through pipeline
        #define lambda file that will be used to deploy through pipeline as a staged asset
        app_lambda = _lambda.Function(
            self, 'helloworldHandler',
            runtime = _lambda.Runtime.PYTHON_3_8,
            #asset pulls from adjacent folder under ./lambda/helloworld.py
            code = _lambda.Code.asset('lambda'),
            handler = 'helloworld.handler'
        )