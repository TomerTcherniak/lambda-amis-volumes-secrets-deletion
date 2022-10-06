# lambda-amis-autoscaling-to-be-deleted

AWS lambda function

# author

Tomer Tcherniak

# info

```
It has 4 functions:

1. calculate unused volumes to be deleted
2. calculate autoscaling instances not healthy
3. calculate amis to be deleted
4. calculate autoscaling to be deleted
```

# terraform plan
```
data.archive_file.init: Reading...
data.archive_file.init: Read complete after 0s
data.aws_iam_policy_document.logging_policy_document: Reading...
data.aws_iam_policy_document.ec2_policy_document: Reading...
data.aws_iam_policy_document.ec2_describe_policy_ami: Reading...
data.aws_iam_policy_document.lambda_assume_policy: Reading...
data.aws_iam_policy_document.logging_policy_document: Read complete after 0s
data.aws_iam_policy_document.ec2_policy_document: Read complete after 0s
data.aws_iam_policy_document.ec2_describe_policy_ami: Read complete after 0s
data.aws_iam_policy_document.lambda_assume_policy: Read complete after 0s
```
