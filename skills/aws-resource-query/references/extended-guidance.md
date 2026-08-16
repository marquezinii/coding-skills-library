<!-- Extracted from SKILL.md for progressive disclosure; preserve section semantics. -->

### SECURITY & IDENTITY

#### IAM
```bash
# "IAM users" / "list users"
aws iam list-users \
  --query 'Users[].[UserName,UserId,CreateDate,PasswordLastUsed]' --output table

# "IAM roles" / "list roles"
aws iam list-roles \
  --query 'Roles[].[RoleName,RoleId,CreateDate]' --output table

# "IAM policies attached to role <name>"
aws iam list-attached-role-policies --role-name <name> \
  --query 'AttachedPolicies[].[PolicyName,PolicyArn]' --output table

# "IAM groups"
aws iam list-groups \
  --query 'Groups[].[GroupName,GroupId,CreateDate]' --output table

# "IAM policies (customer managed)"
aws iam list-policies --scope Local \
  --query 'Policies[].[PolicyName,AttachmentCount,CreateDate]' --output table

# "who has MFA enabled" / "MFA devices"
aws iam list-virtual-mfa-devices \
  --query 'VirtualMFADevices[].[SerialNumber,User.UserName,EnableDate]' --output table

# "IAM account password policy"
aws iam get-account-password-policy

# "IAM account summary"
aws iam get-account-summary
```

#### Secrets Manager
```bash
# "list secrets" / "Secrets Manager secrets" / "show secrets"
aws secretsmanager list-secrets \
  --query 'SecretList[].[Name,ARN,LastChangedDate,LastAccessedDate,Description]' --output table

# "secret metadata for <name>"
aws secretsmanager describe-secret --secret-id <name> \
  --query '{Name:Name,ARN:ARN,RotationEnabled:RotationEnabled,LastRotatedDate:LastRotatedDate,Tags:Tags}'

# "secrets with rotation enabled"
aws secretsmanager list-secrets \
  --query 'SecretList[?RotationEnabled==`true`].[Name,LastRotatedDate]' --output table
```

> ⚠️ **Note**: Secret **values** are never retrieved (`get-secret-value` is excluded). Only metadata is shown.

#### SSM Parameter Store
```bash
# "SSM parameters" / "Parameter Store"
aws ssm describe-parameters \
  --query 'Parameters[].[Name,Type,LastModifiedDate,Description]' --output table

# "SSM parameters by path <path>"
aws ssm describe-parameters \
  --parameter-filters "Key=Path,Values=<path>" \
  --query 'Parameters[].[Name,Type,LastModifiedDate]' --output table
```

> ⚠️ **Note**: Parameter **values** are never retrieved (`get-parameter` is excluded). Only metadata is shown.

#### KMS & Certificates
```bash
# "KMS keys" / "encryption keys"
aws kms list-keys --query 'Keys[].[KeyId,KeyArn]' --output table

# "KMS key details for <id>"
aws kms describe-key --key-id <id> \
  --query 'KeyMetadata.[KeyId,Description,KeyState,KeyUsage,CreationDate,Enabled]'

# "KMS aliases"
aws kms list-aliases \
  --query 'Aliases[].[AliasName,AliasArn,TargetKeyId]' --output table

# "SSL certificates" / "ACM certificates"
aws acm list-certificates \
  --query 'CertificateSummaryList[].[CertificateArn,DomainName,Status,RenewalEligibility]' --output table

# "certificate details for <arn>"
aws acm describe-certificate --certificate-arn <arn> \
  --query 'Certificate.[DomainName,Status,NotAfter,NotBefore,InUseBy]'
```

#### GuardDuty, Security Hub & Config
```bash
# "GuardDuty detectors"
aws guardduty list-detectors --query 'DetectorIds' --output table

# "GuardDuty findings"
aws guardduty list-findings --detector-id <id> --query 'FindingIds' --output table

# "Security Hub findings"
aws securityhub get-findings \
  --query 'Findings[].[Title,Severity.Label,WorkflowState,UpdatedAt]' --output table

# "AWS Config rules"
aws configservice describe-config-rules \
  --query 'ConfigRules[].[ConfigRuleName,ConfigRuleState,Source.SourceIdentifier]' --output table

# "non-compliant resources"
aws configservice get-compliance-summary-by-config-rule \
  --query 'ComplianceSummariesByConfigRule[].[ConfigRuleName,Compliance.ComplianceType]' --output table
```

---

### MESSAGING & EVENTS

```bash
# "SQS queues" / "list queues"
aws sqs list-queues --query 'QueueUrls' --output table

# "SQS queue details / message count for <url>"
aws sqs get-queue-attributes --queue-url <url> \
  --attribute-names ApproximateNumberOfMessages,ApproximateNumberOfMessagesNotVisible,ApproximateAgeOfOldestMessage

# "SNS topics"
aws sns list-topics --query 'Topics[].TopicArn' --output table

# "SNS subscriptions"
aws sns list-subscriptions \
  --query 'Subscriptions[].[SubscriptionArn,Protocol,Endpoint,TopicArn]' --output table

# "EventBridge rules"
aws events list-rules \
  --query 'Rules[].[Name,State,ScheduleExpression,EventPattern]' --output table

# "EventBridge event buses"
aws events list-event-buses \
  --query 'EventBuses[].[Name,Arn]' --output table

# "Kinesis streams"
aws kinesis list-streams --query 'StreamNames' --output table

# "Kinesis Firehose delivery streams"
aws firehose list-delivery-streams --query 'DeliveryStreamNames' --output table
```

