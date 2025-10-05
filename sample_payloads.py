process_bulk_notification = {
  "recipients": [
    {
      "email": "user1@example.com",
      "phone": "+1234567890",
      "whatsapp": "+1234567890",
      "name": "John Doe",
      "user_id": "user_001",
      "custom_data": {
        "first_name": "John",
        "last_name": "Doe",
        "subscription_type": "premium",
        "balance": 1250.50
      }
    },
    {
      "email": "user2@example.com",
      "phone": "+1234567891",
      "whatsapp": "+1234567891",
      "name": "Jane Smith",
      "user_id": "user_002",
      "custom_data": {
        "first_name": "Jane",
        "last_name": "Smith",
        "subscription_type": "basic",
        "balance": 450.75
      }
    }
  ],
  "content": {
    "email_content": {
      "subject": "Account Balance Update for {first_name}",
      "html_body": "<h1>Hi {first_name}!</h1><p>Your current balance is ${balance}.</p><p>Subscription: {subscription_type}</p>",
      "text_body": "Hi {first_name}! Your current balance is ${balance}. Subscription: {subscription_type}",
      "sender_name": "Account Team",
      "reply_to": "support@example.com",
      "use_bcc": False,
      "batch_size": 100,
      "personalization_enabled": True
    },
    "sms_content": {
      "message": "Hi {first_name}! Your account balance: ${balance}. Type HELP for support.",
      "sender_id": "MYBANK",
      "message_type": "transactional",
      "batch_size": 50,
      "rate_limit_per_second": 10,
      "personalization_enabled": True,
      "delivery_reports": True
    },
    "whatsapp_content": {
      "message_type": "template",
      "template_name": "balance_update",
      "template_language": "en",
      "default_template_parameters": ["{first_name}", "{balance}", "{subscription_type}"],
      "batch_size": 20,
      "rate_limit_per_second": 5,
      "personalization_enabled": True
    },
    "fallback_message": "Account update notification"
  },
  "channels": ["email", "sms", "whatsapp"],
  "mode": "bulk",
  "processing_strategy": "batched",
  "priority": "high",
  "campaign_id": "balance_update_2024",
  "metadata": {
    "department": "finance",
    "notification_type": "account_update"
  }
}