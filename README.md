# Spacesonic ERP Database Schema

## Database

```text
mrp_db
```

---

# MASTER DATA

## materials

### Purpose

Master κατάλογος όλων των υλικών.

### Primary Key

```text
material_code
```

### Current Fields

| Field          | Description               |
| -------------- | ------------------------- |
| material_code  | Unique material code      |
| material_name  | Material description      |
| stock_on_hand  | Current stock (temporary) |
| unit           | Unit of Measure           |
| supplier       | Default supplier          |
| lead_time_days | Default lead time         |

### Used By

* Production
* Receipts
* Dashboard
* Procurement
* Inventory Report

### Future

Το `stock_on_hand` θα μεταφερθεί στο inventory layer (`items`).

---

## models

### Purpose

Master κατάλογος προϊόντων.

---

## suppliers

### Purpose

Master κατάλογος προμηθευτών.

Primary Key

```text
supplier_id
```

---

## employees

### Purpose

Master κατάλογος εργαζομένων.

Primary Key

```text
employee_id
```

---

## production_stages

### Purpose

Ορισμός σταδίων παραγωγής.

---

## stage_inputs

### Purpose

BOM εισόδων.

---

## stage_outputs

### Purpose

BOM εξόδων.

---

# INVENTORY

## items

### Purpose

Inventory objects.

Ο πίνακας αυτός ΔΕΝ αντικαθιστά τον materials.

Αποθηκεύει inventory ανά κατάσταση.

### Primary Key

```text
item_id
```

### Unique

```text
(material_code, stage_code)
```

### Item Types

```text
RAW
WIP
FINAL
```

### Current Fields

| Field         | Description        |
| ------------- | ------------------ |
| item_id       | Inventory Item ID  |
| material_code | Material Reference |
| stage_code    | Production Stage   |
| item_name     | Description        |
| unit          | Unit               |
| item_type     | RAW / WIP / FINAL  |
| stock_on_hand | Current Inventory  |

---

## stocktransactions

### Purpose

Inventory movements.

Future source of truth.

Examples

* Receipt
* Production
* Adjustment
* Transfer
* Scrap

---

## vw_currentstock

### Purpose

Reporting View.

---

# TRANSACTIONS

## production_log

Purpose

Production history.

---

## receipts

Purpose

Receipt history.

---

## purchaseorders

Purpose

Purchase Order Header.

Status values

```text
DRAFT
OPEN
PARTIAL
RECEIVED
CLOSED
```

---

## purchaseorder_lines

Purpose

Purchase Order Lines.

---

## workorders

Purpose

Production execution.

Future implementation.

---

# PROCUREMENT

## item_suppliers

Purpose

Material ↔ Supplier mapping.

Status

Future module.

---

# SYSTEM

## audit_log

Purpose

Audit trail.

---

# RELATIONSHIPS

```text
materials
     │
     │
     ├──────────────┐
     │              │
     ▼              ▼
receipts        stage_inputs

     │

production_log
     │
     ▼

inventory

     │
     ▼

items

     │
     ▼

stocktransactions

     │
     ▼

purchaseorders

     │
     ▼

purchaseorder_lines
```

---

# Architecture Rules

Rule 1

Master data δεν ενημερώνεται από UI logic.

---

Rule 2

Όλα τα INSERT / UPDATE / DELETE περνούν από Services.

---

Rule 3

Tabs δεν περιέχουν SQL.

---

Rule 4

Inventory calculations δεν γίνονται μέσα στα tabs.

---

Rule 5

Κάθε νέα λειτουργία απαιτεί:

```text
Database

↓

Service

↓

UI

↓

Testing

↓

Documentation
```
