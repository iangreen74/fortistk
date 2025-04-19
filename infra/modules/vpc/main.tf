resource "aws_vpc" "fortistk" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags = {
    Name = "fortistk-vpc"
  }
}

resource "aws_internet_gateway" "fortistk_igw" {
  vpc_id = aws_vpc.fortistk.id
  tags = {
    Name = "fortistk-igw"
  }
}

resource "aws_subnet" "public" {
  count                   = length(var.public_subnet_cidrs)
  vpc_id                  = aws_vpc.fortistk.id
  cidr_block              = var.public_subnet_cidrs[count.index]
  map_public_ip_on_launch = true
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  tags = {
    Name = "fortistk-public-${count.index}"
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.fortistk.id
  tags = {
    Name = "fortistk-public-rt"
  }
}

resource "aws_route" "igw" {
  route_table_id         = aws_route_table.public.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.fortistk_igw.id
}

resource "aws_route_table_association" "public" {
  count          = length(aws_subnet.public)
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

data "aws_availability_zones" "available" {}
