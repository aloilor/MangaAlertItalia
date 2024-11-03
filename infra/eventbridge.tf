resource "aws_iam_role" "manga_alert_events_role" {
  name = "manga-alert-ecs-events-role"

  assume_role_policy = <<DOC
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Sid": "",
        "Effect": "Allow",
        "Principal": {
          "Service": "events.amazonaws.com"
        },
        "Action": "sts:AssumeRole"
      }
    ]
  }
  DOC
}

resource "aws_iam_role_policy" "ecs_events_run_task" {
  name = "manga-alert-ecs-events-run-task-policy"
  role = aws_iam_role.manga_alert_events_role.id

  policy = <<DOC
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": [
          "ecs:RunTask",
          "ecs:DescribeTasks",
          "ecs:DescribeTaskDefinition"
        ],
        "Resource": [
          "*"
        ]
      },
      {
        "Effect": "Allow",
        "Action": "iam:PassRole",
        "Resource": [
          "*"
        ],
        "Condition": {
          "StringLike": {
            "iam:PassedToService": "ecs-tasks.amazonaws.com"
          }
        }
      }
    ]
  }
  DOC
}

#### CRON SCRAPER
resource "aws_cloudwatch_event_rule" "manga_alert_scraper_cron_six_hours" {
  name                = "manga-alert-scraper-cron-six-hours"
  description         = "Schedule trigger to run the Manga Alert Scraper every 6 hours"
  schedule_expression = "rate(6 hours)"
}

resource "aws_cloudwatch_event_target" "main_manga_alert_scraper_every_6_hours" {
  target_id = "run-manga-alert-scraper-eventbridge-every-6-hours"
  arn       = aws_ecs_cluster.manga_alert_ecs_cluster.arn
  rule      = aws_cloudwatch_event_rule.manga_alert_scraper_cron_six_hours.name
  role_arn  = aws_iam_role.manga_alert_events_role.arn

  ecs_target {
    task_count          = 1
    task_definition_arn = aws_ecs_task_definition.manga_alert_scraper_ecs_definition.arn
    launch_type         = "EC2"
  }

  depends_on = [
    aws_ecs_task_definition.manga_alert_scraper_ecs_definition
  ]
}


#### CRON NOTIFIER
resource "aws_cloudwatch_event_rule" "manga_alert_notifier_cron_six_hours" {
  name                = "manga-alert-notifier-cron-six-hours"
  description         = "Schedule trigger to run the Manga Alert Notifier every 6 hours"
  schedule_expression = "rate(2 minutes)"
}

resource "aws_cloudwatch_event_target" "main_manga_alert_notifier_every_6_hours" {
  target_id = "run-manga-alert-notifier-eventbridge-every-6-hours"
  arn       = aws_ecs_cluster.manga_alert_ecs_cluster.arn
  rule      = aws_cloudwatch_event_rule.manga_alert_notifier_cron_six_hours.name
  role_arn  = aws_iam_role.manga_alert_events_role.arn

  ecs_target {
    task_count          = 1
    task_definition_arn = aws_ecs_task_definition.manga_alert_notifier_ecs_definition.arn
    launch_type         = "EC2"
  }

  depends_on = [
    aws_ecs_task_definition.manga_alert_notifier_ecs_definition
  ]
}