---

### API GATEWAY & SERVERLESS

```bash
# "API Gateway APIs" / "REST APIs"
aws apigateway get-rest-apis \
  --query 'items[].[id,name,description,createdDate]' --output table

# "HTTP APIs" / "API Gateway v2"
aws apigatewayv2 get-apis \
  --query 'Items[].[ApiId,Name,ProtocolType,ApiEndpoint,CreatedDate]' --output table

# "Step Functions state machines" / "workflows"
aws stepfunctions list-state-machines \
  --query 'stateMachines[].[name,stateMachineArn,type,creationDate]' --output table

# "Step Functions executions for <arn>"
aws stepfunctions list-executions --state-machine-arn <arn> \
  --query 'executions[].[name,status,startDate,stopDate]' --output table
```

---

### MONITORING & OBSERVABILITY

```bash
# "CloudWatch alarms" / "list alarms"
aws cloudwatch describe-alarms \
  --query 'MetricAlarms[].[AlarmName,StateValue,MetricName,Namespace,Threshold]' --output table

# "alarms in ALARM state" / "triggered alarms"
aws cloudwatch describe-alarms --state-value ALARM \
  --query 'MetricAlarms[].[AlarmName,MetricName,StateReason]' --output table

# "CloudWatch dashboards"
aws cloudwatch list-dashboards \
  --query 'DashboardEntries[].[DashboardName,LastModified,Size]' --output table

# "CloudWatch log groups"
aws logs describe-log-groups \
  --query 'logGroups[].[logGroupName,retentionInDays,storedBytes]' --output table

# "CloudTrail trails"
aws cloudtrail describe-trails \
  --query 'trailList[].[Name,S3BucketName,IsMultiRegionTrail,LogFileValidationEnabled]' --output table

# "ECR repositories" / "container registries"
aws ecr describe-repositories \
  --query 'repositories[].[repositoryName,repositoryUri,createdAt]' --output table
```

---

### COST & BILLING

```bash
# "current month cost" / "how much am I spending"
aws ce get-cost-and-usage \
  --time-period Start=$(date -u +%Y-%m-01),End=$(date -u +%Y-%m-%d) \
  --granularity MONTHLY --metrics BlendedCost \
  --query 'ResultsByTime[].[TimePeriod.Start,Total.BlendedCost.Amount,Total.BlendedCost.Unit]' \
  --output table

# "cost by service" / "spending breakdown"
aws ce get-cost-and-usage \
  --time-period Start=$(date -u -d '30 days ago' +%Y-%m-%d),End=$(date -u +%Y-%m-%d) \
  --granularity MONTHLY --metrics BlendedCost \
  --group-by Type=DIMENSION,Key=SERVICE --output table

# "AWS Budgets"
aws budgets describe-budgets \
  --account-id $(aws sts get-caller-identity --query Account --output text) \
  --query 'Budgets[].[BudgetName,BudgetType,BudgetLimit.Amount,CalculatedSpend.ActualSpend.Amount]' \
  --output table

# "Trusted Advisor recommendations"
aws support describe-trusted-advisor-checks --language en \
  --query 'checks[].[id,name,category]' --output table
```

---

### CROSS-SERVICE QUERIES

```bash
# "resources tagged Environment=production" / "all production resources"
aws resourcegroupstaggingapi get-resources \
  --tag-filters Key=Environment,Values=production \
  --query 'ResourceTagMappingList[].[ResourceARN]' --output table

# "all resources tagged <key>=<value>"
aws resourcegroupstaggingapi get-resources \
  --tag-filters Key=<key>,Values=<value> \
  --query 'ResourceTagMappingList[].[ResourceARN,Tags]' --output table

# "inventory of all resources" (AWS Config)
aws configservice list-discovered-resources --resource-type <type> \
  --query 'resourceIdentifiers[].[resourceType,resourceId,resourceName]' --output table
```

---

## Output Formatting Rules

1. Always use `--output table` for list results; use `--output json` only when deep detail is explicitly requested
2. Always use `--query` to extract only relevant fields — never dump raw JSON
3. For large result sets (>20 items), show a count first, then offer to filter
4. When a command returns nothing, explain why (wrong region, no resources, insufficient permissions)
5. Offer to drill into a specific resource: "Found 47 EC2 instances. Filter by state, type, or tag?"

## Error Handling

| Error | Response |
|---|---|
| `AccessDenied` | "You don't have permission to list [resource]. Required: `<service>:<Action>`." |
| `NoCredentialProviders` | "Run `aws configure` or set `AWS_PROFILE`." |
| Empty result | "No [resources] found in [region]. Check another region?" |
| Invalid identifier | "Could not find '[name]'. Check the name or provide the resource ID." |
