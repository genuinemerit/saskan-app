# Message Brokers

## BowDataSchema.CodeGenerator

---

### Data Schema Request-Response Events

_Event is_ __GetDataCodeObject()__

_Approved Requestors_ are __BowDataAdmin.{services}__

Listen

- Request_CreateSaskanDataObject()

Send

- Generic
  - AcknowledgeRequest()
  - DenyRequest()
  - AcceptRequest()

- Response_CreateSaskanDataObject()

---

### CodeGenerator --> SaskanConcept Pub-Sub

_Topic Manager is_ __BowDataSchema.SaskanConcept__

- Topics
  - SaskanConcept

Listen

- Generic
  - AcknowledgeRequest()
  - DenyRequest()
  - AcceptRequest()

- Notify_SaskanConceptListChange()
- Publish_SaskanConceptList()
- Notify_SaskanConceptObjectChange()
- Publish_SaskanConceptObject()

Send

- Subscribe_SaskanConceptList()
- Subscribe_SaskanConceptObject()

---

### CodeGenerator --> SQLite Pub-Sub

_Topic Manager is_ __BowDataSchema.CodeGenerator.SQLiteCode__

- Topics
  - SQLiteCode

Listen

- Generic
  - AcknowledgeRequest()
  - DenyRequest()
  - AcceptRequest()

- Notify_SQLiteCodeChange()
- Publish_SQLiteCode()

Send

- Subscribe_SQLiteCode()

---

### CodeGenerator --> Postgres Pub-Sub

_Topic Manager is_ __BowDataSchema.CodeGenerator.PostgresCode__

- Topics
  - PostgresCode

Listen

- Generic
  - AcknowledgeRequest()
  - DenyRequest()
  - AcceptRequest()

- Notify_PostgresCodeChange()
- Publish_PostgresCode()

Send

- Subscribe_PostgresCode()

---

### CodeGenerator --> DataAPI Pub-Sub

_Topic Manager is_ __BowDataSchema.CodeGenerator.DataAPICode__

- Topics
  - DataAPICode

Listen

- Generic
  - AcknowledgeRequest()
  - DenyRequest()
  - AcceptRequest()

- Notify_DataAPICodeChange()
- Publish_DataAPICode()

Send

- Subscribe_DataAPICode()

---

## BowDataSchema.CodeGenerator.SQlite

---

### SQlite --> CodeGenerator Pub-Sub

_Topic Manager is_ __BowDataSchema.SaskanConcept.SQLiteCode__

- Topics
  - SQLiteCode

Listen

- Subscribe_SQLiteCode()

Send

- Generic
  - AcknowledgeRequest()
  - DenyRequest()
  - AcceptRequest()

- Notify_SQLiteCodeChange()
- Publish_SQLiteCode()

Manage

- MonitorSQLiteCodeChanges()
  - ListSQLiteCodeChanges()

- NotifySubscribers_SQLiteCodeChange()
- HandleSubscriptions_SQLiteCode()

---

## BowDataSchema.CodeGenerator.Postgres

---

### Postgres --> CodeGenerator Pub-Sub

_Topic Manager is_ __BowDataSchema.SaskanConcept.PostgresCode__

- Topics
  - PostgresCode

Listen

- Subscribe_PostgresCode()

Send

- Generic
  - AcknowledgeRequest()
  - DenyRequest()
  - AcceptRequest()

- Notify_PostgresCodeChange()
- Publish_PostgresCode()

Manage

- MonitorPostgresCodeChanges()
  - ListPostgresCodeChanges()

- NotifySubscribers_PostgresCodeChange()
- HandleSubscriptions_PostgresCode()

---

## BowDataSchema.CodeGenerator.DataAPI

---

### DataAPI --> CodeGenerator Pub-Sub

_Topic Manager is_ __BowDataSchema.SaskanConcept.DataAPICode__

- Topics
  - DataAPICode

Listen

- Subscribe_DataAPICode()

Send

- Generic
  - AcknowledgeRequest()
  - DenyRequest()
  - AcceptRequest()

- Notify_DataAPICodeChange()
- Publish_DataAPICode()

Manage

- MonitorDataAPICodeChanges()
  - ListDataAPICodeChanges()

- NotifySubscribers_DataAPICodeChange()
- HandleSubscriptions_DataAPICode()

---

## BowDataSchema.SaskanConcept

---

### SaskanConcept --> Code Generator Pub-Sub

_Topic Manager is_ __BowDataSchema.SaskanConcept__

- Topics
  - SaskanConcept

Listen

- Subscribe_SaskanConceptList()
- Subscribe_SaskanConceptObject()

Send

- Generic
  - AcknowledgeRequest()
  - DenyRequest()
  - AcceptRequest()

- Notify_SaskanConceptListChange()
- Publish_SaskanConceptList()
- Notify_SaskanConceptObjectChange()
- Publish_SaskanConceptObject()

Manage

- MonitorSaskanConceptChanges()
  - ListSaskanConcepts()
  - DescribeSaskanConcept()

- NotifySubscribers_SaskanConceptChange()
- HandleSubscriptions_SaskanConceptObject()

---

### SaskanConcept --> SubClass, Properties Pub-Sub

_Topic Manager is_ __BowDataSchema.SaskanConcept.SubClass__

_Topic Manager is_ __BowDataSchema.SaskanConcept.Properties__

- Topics
  - SaskanConceptSubClass
  - SaskanConceptProperties

Listen

- Generic
  - AcknowledgeRequest()
  - DenyRequest()
  - AcceptRequest()

- SubClass
  - Notify_SaskanConceptSubClassChange()
  - Publish_SaskanConceptSubClass()

- Properties
  - Notify_SaskanConceptPropertiesChange()
  - Publish_SaskanConceptProperties()

Send

- SubClass
  - Subscribe_SaskanConceptSubClassList()

- Properties
  - Subscribe_SaskanConceptProperties()

---

## BowDataSchema.SaskanConcept.SubClass

---

### Saskan SubClass --> SaskanConcept Pub-Sub

_Topic Manager is_ __BowDataSchema.SaskanConcept.SubClass__

- Topics
  - SaskanConceptSubClass

Listen

- Subscribe_SaskanConceptSubClassList()

Send

- Generic
  - AcknowledgeRequest()
  - DenyRequest()
  - AcceptRequest()

- Notify_SaskanConceptSubClassListChange()
- Publish_SaskanConceptSubClassList()

Manage

- MonitorSaskanConceptSubClassListChanges()
  - ListSaskanConceptSubClasses()

- NotifySubscribers_SaskanConceptSubClassList()
- HandleSubscriptions_SaskanConceptSubClassList()

---

## BowDataSchema.SaskanConcept.Properties

---

### Properties --> SaskanConcept Pub-Sub

_Topic Manager is_ __BowDataSchema.SaskanConcept.Properties__

- Topics
  - SaskanConceptProperties

Listen

- Subscribe_SaskanConceptProperties()

Send

- Generic
  - AcknowledgeRequest()
  - DenyRequest()
  - AcceptRequest()

- Notify_SaskanConceptPropertiesChange()
- Publish_SaskanConceptProperties()

Manage

- MonitorSaskanConceptPropertiesChanges()
  - DescribeSaskanConceptProperties()

- NotifySubscribers_SaskanConceptProperties()
- HandleSubscriptions_SaskanConceptProperties()
