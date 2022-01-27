provider "aws" {
  region  = "eu-west-1"
  profile = "rnd"


}

terraform {
  backend "local" {
    path = "terraform.tfstate"
  }
}
