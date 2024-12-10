# ORGANIZATION
resource "aws_organizations_organization" "main_org" {
  aws_service_access_principals = ["account.amazonaws.com", "sso.amazonaws.com"]
  enabled_policy_types          = []
  feature_set                   = "ALL"
}


#### ORGANIZATIONAL UNITS

resource "aws_organizations_organizational_unit" "dev_org_unit" {
  name      = "development"
  parent_id = aws_organizations_organization.main_org.roots[0].id
}

resource "aws_organizations_organizational_unit" "prod_org_unit" {
  name      = "production"
  parent_id = aws_organizations_organization.main_org.roots[0].id
}


#### ACCOUNTS ####
resource "aws_organizations_account" "org_root_account" {
  email     = "aloisi.lorenzo99@gmail.com"
  name      = "aloilor-root"
  parent_id = aws_organizations_organization.main_org.roots[0].id
}
