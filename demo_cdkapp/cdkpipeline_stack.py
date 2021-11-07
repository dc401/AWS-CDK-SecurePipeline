#!/usr/env/python 3
from demo_cdkapp.cdkpipeline_stage import CdkPipelineStage
from aws_cdk import (
    core,
    aws_codecommit as codecommit,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    pipelines,
    aws_codegurureviewer as reviewer
)

class CdkPipelineStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        '''
        high level construct of cdk pipelines that self mutate
        create a repo to place code via codecommit
        1. First run a cdk bootstrap --cloudformation-execution-policies arn:aws:iam::aws:policy/AdministratorAccess
        2. Then do a cdk deploy to build out the codecommit, pipeline, codeguru
        3. Do a git commit push which will send a copy of stackset to codecommit through the pipeline to self mutate
        '''
        
        #create a repo to store our code that the pipeline pulls from
        demo_repo = codecommit.Repository(self, 'DemoCICDPipelineRepo', repository_name= 'demo_cicid_pipeline_repo')

        #The pipeline will then wrap around the original cdk iac stack
        #create codepipeline artifact to hold source code from code commit repo
        sourcecode_artifact = codepipeline.Artifact()
        
        #create codepipline artifact taht will hold the cloudformation synth assembly
        cloud_asm_artifact = codepipeline.Artifact()
        
        #pipeline init construct
        cdkapps_pipeline = pipelines.CdkPipeline(self, 'CdkAppsPipeline',
        pipeline_name= 'CdkAppsPipeline',
        cloud_assembly_artifact= cloud_asm_artifact,
        source_action= codepipeline_actions.CodeCommitSourceAction(
            action_name= 'CodeCommit',
            output= sourcecode_artifact,
            repository= demo_repo
        ),

        synth_action= pipelines.SimpleSynthAction.standard_npm_synth(
            source_artifact= sourcecode_artifact,
            cloud_assembly_artifact= cloud_asm_artifact,
            install_command= 'npm install -g aws-cdk@1.84.0 && python -m pip install -r "requirements.txt" && pip3 install bridgecrew && pip3 install bandit',
            #skipping checks for s3 artifact bucket false positives
            build_command= 'cdk synth && bridgecrew -f cdk.out/CdkPipelineStack.template.json --skip-check CKV_AWS_7,CKV_AWS_18,CKV_AWS_21 && bandit -r lambda/'
            )
        )

        #add codeguru reviewer so that dev can inspect issues before approvals
        codeguru_reviewer = reviewer.CfnRepositoryAssociation(
            self, 'CodeGuruReviewerInst',
            name= 'demo_cicid_pipeline_repo',
            type= 'CodeCommit'
        )
        #create deployment stage cdkpipeline_stage.py and push through the pipeline
        #also require human approval after review 
        deploy = CdkPipelineStage(self, 'deploy')
        cdkapps_pipeline.add_application_stage(deploy, manual_approvals=True)
        '''
        Accidental pipeline stack modification with insecure practices
        uncomment this code from the project to ensure it does not flag in the CF template
        bridgecrew rule: CKV_AWS_27 Ensure all data stored in the SQS queue is encrypted
        '''
        '''
        from aws_cdk import aws_sqs as sqs
        insecurequeue = sqs.Queue(
            self, 'insecurequeue',
            encryption=sqs.QueueEncryption.UNENCRYPTED
            )
        '''