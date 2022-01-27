

variable "region" {
  default     = "eu-west-1"
  description = "Region to deploy this lambda to"
}

variable "memory_size" {
  default     = 512
  description = "Size in MB to allocate to the Lambda for this function"
}

variable "timeout" {
  default     = 900
  description = "Default Timeout in Seconds before the Lambda is considered Failed"
}

variable "use_profile" {
  default = "false"
  description = "use profile - used for debug"
}

variable "delete_flag" {
  default = "true"
  description = "use deletion - used for debug"
}


variable "days_count" {
  default     = 180
  description = "Images more than X days which are not used by any instance will be notify as not used."
}

variable "regions_arr" {
  default     = "eu-west-1,eu-central-1,ap-southeast-2,us-east-1,us-west-2,us-east-2" #,us-east-2
  description = "run on all the below regions"
}
