# Get existing hosted zone
data "aws_route53_zone" "dataiesb" {
  name = "dataiesb.com"
}

# Create ACM certificate for osintube subdomain
resource "aws_acm_certificate" "osintube" {
  domain_name       = "osintube.dataiesb.com"
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }
}

# Create DNS validation records
resource "aws_route53_record" "osintube_validation" {
  for_each = {
    for dvo in aws_acm_certificate.osintube.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = data.aws_route53_zone.dataiesb.zone_id
}

# Validate certificate
resource "aws_acm_certificate_validation" "osintube" {
  certificate_arn         = aws_acm_certificate.osintube.arn
  validation_record_fqdns = [for record in aws_route53_record.osintube_validation : record.fqdn]
}

# Create A record pointing to load balancer
resource "aws_route53_record" "osintube" {
  zone_id = data.aws_route53_zone.dataiesb.zone_id
  name    = "osintube.dataiesb.com"
  type    = "A"
  
  alias {
    name                   = "k8s-default-ingressi-73bd0705e3-102651203.sa-east-1.elb.amazonaws.com"
    zone_id                = "Z2P70J7HTTTPLU"
    evaluate_target_health = true
  }
}
