output "ssm_role_arn" {
  description = "The arn for the IAM role for ssm"
  value       = aws_iam_role.ssm.arn
}

output "ssm_profile_id" {
  description = "The ID for the Instance profile for ssm"
  value       = aws_iam_instance_profile.ssm.id
}
