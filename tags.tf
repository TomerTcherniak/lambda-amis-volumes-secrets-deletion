locals {
  common_tags = {
    managed_by_terraform = "true"
    type                 = "Lambda amis autoscaling to be deleted"
    description          = "visibility for images to be deleted . reservation status ."
    stack                = "lambda-amis-autoscaling-to-be-deleted"
  }
}
