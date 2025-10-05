from app.constants.enums import BulkProcessingStrategy, NotificationType
from app.schemas.bulk_notification import (
    BulkEmailKafkaPayload,
    BulkNotificationRequest,
    BulkNotificationResponse,
    BulkRecipient,
    BulkSMSKafkaPayload,
    BulkWhatsAppKafkaPayload,
)

_analyze_recipients_by_channel_op = {
    NotificationType.EMAIL: [
        BulkRecipient(email="user1@example.com", phone="+1234567890", name="John Doe"),
        BulkRecipient(email="user2@example.com", whatsapp="+1987654321", name="Jane Smith")
    ],
    NotificationType.SMS: [
        BulkRecipient(email="user1@example.com", phone="+1234567890", name="John Doe"),
        BulkRecipient(phone="+1555666777", whatsapp="+1555666777", name="Bob Wilson")
    ],
    NotificationType.WHATSAPP: [
        BulkRecipient(email="user2@example.com", whatsapp="+1987654321", name="Jane Smith"),
        BulkRecipient(phone="+1555666777", whatsapp="+1555666777", name="Bob Wilson")
    ]
}

# Sample outputs for _create_service_batches method
# This method creates optimized batches for different notification services

# EMAIL channel output - 150 recipients, batch_size=100, results in 2 batches
_create_service_batches_email_output = [
    {
        "service_type": "email",
        "notification_id": "bulk_20241005_150938_001",
        "batch_id": "balance_update_2024_email_1",
        "correlation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "recipients": [
            {
                "email": "user1@example.com",
                "name": "John Doe",
                "user_id": "user_001",
                "personalized_data": {
                    "first_name": "John",
                    "last_name": "Doe",
                    "subscription_type": "premium",
                    "balance": "1250.50"
                }
            },
            {
                "email": "user2@example.com", 
                "name": "Jane Smith",
                "user_id": "user_002",
                "personalized_data": {
                    "first_name": "Jane",
                    "last_name": "Smith",
                    "subscription_type": "basic",
                    "balance": "450.75"
                }
            },
            # ... (98 more recipients for batch 1)
        ],
        "email_content": {
            "subject": "Account Balance Update for {first_name}",
            "html_body": "<h1>Hi {first_name}!</h1><p>Your current balance is ${balance}.</p><p>Subscription: {subscription_type}</p>",
            "text_body": "Hi {first_name}! Your current balance is ${balance}. Subscription: {subscription_type}",
            "sender_name": "Account Team",
            "reply_to": "support@example.com",
            "use_bcc": False,
            "batch_size": 100,
            "personalization_enabled": True,
            "template_id": None,
            "default_template_data": None,
            "attachments": None,
            "headers": None
        },
        "processing_strategy": "batched",
        "priority": "high",
        "batch_number": 1,
        "total_batches": 2,
        "total_recipients": 100,
        "metadata": {
            "department": "finance",
            "notification_type": "account_update"
        }
    },
    {
        "service_type": "email",
        "notification_id": "bulk_20241005_150938_001",
        "batch_id": "balance_update_2024_email_2",
        "correlation_id": "b2c3d4e5-f6g7-8901-bcde-f23456789012",
        "recipients": [
            # ... (50 remaining recipients for batch 2)
        ],
        "email_content": {
            "subject": "Account Balance Update for {first_name}",
            "html_body": "<h1>Hi {first_name}!</h1><p>Your current balance is ${balance}.</p><p>Subscription: {subscription_type}</p>",
            "text_body": "Hi {first_name}! Your current balance is ${balance}. Subscription: {subscription_type}",
            "sender_name": "Account Team",
            "reply_to": "support@example.com",
            "use_bcc": False,
            "batch_size": 100,
            "personalization_enabled": True,
            "template_id": None,
            "default_template_data": None,
            "attachments": None,
            "headers": None
        },
        "processing_strategy": "batched",
        "priority": "high",
        "batch_number": 2,
        "total_batches": 2,
        "total_recipients": 50,
        "metadata": {
            "department": "finance",
            "notification_type": "account_update"
        }
    }
]

