# lambda-amis-autoscaling-to-be-deleted

AWS lambda function

# author

Tomer Tcherniak

# info

```
This lambda stack contains:
1) calculate volumes to be deleted:
   volumes with status available and more than num days can be deleted as they are not used by any instance
2) calculate autoscaling to be deleted:
   autoscaling groups which have no instances attached
3) check reservation set up for each ec2 instance
4) calculate images to be deleted:  
   images which are not used by any instance or launch config and more than num days can be deleted
```
# lambda environment variables

```
region      : "region to deploy this lambda to"
memory_size : "size in MB to allocate to the Lambda for this function"
timeout     : "default Timeout in Seconds before the Lambda is considered Failed"
use_profile : "use profile - used for debug , if would like to run from a local machine"
delete_flag : "used for debug , if true - deletion is activated"
days_count  : "Images more than X days which are not used by any instance will be notify as not used."
regions_arr : "Run on all the the regions whcih are set"
```

# prerequisite

Change self.slackurl = "https://hooks.slack.com/services/ChangeME" to a proper slack webhook url

# terraform version

Terraform v1.1.4


# slack info

```
Reservation slack info:
eu-west-1 # ec2  # NoneReserved : Type m5, Running : 6
eu-west-1 # ec2  # NoneReserved : Type r4, Running : 8
eu-west-1 # ec2  # NoneReserved : Type t3, Running : 2

Image slack info:
Debug Images removal AWS_REGION eu-west-1 CreationDate 2020-04-21T14:32:59.000Z, Name XXXXX, ImageId ami-yyyy

ASG slack info:
ASG in eu-west-1 / accountid XXXXX , Instance count :0 , Creation Date :2019-09-12 13
```

# terrafrom Apply

