# DynamoDB Tables for Wallet Scores, Analysis History, and Agent State

resource "aws_dynamodb_table" "wallet_scores" {
  name           = "${var.environment}-wallet-scores"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "wallet_address"
  range_key      = "timestamp"

  attribute {
    name = "wallet_address"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "N"
  }

  attribute {
    name = "risk_score"
    type = "N"
  }

  global_secondary_index {
    name            = "RiskScoreIndex"
    hash_key        = "risk_score"
    range_key       = "timestamp"
    projection_type = "ALL"
  }

  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  point_in_time_recovery {
    enabled = true
  }

  tags = {
    Name        = "wallet-scores"
    Environment = var.environment
  }
}

resource "aws_dynamodb_table" "analysis_history" {
  name           = "${var.environment}-analysis-history"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "analysis_id"
  range_key      = "timestamp"

  attribute {
    name = "analysis_id"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "N"
  }

  attribute {
    name = "wallet_address"
    type = "S"
  }

  global_secondary_index {
    name            = "WalletAddressIndex"
    hash_key        = "wallet_address"
    range_key       = "timestamp"
    projection_type = "ALL"
  }

  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  point_in_time_recovery {
    enabled = true
  }

  tags = {
    Name        = "analysis-history"
    Environment = var.environment
  }
}

resource "aws_dynamodb_table" "agent_state" {
  name           = "${var.environment}-agent-state"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "agent_id"
  range_key      = "state_timestamp"

  attribute {
    name = "agent_id"
    type = "S"
  }

  attribute {
    name = "state_timestamp"
    type = "N"
  }

  point_in_time_recovery {
    enabled = true
  }

  tags = {
    Name        = "agent-state"
    Environment = var.environment
  }
}

# Backup configurations
resource "aws_backup_vault" "dynamodb_vault" {
  name = "${var.environment}-dynamodb-backup-vault"

  tags = {
    Name        = "dynamodb-backup-vault"
    Environment = var.environment
  }
}

resource "aws_backup_plan" "dynamodb_backup" {
  name = "${var.environment}-dynamodb-backup-plan"

  rule {
    rule_name         = "daily_backup"
    target_vault_name = aws_backup_vault.dynamodb_vault.name
    schedule          = "cron(0 2 * * ? *)"

    lifecycle {
      delete_after = 30
    }
  }

  rule {
    rule_name         = "weekly_backup"
    target_vault_name = aws_backup_vault.dynamodb_vault.name
    schedule          = "cron(0 3 ? * 1 *)"

    lifecycle {
      delete_after = 90
    }
  }
}

resource "aws_backup_selection" "dynamodb_selection" {
  name         = "${var.environment}-dynamodb-backup-selection"
  iam_role_arn = aws_iam_role.backup_role.arn
  plan_id      = aws_backup_plan.dynamodb_backup.id

  resources = [
    aws_dynamodb_table.wallet_scores.arn,
    aws_dynamodb_table.analysis_history.arn,
    aws_dynamodb_table.agent_state.arn
  ]
}

resource "aws_iam_role" "backup_role" {
  name = "${var.environment}-dynamodb-backup-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "backup.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "backup_policy" {
  role       = aws_iam_role.backup_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSBackupServiceRolePolicyForBackup"
}

resource "aws_iam_role_policy_attachment" "restore_policy" {
  role       = aws_iam_role.backup_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSBackupServiceRolePolicyForRestores"
}