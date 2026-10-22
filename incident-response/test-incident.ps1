$payload = @{
  status = "firing"
  alerts = @(@{
    status = "firing"
    labels = @{ alertname = "GuardianAngelAssessmentFailures"; allow_fix = "false" }
    annotations = @{ summary = "Assessment schema validation failures" }
    startsAt = (Get-Date).ToUniversalTime().ToString("o")
  })
} | ConvertTo-Json -Depth 5

Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8001/alerts" -ContentType "application/json" -Body $payload