```
Terraform used the selected providers to generate the following execution plan. Resource actions are indicated with the following symbols:
  + create

Terraform will perform the following actions:

  # aws_cloudwatch_event_rule.every_day will be created
  + resource "aws_cloudwatch_event_rule" "every_day" {
      + arn                 = (known after apply)
      + description         = "triggers every day"
      + event_bus_name      = "default"
      + id                  = (known after apply)
      + is_enabled          = true
      + name                = "every-day"
      + name_prefix         = (known after apply)
      + schedule_expression = "rate(1 day)"
      + tags_all            = (known after apply)
    }

  # aws_cloudwatch_event_target.monitor_lambda_amis_autoscaling_to_be_deleted_every_day will be created
  + resource "aws_cloudwatch_event_target" "monitor_lambda_amis_autoscaling_to_be_deleted_every_day" {
      + arn            = (known after apply)
      + event_bus_name = "default"
      + id             = (known after apply)
      + rule           = "every-day"
      + target_id      = "lambda-amis-autoscaling-to-be-deleted"
    }

  # aws_iam_role.iam_role will be created
  + resource "aws_iam_role" "iam_role" {
      + arn                   = (known after apply)
      + assume_role_policy    = jsonencode(
            {
              + Statement = [
                  + {
                      + Action    = "sts:AssumeRole"
                      + Effect    = "Allow"
                      + Principal = {
                          + Service = "lambda.amazonaws.com"
                        }
                      + Sid       = ""
                    },
                ]
              + Version   = "2012-10-17"
            }
        )
      + create_date           = (known after apply)
      + force_detach_policies = false
      + id                    = (known after apply)
      + managed_policy_arns   = (known after apply)
      + max_session_duration  = 3600
      + name                  = "lambda-amis-autoscaling-to-be-deleted-eu-west-1-iam-role"
      + name_prefix           = (known after apply)
      + path                  = "/"
      + tags_all              = (known after apply)
      + unique_id             = (known after apply)

      + inline_policy {
          + name   = (known after apply)
          + policy = (known after apply)
        }
    }

  # aws_iam_role_policy.ec2_ami_launch_config_policy will be created
  + resource "aws_iam_role_policy" "ec2_ami_launch_config_policy" {
      + id     = (known after apply)
      + name   = "ec2_ami_launch_config"
      + policy = jsonencode(
            {
              + Statement = [
                  + {
                      + Action   = [
                          + "ec2:DeregisterImage*",
                          + "autoscaling:DescribeLaunchConfigurations",
                        ]
                      + Effect   = "Allow"
                      + Resource = "*"
                      + Sid      = "CreateLogStream"
                    },
                ]
              + Version   = "2012-10-17"
            }
        )
      + role   = (known after apply)
    }

  # aws_iam_role_policy.ec2_describe_policy will be created
  + resource "aws_iam_role_policy" "ec2_describe_policy" {
      + id     = (known after apply)
      + name   = "ec2_describe"
      + policy = jsonencode(
            {
              + Statement = [
                  + {
                      + Action   = [
                          + "rds:Describe*",
                          + "ec2:describe*",
                          + "autoscaling:DescribeAutoScalingGroups",
                        ]
                      + Effect   = "Allow"
                      + Resource = "*"
                      + Sid      = "CreateLogStream"
                    },
                ]
              + Version   = "2012-10-17"
            }
        )
      + role   = (known after apply)
    }

  # aws_iam_role_policy.logging_policy will be created
  + resource "aws_iam_role_policy" "logging_policy" {
      + id     = (known after apply)
      + name   = "logging"
      + policy = jsonencode(
            {
              + Statement = [
                  + {
                      + Action   = [
                          + "logs:PutLogEvents",
                          + "logs:GetLogEvents",
                          + "logs:FilterLogEvents",
                          + "logs:DescribeLogStreams",
                          + "logs:DescribeLogGroups",
                          + "logs:CreateLogStream",
                          + "logs:CreateLogGroup",
                        ]
                      + Effect   = "Allow"
                      + Resource = "*"
                      + Sid      = "CreateLogStream"
                    },
                ]
              + Version   = "2012-10-17"
            }
        )
      + role   = (known after apply)
    }

  # aws_iam_role_policy_attachment.basic_lambda_exec_role will be created
  + resource "aws_iam_role_policy_attachment" "basic_lambda_exec_role" {
      + id         = (known after apply)
      + policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
      + role       = "lambda-amis-autoscaling-to-be-deleted-eu-west-1-iam-role"
    }

  # aws_lambda_function.lambda will be created
  + resource "aws_lambda_function" "lambda" {
      + architectures                  = (known after apply)
      + arn                            = (known after apply)
      + description                    = "Function for sre visibility channel"
      + filename                       = "./lambda-amis-autoscaling-to-be-deleted.zip"
      + function_name                  = "lambda-amis-autoscaling-to-be-deleted"
      + handler                        = "lambda-amis-autoscaling-to-be-deleted.lambda_handler"
      + id                             = (known after apply)
      + invoke_arn                     = (known after apply)
      + last_modified                  = (known after apply)
      + memory_size                    = 512
      + package_type                   = "Zip"
      + publish                        = false
      + qualified_arn                  = (known after apply)
      + reserved_concurrent_executions = 1
      + role                           = (known after apply)
      + runtime                        = "python3.6"
      + signing_job_arn                = (known after apply)
      + signing_profile_version_arn    = (known after apply)
      + source_code_hash               = "G5aTl8ERNG5WW6ksf/eyTDBdGU60qo8XRqVV8TNZNqg="
      + source_code_size               = (known after apply)
      + tags_all                       = (known after apply)
      + timeout                        = 900
      + version                        = (known after apply)

      + environment {
          + variables = {
              + "days_count"  = "180"
              + "delete_flag" = "true"
              + "region"      = "eu-west-1"
              + "regions_arr" = "eu-west-1,eu-central-1,ap-southeast-2,us-east-1,us-west-2,us-east-2"
              + "use_profile" = "false"
            }
        }

      + tracing_config {
          + mode = (known after apply)
        }
    }

  # aws_lambda_permission.allow_cloudwatch_to_call_check_foo will be created
  + resource "aws_lambda_permission" "allow_cloudwatch_to_call_check_foo" {
      + action        = "lambda:InvokeFunction"
      + function_name = "lambda-amis-autoscaling-to-be-deleted"
      + id            = (known after apply)
      + principal     = "events.amazonaws.com"
      + source_arn    = (known after apply)
      + statement_id  = "AllowExecutionFromCloudWatch"
    }

Plan: 9 to add, 0 to change, 0 to destroy.

Changes to Outputs:
  + days_count           = 180
  + lambda_arn           = (known after apply)
  + lambda_iam_role_arn  = (known after apply)
  + lambda_iam_role_name = "lambda-amis-autoscaling-to-be-deleted-eu-west-1-iam-role"
  + lambda_name          = "lambda-amis-autoscaling-to-be-deleted"
  + regions_arr          = "eu-west-1,eu-central-1,ap-southeast-2,us-east-1,us-west-2,us-east-2"
  + use_profile          = "false"

Do you want to perform these actions?
  Terraform will perform the actions described above.
  Only 'yes' will be accepted to approve.

  Enter a value: yes

aws_cloudwatch_event_rule.every_day: Creating...
aws_iam_role.iam_role: Creating...
aws_cloudwatch_event_rule.every_day: Creation complete after 1s [id=every-day]
aws_iam_role.iam_role: Creation complete after 3s [id=lambda-amis-autoscaling-to-be-deleted-eu-west-1-iam-role]
aws_iam_role_policy.logging_policy: Creating...
aws_iam_role_policy.ec2_ami_launch_config_policy: Creating...
aws_iam_role_policy.ec2_describe_policy: Creating...
aws_iam_role_policy_attachment.basic_lambda_exec_role: Creating...
aws_lambda_function.lambda: Creating...
aws_iam_role_policy.logging_policy: Creation complete after 1s [id=lambda-amis-autoscaling-to-be-deleted-eu-west-1-iam-role:logging]
aws_iam_role_policy.ec2_ami_launch_config_policy: Creation complete after 1s [id=lambda-amis-autoscaling-to-be-deleted-eu-west-1-iam-role:ec2_ami_launch_config]
aws_iam_role_policy_attachment.basic_lambda_exec_role: Creation complete after 1s [id=lambda-amis-autoscaling-to-be-deleted-eu-west-1-iam-role-20220127141125378700000001]
aws_iam_role_policy.ec2_describe_policy: Creation complete after 1s [id=lambda-amis-autoscaling-to-be-deleted-eu-west-1-iam-role:ec2_describe]
aws_lambda_function.lambda: Still creating... [10s elapsed]
aws_lambda_function.lambda: Creation complete after 16s [id=lambda-amis-autoscaling-to-be-deleted]
aws_lambda_permission.allow_cloudwatch_to_call_check_foo: Creating...
aws_cloudwatch_event_target.monitor_lambda_amis_autoscaling_to_be_deleted_every_day: Creating...
aws_lambda_permission.allow_cloudwatch_to_call_check_foo: Creation complete after 1s [id=AllowExecutionFromCloudWatch]
aws_cloudwatch_event_target.monitor_lambda_amis_autoscaling_to_be_deleted_every_day: Creation complete after 1s [id=every-day-lambda-amis-autoscaling-to-be-deleted]

Apply complete! Resources: 9 added, 0 changed, 0 destroyed.

Outputs:

days_count = 180
lambda_arn = "arn:aws:apigateway:eu-west-1:lambda:path/2015-03-31/functions/arn:aws:lambda:eu-west-1:accountid:function:lambda-amis-autoscaling-to-be-deleted/invocations"
lambda_iam_role_arn = "arn:aws:iam::accountid:role/lambda-amis-autoscaling-to-be-deleted-eu-west-1-iam-role"
lambda_iam_role_name = "lambda-amis-autoscaling-to-be-deleted-eu-west-1-iam-role"
lambda_name = "lambda-amis-autoscaling-to-be-deleted"
regions_arr = "eu-west-1,eu-central-1,ap-southeast-2,us-east-1,us-west-2,us-east-2"
use_profile = "false"
```