# SMS channel output - 120 recipients, batch_size=50, results in 3 batches
_create_service_batches_sms_output = [
    {
        "service_type": "sms",
        "notification_id": "bulk_20241005_150938_001",
        "batch_id": "balance_update_2024_sms_1",
        "correlation_id": "c3d4e5f6-g7h8-9012-cdef-345678901234",
        "recipients": [
            {
                "phone": "+1234567890",
                "name": "John Doe",
                "user_id": "user_001",
                "personalized_message": "Hi John! Your account balance: $1250.50. Type HELP for support.",
                "personalized_data": {
                    "first_name": "John",
                    "balance": "1250.50"
                }
            },
            {
                "phone": "+1234567891",
                "name": "Jane Smith", 
                "user_id": "user_002",
                "personalized_message": "Hi Jane! Your account balance: $450.75. Type HELP for support.",
                "personalized_data": {
                    "first_name": "Jane",
                    "balance": "450.75"
                }
            },
            # ... (48 more recipients for batch 1)
        ],
        "sms_content": {
            "message": "Hi {first_name}! Your account balance: ${balance}. Type HELP for support.",
            "sender_id": "MYBANK",
            "message_type": "transactional",
            "batch_size": 50,
            "rate_limit_per_second": 10,
            "personalization_enabled": True,
            "unicode_message": False,
            "delivery_reports": True,
            "validity_period": None
        },
        "processing_strategy": "batched",
        "priority": "high",
        "rate_limit_per_second": 10,
        "batch_number": 1,
        "total_batches": 3,
        "metadata": {
            "department": "finance",
            "notification_type": "account_update"
        }
    },
    {
        "service_type": "sms",
        "notification_id": "bulk_20241005_150938_001",
        "batch_id": "balance_update_2024_sms_2",
        "correlation_id": "d4e5f6g7-h8i9-0123-def0-456789012345",
        "recipients": [
            # ... (50 recipients for batch 2)
        ],
        "sms_content": {
            "message": "Hi {first_name}! Your account balance: ${balance}. Type HELP for support.",
            "sender_id": "MYBANK",
            "message_type": "transactional",
            "batch_size": 50,
            "rate_limit_per_second": 10,
            "personalization_enabled": True,
            "unicode_message": False,
            "delivery_reports": True,
            "validity_period": None
        },
        "processing_strategy": "batched",
        "priority": "high",
        "rate_limit_per_second": 10,
        "batch_number": 2,
        "total_batches": 3,
        "metadata": {
            "department": "finance",
            "notification_type": "account_update"
        }
    },
    {
        "service_type": "sms",
        "notification_id": "bulk_20241005_150938_001",
        "batch_id": "balance_update_2024_sms_3",
        "correlation_id": "e5f6g7h8-i9j0-1234-ef01-567890123456",
        "recipients": [
            # ... (20 remaining recipients for batch 3)
        ],
        "sms_content": {
            "message": "Hi {first_name}! Your account balance: ${balance}. Type HELP for support.",
            "sender_id": "MYBANK",
            "message_type": "transactional",
            "batch_size": 50,
            "rate_limit_per_second": 10,
            "personalization_enabled": True,
            "unicode_message": False,
            "delivery_reports": True,
            "validity_period": None
        },
        "processing_strategy": "batched",
        "priority": "high",
        "rate_limit_per_second": 10,
        "batch_number": 3,
        "total_batches": 3,
        "metadata": {
            "department": "finance",
            "notification_type": "account_update"
        }
    }
]

# WhatsApp channel output - 45 recipients, batch_size=20, results in 3 batches
_create_service_batches_whatsapp_output = [
    {
        "service_type": "whatsapp",
        "notification_id": "bulk_20241005_150938_001",
        "batch_id": "balance_update_2024_whatsapp_1",
        "correlation_id": "f6g7h8i9-j0k1-2345-f012-678901234567",
        "recipients": [
            {
                "whatsapp": "+1234567890",
                "name": "John Doe",
                "user_id": "user_001", 
                "template_parameters": ["John", "1250.50", "premium"],
                "personalized_data": {
                    "first_name": "John",
                    "balance": "1250.50",
                    "subscription_type": "premium"
                }
            },
            {
                "whatsapp": "+1234567891",
                "name": "Jane Smith",
                "user_id": "user_002",
                "template_parameters": ["Jane", "450.75", "basic"],
                "personalized_data": {
                    "first_name": "Jane", 
                    "balance": "450.75",
                    "subscription_type": "basic"
                }
            },
            # ... (18 more recipients for batch 1)
        ],
        "whatsapp_content": {
            "message_type": "template",
            "template_name": "balance_update",
            "template_language": "en",
            "default_template_parameters": ["{first_name}", "{balance}", "{subscription_type}"],
            "text": None,
            "batch_size": 20,
            "rate_limit_per_second": 5,
            "personalization_enabled": True
        },
        "processing_strategy": "batched",
        "priority": "high",
        "batch_number": 1,
        "total_batches": 3,
        "estimated_cost": 12.0,
        "metadata": {
            "department": "finance",
            "notification_type": "account_update"
        }
    },
    {
        "service_type": "whatsapp", 
        "notification_id": "bulk_20241005_150938_001",
        "batch_id": "balance_update_2024_whatsapp_2",
        "correlation_id": "g7h8i9j0-k1l2-3456-0123-789012345678",
        "recipients": [
            # ... (20 recipients for batch 2)
        ],
        "whatsapp_content": {
            "message_type": "template",
            "template_name": "balance_update",
            "template_language": "en", 
            "default_template_parameters": ["{first_name}", "{balance}", "{subscription_type}"],
            "text": None,
            "batch_size": 20,
            "rate_limit_per_second": 5,
            "personalization_enabled": True
        },
        "processing_strategy": "batched",
        "priority": "high",
        "batch_number": 2,
        "total_batches": 3,
        "estimated_cost": 12.0,
        "metadata": {
            "department": "finance",
            "notification_type": "account_update"
        }
    },
    {
        "service_type": "whatsapp",
        "notification_id": "bulk_20241005_150938_001", 
        "batch_id": "balance_update_2024_whatsapp_3",
        "correlation_id": "h8i9j0k1-l2m3-4567-1234-890123456789",
        "recipients": [
            # ... (5 remaining recipients for batch 3)
        ],
        "whatsapp_content": {
            "message_type": "template",
            "template_name": "balance_update",
            "template_language": "en",
            "default_template_parameters": ["{first_name}", "{balance}", "{subscription_type}"],
            "text": None,
            "batch_size": 20,
            "rate_limit_per_second": 5,
            "personalization_enabled": True
        },
        "processing_strategy": "batched",
        "priority": "high",
        "batch_number": 3,
        "total_batches": 3,
        "estimated_cost": 3.0,
        "metadata": {
            "department": "finance",
            "notification_type": "account_update"
        }
    }
]

