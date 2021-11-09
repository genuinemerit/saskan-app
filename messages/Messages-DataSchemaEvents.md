# Message Brokers

## BowDataSchema.CodeGenerator

---

### Data Schema Request-Response Events

_Event is_ __GetDataCodeObject()__

_Approved Requestors are __BowDataAdmin.{services}__

__Receive/Listen__

- Request_CreateSaskanDataObject()

__Send__

- Response_CreateSaskanDataObject()

---

### Code Generator / Ontology Pub-Sub

_Topic Manager is_ __BowDataSchema.SaskanConcept__

- Topics
    - SaskanConcept

__Receive/Listen__

- AcknowledgeRequest()
- DenyRequest()
- AcceptRequest()
- Notify_SaskanConceptListChange()
- Notify_SaskanConceptObjectChange()
- Publish_SaskanConceptList()
- Publish_SaskanConceptObject()

__Send__

- Subscribe_SaskanConceptList()
- Subscribe_SaskanConceptObject()

---

{TAG} SQLite Code Generator

{TAG} Postgres Code Generator

{TAG} Data API Code Generator

---

## BowDataSchema.SaskanConcept

### Code Generator / Ontology Pub-Sub

_Topic Manager is_ __BowDataSchema.SaskanConcept__

- Topics
    - SaskanConcept

#### Receive/Listen

- Subscribe_SaskanConceptList()
- Subscribe_SaskanConceptObject()

#### Send

- AcknowledgeRequest()
- DenyRequest()
- AcceptRequest()
- Notify_SaskanConceptListChange()
- Notify_SaskanConceptObjectChange()
- Publish_SaskanConceptList()
- Publish_SaskanConceptObject()

__Manage__

- MonitorSaskanConceptChanges()
    - ListSaskanConcepts()
    - DescribeSaskanConcept()
- NotifySubscribers_SaskanConceptChange()
- HandleSubscriptions_SaskanConceptObject()

---

### Saskan Concept / SubClass, Properties Pub-Sub

_Topic Manager is_ __BowDataSchema.SaskanSubClass__

_Topic Manager is_ __BowDataSchema.SaskanProperties__

- Topics
    - SaskanConceptSubClass
    - SaskanConceptProperties

__Receive/Listen__

- AcknowledgeRequest()
- DenyRequest()
- AcceptRequest()
- Notify_SaskanConceptSubClassChange()
- Notify_SaskanConceptPropertiesChange()
- Publish_SaskanConceptSubClass()
- Publish_SaskanConceptProperties()

__Send__

- Subscribe_SaskanConceptSubClassList()
- Subscribe_SaskanConceptProperties()

---

## BowDataSchema.SaskanConceptSubClass

### Saskan Concept / SubClass Pub-Sub

_Topic Manager is_ __BowDataSchema.SaskanConceptSubClass__

- Topics
    - SaskanConceptSubClass

__Receive/Listen__

- Subscribe_SaskanConceptSubClassList()

__Send__

- AcknowledgeRequest()
- DenyRequest()
- AcceptRequest()
- Notify_SaskanConceptSubClassListChange()
- Publish_SaskanConceptSubClassList()

__Manage__

- MonitorSaskanConceptSubClassListChanges()
    - ListSaskanConceptSubClasses()
- NotifySubscribers_SaskanConceptSubClassList()
- HandleSubscriptions_SaskanConceptSubClassList()

---

## BowDataSchema.SaskanConceptProperties

### Saskan Concept / Properties Pub-Sub

_Topic Manager is_ __BowDataSchema.SaskanConceptProperties__

- Topics
    - SaskanConceptProperties

__Receive/Listen__

- Subscribe_SaskanConceptProperties()

__Send__

- AcknowledgeRequest()
- DenyRequest()
- AcceptRequest()
- Notify_SaskanConceptPropertiesChange()
- Publish_SaskanConceptProperties()

__Manage__

- MonitorSaskanConceptPropertiesChanges()
    - DescribeSaskanConceptProperties()
- NotifySubscribers_SaskanConceptProperties()
- HandleSubscriptions_SaskanConceptProperties()
