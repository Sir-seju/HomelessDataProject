variable "enhanced_reporting_enabled" {
  type        = bool
  default     = true
  description = "Whether to enable \"enhanced\" health reporting for this environment.  If false, \"basic\" reporting is used.  When you set this to false, you must also set `enable_managed_actions` to false"
}