# EMAIL with BCC enabled - 500 recipients, batch_size=500, results in 1 batch
_create_service_batches_email_bcc_output = [
    {
        "service_type": "email",
        "notification_id": "bulk_20241005_150938_002",
        "batch_id": "newsletter_campaign_email_1",
        "correlation_id": "i9j0k1l2-m3n4-5678-2345-901234567890",
        "recipients": [
            {
                "email": "subscriber1@example.com",
                "name": "Alice Johnson",
                "user_id": "sub_001",
                "personalized_data": {
                    "first_name": "Alice"
                }
            },
            # ... (499 more recipients in single BCC batch)
        ],
        "email_content": {
            "subject": "Monthly Newsletter - March 2024",
            "html_body": "<h1>Welcome to our Newsletter!</h1><p>Hello {first_name}, here are this month's updates...</p>",
            "text_body": "Welcome to our Newsletter! Hello {first_name}, here are this month's updates...",
            "sender_name": "Marketing Team",
            "reply_to": "newsletter@example.com",
            "use_bcc": True,
            "batch_size": 500,
            "personalization_enabled": True,
            "template_id": None,
            "default_template_data": None,
            "attachments": None,
            "headers": None
        },
        "processing_strategy": "batched",
        "priority": "medium",
        "batch_number": 1,
        "total_batches": 1,
        "total_recipients": 500,
        "metadata": {
            "department": "marketing",
            "notification_type": "newsletter"
        }
    }
]

# Small batch example - 5 recipients across different channels
_create_service_batches_small_batch_email = [
    {
        "service_type": "email",
        "notification_id": "bulk_20241005_150938_003",
        "batch_id": "urgent_alert_email_1", 
        "correlation_id": "j0k1l2m3-n4o5-6789-3456-012345678901",
        "recipients": [
            {
                "email": "admin1@company.com",
                "name": "System Admin",
                "user_id": "admin_001",
                "personalized_data": {
                    "first_name": "Admin",
                    "alert_level": "Critical"
                }
            },
            {
                "email": "admin2@company.com",
                "name": "Backup Admin", 
                "user_id": "admin_002",
                "personalized_data": {
                    "first_name": "Backup",
                    "alert_level": "Critical"
                }
            },
            # ... (3 more recipients)
        ],
        "email_content": {
            "subject": "URGENT: System Alert - {alert_level}",
            "html_body": "<h1>System Alert</h1><p>Hi {first_name}, we have a {alert_level} system issue that requires immediate attention.</p>",
            "text_body": "Hi {first_name}, we have a {alert_level} system issue that requires immediate attention.",
            "sender_name": "System Monitor",
            "reply_to": "alerts@company.com",
            "use_bcc": False,
            "batch_size": 100,
            "personalization_enabled": True,
            "template_id": None,
            "default_template_data": None,
            "attachments": None,
            "headers": None
        },
        "processing_strategy": "batched",
        "priority": "urgent",
        "batch_number": 1,
        "total_batches": 1,
        "total_recipients": 5,
        "metadata": {
            "department": "IT",
            "notification_type": "system_alert"
        }
    }
]