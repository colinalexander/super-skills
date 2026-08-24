# Model proposal

Goal: predict which accounts will churn in the next 30 days so a five-person retention team can contact the highest-risk 200 accounts each week.

Current approach:

- One row per account-month from January through June.
- Label is whether the account closes within 30 days after month end.
- Features include prior-30-day usage, plan, tenure, cancellation reason, account closure timestamp, and support tickets opened in the following 30 days.
- Rows are randomly split 80/20.
- A gradient-boosted model reports 98.7% accuracy.
- The base churn rate is 3.1%.
- No retention intervention has yet been evaluated.
