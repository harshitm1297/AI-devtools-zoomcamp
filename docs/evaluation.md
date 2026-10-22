# Evaluation plan

`data/evaluation-cases.json` contains six transparent threshold cases. The expected deterministic
classification is 6/6. Automated tests also require 100% citation validity: every cited ID must be
in the retrieved set.

For live multimodal evaluation, prepare ten synthetic receipt images, label merchant/date/currency/
total/category manually, and report exact-field accuracy. Do not publish the earlier hackathon's
82% or 88% figures as results for this reduced implementation.

Report provider/model identifier, date, dataset version, extraction accuracy, structured-output
success rate, citation validity, mean latency, and failure cases.

